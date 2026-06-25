/**
 * Discuss-with-AI chat page: keeps the conversation history client-side and
 * POSTs it to the discussion endpoint, appending each reply. Framework-free.
 */
(function () {
  function init() {
    const chat = document.getElementById("discuss-chat");
    const form = document.getElementById("discuss-form");
    const input = document.getElementById("discuss-input");
    const sendBtn = document.getElementById("discuss-send");
    if (!chat || !form || !input || !sendBtn) {
      return;
    }

    const url = chat.getAttribute("data-discuss-url");
    const errorText = chat.getAttribute("data-error-text") || "Error";
    const thinkingText = chat.getAttribute("data-thinking-text") || "…";
    const history = [];

    function addBubble(role, text) {
      const wrap = document.createElement("div");
      wrap.className = "mb-2 " + (role === "user" ? "text-end" : "text-start");
      const bubble = document.createElement("span");
      bubble.className =
        "d-inline-block px-3 py-2 rounded " +
        (role === "user" ? "bg-primary text-white" : "bg-light border");
      // Preserve newlines/indentation from the reply (plain text, no Markdown).
      bubble.style.whiteSpace = "pre-wrap";
      bubble.textContent = text;
      wrap.appendChild(bubble);
      chat.appendChild(wrap);
      chat.scrollTop = chat.scrollHeight;
      return bubble;
    }

    function setBusy(busy) {
      input.disabled = busy;
      sendBtn.disabled = busy;
      if (!busy) {
        input.focus();
      }
    }

    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const text = (input.value || "").trim();
      if (!text) {
        return;
      }

      addBubble("user", text);
      history.push({ role: "user", content: text });
      input.value = "";
      setBusy(true);

      const pending = addBubble("assistant", thinkingText);

      let data = {};
      try {
        const res = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify({ messages: history }),
        });
        data = await res.json().catch(function () {
          return {};
        });
        if (!res.ok || typeof data.reply !== "string") {
          throw new Error((data && data.error) || errorText);
        }
      } catch (err) {
        pending.textContent = errorText;
        pending.className = "d-inline-block px-3 py-2 rounded bg-danger text-white";
        setBusy(false);
        return;
      }

      pending.textContent = data.reply;
      history.push({ role: "assistant", content: data.reply });
      setBusy(false);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
