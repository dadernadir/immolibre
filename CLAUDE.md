# ImmoLibre.be — mémoire du projet

Fichier lu automatiquement par Claude Code au démarrage d'une session sur ce dépôt.
À coller aussi en début de conversation Claude classique pour donner le contexte.
Dernière mise à jour : 11/11/2026.

## Le projet

- Site immobilier belge gratuit (particuliers et agences) : https://immolibre.be
- Hébergement : **Netlify** (déploiement par glisser-déposer d'un zip).
- Base de données, comptes, stockage des photos : **Supabase**, projet `svjkpexgckghrtrfowtq` (région eu-west-1).
- E-mails : **Resend** (SMTP des e-mails Supabase + fonctions d'envoi).
- Paiements : **Stripe** (webhook `stripe-webhook` qui active les abonnements et les boosts).
- Appli Android : TWA générée avec PWABuilder, package `be.immolibre.twa`.
- Langues : français, blog aussi en néerlandais (`/nl/blog/`).

## Règles de travail (importantes)

1. **Toujours partir de la dernière version déployée.** Avant toute modification, demander le dernier zip.
   Plusieurs conversations ont travaillé en parallèle : une version peut en écraser une autre.
2. Une version = un zip `immolibre-deploy-vXXX.zip`. Changer `CACHE_NAME` dans `sw.js` à chaque version
   (ex. `immolibre-v129`) pour que les visiteurs récupèrent les nouveaux fichiers.
3. **À chaque nouvelle version, régénérer les pages d'annonce** avec `tools/gen_annonces.py` (voir plus bas).
   Sinon les annonces publiées depuis la dernière version n'ont pas de page (elles restent accessibles
   via la page 404 de secours, mais Google ne les voit pas).
4. **Ne jamais régénérer l'appli Android avec une nouvelle clé** sans en parler : Google refuserait les mises à jour.
5. Ne jamais mettre de secret (mot de passe, keystore, clé API privée) dans le site ou le dépôt.
   La clé Supabase publique (anon) présente dans `index.html` est normale.

## Version actuelle : v143 (contrôlée le 11/11/2026, prête à déployer)

Le dépôt GitHub (branche `ccr-f1381ce0-0y9wxt`) contient les fichiers du site en **v143** (identiques au zip v143).
`tools/gen_annonces.py` est dans le dépôt (avec l'échappement `\u003c` du JSON-LD ajouté le 22/10).

Historique récent :
- **v126** : vitesse (supabase-js dans `/vendor/`, Leaflet et jsPDF chargés à la demande, cache Service Worker).
- **v127** : ajout de l'empreinte de la clé de signature Google Play dans `assetlinks.json`.
- **v128** : pages statiques d'annonce `/annonce/ID` + sitemaps nettoyés (référencement Google).
- **v129** : page `404.html` de secours + pages d'annonce régénérées.
- **v130** (déployée le 24/10/2026) : bloc vert « maquette A » — titre « L'immobilier belge sans commission »,
  sous-titre masqué, boutons Acheter · Louer · Filtres (synchronisés avec Tout / Vente / Location), NL traduit ;
  445 pages d'annonce régénérées ; cache `immolibre-v130`.
- **v131** (24/10/2026, préparée, pas encore déployée) : slogan du haut resserré sur téléphone (masqué sous 340 px)
  pour ne plus passer sous le bouton 🌙 ; recherche « Ville ou code postal » (NL « Stad of postcode ») ;
  pages d'annonce vérifiées à jour (mêmes 445, aucune ajoutée ni retirée) ; cache `immolibre-v131`.
  Note : Supabase n'est pas joignable par `--fetch` depuis la session « Check-up complet » (proxy) ;
  la vérification s'y fait via l'accès SQL en lecture.
- **v132** (24/10/2026, contrôlée) : compteur d'annonces relu dans la base avant chaque publication et limité aux
  annonces en ligne (comme `trg_limite_annonces`) ; message clair « Limite atteinte » (lien « Upgrader » masqué
  dans l'appli Android) ; cache `immolibre-v132`.
- **v133** (24/10/2026, contrôlée) : remise en ligne d'une annonce vendue/louée au-delà de la limite → message clair
  au lieu de « LIMITE_ANNONCES:2 », liste « Mes annonces » remise dans son état réel, compteur relu après chaque
  changement de statut ; cache `immolibre-v133`.
- **v134** (déployée, fonctionne) : bouton « Booster » de la fiche (agences) → fonction serveur `use_agency_boost`
  (avant : mise à jour directe de `boosted`, ignorée en silence par `protect_boost_columns` alors que le site affichait
  « boostée ! », cas de l'annonce #671) ; messages de refus clairs ; « déjà boostée jusqu'au … » ;
  448 pages d'annonce (670, 671, 672 ajoutées) ; cache `immolibre-v134`.
  ✅ Annonce #671 boostée jusqu'au 03/11/2026 (vérifié le 25/10).

## Récap v134 → v142 (au 11/11/2026, transmis par Nadir)

**Dernière version déployée : v142.** Netlify : projet `playful-chebakia-520v56` (domaine immolibre.be).
Si la page Netlify reste blanche sur le téléphone : navigation privée (cookies Netlify corrompus).
Table des profils = **`profils`** (pas `profiles`), admin = `profils.is_admin = true`.
Ne jamais supprimer de données sans OK explicite de Nadir.
Ne jamais écrire dans ce dépôt l'adresse e-mail d'un membre, d'un client ou d'un tiers (données personnelles).

| Version | Contenu |
|---|---|
| v134 | Bouton « Booster » agences : vrai appel RPC `use_agency_boost` (quota, limite simultanée, déjà boostée). |
| v135 | Header masqué en descendant, réaffiché en remontant (sticky, z-index 60). |
| v136 | Tri : `boosted desc → tri_visible desc → created_at desc` ; une annonce sans photo garde sa place 7 jours. Repli sur `has_photos` si `tri_visible` absent. Avertissement à la publication sans photo. |
| v137 | Bandeau « 📱 Testez l'app en avant-première » (navigateurs Android hors TWA, FR/NL) → `contacts` sujet `Testeur Android`. |
| v138 | IndexNow (Bing) : clé `2afb14d90df34b60d6e941df2d6c1eca.txt` à la racine, bouton admin « 📡 Prévenir Bing » + envoi auto des nouvelles URL (mémoire `localStorage`), via l'edge function `indexnow`. |
| v139 | Régénération sans l'annonce 482 (affaire Godin). |
| v140 | Régénération sans les 97 annonces Godin passées hors ligne. |
| v141 | Onglet admin **✉️ Contact** : « 📱 Testeurs Android : N / 12 » + « Copier tout », et messages du formulaire de contact. |
| v142 | Compteur de vues réparé (RPC `increment_annonce_views`, 1 fois par annonce et par session) ; toasts de debug retirés. |
| v143 | Photos compressées une par une (avant : en parallèle, des téléphones saturaient et envoyaient l'original de 4 Mo) + décodage de secours via `<img>` + type vide reconnu par l'extension. Annonces `hors_ligne` exclues de la liste, de la carte et de la page agence, même pour l'admin ; bandeau « ⚫ Hors ligne » dans « Mes annonces ». 404 pages d'annonce (bon générateur). |

**Supabase**
- `tri_visible(annonces)` : a des photos OU créée il y a moins de 7 jours.
- Statut `hors_ligne` ajouté (`annonces_status_check`). Lecture : une seule règle `annonces_read_public` =
  `status is distinct from 'hors_ligne' OR auth.uid() = user_id OR admin` (vérifié le 11/11).
- `annonces_hors_ligne_log` : journal des passages hors ligne (ancien statut) pour restaurer.
- Démarcheurs : `expediteurs_bloques(email, raison)` + trigger `trg_filtrer_expediteurs_bloques` (BEFORE INSERT
  sur `messages`, message ignoré en silence) + `messages_bloques_log`. 1 adresse bloquée (démarcheur « estimation
  gratuite »). Tables en RLS sans policy : privées (vérifié le 11/11).
- Edge functions : `indexnow` (admin seulement, URL https://immolibre.be uniquement) ; `supprimer-compte` désactivée (410).
- Le compte admin porte des annonces recopiées d'agences (Inforim 49, La Marquise 17, IGG 12, MCA 10,
  La Priorité 8, Eco-Immo 1) **sans accord écrit**.

**Modération / RGPD** (détails nominatifs : uniquement dans Supabase et la messagerie de Nadir)
- Annonce 443 (arnaque, studio à Ixelles) supprimée ; compte de l'auteur banni.
- Affaire Godin : 482 supprimée ; **97 annonces Godin en `hors_ligne`** (accord oral seulement). Appel avec M. Godin :
  remettre en ligne (biens encore disponibles, idéalement via un compte agence qu'ils gèrent) ou supprimer.
- 2 suppressions RGPD faites (comptes, profils, photos, messages) ; les demandes sont conservées comme preuve.

**Emails** : `contact@immolibre.be` chez Combell, redirigé vers la boîte Gmail de Nadir (vérifié le 11/11).

**Trafic** : Google ≈ 20 visites/jour (légère baisse, passage aux URL `/annonce/ID`) ; Bing exploration max + IndexNow ;
Meta : paiement refusé, compte pub suspendu (carte à mettre à jour + vérification).

**App Android** : bundle v1 dans la bibliothèque Play. Test fermé : 12 testeurs × 14 jours. Nadir a 6 adresses.
À 12 : configurer le test fermé Alpha, s'arrêter avant « Envoyer à Google pour examen » (accord de Nadir).

**À faire / idées**
1. v143 : masquer les annonces `hors_ligne` de la grille d'accueil même pour l'admin connecté ; les garder dans
   « Mes annonces » et le panneau admin, avec le libellé « Hors ligne » dans le menu des statuts.
2. Résultat de l'appel Godin → restaurer depuis `annonces_hors_ligne_log`, ou supprimer.
3. Accord écrit (un email suffit) des autres agences recopiées.
4. Email automatique à Nadir à chaque nouveau signalement.
5. Démarchage d'agences (hausse des tarifs Immoweb 2027) : ImmoLibre comme complément gratuit, avec statistiques réelles.
6. Option : règle anti-démarchage dans les CGU.

**Allègement des photos existantes (11/11/2026)** : photos > 500 Ko réduites à 1600 px max (≈ 20× plus légères),
même adresse. Originaux sauvegardés dans `photos/originaux/` (bucket **public** : ils restent téléchargeables par
quiconque devine l'adresse, avec leurs métadonnées éventuelles, dont la position GPS des photos de téléphone).
→ Une fois le résultat vérifié, supprimer `originaux/` (avec l'OK de Nadir) ou le déplacer dans un bucket privé.
⚠️ Un propriétaire peut remettre lui-même en « Disponible » une annonce passée `hors_ligne` par l'admin
(sans conséquence tant que ce sont les annonces du compte admin ; à bloquer avant de retirer l'annonce d'un autre membre).

**Points relevés au contrôle de la v142 (session « Check-up complet », 11/11)**
- Pages 275 et 615 : JSON-LD avec « < » brut → la v142 a été générée avec l'**ancien** `gen_annonces.py`.
  Utiliser celui du dépôt (`tools/gen_annonces.py`, encode « < » en `<`).
- 403 annonces en ligne pour 402 pages (1 annonce publiée après la génération : couverte par `404.html`).
- `increment_annonce_views` reste appelable par n'importe qui : les vues peuvent être gonflées par un appel direct
  (la limite « 1 fois par session » est côté navigateur). À garder en tête avant de vendre des « statistiques réelles ».

### Référencement Google (v128 → v129)

Problème constaté dans Search Console (16/10/2026) : 125 pages indexées, 467 non indexées.
Cause : une annonce n'avait pas de vraie page. `/?annonce=ID` renvoyait le même `index.html` que l'accueil
(même titre, canonical vers `/`), Google voyait un doublon de l'accueil.

Ce qui a été fait :
- **444 pages statiques** `annonce/<id>.html`, servies à l'adresse `https://immolibre.be/annonce/<id>`.
  Chaque page : titre (« Maison à vendre à Liège — 275 000 € | ImmoLibre »), meta description, canonical propre,
  Open Graph, données structurées `RealEstateListing` + fil d'Ariane, photos (6 max), caractéristiques,
  description, bouton « Voir l'annonce complète et contacter l'annonceur » → `/?annonce=<id>`.
  Aucune donnée privée (pas de téléphone, e-mail ni propriétaire ; seulement les champs publics).
- **`sitemap-annonces.xml` est maintenant un fichier statique** (adresses `/annonce/<id>`).
  L'ancien proxy vers la fonction Supabase `sitemap-annonces` a été **retiré de `netlify.toml`**.
- **`sitemap.xml`** : retrait des 4 adresses `?route=carte|apropos|cgu|privacy` (canonical vers l'accueil). 31 adresses.
- **`index.html`** : `<script id="static-annonces">window.__STATIC_ANNONCES=new Set([...])</script>` dans le `<head>`
  (liste des annonces qui ont une page). Dans `updateSeoForListing`, la canonical d'une annonce devient
  `/annonce/<id>` si elle a une page, sinon reste `/?annonce=<id>`.
- **`404.html`** : si l'adresse est `/annonce/<id>` ou `/annonces/<id>` sans page, redirection JavaScript vers
  `/?annonce=<id>`. Sinon page « Page introuvable » aux couleurs d'ImmoLibre. Statut 404 + `noindex`.
- À faire côté Search Console après déploiement : renvoyer `sitemap-annonces.xml`, puis « Valider la correction »
  sur « Page en double » et « Autre page avec balise canonique correcte ». Comparer les chiffres vers le 05/11/2026.

### Générateur des pages d'annonce : `tools/gen_annonces.py`

```
python3 -I tools/gen_annonces.py --site DOSSIER_DE_LA_VERSION --fetch --version v130
```
- Lit Supabase (REST, clé publique trouvée dans `index.html`) : annonces au statut `disponible` ou `option`.
  Le domaine `svjkpexgckghrtrfowtq.supabase.co` doit être autorisé dans l'environnement de Claude (fait le 22/10).
- Modifie le dossier sur place : pages `annonce/*.html` (supprime les anciennes), `sitemap-annonces.xml`,
  `sitemap.xml` (retire les `?route=`), `index.html` (liste des pages + canonical), `sw.js` (`CACHE_NAME`).
- Option `--data fichier.json` au lieu de `--fetch` pour travailler hors ligne.

### Sécurité et site (session « Check-up complet », 08→20/10/2026)

**Sécurité Supabase (appliqué en production)**
- Les membres ne peuvent plus s'attribuer eux-mêmes un abonnement (is_agence / is_premium / is_pro / stripe_*) :
  trigger `protect_is_admin` étendu + trigger `protect_profil_insert`. Seuls l'admin, le webhook Stripe et
  `use_agency_boost` peuvent modifier ces colonnes. Les 9 profils partenaires sans Stripe sont voulus (mis par l'admin).
- Les profils (e-mails, Stripe) ne sont plus lisibles publiquement ; l'admin les voit via `est_admin()`.
- Plus de publication d'annonce sans compte (policy `pub_insert` neutralisée).
- Statistiques de visites lisibles par l'admin seulement.
- Stockage : envois photos/vidéos réservés aux membres connectés ; photos ≤ 10 Mo (images), vidéos ≤ 50 Mo.
- Scripts SQL de référence : `supabase/securite-checkup-v124.sql` et `supabase/securite-checkup-v124-stockage.sql`.
- **Limite d'annonces en ligne par formule (24/10/2026, appliquée par Nadir après des annonces d'arnaque)** :
  trigger `trg_limite_annonces` → Gratuit 2 · Starter 3 · Premium 5 · Agence et admin illimité ; seules
  « disponible » et « option » comptent. Erreur renvoyée : `LIMITE_ANNONCES:<limite>`. Script : `supabase/limite-annonces-v132.sql`.
  Côté site : entièrement aligné depuis v133.

**Fonctions Supabase (edge functions) verrouillées**
- `send-message-email` et `send-alert-confirmation` relisent le message / l'alerte en base (refus si absent ou > 5 min).
  Confirmations d'alerte : 3 max par adresse et par 24 h. Notifications de message : 5 max / 10 min par destinataire.
- `weekly-report-email` : 1 envoi max tous les 6 jours (table `rapport_hebdo_envois`).
- `audit-real-photos` : réservée à l'admin (ou clé service_role).
- La fonction `sitemap-annonces` existe toujours mais n'est plus utilisée par le site (depuis v128).

**Site**
- Faille XSS corrigée (carte, favoris, import d'annonce par URL).
- CSP complétée dans `netlify.toml` : vidéos YouTube/TikTok/Vimeo, vidéos Supabase, aperçus blob:, worker HEIC.
- Erreurs d'inscription Supabase traduites en français.
- Vitesse : supabase-js hébergé dans `/vendor/` (version figée 2.117.2) ; Leaflet et jsPDF chargés à la demande ;
  Service Worker qui affiche la version en cache après 3,5 s si le réseau traîne ; dernières annonces de l'accueil
  mémorisées dans le navigateur et affichées immédiatement.

## Appli Android (Play Store) — en cours

**Clés (vérifiées le 21/10/2026 dans la console et sur les fichiers) :**
- **Clé de signature Google Play** (celle qui signe l'appli installée) : SHA-256
  `D8:AE:B9:0B:E8:14:82:90:48:4B:9A:D7:3D:AC:84:62:96:08:C1:E5:07:E9:0D:FC:2B:67:4F:26:91:05:67:C1`.
  C'est **l'empreinte indispensable** dans `assetlinks.json` (ajoutée en v127).
- **`signing.keystore`** (zip PWABuilder, alias `my-key-alias`, mot de passe dans `signing-key-info.txt`, à garder hors du dépôt) :
  SHA-1 `D9:2B:2F:A6:…:92:69`, SHA-256 `FC:B0:0B:ED:…:9A:76`. C'est la clé d'importation choisie pour la réinitialisation.
  (Attention : l'ancien document disait que FC:B0 était la clé Google : c'est faux, c'est cette clé locale.)
- Ancien `.aab` envoyé aux tests : signé SHA-1 `78:0E:C0:35…` / SHA-256 `63:48:85:50…` (keystore introuvable).
- `B9:9D:0F:30…` : ancienne clé (premier zip PWABuilder).
- `assetlinks.json` contient les 4 empreintes (D8:AE, FC:B0, B9:9D, 63:48). Servi à `/.well-known/assetlinks.json`.

**Réinitialisation de la clé d'importation :** formulaire ouvert dans la console
(Protégé avec Play → Protection Play Store → Gérer la signature d'application Play → Clé d'importation →
« Demander la réinitialisation », motif « J'ai perdu ma clé d'importation »).
Il reste à **joindre `upload_certificate.pem`** (certificat public de `signing.keystore`) et à cliquer
« Envoyer une demande » : à faire par Nadir (Chrome bloque l'envoi de `.pem` par l'assistant).
Après accord de Google (quelques jours) : envoyer `ImmoLibre.aab` signé avec `signing.keystore` dans « Tests fermés ».

**Fiche et déclarations Play :**
- Fait : fiche (titre, descriptions, icône, bannière, captures), politique de confidentialité, identifiant publicitaire
  (« non »), classification, **Sécurité des données** (collectées : nom, e-mail, téléphone, messages dans l'appli,
  photos et vidéos, activité dans l'appli ; rien de partagé ; localisation et paiements non collectés ;
  chiffrement en transit ; suppression via https://immolibre.be/suppression-compte).
- À faire / vérifier dans « Vue d'ensemble de la publication » : catégorie de contenu, cible et contenu,
  déclaration relative aux annonces, applis de santé, catégorie « Maison et intérieur », instructions de connexion
  (compte de test pour Google), déclarations « Applis gouvernementales » et « Fonctionnalités financières ».
- Test fermé : si compte développeur personnel récent → 12 testeurs pendant 14 jours avant la production.
- Les options payantes (boosts, formules agences) sont masquées dans l'appli (`?app=android`), règle Google Play.

## Publicités Meta (suivi)

- Campagne 1 « Nouvelle Trafic Campagne » (maison brique) → `?utm_source=facebook-ads`.
- Campagne 2 « Votre bien mérite d'être vu » (affiche « Chaque jour ! ») → `?utm_source=facebook-ads-affiche`.
- Décision : garder les deux, ne pas toucher au budget. Comparer les visites par source dans la table
  `visit_sources` (Supabase) après une semaine de données.

## Ce qui reste à faire

1. Play Store : envoyer la demande de réinitialisation (joindre `upload_certificate.pem`), puis tests fermés, compte de test, déclarations restantes.
2. Search Console : renvoyer `sitemap-annonces.xml`, valider les corrections, comparer vers le 05/11/2026.
3. Régénérer les pages d'annonce à chaque version (`tools/gen_annonces.py`).
4. Idée : vignettes photo gratuites (≈ 30 Ko) créées à l'envoi pour alléger l'accueil et les pages d'annonce
   (photos actuelles ≈ 200 Ko en moyenne). Alternative payante : transformations d'images Supabase.
5. ✅ Défauts d'affichage du haut de page corrigés en v131.
6. À surveiller : quota Resend (forfait gratuit ≈ 100 e-mails/jour) ; bande passante Supabase (Organization → Usage → Egress).
