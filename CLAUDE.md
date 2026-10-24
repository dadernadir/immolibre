# ImmoLibre.be — mémoire du projet

Fichier lu automatiquement par Claude Code au démarrage d'une session sur ce dépôt.
À coller aussi en début de conversation Claude classique pour donner le contexte.
Dernière mise à jour : 24/10/2026.

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

## Version actuelle : v130 (déployée le 24/10/2026, accueil vérifié sur téléphone)

Le dépôt GitHub (branche `ccr-f1381ce0-0y9wxt`) contient les fichiers du site en **v130** (identiques au zip v130).
`tools/gen_annonces.py` est dans le dépôt (avec l'échappement `\u003c` du JSON-LD ajouté le 22/10).

Historique récent :
- **v126** : vitesse (supabase-js dans `/vendor/`, Leaflet et jsPDF chargés à la demande, cache Service Worker).
- **v127** : ajout de l'empreinte de la clé de signature Google Play dans `assetlinks.json`.
- **v128** : pages statiques d'annonce `/annonce/ID` + sitemaps nettoyés (référencement Google).
- **v129** : page `404.html` de secours + pages d'annonce régénérées.
- **v130** (déployée le 24/10/2026) : bloc vert « maquette A » — titre « L'immobilier belge sans commission »,
  sous-titre masqué, boutons Acheter · Louer · Filtres (synchronisés avec Tout / Vente / Location), NL traduit ;
  445 pages d'annonce régénérées ; cache `immolibre-v130`.

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
5. Petits défauts d'affichage vus sur téléphone (antérieurs à v130) : slogan du haut qui passe sous le bouton 🌙 ;
   texte de recherche coupé (« Ville, commune, code pos… »).
6. À surveiller : quota Resend (forfait gratuit ≈ 100 e-mails/jour) ; bande passante Supabase (Organization → Usage → Egress).
