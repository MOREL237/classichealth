// En-tête CSRF à joindre à chaque requête POST envoyée avec fetch
window.csrfHeaders = () => {
  const m = document.querySelector('meta[name="csrf-token"]');
  return m ? { "X-CSRF-Token": m.content } : {};
};

// Commun à toutes les pages : bascule thème clair / sombre (mémorisée dans le navigateur)
(function () {
  const racine = document.documentElement;
  try {
    if (localStorage.getItem("theme") === "dark") racine.setAttribute("data-theme", "dark");
  } catch (e) {}

  document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("btn-toggle-theme");
    if (!btn) return;
    btn.addEventListener("click", () => {
      const sombre = racine.getAttribute("data-theme") === "dark";
      if (sombre) racine.removeAttribute("data-theme");
      else racine.setAttribute("data-theme", "dark");
      try { localStorage.setItem("theme", sombre ? "light" : "dark"); } catch (e) {}
    });
  });
})();
