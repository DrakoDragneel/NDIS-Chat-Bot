import { useState, useRef, useEffect } from "react";
import { sendChat } from "./api.js";
import Message from "./components/Message.jsx";
import SuggestionChips from "./components/SuggestionChips.jsx";
import ContactBanner from "./components/ContactBanner.jsx";
import AdminPanel from "./components/AdminPanel.jsx";

const STARTER_SUGGESTIONS = [
  "What is NDIS?",
  "Who is eligible for NDIS?",
  "How do I apply for NDIS?",
];

export default function App() {
  // Admin view: open with #admin in the URL, or set view="admin" on the
  // WordPress shortcode. End users on the normal page never see this.
  const [isAdmin, setIsAdmin] = useState(() => {
    const cfg =
      (typeof window !== "undefined" && window.NDIS_CHATBOT_CONFIG) || {};
    return window.location.hash === "#admin" || cfg.view === "admin";
  });

  useEffect(() => {
    const onHash = () => setIsAdmin(window.location.hash === "#admin");
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  const [messages, setMessages] = useState([]); // {role, content, sources?, suggestions?, show_contact?}
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const listRef = useRef(null);
  const inputRef = useRef(null);

  // The suggestions to show: from the last bot turn, or the starters at the top.
  const lastBot = [...messages].reverse().find((m) => m.role === "assistant");
  const activeSuggestions =
    messages.length === 0
      ? STARTER_SUGGESTIONS
      : lastBot?.suggestions || [];

  const showContact = lastBot?.show_contact && !loading;

  useEffect(() => {
    // Keep the newest message in view.
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages, loading]);

  async function submit(text) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setError("");
    setInput("");

    // Build history from existing messages (role + content only).
    const history = messages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    const userMsg = { role: "user", content: trimmed };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const data = await sendChat(trimmed, history);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          suggestions: data.suggestions,
          show_contact: data.show_contact,
        },
      ]);
    } catch (err) {
      setError(
        err.message ||
          "The assistant could not be reached. Check the connection and try again."
      );
    } finally {
      setLoading(false);
      // Return focus to the input for fast follow-ups.
      if (inputRef.current) inputRef.current.focus();
    }
  }

  function onSubmitForm(e) {
    e.preventDefault();
    submit(input);
  }

  if (isAdmin) {
    return <AdminPanel />;
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header__brand">
          <span className="header__dot" aria-hidden="true" />
          <h1>NDIS Assistant</h1>
        </div>
        <p className="header__tag">
          General information about the NDIS. Not official advice.
        </p>
      </header>

      <main className="chat" ref={listRef} aria-live="polite">
        {messages.length === 0 && (
          <div className="welcome">
            <h2>How can I help with the NDIS?</h2>
            <p>
              Ask about eligibility, funding, providers, plans, or support. Pick
              a question below to get started.
            </p>
          </div>
        )}

        {messages.map((m, i) => (
          <Message
            key={i}
            role={m.role}
            content={m.content}
            sources={m.sources}
          />
        ))}

        {loading && (
          <div className="msg msg--bot">
            <div className="msg__role" aria-hidden="true">
              Assistant
            </div>
            <div className="msg__bubble msg__bubble--typing">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
              <span className="sr-only">Finding an answer</span>
            </div>
          </div>
        )}

        {showContact && <ContactBanner />}

        {error && (
          <div className="error" role="alert">
            {error}
          </div>
        )}
      </main>

      <div className="composer">
        <SuggestionChips
          suggestions={activeSuggestions}
          onPick={submit}
          disabled={loading}
        />
        <form className="composer__form" onSubmit={onSubmitForm}>
          <label htmlFor="chat-input" className="sr-only">
            Type your NDIS question
          </label>
          <input
            id="chat-input"
            ref={inputRef}
            className="composer__input"
            type="text"
            placeholder="Type your question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            autoComplete="off"
          />
          <button
            type="submit"
            className="composer__send"
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
