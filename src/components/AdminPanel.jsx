import { useState } from "react";
import { getUnanswered } from "../api.js";

export default function AdminPanel() {
  const [token, setToken] = useState("");
  const [items, setItems] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    if (!token.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data = await getUnanswered(token.trim());
      setItems(data.items || []);
    } catch (err) {
      setError(err.message || "Could not load the log.");
      setItems(null);
    } finally {
      setLoading(false);
    }
  }

  // Tally the most frequently asked gap questions.
  const tally = {};
  (items || []).forEach((it) => {
    const q = (it.question || "").trim().toLowerCase();
    if (q) tally[q] = (tally[q] || 0) + 1;
  });
  const topGaps = Object.entries(tally)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);

  return (
    <div className="app">
      <header className="header">
        <div className="header__brand">
          <span className="header__dot" aria-hidden="true" />
          <h1>Unanswered questions</h1>
        </div>
        <p className="header__tag">
          Questions the bot could not answer well. Use these to grow the
          dataset.
        </p>
      </header>

      <main className="chat">
        <div className="admin-auth">
          <label htmlFor="admin-token" className="sr-only">
            Admin token
          </label>
          <input
            id="admin-token"
            className="composer__input"
            type="password"
            placeholder="Enter admin token"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && load()}
          />
          <button
            type="button"
            className="composer__send"
            onClick={load}
            disabled={loading || !token.trim()}
          >
            {loading ? "Loading..." : "Load"}
          </button>
        </div>

        {error && (
          <div className="error" role="alert">
            {error}
          </div>
        )}

        {items && items.length === 0 && (
          <div className="welcome">
            <h2>No gaps logged yet</h2>
            <p>
              Once people ask questions the bot cannot answer, they will appear
              here.
            </p>
          </div>
        )}

        {items && items.length > 0 && (
          <>
            {topGaps.length > 0 && (
              <div className="admin-summary">
                <h3>Most common gaps</h3>
                <ol>
                  {topGaps.map(([q, n]) => (
                    <li key={q}>
                      <span className="admin-count">{n}x</span> {q}
                    </li>
                  ))}
                </ol>
              </div>
            )}

            <div className="admin-list">
              <h3>All entries ({items.length})</h3>
              {items.map((it, i) => (
                <div className="admin-row" key={i}>
                  <div className="admin-row__top">
                    <span
                      className={`admin-tag admin-tag--${
                        it.reason === "no_match" ? "gap" : "weak"
                      }`}
                    >
                      {it.reason === "no_match"
                        ? "No match"
                        : "Weak match"}
                    </span>
                    <span className="admin-time">
                      {(it.timestamp || "").replace("T", " ").slice(0, 16)}
                    </span>
                  </div>
                  <p className="admin-q">{it.question}</p>
                  {it.reason === "low_confidence" && (
                    <p className="admin-meta">
                      Closest: {it.closest_match || "—"}
                      {typeof it.top_score === "number"
                        ? ` (score ${it.top_score})`
                        : ""}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
