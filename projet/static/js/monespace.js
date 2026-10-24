// Page Mes consultations : onglets, déplacer / annuler un rendez-vous
document.addEventListener("DOMContentLoaded", () => {
  const $ = (id) => document.getElementById(id);

  // Formatage du téléphone sur le formulaire de connexion
  const tel = $("msTel");
  if (tel) tel.addEventListener("input", (e) => {
    const v = e.target.value.replace(/\D/g, "").slice(0, 9);
    e.target.value = [v.slice(0, 3), v.slice(3, 5), v.slice(5, 7), v.slice(7, 9)].filter(Boolean).join(" ");
  });
  if (!$("listUp")) return;

  // Message affiché après un rechargement
  const flash = sessionStorage.getItem("ms-flash");
  if (flash) {
    sessionStorage.removeItem("ms-flash");
    const t = document.createElement("div");
    t.className = "ms-toast"; t.textContent = flash;
    $("toasts").appendChild(t);
    setTimeout(() => t.remove(), 4500);
  }

  // Onglets
  document.querySelectorAll(".ms-tab").forEach((b) => b.addEventListener("click", () => {
    const haut = b.dataset.onglet === "up";
    document.querySelectorAll(".ms-tab").forEach((x) => x.classList.toggle("active", x === b));
    $("listUp").hidden = !haut;
    $("listPast").hidden = haut;
  }));

  async function envoyer(url, corps) {
    const rep = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...window.csrfHeaders() },
      body: JSON.stringify(corps || {}),
    });
    let data = {};
    try { data = await rep.json(); } catch (e) { data = { erreur: "Réponse inattendue du serveur." }; }
    return { ok: rep.ok && data.ok, data };
  }
  const fermer = () => document.querySelectorAll(".modal-backdrop").forEach((m) => m.classList.remove("open"));
  document.querySelectorAll("[data-fermer]").forEach((b) => b.addEventListener("click", fermer));
  document.querySelectorAll(".modal-backdrop").forEach((m) => m.addEventListener("click", (e) => { if (e.target === m) fermer(); }));
  window.addEventListener("keydown", (e) => { if (e.key === "Escape") fermer(); });

  let carte = null, heure = null;

  // ---- Annuler ----
  document.querySelectorAll("[data-annuler]").forEach((b) => b.addEventListener("click", () => {
    carte = b.closest(".ms-card");
    $("texteAnnuler").textContent = `Voulez-vous annuler votre rendez-vous avec ${carte.dataset.nom} ? Le créneau sera libéré.`;
    $("alerteAnnuler").hidden = true;
    $("modalAnnuler").classList.add("open");
  }));
  $("btnAnnuler").addEventListener("click", async () => {
    const { ok, data } = await envoyer(`/api/mes-rdv/${carte.dataset.id}/annuler`);
    if (ok) { sessionStorage.setItem("ms-flash", "Le rendez-vous a été annulé."); location.reload(); }
    else { $("alerteAnnuler").textContent = data.erreur; $("alerteAnnuler").hidden = false; }
  });

  // ---- Déplacer ----
  async function chargerCreneaux() {
    heure = null; $("btnDeplacer").disabled = true; $("alerteDeplacer").hidden = true;
    const grille = $("nouveauxCreneaux"); grille.innerHTML = "";
    const rep = await fetch(`/api/creneaux/${carte.dataset.medecin}?date=${$("nouvelleDate").value}`);
    const data = await rep.json();
    if (!rep.ok || !data.ouvert) { grille.innerHTML = `<p class="slots-message">${data.erreur || data.message}</p>`; return; }
    data.creneaux.forEach((c) => {
      const b = document.createElement("button");
      b.type = "button"; b.textContent = c.heure; b.disabled = !c.libre;
      b.className = "slot-btn" + (c.libre ? "" : " disabled");
      b.addEventListener("click", () => {
        grille.querySelectorAll(".slot-btn").forEach((x) => x.classList.toggle("selected", x === b));
        heure = c.heure; $("btnDeplacer").disabled = false;
      });
      grille.appendChild(b);
    });
  }
  document.querySelectorAll("[data-deplacer]").forEach((b) => b.addEventListener("click", () => {
    carte = b.closest(".ms-card");
    $("sousDeplacer").textContent = `${carte.dataset.nom} · ${carte.dataset.spec}`;
    $("modalDeplacer").classList.add("open");
    chargerCreneaux();
  }));
  $("nouvelleDate").addEventListener("change", chargerCreneaux);
  $("btnDeplacer").addEventListener("click", async () => {
    const { ok, data } = await envoyer(`/api/mes-rdv/${carte.dataset.id}/deplacer`, { date: $("nouvelleDate").value, heure });
    if (ok) { sessionStorage.setItem("ms-flash", "Votre consultation a été déplacée."); location.reload(); }
    else {
      if (data.champ === "creneau") await chargerCreneaux();
      $("alerteDeplacer").textContent = data.erreur; $("alerteDeplacer").hidden = false;
    }
  });
});
