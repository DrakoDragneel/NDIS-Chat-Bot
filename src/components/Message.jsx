import { useState } from "react";

function Sources({ sources }) {
  const [open, setOpen] = useState(false);
  if (!sources || sources.length === 0) return null;

  return (
    <div className="sources">
      <button
        type="button"
        className="sources__toggle"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        {open ? "Hide" : "Show"} where this came from ({sources.length})
      </button>
      {open && (
        <ul className="sources__list">
          {sources.map((s, i) => (
            <li key={i}>
              <span className="sources__cat">{s.category}</span>
              {s.question}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function Message({ role, content, sources }) {
  const isUser = role === "user";
  return (
    <div className={`msg ${isUser ? "msg--user" : "msg--bot"}`}>
      <div className="msg__role" aria-hidden="true">
        {isUser ? "You" : "Assistant"}
      </div>
      <div className="msg__bubble">
        <p>{content}</p>
        {!isUser && <Sources sources={sources} />}
      </div>
    </div>
  );
}
