// The Hub starts in light mode. The moon button switches to dark, and the choice is remembered in this browser.
try {
  document.documentElement.classList.toggle("dark", localStorage.getItem("crh-theme") === "dark");
} catch (e) {}
