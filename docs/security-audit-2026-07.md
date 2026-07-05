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

## Open — needs a product decision

1. **Privacy deletion never runs (High).** The "privacy-by-design" draft
   content removal (`app/utils/privacy.py`) only logs; `cleanup_draft_content`
   has no callers. Student submissions are retained indefinitely, contradicting
   the platform's stated model. Needs a real scheduled job (cron/task queue)
   and a decision on retention windows.
2. **Open instructor registration (Low).** `is_institutional_email` treats any
   unrecognized domain as an instructor pending approval. If registration
   should be whitelist-only, unknown domains should be rejected outright.
3. **Token storage (Low).** Verification/reset tokens are stored in plaintext
   in SQLite and verification tokens never expire. Hardened comparison is in;
   hashing-at-rest and expiry are follow-ups.
4. **Timing side-channel in forgot-password (Low).** Responses are now
   identical, but the found-path still does token generation + synchronous
   SMTP; sending out-of-band would close the timing signal.

Verified clean: no raw SQL (fastlite throughout), uploads parsed in-memory
(no user-controlled write paths), instructor/student route ownership checks
present, bcrypt via passlib for passwords, all role routes decorated.
