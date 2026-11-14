/* ==========================================================================
   Company Gecko Suisse — script commun à toutes les pages
   ========================================================================== */
(function () {
  'use strict';

  /* ---------- Réglages ---------------------------------------------------- */

  // Mesure d'audience. Indiquer ici le code du site GoatCounter, c'est-à-dire
  // la partie placée avant « .goatcounter.com ». Tant que la valeur est vide,
  // aucune mesure n'est faite et le bandeau de consentement ne s'affiche pas.
  var MESURE = { goatcounter: '' };

  // Numéro WhatsApp. Il est assemblé ici, à l'affichage, pour ne pas figurer
  // en clair dans le code des pages que lisent les robots collecteurs de numéros.
  var TEL = ['41', '79', '723', '50', '33'];

  var CLE = 'cgs-mesure';
  var DUREE_CHOIX = 180 * 24 * 3600 * 1000; // le choix du visiteur vaut six mois

  // Adresse de la racine du site, déduite de l'emplacement de ce fichier
  // (utile sur la page 404, qui peut s'afficher à n'importe quelle adresse).
  var ceScript = document.currentScript;
  var RACINE = ceScript && ceScript.src ? ceScript.src.replace(/[^\/]*$/, '') : '';

  function toutes(selecteur, fn) {
    Array.prototype.forEach.call(document.querySelectorAll(selecteur), fn);
  }

  /* ---------- Contact WhatsApp -------------------------------------------- */

  function lienWhatsApp(texte) {
    return 'https://wa.me/' + TEL.join('') + (texte ? '?text=' + encodeURIComponent(texte) : '');
  }

  toutes('a[data-wa]', function (a) {
    a.href = lienWhatsApp(a.getAttribute('data-wa'));
    a.rel = 'noopener';
  });
  toutes('[data-tel]', function (el) {
    el.textContent = (el.getAttribute("data-tel") || "") + "0" + TEL.slice(1).join(" ");
  });

  /* ---------- Mesure d'audience, uniquement sur consentement --------------- */

  var mesureConfiguree = !!MESURE.goatcounter;
  var bandeau = null;
  var mesureChargee = false;

  function lireChoix() {
    try {
      var v = JSON.parse(localStorage.getItem(CLE) || 'null');
      if (v && (v.c === 'oui' || v.c === 'non') && Date.now() - v.t < DUREE_CHOIX) return v.c;
    } catch (e) { /* stockage indisponible : on redemandera */ }
    return null;
  }

  function noterChoix(choix) {
    try { localStorage.setItem(CLE, JSON.stringify({ c: choix, t: Date.now() })); } catch (e) { /* idem */ }
  }

  function chargerMesure() {
    if (mesureChargee) return;
    mesureChargee = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://gc.zgo.at/count.js';
    s.setAttribute('data-goatcounter', 'https://' + MESURE.goatcounter + '.goatcounter.com/count');
    document.body.appendChild(s);
  }

  function fermerBandeau() {
    if (bandeau && bandeau.parentNode) bandeau.parentNode.removeChild(bandeau);
    bandeau = null;
  }

  function ouvrirBandeau(avecFocus) {
    if (!bandeau) {
      bandeau = document.createElement('div');
      bandeau.className = 'consent';
      bandeau.setAttribute('role', 'region');
      bandeau.setAttribute('aria-label', 'Mesure d’audience');
      bandeau.innerHTML =
        '<p>Ce site ne dépose aucun cookie et n’affiche aucune publicité. ' +
        'Acceptez-vous une mesure d’audience anonyme, qui m’aide simplement à savoir quelles pages sont utiles ? ' +
        '<a class="lien" href="' + RACINE + 'confidentialite.html#mesure">En savoir plus</a></p>' +
        '<div class="consent__actions">' +
        '<button type="button" data-choix="non">Refuser</button>' +
        '<button type="button" data-choix="oui">Accepter</button>' +
        '</div>';
      document.body.appendChild(bandeau);
      toutes('.consent button', function (b) {
        b.addEventListener('click', function () {
          var choix = b.getAttribute('data-choix');
          noterChoix(choix);
          fermerBandeau();
          if (choix === 'oui') chargerMesure();
        });
      });
    }
    if (avecFocus) bandeau.querySelector('button').focus();
  }

  if (mesureConfiguree) {
    var choixConnu = lireChoix();
    if (choixConnu === 'oui') chargerMesure();
    else if (choixConnu === null) ouvrirBandeau(false);

    // Liens « modifier mon choix » et texte de la page de confidentialité
    toutes('[data-mesure-lien]', function (el) { el.hidden = false; });
    toutes('[data-mesure-ouvrir]', function (b) {
      b.addEventListener('click', function () { ouvrirBandeau(true); });
    });
    toutes('[data-mesure-etat]', function (el) {
      el.hidden = el.getAttribute('data-mesure-etat') !== 'active';
    });
  }

  /* ---------- Formulaire de réservation ----------------------------------- */

  var f = document.getElementById('reservation');
  if (!f) return;

  var ouverture = Date.now();

  // Une règle par champ obligatoire : renvoie le message d'erreur, ou '' si tout va bien
  var REGLES = {
    nom: function (v) {
      if (!v) return 'Indiquez votre nom.';
      if (v.length < 2) return 'Ce nom semble trop court.';
      if (/(https?:\/\/|www\.)/i.test(v)) return 'Indiquez simplement votre nom, sans lien.';
      return '';
    },
    gecko: function (v) { return v ? '' : 'Choisissez un gecko, ou la dernière réponse si vous hésitez.'; },
    experience: function (v) { return v ? '' : 'Choisissez la réponse qui vous correspond.'; },
    installation: function (v) { return v ? '' : 'Choisissez la réponse qui vous correspond.'; }
  };

  function valeur(nom) {
    var el = f.elements[nom];
    return el && el.value ? el.value.trim() : '';
  }

  function controler(nom) {
    var el = f.elements[nom];
    var p = document.getElementById('e-' + nom);
    var message = REGLES[nom](valeur(nom));
    if (message) {
      el.setAttribute('aria-invalid', 'true');
      p.textContent = message;
      p.hidden = false;
    } else {
      el.removeAttribute('aria-invalid');
      p.textContent = '';
      p.hidden = true;
    }
    return !message;
  }

  Object.keys(REGLES).forEach(function (nom) {
    var el = f.elements[nom];
    el.addEventListener('change', function () { controler(nom); });
    el.addEventListener('input', function () { if (el.getAttribute('aria-invalid')) controler(nom); });
  });

  // « Réserver ce gecko » : présélectionne l'animal dans le formulaire
  toutes('.reserver-ce', function (a) {
    a.addEventListener('click', function () {
      var liste = f.elements.gecko;
      var cible = a.getAttribute('data-gecko');
      Array.prototype.forEach.call(liste.options, function (o) {
        if (o.value === cible) liste.value = cible;
      });
      controler('gecko');
      setTimeout(function () { f.elements.nom.focus({ preventScroll: true }); }, 500);
    });
  });

  f.addEventListener('submit', function (e) {
    e.preventDefault();

    var enErreur = Object.keys(REGLES).filter(function (nom) { return !controler(nom); });
    if (enErreur.length) {
      f.elements[enErreur[0]].focus();
      return;
    }

    // Anti-spam : champ piège rempli, ou envoi trop rapide pour être humain
    if (valeur('site') || Date.now() - ouverture < 3000) return;

    var l = [];
    l.push('Bonjour, je vous écris depuis votre site pour une demande de réservation.');
    l.push('');
    l.push('Nom : ' + valeur('nom'));
    if (valeur('lieu')) l.push('Région : ' + valeur('lieu'));
    l.push('Gecko souhaité : ' + valeur('gecko'));
    l.push('Expérience : ' + valeur('experience'));
    l.push('Installation : ' + valeur('installation'));
    if (valeur('motivation')) { l.push(''); l.push('Quelques mots : ' + valeur('motivation')); }
    l.push('');
    l.push('Merci d\'avance pour votre retour.');

    var url = lienWhatsApp(l.join('\n'));

    // Lien de secours, au cas où WhatsApp ne s'ouvrirait pas tout seul
    var suite = document.getElementById('form-suite');
    if (suite) {
      suite.querySelector('a').href = url;
      suite.hidden = false;
    }

    var fenetre = window.open(url, '_blank');
    if (fenetre) {
      try { fenetre.opener = null; } catch (err) { /* sans importance */ }
    } else {
      window.location.href = url; // fenêtre bloquée : on ouvre dans l'onglet courant
    }
  });
})();
