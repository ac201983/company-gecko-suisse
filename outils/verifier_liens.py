#!/usr/bin/env python3
"""Vérifie tous les liens internes du site : fichiers, images, ancres, plan de site.

Usage, depuis la racine du site :   python3 outils/verifier_liens.py
Les liens externes sont seulement listés (à contrôler à la main).
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

RACINE = Path(__file__).resolve().parent.parent
PREFIXE = "/company-gecko-suisse/"          # chemin du site sur GitHub Pages
SITE = "https://ac201983.github.io" + PREFIXE


class Collecte(HTMLParser):
    def __init__(self):
        super().__init__()
        self.liens, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        for cle in ("href", "src"):
            if a.get(cle):
                self.liens.append((tag, a[cle]))
        for cle in ("srcset",):
            if a.get(cle):
                for morceau in a[cle].split(","):
                    self.liens.append((tag, morceau.strip().split()[0]))
        if tag == "meta" and a.get("property") in ("og:image", "og:url") and a.get("content"):
            self.liens.append((tag, a["content"]))


def analyser(fichier: Path) -> Collecte:
    c = Collecte()
    c.feed(fichier.read_text(encoding="utf-8"))
    return c


def main() -> int:
    pages = sorted(RACINE.glob("*.html"))
    infos = {p.name: analyser(p) for p in pages}
    erreurs, externes, total = [], set(), 0

    def resoudre(page: str, url: str):
        """Renvoie (fichier cible, ancre) pour un lien interne, ou None pour un lien externe."""
        if url.startswith(SITE):
            url = PREFIXE + url[len(SITE):]
        u = urlsplit(url)
        if u.scheme in ("http", "https") or url.startswith("//"):
            externes.add(url)
            return None
        if u.scheme:            # mailto:, tel:, data:…
            return None
        chemin = unquote(u.path)
        if chemin.startswith(PREFIXE):
            cible = RACINE / chemin[len(PREFIXE):]
        elif chemin.startswith("/"):
            return ("HORS-SITE", chemin)
        elif chemin in ("", "./"):
            cible = RACINE / (page if chemin == "" else "index.html")
        else:
            cible = RACINE / chemin
        if cible.is_dir():
            cible = cible / "index.html"
        return (cible, u.fragment)

    for nom, c in infos.items():
        for tag, url in c.liens:
            total += 1
            r = resoudre(nom, url)
            if r is None:
                continue
            cible, ancre = r
            if cible == "HORS-SITE":
                erreurs.append(f"{nom}: chemin absolu hors du site : {url}")
                continue
            if not cible.exists():
                erreurs.append(f"{nom}: fichier introuvable : {url}")
                continue
            if ancre and cible.suffix == ".html":
                ids = infos[cible.name].ids if cible.name in infos else analyser(cible).ids
                if ancre not in ids:
                    erreurs.append(f"{nom}: ancre inexistante : {url}")

    # feuille de style : url(...)
    css = (RACINE / "style.css").read_text(encoding="utf-8")
    for url in re.findall(r"url\(([^)]+)\)", css):
        total += 1
        if not (RACINE / url.strip("\"'")).exists():
            erreurs.append(f"style.css: fichier introuvable : {url}")

    # plan de site et manifeste
    for loc in re.findall(r"<loc>([^<]+)</loc>", (RACINE / "sitemap.xml").read_text()):
        total += 1
        r = resoudre("sitemap.xml", loc)
        if r is None or r[0] == "HORS-SITE" or not r[0].exists():
            erreurs.append(f"sitemap.xml: adresse sans fichier : {loc}")
    for icone in json.loads((RACINE / "site.webmanifest").read_text())["icons"]:
        total += 1
        if not (RACINE / icone["src"]).exists():
            erreurs.append(f"site.webmanifest: icône introuvable : {icone['src']}")

    print(f"{len(pages)} pages, {total} liens et fichiers vérifiés, {len(erreurs)} erreur(s)")
    for e in erreurs:
        print("  ERREUR", e)
    print("Liens externes (non testés ici) :")
    for e in sorted(externes):
        print("  ", e)
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
