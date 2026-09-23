/* Circular reveal retained from installed theme: 400 ms, same origin/radius/easing. */
document.addEventListener("DOMContentLoaded", function () {
  var themeToggle = document.getElementById("themeToggle");
  var themeAnimating = false;

  function applyTheme(newDark) {
    if (newDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    themeToggle.setAttribute("aria-pressed", String(newDark));
    themeToggle.setAttribute(
      "aria-label",
      newDark ? "Switch to light mode" : "Switch to dark mode",
    );
    try {
      localStorage.setItem("crh-theme", newDark ? "dark" : "light");
    } catch (e) {}
  }

  if (themeToggle) {
    themeToggle.setAttribute(
      "aria-pressed",
      String(document.documentElement.classList.contains("dark")),
    );
    themeToggle.addEventListener("click", function () {
      if (themeAnimating) return;

      var btn = themeToggle;
      var rect = btn.getBoundingClientRect();
      var x = rect.left + rect.width / 2;
      var y = rect.top + rect.height / 2;
      var endRadius = Math.hypot(
        Math.max(x, window.innerWidth - x),
        Math.max(y, window.innerHeight - y),
      );
      var newDark = !document.documentElement.classList.contains("dark");

      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        applyTheme(newDark);
        return;
      }
      themeAnimating = true;

      /* Modern path: View Transitions API */
      if ("startViewTransition" in document) {
        var transition = document.startViewTransition(function () {
          applyTheme(newDark);
        });
        transition.ready
          .then(function () {
            document.documentElement.animate(
              {
                clipPath: [
                  "circle(0px at " + x + "px " + y + "px)",
                  "circle(" + endRadius + "px at " + x + "px " + y + "px)",
                ],
              },
              {
                duration: 400,
                easing: "cubic-bezier(0.4, 0, 0.2, 1)",
                pseudoElement: "::view-transition-new(root)",
              },
            );
          })
          .catch(function () {
            applyTheme(newDark);
          });
        transition.finished
          .catch(function () {
            applyTheme(newDark);
          })
          .finally(function () {
            themeAnimating = false;
          });
      } else {
        /* Fallback: clip-path overlay */
        var overlay = document.createElement("div");
        overlay.style.cssText =
          "position:fixed;top:0;left:0;width:100%;height:100%;z-index:9999;" +
          "pointer-events:none;will-change:clip-path;" +
          "background:" +
          (newDark ? "#0c0f1a" : "#ffffff") +
          ";" +
          "clip-path:circle(0px at " +
          x +
          "px " +
          y +
          "px);";
        document.body.appendChild(overlay);

        requestAnimationFrame(function () {
          overlay.style.transition =
            "clip-path 0.4s cubic-bezier(0.4, 0, 0.2, 1)";
          overlay.style.clipPath =
            "circle(" + endRadius * 1.5 + "px at " + x + "px " + y + "px)";
        });

        /* Apply theme mid-animation */
        setTimeout(function () {
          applyTheme(newDark);
        }, 150);

        /* Clean up */
        setTimeout(function () {
          overlay.remove();
          themeAnimating = false;
        }, 420);
      }
    });
  }
});
