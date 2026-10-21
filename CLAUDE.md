# ImmoLibre.be — mémoire du projet

Fichier lu automatiquement par Claude Code au démarrage d'une session sur ce dépôt.
À coller aussi en début de conversation Claude classique pour donner le contexte.
Dernière mise à jour : 21/10/2026.

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
   (ex. `immolibre-v126`) pour que les visiteurs récupèrent les nouveaux fichiers.
3. **Ne jamais régénérer l'appli Android avec une nouvelle clé** sans en parler : Google refuserait les mises à jour.
4. Ne jamais mettre de secret (mot de passe, keystore, clé API) dans le site ou le dépôt.

## Version actuelle : v127 (21/10/2026)

Zip de référence : `immolibre-deploy-v127.zip` (CACHE_NAME `immolibre-v127`).
v127 = v126 + clé de signature Google `D8:AE…` ajoutée dans `assetlinks.json`. Rien d'autre ne change.
Le dépôt (branche ci-dessous) est identique au zip v127.

Branche GitHub : `ccr-f1381ce0-0y9wxt`.

### Ce qui a été fait (session « Check-up complet », 08→20/10/2026)

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

**Site**
- Faille XSS corrigée (carte, favoris, import d'annonce par URL).
- CSP complétée dans `netlify.toml` : vidéos YouTube/TikTok/Vimeo, vidéos Supabase, aperçus blob:, worker HEIC.
- Erreurs d'inscription Supabase traduites en français (mot de passe trop courant, quota, délai de 60 s…).
- Vitesse : supabase-js hébergé dans `/vendor/` (version figée 2.117.2) ; Leaflet et jsPDF chargés à la demande ;
  Service Worker qui affiche la version en cache après 3,5 s si le réseau traîne ; dernières annonces de l'accueil
  mémorisées dans le navigateur et affichées immédiatement.
- v125 (autre conversation) : bouton « Publier » masqué quand une fenêtre est ouverte — intégré dans la v126.

**Appli Android**
- `assetlinks.json` contient 4 empreintes SHA-256 :
  - `D8:AE:B9:0B:…:67:C1` = **clé de signature Google Play** (lue dans la Play Console le 21/10/2026).
    C'est elle qui permet l'ouverture plein écran de l'appli installée depuis le Play Store.
  - `FC:B0:0B:ED:…:9A:76` = SHA-256 du keystore local `playpkg/signing.keystore` = clé d'importation.
  - `63:48:85:50:…:F6:4C` = clé qui signe le fichier `ImmoLibre.aab` du 03/10/2026. **Aucun keystore trouvé** pour elle.
  - `B9:9D:0F:30:…:B9:93` = ancienne clé (probablement le tout premier zip PWABuilder).
- Les options payantes (boosts, formules agences) sont masquées dans l'appli (`?app=android`), règle Google Play.

## Ce qui reste à faire

1. **Play Store — clés** (à faire dans cet ordre) :
   a. Lire dans la Play Console (Protégé avec Play → Protection Play Store → Signature d'application Play) :
      - ✅ clé de signature d'application = `D8:AE…`, ajoutée dans `assetlinks.json` (v127) ;
      - SHA-256 du « Certificat de la clé d'importation » (s'il existe) ;
      - le SHA1 « attendu » indiqué dans le message de refus du `.aab`.
   b. Si la clé d'importation attendue = `FC:B0…` (signing.keystore local) → **pas de réinitialisation** :
      re-signer / régénérer le `.aab` avec `playpkg/signing.keystore`.
   c. Sinon → réinitialiser la clé d'importation avec un certificat exporté de `signing.keystore`
      (PAS avec `upload_certificate.pem` de 63:48, dont la clé privée est introuvable), puis re-signer le `.aab`.
2. **Test fermé** : si compte développeur personnel récent → 12 testeurs pendant 14 jours avant la production.
3. **Accès à l'appli** : créer un compte de test (e-mail + mot de passe) pour l'équipe de Google.
4. Catégorie Play Store : « Maison et intérieur ». Sécurité des données : e-mail, téléphone, photos, messages,
   position approximative ; suppression de compte : https://immolibre.be/suppression-compte ;
   confidentialité : https://immolibre.be/confidentialite.
5. Idée proposée, pas encore faite : vignettes photo gratuites (≈ 30 Ko) créées à l'envoi pour alléger l'accueil
   (photos actuelles ≈ 200 Ko en moyenne, 5 061 photos). Alternative payante : transformations d'images Supabase
   (forfait Pro 25 $/mois + 5 $ / 1 000 photos).
6. À surveiller : quota Resend (forfait gratuit ≈ 100 e-mails/jour, partagé entre inscriptions, messages et alertes) ;
   bande passante Supabase (Organization → Usage → Egress).
