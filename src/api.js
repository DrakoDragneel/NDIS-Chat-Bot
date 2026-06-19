// Base URL of the FastAPI / Node backend.
// Priority: WordPress-injected config (set in the WP admin) > build-time env > local default.
const WP_CONFIG =
  typeof window !== "undefined" ? window.NDIS_CHATBOT_CONFIG || {} : {};

const API_URL =
  WP_CONFIG.apiUrl || import.meta.env.VITE_API_URL || "http://localhost:5000";

/**
 * Send a chat message to the backend.
 *
 * @param {string} message - the user's question
 * @param {Array<{role: string, content: string}>} history - prior turns
 * @returns {Promise<{answer: string, suggestions: string[], show_contact: boolean, sources: object[]}>}
 */
export async function sendChat(message, history) {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok) {
    let detail = "";
    try {
      const data = await response.json();
      detail = data.detail || "";
    } catch {
      // response had no JSON body
    }
    throw new Error(detail || `Request failed (${response.status}).`);
  }

  return response.json();
}

/**
 * Fetch the logged gap questions (unanswered + low-confidence) for review.
 * Requires the admin token that matches ADMIN_TOKEN on the backend.
 *
 * @param {string} token
 * @returns {Promise<{count: number, items: object[]}>}
 */
export async function getUnanswered(token) {
  const response = await fetch(
    `${API_URL}/api/unanswered?token=${encodeURIComponent(token)}`
  );

  if (response.status === 403) {
    throw new Error("Wrong or missing admin token.");
  }
  if (!response.ok) {
    throw new Error(`Request failed (${response.status}).`);
  }

  return response.json();
}
