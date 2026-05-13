/**
 * New / edit note page: Search button calls /api/books/search and lists results under Book.
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

      const ul = document.createElement("ul");
      ul.className = "list-unstyled mb-0 border rounded p-2 bg-light";

      items.forEach(function (item) {
        const li = document.createElement("li");
        li.className = "py-1 border-bottom";

        const strong = document.createElement("strong");
        strong.textContent = item.title || "";
        li.appendChild(strong);

        if (item.author) {
          li.appendChild(document.createElement("br"));
          const span = document.createElement("span");
          span.className = "text-muted";
          span.textContent = item.author;
          li.appendChild(span);
        }

        ul.appendChild(li);
      });

      resultsEl.appendChild(ul);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
