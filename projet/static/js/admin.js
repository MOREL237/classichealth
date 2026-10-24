// Liste des rendez-vous : changement de statut sans recharger la page
document.addEventListener("DOMContentLoaded", () => {
  const table = document.getElementById("tableRdv");
  if (!table) return;
  const LIBELLES = { prevu: "Prévu", effectue: "Effectué", annule: "Annulé" };
  const ACTIONS = {
    prevu: [["effectue", "Marquer effectué", "btn-primary"], ["annule", "Annuler", "btn-danger"]],
    effectue: [["prevu", "Rétablir", "btn-secondary"]],
    annule: [["prevu", "Rétablir", "btn-secondary"]],
  };

  function dessiner(cellule, statut) {
    cellule.dataset.statut = statut;
    cellule.innerHTML = ACTIONS[statut]
      .map(([cible, texte, classe]) => `<button type="button" class="btn btn-sm ${classe}" data-cible="${cible}">${texte}</button>`)
      .join("");
  }
  table.querySelectorAll("[data-actions]").forEach((c) => dessiner(c, c.dataset.statut));

  table.addEventListener("click", async (e) => {
    const bouton = e.target.closest("[data-cible]");
    if (!bouton) return;
    const ligne = bouton.closest("tr");
    bouton.disabled = true;
    try {
      const rep = await fetch(`/admin/api/rendez-vous/${ligne.dataset.id}/statut`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...window.csrfHeaders() },
        body: JSON.stringify({ statut: bouton.dataset.cible }),
      });
      const data = await rep.json();
      if (!rep.ok) throw new Error(data.erreur || "Erreur");
      const badge = ligne.querySelector("[data-badge]");
      badge.textContent = LIBELLES[data.statut];
      badge.className = `ms-badge st-${data.statut}`;
      dessiner(ligne.querySelector("[data-actions]"), data.statut);
    } catch (err) {
      bouton.disabled = false;
      alert(err.message === "Failed to fetch" ? "Connexion impossible." : err.message);
    }
  });
});
