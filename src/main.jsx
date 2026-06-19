import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
// Import the CSS as a string so we can inject it inside a Shadow DOM,
// which fully isolates the widget from the host theme (and vice versa).
import cssText from "./styles.css?inline";

const host =
  document.getElementById("ndis-chatbot-root") ||
  document.getElementById("root");

let mount;

if (host && host.attachShadow) {
  // Preferred path: render inside a shadow root. No theme CSS can leak in,
  // and none of the widget's CSS can leak out.
  const shadow = host.attachShadow({ mode: "open" });

  const styleEl = document.createElement("style");
  styleEl.textContent = cssText;
  shadow.appendChild(styleEl);

  mount = document.createElement("div");
  mount.className = "ndis-cb";
  shadow.appendChild(mount);
} else if (host) {
  // Fallback for very old browsers without Shadow DOM: scope via class and
  // inject styles into the document head.
  const styleEl = document.createElement("style");
  styleEl.textContent = cssText;
  document.head.appendChild(styleEl);

  mount = document.createElement("div");
  mount.className = "ndis-cb";
  host.appendChild(mount);
}

if (mount) {
  ReactDOM.createRoot(mount).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}
