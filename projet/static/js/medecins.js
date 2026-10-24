// Page Médecins & Spécialités : recherche, filtre par spécialité, fenêtre de disponibilités
document.addEventListener("DOMContentLoaded", () => {
  const cartes = Array.from(document.querySelectorAll(".med-card"));
  const puces = Array.from(document.querySelectorAll(".filter-chip"));
  const champ = document.getElementById("searchInput");
  const compteur = document.getElementById("resultsCount");
  const vide = document.getElementById("emptyState");

  let specialite = document.querySelector(".filter-chip.active")?.dataset.specialite || "";
  let recherche = "";

  function filtrer() {
    const q = recherche.trim().toLowerCase();
    let n = 0;
    cartes.forEach((c) => {
      const ok = (!specialite || c.dataset.specialite === specialite) && (!q || c.dataset.recherche.includes(q));
      c.hidden = !ok;
      if (ok) n++;
    });
    vide.hidden = n !== 0;
    compteur.innerHTML = `Affichage de <strong>${n} praticien${n > 1 ? "s" : ""}</strong> ` +
      (specialite ? "en " + specialite : "disponibles à Douala");
  }

  puces.forEach((p) => p.addEventListener("click", () => {
    specialite = p.dataset.specialite;
    puces.forEach((x) => { x.classList.toggle("active", x === p); x.setAttribute("aria-selected", x === p); });
    filtrer();
  }));

  let delai;
  champ.addEventListener("input", (e) => {
    clearTimeout(delai);
    delai = setTimeout(() => { recherche = e.target.value; filtrer(); }, 150);
  });

  document.getElementById("btnReset").addEventListener("click", () => {
    recherche = ""; champ.value = "";
    puces[0].click();
  });

  // ---- Fenêtre de disponibilités ----
  const modale = document.getElementById("reservationModal");
  const entete = document.getElementById("modalDoctorHeader");
  const grille = document.getElementById("modalSlotsGrid");
  const champDate = document.getElementById("consultationDateInput");
  const btnConfirmer = document.getElementById("confirmSlotBtn");
  let carte = null, heureChoisie = null;

  function ouvrir(id) {
    carte = document.querySelector(`.med-card[data-id="${id}"]`);
    entete.innerHTML = carte.querySelector(".med-header").innerHTML;
    champDate.value = champDate.min;
    modale.classList.add("open");
    document.body.style.overflow = "hidden";
    chargerCreneaux();
  }
  function fermer() {
    modale.classList.remove("open");
    document.body.style.overflow = "";
  }

  async function chargerCreneaux() {
    heureChoisie = null;
    btnConfirmer.disabled = true;
    grille.innerHTML = "";
    try {
      const rep = await fetch(`/api/creneaux/${carte.dataset.id}?date=${champDate.value}`);
      const data = await rep.json();
      if (!rep.ok || !data.ouvert) {
        grille.innerHTML = `<p class="slots-message">${data.erreur || data.message}</p>`;
        return;
      }
      data.creneaux.forEach((c) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "slot-btn" + (c.libre ? "" : " disabled");
        b.textContent = c.heure;
        b.disabled = !c.libre;
        b.setAttribute("aria-label", `Créneau de ${c.heure} ${c.libre ? "disponible" : "occupé"}`);
        b.addEventListener("click", () => {
          grille.querySelectorAll(".slot-btn").forEach((x) => x.classList.remove("selected"));
          b.classList.add("selected");
          heureChoisie = c.heure;
          btnConfirmer.disabled = false;
              });
        grille.appendChild(b);
      });
    } catch (e) {
      grille.innerHTML = '<p class="slots-message">Impossible de charger les créneaux. Réessayez.</p>';
    }
  }

  document.querySelectorAll("[data-ouvrir]").forEach((b) => b.addEventListener("click", () => ouvrir(b.dataset.ouvrir)));
  document.querySelectorAll("[data-fermer]").forEach((b) => b.addEventListener("click", fermer));
  champDate.addEventListener("change", chargerCreneaux);
  modale.addEventListener("click", (e) => { if (e.target === modale) fermer(); });
  window.addEventListener("keydown", (e) => { if (e.key === "Escape" && modale.classList.contains("open")) fermer(); });

  btnConfirmer.addEventListener("click", () => {
    if (!heureChoisie) return;
    const q = new URLSearchParams({ medecin: carte.dataset.id, date: champDate.value, heure: heureChoisie });
    window.location.href = modale.dataset.rdvUrl + "?" + q;
  });

  filtrer();
});
