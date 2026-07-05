# Security & privacy audit — 2026-07-06

Fifteen findings from a full pass over auth, session handling, secrets,
injection surfaces, access control, and privacy. Eleven were fixed in the
same pass (commit references in git history); four need product decisions.

## Fixed

| Severity | Issue | Fix |
|---|---|---|
| High | `fast_app(live=True, debug=True)` always on — stack traces/source leaked on errors in production | Dev-only, driven by `FEEDFORWARD_ENV=production` (set in docker-compose.prod.yml) |
| High | LLM API keys encrypted with a key derived from a public default `SECRET_KEY` | App refuses to start in production with an unset/default/placeholder `SECRET_KEY` (`app/utils/crypto.py`) |
| Med | Default admin password `Admin123!` baked into `init_db.py` | Production seeding requires `ADMIN_PASSWORD`; default remains dev-only |
| Med | `.env.production` tracked in the public repo (placeholders, but invites a real-secret commit) | Untracked + gitignored; `.env.production.example` remains |
| Med | User enumeration: registration said "User already exists"; forgot-password responses differed by account existence | Generic identical responses in both flows |
| Med | `login_required`/`role_required` ignored `verified`/`approved` flags | Both now reject unverified users; unapproved instructors are logged out |
| Med | No session rotation on login; year-long session cookies without Secure | `session.clear()` on login; `same_site=lax`, `sess_https_only` in production, 7-day `max_age` |
| Med | Email-send failure rendered live verification/reset links in the HTTP response | Dev-only convenience; production returns a generic message |
| Low | `/verify` raised global logging to DEBUG per request and logged emails + tokens | Removed |
| Low | Token-bearing links (verify/reset/invitation) written to logs/stdout | Removed |
| Low | Non-constant-time token comparison | `secrets.compare_digest` for verification and reset tokens |
| Low | Docs path traversal defence was `path.replace("..", "")` | `Path.resolve().is_relative_to(docs_root)` containment check |

## Resolved by product decision (2026-07-06)

1. **Privacy deletion** — decided: FeedForward *retains* draft content so
   students and instructors can track progress across drafts (students can
   hide drafts from their own view). The deletion machinery — including an
   active wipe in `feedback_generator` that erased draft text the moment
   feedback was ready — was removed, and the "temporary storage" claims in
   the privacy policy, terms, README, and docs were corrected.
2. **Open instructor registration** — policy kept (any domain may register,
   pending admin approval), now mitigated with per-IP rate limiting on
   register (5/15 min), login (10/5 min), and forgot-password (5/15 min) —
   `app/utils/rate_limit.py`.
4. **Timing side-channel in forgot-password** — fixed: account emails
   (verification, reset) are sent on a background thread in production
   (`send_email_async`), so response timing no longer depends on account
   existence. Relatedly, the app no longer emails students at all:
   invitations are join links the instructor distributes via their own
   channel (LMS, cohort email).

## Still open

3. **Token storage (Low).** Verification/reset tokens are stored in plaintext
   in SQLite and verification tokens never expire. Hardened comparison is in;
   hashing-at-rest and expiry are follow-ups.

Verified clean: no raw SQL (fastlite throughout), uploads parsed in-memory
(no user-controlled write paths), instructor/student route ownership checks
present, bcrypt via passlib for passwords, all role routes decorated.
