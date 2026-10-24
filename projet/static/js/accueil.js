// Page d'accueil : splash screen de 3 secondes avec barre de progression
document.addEventListener("DOMContentLoaded", () => {
  const splash = document.getElementById("splash-screen");
  if (!splash) return;
  const barre = document.getElementById("splash-progress-bar");
  const pourcent = document.getElementById("splash-percent-txt");
  const btnPasser = document.getElementById("btn-skip-splash");

  const duree = 3000, pas = 30;
  const increment = 100 / (duree / pas);
  let progression = 0;

  const masquer = () => {
    splash.classList.add("fade-out");
    setTimeout(() => { splash.style.display = "none"; }, 600);
  };

  const minuteur = setInterval(() => {
    progression += increment;
    if (progression >= 100) {
      progression = 100;
      clearInterval(minuteur);
      setTimeout(masquer, 150);
    }
    barre.style.width = progression + "%";
    pourcent.textContent = Math.floor(progression) + "%";
  }, pas);

  btnPasser.addEventListener("click", () => { clearInterval(minuteur); masquer(); });
});
