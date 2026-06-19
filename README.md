# NDIS Assistant - React Frontend

A chat interface for the NDIS chatbot backend (Python FastAPI or Node).
Built with React + Vite. Connects to the backend's `/api/chat` endpoint.

## Features

- Multi-turn chat: sends conversation history so follow-up questions work
- Clickable suggested questions (from the backend)
- Expandable "where this came from" sources under each answer
- Contact banner appears when the bot recommends reaching a human
- Accessible: large readable type, high contrast, keyboard focus styles,
  screen-reader live region, and respects reduced-motion

## Requirements

- Node.js 18 or newer
- The NDIS backend running and reachable

## Setup

```bash
npm install
cp .env.example .env     # set VITE_API_URL to your backend URL
npm run dev
```

Open the URL Vite prints (default http://localhost:5173).

## Connecting to the backend

The frontend reads the backend URL from `VITE_API_URL` in `.env`:

```env
VITE_API_URL=http://localhost:5000
```

If the backend runs elsewhere (a server, Render, etc.), set that URL instead.
Make sure the backend's CORS settings allow this frontend's domain.

## Build for production

```bash
npm run build
```

The static site is written to `dist/`. Host it anywhere static files are
served (Netlify, Vercel, a CDN, or alongside your backend). To preview the
production build locally:

```bash
npm run preview
```

## Project structure

```
ndis-chatbot-react/
  index.html
  vite.config.js
  .env.example
  src/
    main.jsx
    App.jsx                  # main chat logic + state
    api.js                   # fetch wrapper for /api/chat
    styles.css               # design system
    components/
      Message.jsx            # chat bubble + sources
      SuggestionChips.jsx    # clickable follow-ups
      ContactBanner.jsx      # "speak with someone" banner
```

## Notes

- Fonts (Bricolage Grotesque, Hanken Grotesk) load from Google Fonts. If you
  need fully offline/self-hosted fonts, download them and update `index.html`.
- The phone numbers in the contact banner are the standard NDIA and NDIS
  Commission lines. Confirm them with your client before launch.
