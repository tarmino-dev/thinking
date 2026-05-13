/**
 * New / edit note page: Search calls /api/books/search; clicking a result fills Book and clears the list.
 */
(function () {
  function showMessage(container, text, className) {
    container.textContent = "";
    const div = document.createElement("div");
    div.className = className;
    div.textContent = text;
    container.appendChild(div);
  }

  function init() {
    const btn = document.getElementById("book-search-btn");
    const input = document.getElementById("note-book-input");
    const resultsEl = document.getElementById("book-search-results");
    if (!btn || !input || !resultsEl) {
      return;
    }

    btn.addEventListener("click", async function () {
      const q = (input.value || "").trim();
      resultsEl.textContent = "";

      if (q.length < 2) {
        showMessage(
          resultsEl,
          "Enter at least 2 characters to search.",
          "text-danger"
        );
        return;
      }

      showMessage(resultsEl, "Searching…", "text-muted");

      let res;
      try {
        res = await fetch(
          "/api/books/search?q=" + encodeURIComponent(q),
          { headers: { Accept: "application/json" } }
        );
      } catch (err) {
        resultsEl.textContent = "";
        showMessage(resultsEl, "Network error.", "text-danger");
        return;
      }

      let data = {};
      try {
        data = await res.json();
      } catch (err) {
        resultsEl.textContent = "";
        showMessage(resultsEl, "Invalid response from server.", "text-danger");
        return;
      }

      resultsEl.textContent = "";

      if (!res.ok) {
        const msg =
          (data && (data.message || data.error)) || res.statusText || "Error";
        showMessage(resultsEl, String(msg), "text-danger");
        return;
      }

      const items = Array.isArray(data.results) ? data.results : [];
      if (items.length === 0) {
        showMessage(resultsEl, "No results.", "text-muted");
        return;
      }

      function pickDisplay(item) {
        if (item.display && String(item.display).trim()) {
          return String(item.display).trim();
        }
        const t = (item.title || "").trim();
        const a = (item.author || "").trim();
        if (t && a) {
          return t + " — " + a;
        }
        return t || a;
      }

      const list = document.createElement("div");
      list.className = "list-group list-group-flush border rounded small";

      items.forEach(function (item) {
        const choice = document.createElement("button");
        choice.type = "button";
        choice.className =
          "list-group-item list-group-item-action text-start py-2";
        choice.setAttribute("aria-label", "Use this book for the note");

        const strong = document.createElement("strong");
        strong.textContent = item.title || "";
        choice.appendChild(strong);

        if (item.author) {
          choice.appendChild(document.createElement("br"));
          const span = document.createElement("span");
          span.className = "text-muted";
          span.textContent = item.author;
          choice.appendChild(span);
        }

        choice.addEventListener("click", function () {
          input.value = pickDisplay(item);
          resultsEl.textContent = "";
        });

        list.appendChild(choice);
      });

      resultsEl.appendChild(list);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
