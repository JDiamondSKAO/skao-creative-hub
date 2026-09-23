try {
  const p = localStorage.getItem("crh-theme");
  document.documentElement.classList.toggle(
    "dark",
    p === "dark" || (!p && matchMedia("(prefers-color-scheme: dark)").matches),
  );
} catch (e) {
  document.documentElement.classList.toggle(
    "dark",
    matchMedia("(prefers-color-scheme: dark)").matches,
  );
}
