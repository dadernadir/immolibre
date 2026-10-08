-- ════════════════════════════════════════════════════════════════════════════
-- ImmoLibre — correctifs de sécurité Supabase (check-up v124, 08/10/2026)
--
-- PARTIE 1/2 (base de données). À exécuter dans Supabase → SQL Editor, d'un seul bloc.
-- La partie stockage est dans securite-checkup-v124-stockage.sql.
-- Tout est dans une transaction : en cas d'erreur, rien n'est modifié.
-- Après exécution : tester connexion, publication d'annonce (photos + vidéo),
-- boost agence, panneau admin (membres + statistiques).
-- ════════════════════════════════════════════════════════════════════════════
begin;

-- ─── 0. Fonction utilitaire : l'utilisateur connecté est-il admin ? ─────────
-- SECURITY DEFINER pour pouvoir l'utiliser dans les policies de « profils »
-- sans récursion infinie.
create or replace function public.est_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select coalesce((select is_admin from public.profils where id = auth.uid()), false);
$$;
revoke execute on function public.est_admin() from public, anon;
grant execute on function public.est_admin() to authenticated;

-- ─── 1. CRITIQUE : abonnements payants gratuits ─────────────────────────────
-- Aujourd'hui, la policy « profils_update_own » laisse un membre modifier sa
-- propre ligne : seul is_admin est protégé. N'importe qui peut donc se mettre
-- is_agence / is_premium / is_pro = true depuis la console du navigateur et
-- obtenir les boosts agence sans payer. On protège toutes les colonnes de
-- facturation : seuls le webhook Stripe (service_role), les fonctions internes
-- (use_agency_boost…) et les admins peuvent les changer.
-- La fonction devient SECURITY INVOKER : current_user vaut alors 'anon' ou
-- 'authenticated' pour un appel direct depuis le site, et le propriétaire de
-- la fonction quand c'est use_agency_boost (SECURITY DEFINER) qui écrit.
create or replace function public.protect_is_admin()
returns trigger
language plpgsql
security invoker
set search_path = public
as $$
begin
  if current_user in ('anon', 'authenticated') and not public.est_admin() then
    if new.is_admin                is distinct from old.is_admin
    or new.is_agence               is distinct from old.is_agence
    or new.is_starter              is distinct from old.is_starter
    or new.is_pro                  is distinct from old.is_pro
    or new.is_premium              is distinct from old.is_premium
    or new.stripe_customer_id      is distinct from old.stripe_customer_id
    or new.stripe_subscription_id  is distinct from old.stripe_subscription_id
    or new.agency_boosts_used      is distinct from old.agency_boosts_used
    or new.agency_boosts_month     is distinct from old.agency_boosts_month
    then
      raise exception 'Modification réservée à ImmoLibre (abonnement / droits)';
    end if;
  end if;
  return new;
end;
$$;
-- (le trigger trg_protect_is_admin existant appelle déjà cette fonction)

-- Même faille à l'inscription : « user_insert_own_profil » permettrait de créer
-- son profil directement en premium / admin. On force des valeurs neutres.
create or replace function public.protect_profil_insert()
returns trigger
language plpgsql
security invoker
set search_path = public
as $$
begin
  if current_user in ('anon', 'authenticated') then
    new.is_admin := false;
    new.is_agence := false;
    new.is_starter := false;
    new.is_pro := false;
    new.is_premium := false;
    new.stripe_customer_id := null;
    new.stripe_subscription_id := null;
    new.agency_boosts_used := 0;
    new.agency_boosts_month := null;
  end if;
  return new;
end;
$$;
drop trigger if exists trg_protect_profil_insert on public.profils;
create trigger trg_protect_profil_insert
  before insert on public.profils
  for each row execute function public.protect_profil_insert();

-- ─── 2. CRITIQUE : fuite des e-mails de tous les membres ────────────────────
-- « Lecture publique profils » (using true) expose à tout visiteur l'e-mail,
-- les identifiants Stripe et les droits de chaque membre. Le site ne lit que
-- son propre profil (policy profils_read_own) ; le panneau admin lit tout.
drop policy if exists "Lecture publique profils" on public.profils;
create policy profils_admin_read on public.profils
  for select to authenticated
  using (public.est_admin());

-- ─── 3. CRITIQUE : publication d'annonces sans compte ───────────────────────
-- « pub_insert » (with check true) annule la règle « auth.uid() = user_id » :
-- un anonyme peut créer des annonces au nom de n'importe quel membre. Combiné
-- à l'absence d'échappement corrigée dans index.html, c'était une porte
-- d'entrée pour du code malveillant affiché à tous les visiteurs.
drop policy if exists pub_insert on public.annonces;

-- ─── 4. Statistiques de visites lisibles par tous ───────────────────────────
-- « Lecture visites public » annule « visites_read_none ». Seul l'admin lit.
drop policy if exists "Lecture visites public" on public.visites;
create policy visites_admin_read on public.visites
  for select to authenticated
  using (public.est_admin());

drop policy if exists "Anyone can read aggregated stats" on public.visit_sources;
create policy visit_sources_admin_read on public.visit_sources
  for select to authenticated
  using (public.est_admin());

-- ─── 6. Fonctions exposées inutilement ──────────────────────────────────────
-- Fonctions de trigger : jamais appelées directement par le site.
revoke execute on function public.create_profil_on_signup() from public, anon, authenticated;
revoke execute on function public.protect_is_admin() from public, anon, authenticated;
revoke execute on function public.protect_profil_insert() from public, anon, authenticated;
-- Boosts : réservés aux membres connectés (les fonctions vérifient déjà les droits).
revoke execute on function public.admin_toggle_boost(bigint, boolean) from public, anon;
revoke execute on function public.use_agency_boost(bigint) from public, anon;

-- search_path figé (alerte « Function Search Path Mutable » de Supabase).
alter function public.create_profil_on_signup() set search_path = public;
alter function public.track_price_change() set search_path = public;

commit;
