# Company Gecko Suisse

Site de l'élevage, publié avec GitHub Pages : https://ac201983.github.io/company-gecko-suisse/

## Les fichiers

- `index.html` : la page d'accueil, avec tout le contenu de l'élevage
- `confidentialite.html`, `conditions.html` : les pages légales
- `404.html` : la page affichée pour une adresse qui n'existe pas
- `style.css` : l'apparence, commune à toutes les pages
- `site.js` : le formulaire, le contact WhatsApp et le bandeau de consentement
- `photos/` : les photos, avec pour chacune le `.jpg` d'origine et ses versions allégées `.avif` et `.webp`
- `polices/` : les polices, hébergées sur le site
- `sitemap.xml`, `robots.txt`, `site.webmanifest` : pour les moteurs de recherche et les navigateurs
- `outils/` : deux scripts d'entretien, pour les images et pour la vérification des liens

## Les modifications courantes

Tout peut se faire depuis github.com : ouvrir le fichier, cliquer sur le crayon, modifier, puis « Commit changes ». Le site est à jour une à deux minutes plus tard.

**Marquer un gecko comme réservé.** Dans `index.html`, chercher sa date de naissance. Sur la ligne `<article class="jeune">` placée juste au-dessus, écrire `<article class="jeune jeune--reserve">`. Remplacer ensuite `<p class="statut statut--libre">Libre</p>` par `<p class="statut statut--reserve">Réservé</p>`. Ses photos passent en gris et son bouton « Réserver ce gecko » disparaît. Retirer aussi sa ligne `<option>` dans le formulaire, plus bas dans la page.

**Changer un prix.** Il apparaît trois fois pour chaque gecko dans `index.html` : le prix affiché, l'attribut `data-gecko` du bouton, et la ligne `<option>` du formulaire. Ces deux derniers textes doivent rester identiques au caractère près, sinon le bouton ne présélectionne plus le bon animal.

**Changer ou ajouter une photo.** Déposer le `.jpg` dans `photos/`, puis lancer `python3 outils/optimiser_images.py`, qui fabrique les versions allégées. Sans ce passage, la page continue d'afficher les anciennes versions.

**Mesure d'audience.** Elle passe par le compte GoatCounter `companygecko`, renseigné dans `site.js` à la ligne `var MESURE = { goatcounter: 'companygecko' };`. Elle ne démarre qu'après accord du visiteur dans le bandeau. Vider la valeur (`''`) coupe la mesure, fait disparaître le bandeau et remet la page de confidentialité à l'état « aucun outil actif ».

**Après une modification de `style.css` ou de `site.js`.** Augmenter le numéro qui suit `style.css?v=` et `site.js?v=`, en tête des quatre pages, pour que les navigateurs rechargent le fichier.

## Vérifier avant de publier

`python3 outils/verifier_liens.py` contrôle tous les liens internes, les images et les ancres du site.
