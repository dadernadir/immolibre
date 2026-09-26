# Fiche Google Play — ImmoLibre

Textes à copier-coller dans la Play Console (Présence sur le Store → Fiche principale).
Limites de Google : titre 30 caractères, description courte 80, description complète 4 000.

## Nom de l'application (30 max)

ImmoLibre: Immobilier Belgique

## Description courte (80 max)

Achetez, louez ou vendez en Belgique sans agence ni commission. 100 % gratuit.

## Description complète (4 000 max)

ImmoLibre, c'est l'immobilier belge entre particuliers : gratuit, simple et sans commission.

Vous vendez ou louez un bien ? Publiez votre annonce gratuitement en quelques minutes, avec photos et vidéos, et échangez directement avec les personnes intéressées. Vous cherchez une maison, un appartement ou un kot ? Parcourez les annonces partout en Belgique et contactez le propriétaire en direct.

🏠 POUR LES ACHETEURS ET LOCATAIRES
• Des annonces de maisons, appartements, studios, terrains, commerces et garages dans toute la Belgique
• Des filtres précis : prix, nombre de chambres, type de bien, ville
• « Près de moi » : les biens autour de vous, dans le rayon de votre choix
• La carte interactive pour visualiser les biens par quartier
• Des favoris pour garder les annonces qui vous plaisent
• Des alertes pour être prévenu dès qu'un bien correspond à votre recherche
• La messagerie intégrée et les demandes de visite en un clic

🔑 POUR LES VENDEURS ET PROPRIÉTAIRES
• Une annonce gratuite, sans commission sur la vente ou la location
• Des photos et vidéos pour mettre votre bien en valeur
• Les messages des intéressés directement dans l'application
• Des notifications pour ne manquer aucun contact
• La gestion de vos annonces et visites depuis votre compte

📚 DES OUTILS ET GUIDES GRATUITS
• Un calculateur de frais de notaire en Belgique (Wallonie, Bruxelles, Flandre)
• Des guides pratiques : certificat PEB, estimation du prix, vente sans agence, kots étudiants à Bruxelles, Liège, Louvain-la-Neuve, Namur, Mons…

🇧🇪 100 % BELGE, 100 % TRANSPARENT
• 0 € de commission : vous gardez tout le fruit de votre vente
• Pas de publicité ciblée, vos données ne sont jamais vendues
• Données hébergées dans l'Union européenne, dans le respect du RGPD

ImmoLibre est une plateforme de mise en relation entre particuliers. Les agences immobilières qui l'utilisent doivent disposer des agréments requis (IPI).

Une question ? contact@immolibre.be

## Informations de la fiche

- Catégorie : Maison et intérieur (ou « Style de vie »)
- Tags : Immobilier, Location, Achat de maison
- E-mail de contact : contact@immolibre.be
- Site web : https://immolibre.be
- Règles de confidentialité : https://immolibre.be/confidentialite

## Éléments graphiques à fournir

- Icône 512 × 512 : `icon-512.png` (déjà dans le dépôt)
- Image de présentation 1024 × 500 : bandeau vert avec le logo et le slogan « L'immobilier belge gratuit »
- Au moins 2 captures d'écran de téléphone (idéalement 4 à 8) : accueil avec annonces, fiche d'un bien, carte, publication d'une annonce, messagerie

---

# Sécurité des données (Play Console → Contenu de l'appli → Sécurité des données)

Réponses correspondant au fonctionnement actuel du site (à revérifier si le site change) :

- Collecte ou partage de données utilisateur requises : **Oui**
- Toutes les données sont chiffrées en transit : **Oui**
- Les utilisateurs peuvent demander la suppression de leurs données : **Oui**
- URL de suppression du compte : **https://immolibre.be/suppression-compte**

| Type de données (Google) | Collectée | Partagée* | Facultative | Finalités |
|---|---|---|---|---|
| Informations personnelles → Adresse e-mail | Oui | Non | Non (compte) | Fonctionnalité de l'appli, gestion du compte |
| Informations personnelles → Nom | Oui | Non | Oui | Fonctionnalité de l'appli |
| Informations personnelles → Numéro de téléphone | Oui | Non | Oui | Fonctionnalité de l'appli |
| Informations personnelles → Adresse (du bien) | Oui | Non | Oui | Fonctionnalité de l'appli |
| Messages → Autres messages intégrés | Oui | Non | Oui | Fonctionnalité de l'appli |
| Photos et vidéos | Oui | Non | Oui | Fonctionnalité de l'appli |
| Activité dans l'appli → Autre contenu généré par l'utilisateur (annonces) | Oui | Non | Oui | Fonctionnalité de l'appli |
| Localisation approximative / précise | **Non** (utilisée uniquement sur l'appareil, jamais envoyée) | Non | — | — |
| Identifiants de l'appareil ou autres | Non | Non | — | — |

\* Google ne compte pas comme « partage » l'envoi à des sous-traitants (Supabase, Netlify) qui traitent les données pour ton compte.

# Autres questionnaires de la Play Console

- **Classification du contenu** : application de type « utilitaire / marketplace ». Répondre Oui à « les utilisateurs peuvent interagir ou échanger des contenus » (messagerie et annonces). Aucune violence, jeu d'argent ou contenu sexuel.
- **Public cible** : 18 ans et plus.
- **Annonces publicitaires** : Non, l'application ne contient pas de publicité.
- **Accès à l'application** : fournir à Google un compte de test (e-mail + mot de passe) pour qu'il puisse vérifier la messagerie et la publication d'annonces.

# ⚠️ Point bloquant à régler avant l'envoi : les paiements

Les boosts et options Premium sont payés par Stripe. Dans une application du Play Store, Google impose son propre système de paiement (« Google Play Billing ») pour les services numériques, et une option de visibilité en est un. Deux solutions :

1. **Masquer les options payantes dans l'application Android** : elles restent disponibles sur le site web. C'est la solution la plus simple et la plus courante.
2. Brancher Google Play Billing : plus complexe, et Google prélève 15 % sur chaque paiement.
