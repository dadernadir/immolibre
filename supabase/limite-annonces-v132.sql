-- ImmoLibre v132 : limite du nombre d'annonces EN LIGNE par formule, vérifiée côté serveur.
-- ✅ Appliqué en production par Nadir (vérifié le 24/10/2026 : trigger trg_limite_annonces actif).
-- Gratuit 2 · Starter 3 · Premium 5 · Agence et admin : illimité.
-- Seules les annonces « disponible » et « option » comptent (vendu / loué ne comptent pas).

create or replace function public.check_limite_annonces()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  v_agence  boolean;
  v_premium boolean;
  v_starter boolean;
  v_admin   boolean;
  v_limite  integer;
  v_nb      integer;
begin
  -- Seules les annonces qui deviennent visibles sont concernées
  if new.status not in ('disponible', 'option') then
    return new;
  end if;
  -- En modification : seulement si l'annonce repasse en ligne (ex. « vendu » -> « disponible »)
  if tg_op = 'UPDATE' then
    if old.status in ('disponible', 'option') and old.user_id is not distinct from new.user_id then
      return new;
    end if;
  end if;
  if new.user_id is null then
    return new;
  end if;

  -- Une publication à la fois par compte (deux envois simultanés ne passent pas tous les deux)
  perform pg_advisory_xact_lock(hashtext('limite_annonces:' || new.user_id::text));

  select coalesce(is_agence, false), coalesce(is_premium, false), coalesce(is_starter, false), coalesce(is_admin, false)
    into v_agence, v_premium, v_starter, v_admin
  from public.profils where id = new.user_id;

  if coalesce(v_agence, false) or coalesce(v_admin, false) then
    return new;
  end if;

  v_limite := case
    when coalesce(v_premium, false) then 5
    when coalesce(v_starter, false) then 3
    else 2
  end;

  select count(*) into v_nb
  from public.annonces
  where user_id = new.user_id
    and status in ('disponible', 'option')
    and id is distinct from new.id;

  if v_nb >= v_limite then
    raise exception 'LIMITE_ANNONCES:%', v_limite
      using errcode = 'P0001',
            hint = 'Limite d''annonces en ligne atteinte pour cette formule.';
  end if;

  return new;
end;
$$;

revoke all on function public.check_limite_annonces() from public, anon, authenticated;

drop trigger if exists trg_limite_annonces on public.annonces;
create trigger trg_limite_annonces
  before insert or update of status, user_id on public.annonces
  for each row execute function public.check_limite_annonces();
