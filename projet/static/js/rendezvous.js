// Page Prendre rendez-vous : tunnel en 4 étapes (médecin, créneau, coordonnées, confirmation)
document.addEventListener("DOMContentLoaded", () => {
  const $ = (id) => document.getElementById(id);
  const JOURS = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"];
  const MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
  const pad = (n) => String(n).padStart(2, "0");
  const iso = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const parse = (s) => { const [a, b, c] = s.split("-").map(Number); return new Date(a, b - 1, c); };
  const longue = (s) => { const d = parse(s); return `${JOURS[d.getDay()]} ${d.getDate()} ${MOIS[d.getMonth()]} ${d.getFullYear()}`; };
  const fin = (h) => { let [a, m] = h.split(":").map(Number); m += 30; return `${pad(a + Math.floor(m / 60))}:${pad(m % 60)}`; };

  const cartes = Array.from(document.querySelectorAll(".rv-doc"));
  const panneaux = [null, $("rvPanel1"), $("rvPanel2"), $("rvPanel3"), $("rvPanel4")];
  const etapes = Array.from(document.querySelectorAll(".rv-step"));
  const alerte = $("rvAlert"), btnPrev = $("rvPrev"), btnNext = $("rvNext");
  const LIBELLES = ["", "Continuer vers l'horaire", "Continuer vers mes coordonnées", "Vérifier mon rendez-vous", "Confirmer le rendez-vous"];

  let etape = 1, medecin = null, jour = null, heure = null, envoi = false;
  let motif = document.querySelector(".rv-pill.selected").dataset.valeur;

  const montrerAlerte = (msg) => { alerte.textContent = msg; alerte.hidden = !msg; };
  const erreurChamp = (champ, msg) => {
    const el = document.querySelector(`.rv-error[data-champ="${champ}"]`);
    if (el) el.textContent = msg || "";
  };
  const viderErreurs = () => document.querySelectorAll(".rv-error").forEach((e) => (e.textContent = ""));

  // ---- Récapitulatif latéral ----
  function majResume() {
    $("sInit").textContent = medecin ? medecin.initiales : "?";
    $("sSpec").textContent = medecin ? medecin.specialite : "Spécialité";
    $("sNom").textContent = medecin ? medecin.nom : "Aucun médecin choisi";
    $("sDate").textContent = jour ? longue(jour) : "À choisir";
    $("sHeure").textContent = heure ? `${heure} – ${fin(heure)}` : "À choisir";
  }

  // ---- Étape 1 : médecin ----
  document.querySelectorAll("#rvChips .filter-chip").forEach((puce) => puce.addEventListener("click", () => {
    document.querySelectorAll("#rvChips .filter-chip").forEach((p) => p.classList.toggle("active", p === puce));
    cartes.forEach((c) => { c.hidden = puce.dataset.specialite && c.dataset.specialite !== puce.dataset.specialite; });
  }));

  function choisirMedecin(carte) {
    cartes.forEach((c) => c.classList.toggle("selected", c === carte));
    const d = carte.dataset;
    if (!medecin || medecin.id !== d.id) { jour = null; heure = null; }
    medecin = { id: d.id, nom: d.nom, specialite: d.specialite, initiales: d.initiales, jours: d.jours.split(",").map(Number) };
    montrerAlerte("");
    majResume();
  }
  cartes.forEach((c) => c.addEventListener("click", () => choisirMedecin(c)));

  // ---- Étape 2 : date et créneau ----
  function rendreDates() {
    const noms = medecin.jours.map((j) => JOURS[j % 7]).join(", ");
    $("rvHint").textContent = `${medecin.nom} consulte le ${noms.toLowerCase()} (08h00 – 12h00).`;
    const dates = [];
    for (let i = 0; i < 40 && dates.length < 6; i++) {
      const d = new Date(); d.setDate(d.getDate() + i);
      if (medecin.jours.includes(d.getDay() === 0 ? 7 : d.getDay())) dates.push(d);
    }
    $("rvDates").innerHTML = "";
    dates.forEach((d) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "rv-date" + (iso(d) === jour ? " selected" : "");
      b.innerHTML = `<small>${JOURS[d.getDay()].slice(0, 3)}</small><b>${d.getDate()}</b><small>${MOIS[d.getMonth()].slice(0, 4)}.</small>`;
      b.addEventListener("click", () => { jour = iso(d); heure = null; rendreDates(); chargerCreneaux(); majResume(); });
      $("rvDates").appendChild(b);
    });
  }

  async function chargerCreneaux() {
    const grille = $("rvSlots");
    if (!jour) { grille.innerHTML = '<p class="slots-message">Choisissez d\'abord une date.</p>'; return; }
    grille.innerHTML = "";
    try {
      const rep = await fetch(`/api/creneaux/${medecin.id}?date=${jour}`);
      const data = await rep.json();
      if (!rep.ok || !data.ouvert) { grille.innerHTML = `<p class="slots-message">${data.erreur || data.message}</p>`; return; }
      if (heure && !data.creneaux.some((c) => c.heure === heure && c.libre)) heure = null;
      data.creneaux.forEach((c) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "slot-btn" + (c.libre ? "" : " disabled") + (c.heure === heure ? " selected" : "");
        b.textContent = c.heure;
        b.disabled = !c.libre;
        b.addEventListener("click", () => {
          heure = c.heure;
          grille.querySelectorAll(".slot-btn").forEach((x) => x.classList.toggle("selected", x === b));
          montrerAlerte(""); majResume();
        });
        grille.appendChild(b);
      });
      majResume();
    } catch (e) {
      grille.innerHTML = '<p class="slots-message">Impossible de charger les créneaux. Réessayez.</p>';
    }
  }

  // ---- Étape 3 : coordonnées ----
  document.querySelectorAll(".rv-pill").forEach((pill) => pill.addEventListener("click", () => {
    document.querySelectorAll(".rv-pill").forEach((p) => {
      p.classList.toggle("selected", p === pill);
      p.setAttribute("aria-checked", p === pill);
    });
    motif = pill.dataset.valeur;
  }));
  $("fTel").addEventListener("input", (e) => {
    const v = e.target.value.replace(/\D/g, "").slice(0, 9);
    e.target.value = [v.slice(0, 3), v.slice(3, 5), v.slice(5, 7), v.slice(7, 9)].filter(Boolean).join(" ");
  });
  const chiffres = () => $("fTel").value.replace(/\D/g, "");

  function validerFormulaire() {
    viderErreurs();
    let ok = true;
    const err = (champ, msg) => { erreurChamp(champ, msg); ok = false; };
    if ($("fNom").value.trim().length < 2) err("nom", "Indiquez votre nom.");
    if ($("fPrenom").value.trim().length < 2) err("prenom", "Indiquez votre prénom.");
    const n = $("fNaissance").value;
    if (!n) err("date_naissance", "Indiquez votre date de naissance.");
    else if (n > iso(new Date())) err("date_naissance", "Date de naissance invalide.");
    if (!/^6\d{8}$/.test(chiffres())) err("telephone", "9 chiffres commençant par 6 (ex. 699 45 88 12).");
    return ok;
  }

  // ---- Étape 4 : récapitulatif ----
  function remplirTicket() {
    $("tDoc").textContent = medecin.nom;
    $("tSpec").textContent = medecin.specialite;
    $("tDate").textContent = longue(jour);
    $("tHeure").textContent = `${heure} – ${fin(heure)}`;
    $("tPatient").textContent = `${$("fPrenom").value.trim()} ${$("fNom").value.trim()}`;
    $("tTel").textContent = "+237 " + $("fTel").value;
    $("tVille").textContent = $("fVille").value;
    $("tMotif").textContent = motif;
  }

  // ---- Navigation ----
  function afficher(n) {
    etape = n;
    panneaux.forEach((p, i) => { if (p) p.hidden = i !== n; });
    etapes.forEach((li, i) => {
      li.classList.toggle("active", i + 1 === n);
      li.classList.toggle("done", i + 1 < n);
      li.querySelector(".rv-step-num").textContent = i + 1 < n ? "✓" : i + 1;
    });
    btnPrev.style.visibility = n === 1 ? "hidden" : "visible";
    btnNext.textContent = LIBELLES[n];
    montrerAlerte("");
    if (n === 2) { rendreDates(); chargerCreneaux(); }
    if (n === 3) $("rvMotifHint").textContent = `Permet à ${medecin.nom} de préparer votre consultation.`;
    if (n === 4) remplirTicket();
    $("rvStepper").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function valider() {
    if (etape === 1 && !medecin) { montrerAlerte("Veuillez choisir un médecin."); return false; }
    if (etape === 2) {
      if (!jour) { montrerAlerte("Veuillez choisir une date."); return false; }
      if (!heure) { montrerAlerte("Veuillez choisir un créneau."); return false; }
    }
    if (etape === 3) return validerFormulaire();
    return true;
  }

  async function confirmer() {
    if (envoi) return;
    envoi = true; btnNext.disabled = true; btnNext.textContent = "Enregistrement...";
    try {
      const rep = await fetch("/api/rendez-vous", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...window.csrfHeaders() },
        body: JSON.stringify({
          medecin_id: medecin.id, date: jour, heure,
          nom: $("fNom").value, prenom: $("fPrenom").value, date_naissance: $("fNaissance").value,
          telephone: $("fTel").value, ville: $("fVille").value, motif, notes: $("fNotes").value,
        }),
      });
      const data = await rep.json();
      if (rep.ok && data.ok) { window.location.href = data.url; return; }
      if (data.champ === "creneau" || data.champ === "heure" || data.champ === "date") {
        heure = null; majResume(); afficher(2); montrerAlerte(data.erreur);
      } else if (data.champ === "medecin") {
        afficher(1); montrerAlerte(data.erreur);
      } else {
        afficher(3); erreurChamp(data.champ, data.erreur); montrerAlerte(data.erreur);
      }
    } catch (e) {
      montrerAlerte("Connexion impossible. Vérifiez votre réseau et réessayez.");
    } finally {
      envoi = false; btnNext.disabled = false; btnNext.textContent = LIBELLES[etape];
    }
  }

  btnNext.addEventListener("click", () => {
    if (!valider()) return;
    if (etape < 4) afficher(etape + 1); else confirmer();
  });
  btnPrev.addEventListener("click", () => { if (etape > 1) afficher(etape - 1); });
  etapes.forEach((li) => li.addEventListener("click", () => {
    const cible = Number(li.dataset.step);
    if (cible < etape) afficher(cible);
    else if (cible === etape + 1 && valider()) afficher(cible);
  }));

  // ---- Arrivée depuis la page Médecins (?medecin=ID&date=...&heure=...) ----
  const params = new URLSearchParams(window.location.search);
  const carteInitiale = cartes.find((c) => c.dataset.id === params.get("medecin"));
  if (carteInitiale) {
    choisirMedecin(carteInitiale);
    const d = params.get("date"), h = params.get("heure");
    if (/^\d{4}-\d{2}-\d{2}$/.test(d || "") && medecin.jours.includes(parse(d).getDay() || 7) && d >= iso(new Date())) {
      jour = d;
      if (/^\d{2}:\d{2}$/.test(h || "")) heure = h;
    }
    majResume();
    afficher(2);
  } else {
    afficher(1);
  }
});
