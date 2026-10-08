-- ════════════════════════════════════════════════════════════════════════════
-- ImmoLibre — PARTIE 2/2 (stockage photos / vidéos), check-up v124
-- ✅ APPLIQUÉ le 08/10/2026 (policies d'envoi restreintes à « authenticated »).
-- Si l'éditeur répond « must be owner of table objects » : faire la même chose
-- depuis l'interface (voir instructions en bas de ce fichier).
-- ════════════════════════════════════════════════════════════════════════════
begin;

-- ─── 5. Stockage : envois anonymes sans limite de taille ni de type ─────────
-- Les buckets « photos » et « videos » acceptent n'importe quel fichier, de
-- n'importe quelle taille, envoyé par n'importe qui. Le site n'envoie qu'en
-- étant connecté, des images (compressées en webp/jpeg quand c'est plus léger,
-- sinon le fichier d'origine) et des vidéos.
update storage.buckets
   set file_size_limit = 10485760,                -- 10 Mo
       allowed_mime_types = array['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/avif']
 where id = 'photos';
update storage.buckets
   set file_size_limit = 52428800,                -- 50 Mo
       allowed_mime_types = array['video/*']
 where id = 'videos';

alter policy "Upload photos public" on storage.objects to authenticated;

alter policy "Upload videos agence" on storage.objects to authenticated;

commit;

-- ─── Si erreur de droits : via l'interface Supabase ──────────────────────────
-- Storage → bucket « photos » → Edit bucket : limite 10 MB,
--   types autorisés : image/jpeg, image/png, image/webp, image/gif, image/avif
-- Storage → bucket « videos » → Edit bucket : limite 50 MB, type : video/*
-- Storage → Policies : supprimer « Upload photos public » et « Upload videos
--   agence », puis créer pour chaque bucket une policy INSERT réservée au rôle
--   « authenticated ».
