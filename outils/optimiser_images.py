#!/usr/bin/env python3
"""Génère les versions allégées (AVIF et WebP, plusieurs largeurs) des images du site.

Les fichiers d'origine (.jpg, logo.png) ne sont jamais modifiés : ils servent
de source et de solution de repli pour les anciens navigateurs.

Usage, depuis la racine du site :   python3 outils/optimiser_images.py
Dépendance : Pillow 11.3 ou plus récent (pip install pillow), pour l'AVIF.

Après avoir ajouté ou remplacé une photo .jpg, relancer ce script : il recrée
les fichiers "nom-LARGEUR.avif" et "nom-LARGEUR.webp" appelés par les pages.
"""
from pathlib import Path
from PIL import Image

RACINE = Path(__file__).resolve().parent.parent

# (motif des sources, largeurs à produire, qualité AVIF, qualité WebP)
TACHES = [
    ("banniere.jpg",           [1200, 1710], 60, 80),
    ("banniere-mobile.jpg",    [750, 1000],  60, 80),
    ("photos/akame.jpg",       [640, 960],   58, 76),
    ("photos/winry.jpg",       [640, 960],   58, 76),
    ("photos/power.jpg",       [640, 960],   58, 76),
    ("photos/gecko*-*.jpg",    [400, 720],   58, 76),
]


def variantes(src: Path, largeur: int, q_avif: int, q_webp: int) -> list[Path]:
    im = Image.open(src).convert("RGB")
    if largeur < im.width:
        hauteur = round(im.height * largeur / im.width)
        im = im.resize((largeur, hauteur), Image.LANCZOS)
    avif = src.with_name(f"{src.stem}-{largeur}.avif")
    webp = src.with_name(f"{src.stem}-{largeur}.webp")
    im.save(avif, "AVIF", quality=q_avif, speed=3)
    im.save(webp, "WEBP", quality=q_webp, method=6)
    return [avif, webp]


def palette(im: Image.Image) -> Image.Image:
    """Réduit un PNG à 256 couleurs : trois à cinq fois plus léger, sans différence visible à ces tailles."""
    if im.mode == "RGBA":
        return im.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG)
    return im.convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)


def icones_et_apercu() -> None:
    """Logo de la barre de navigation, icônes du site et image d'aperçu pour les réseaux sociaux."""
    logo = Image.open(RACINE / "logo.png").convert("RGBA")

    # barre de navigation : affiché en 34 px, on prévoit les écrans 3x
    petit = logo.resize((102, 102), Image.LANCZOS)
    petit.save(RACINE / "logo-102.webp", "WEBP", quality=88, method=6)
    palette(petit).save(RACINE / "logo-102.png", optimize=True)

    for taille in (192, 512):
        palette(logo.resize((taille, taille), Image.LANCZOS)).save(RACINE / f"icone-{taille}.png", optimize=True)

    # iOS ne gère pas la transparence : fond noir, logo légèrement en retrait
    fond = Image.new("RGBA", (180, 180), (0, 0, 0, 255))
    fond.alpha_composite(logo.resize((168, 168), Image.LANCZOS), (6, 6))
    palette(fond.convert("RGB")).save(RACINE / "apple-touch-icon.png", optimize=True)

    # aperçu de partage, 1200 x 630 : la bannière centrée sur fond noir
    ban = Image.open(RACINE / "banniere.jpg").convert("RGB")
    h = round(ban.height * 1200 / ban.width)
    apercu = Image.new("RGB", (1200, 630), (0, 0, 0))
    apercu.paste(ban.resize((1200, h), Image.LANCZOS), (0, (630 - h) // 2))
    apercu.save(RACINE / "apercu.jpg", "JPEG", quality=84, optimize=True, progressive=True)

    for f in ("logo-102.webp", "logo-102.png", "icone-192.png", "icone-512.png", "apple-touch-icon.png", "apercu.jpg"):
        print(f"{f:38} {(RACINE / f).stat().st_size / 1024:6.0f} Ko")


def main() -> None:
    total_src = 0
    total = {".avif": 0, ".webp": 0}
    for motif, largeurs, q_avif, q_webp in TACHES:
        for src in sorted(RACINE.glob(motif)):
            if src.stem[-1].isdigit() and "-" in src.stem and src.stem.rsplit("-", 1)[1].isdigit() \
                    and int(src.stem.rsplit("-", 1)[1]) >= 300:
                continue  # déjà une variante (ex. banniere-1200.jpg)
            total_src += src.stat().st_size
            for largeur in largeurs:
                for dest in variantes(src, largeur, q_avif, q_webp):
                    total[dest.suffix] += dest.stat().st_size
                    print(f"{dest.relative_to(RACINE)!s:38} {dest.stat().st_size / 1024:6.0f} Ko")

    icones_et_apercu()

    print(f"\nSources JPEG : {total_src / 1024:.0f} Ko")
    print(f"Variantes AVIF : {total['.avif'] / 1024:.0f} Ko   Variantes WebP : {total['.webp'] / 1024:.0f} Ko")


if __name__ == "__main__":
    main()
