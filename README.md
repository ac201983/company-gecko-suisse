# Company Gecko Suisse

Site vitrine de l'élevage, publié avec GitHub Pages.

## Mettre à jour le site

Tout se fait depuis github.com, sans rien installer.

**Changer une photo de jeune** : ouvrir le dossier `photos`, cliquer sur `jeune-1.jpg` (ou 2, 3, 4), puis sur l'icône de corbeille pour la supprimer. Ensuite revenir dans `photos`, cliquer sur « Add file » puis « Upload files », et déposer votre photo en la renommant exactement `jeune-1.jpg`. Les photos carrées rendent le mieux.

**Marquer un bébé comme réservé** : ouvrir `index.html`, cliquer sur le crayon, chercher `<figcaption>Disponible</figcaption>` et remplacer `Disponible` par `Réservé`. Puis « Commit changes » en bas.

**Ajouter ou retirer un emplacement photo** : dans `index.html`, dupliquer ou supprimer une ligne complète qui commence par `<figure>`.

Chaque modification est en ligne une à deux minutes plus tard.

## Structure

- `index.html` — tout le site, une seule page
- `photos/` — les photos des jeunes de la saison
