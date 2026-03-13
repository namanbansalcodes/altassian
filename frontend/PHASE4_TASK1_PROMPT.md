Task: Phase 4 — Fix TypeScript compilation errors and ensure a clean production build.

Steps (run in this repo):
1) npm ci
2) npm run build  # capture all TS errors
3) Fix ALL TypeScript errors and lints (strict where reasonable) until build succeeds
4) Add Vite env for API base URL (VITE_API_BASE) and ensure axios client reads it
5) Verify dev server with backend: npm run dev, test login flow against http://localhost:8000/api/
6) Git commit AND PUSH after each meaningful chunk (use clear messages)

When completely finished, run: openclaw system event --text "Done: Phase 4 — Frontend builds clean; TS errors resolved; login flow verified" --mode now
