# SpeakMate AI

**Speak More. Improve Faster.**

An AI speaking-practice platform for English learners, built entirely in Python with
Streamlit. You pick a prompt, record an answer in the browser, and get a scored report:
fluency, grammar, vocabulary and coherence, with corrections tied to what you actually
said. Progress, streaks and a personal vocabulary list carry across sessions.

SpeakMate AI is an original project. It is not affiliated with any language-learning
company or examination board, and no branding, copy, interface or code has been taken
from another product.

---

## Features

- **Landing page** with pricing and FAQ for signed-out visitors
- **Accounts** — register, sign in, sign out, PBKDF2-SHA256 password hashing, per-session
  login throttling
- **Onboarding** — first language, CEFR level (A1–C2), goal, interests, daily target
- **Dashboard** — speaking time, sessions, words learned, streak, today's prompt, latest
  feedback, words due for review, 14-day activity charts
- **Speaking practice** — free talk, job interview, role play and IELTS Parts 1–3;
  in-browser recording, file upload fallback, and a typed-answer mode for when no
  microphone is available
- **Speech to text** via an OpenAI-compatible transcription endpoint
- **AI analysis** validated with Pydantic, with a built-in offline analyser as a fallback
- **Grammar corrections** — your sentence, the fix, and the rule in one line; capped at
  two corrections for A1/A2 learners
- **Vocabulary feedback** — stronger replacements for words you overused, saveable in one
  click, with meanings, examples and difficulty
- **Fluency analysis** — filler words, repetition, word variety, sentence length, linking
  words and speaking pace, all computed from your transcript
- **Pronunciation (experimental)** — volume and pausing measured from the waveform, with
  an explicit statement that this is not phoneme-level scoring. No score is invented when
  it cannot be measured.
- **Vocabulary** — list, search, flashcards with mastery grading, a quiz built from your
  own words, manual entry, CSV export
- **History** — every past session, reopenable as a full report, deletable
- **Progress** — sessions, minutes, band averages, score trend, vocabulary growth
- **Streaks** — current and longest, reset correctly after a missed day
- **Profile and settings** — level, goals, interests, daily target, bio, recording-storage
  preference, password change
- **Admin** — users, sessions, platform statistics, topic library management
- **Free plan** — five AI analyses a day, tracked and enforced, with a clear message at
  the limit. No payment is collected.

---

## Architecture

```
speakmate/
├── app.py                  entry point, session bootstrap, routing, error boundary
├── requirements.txt
├── check_setup.py          verifies the layout before deploying
├── README.md
├── .gitignore
├── .env.example
├── database/
│   ├── database.py         engine, session_scope(), init_db()
│   ├── models.py           users, profiles, practice_sessions, feedback,
│   │                       grammar_corrections, vocabulary, progress,
│   │                       practice_topics, settings
│   └── seed.py             practice topics + first administrator
├── pages/
│   ├── auth.py             landing page, sign in, register
│   ├── onboarding.py       first-run setup
│   ├── dashboard.py
│   ├── practice.py         the core loop
│   ├── vocabulary.py       list, flashcards, quiz, add
│   ├── progress.py
│   ├── history.py
│   ├── profile.py
│   ├── settings.py
│   └── admin.py
├── services/
│   ├── auth_service.py     registration, login, authorization
│   ├── ai_service.py       prompts, Pydantic validation, fallback
│   ├── speech_service.py   transcription, waveform measurements
│   ├── feedback_service.py offline analysis + persistence
│   └── progress_service.py streaks, rollups, usage limits, vocabulary
├── components/
│   ├── sidebar.py  cards.py  charts.py  feedback.py  ui.py
├── utils/
│   ├── config.py  validation.py  helpers.py
├── tests/test_speakmate.py
├── data/speakmate.db       created on first run
└── .streamlit/config.toml
```

Pages are plain modules exposing `render(user)`. Navigation is a custom sidebar, and
Streamlit's automatic page list is hidden so the sidebar stays the single source of truth.

**Layering.** Pages never touch the ORM directly for business logic; they call services.
Services own transactions through `session_scope()`. Every query that reads user data is
filtered by `user_id`, so one account cannot read another's sessions or vocabulary by
guessing an id.

---

## Installation

Requires **Python 3.11 or newer**.

```bash
git clone <your-repo-url>
cd speakmate

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Environment variables

```bash
cp .env.example .env
```

| Variable | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | for AI features | Transcription and analysis |
| `OPENAI_BASE_URL` | no | Point at any OpenAI-compatible gateway |
| `SPEAKMATE_CHAT_MODEL` | no | Analysis model (default `gpt-4o-mini`) |
| `SPEAKMATE_STT_MODEL` | no | Transcription model (default `whisper-1`) |
| `SPEAKMATE_DB_URL` | no | Database URL (default local SQLite) |
| `SPEAKMATE_FREE_DAILY_ANALYSES` | no | Free-plan daily cap (default 5) |
| `SPEAKMATE_MAX_TRANSCRIPT_CHARS` | no | Transcript cap sent to the model (default 1800) |
| `SPEAKMATE_MAX_AUDIO_MB` | no | Upload ceiling (default 12) |
| `SPEAKMATE_ADMIN_EMAIL` / `SPEAKMATE_ADMIN_PASSWORD` | no | Seeded admin account |

**The app runs without an API key.** Transcription is disabled, and the typed-answer mode
is scored by the built-in offline analyser, which is labelled as such in the report.

### OpenAI setup

1. Create a key at <https://platform.openai.com/api-keys>.
2. Put it in `.env` as `OPENAI_API_KEY=sk-...`.
3. Restart the app.

Keys are read from Streamlit secrets or the environment at call time. They are never
written to the database, never placed in session state, and never rendered in the UI.

### Run locally

```bash
streamlit run app.py
```

Open <http://localhost:8501>. The database is created automatically on first run, along
with about 30 practice topics. **The first account you register becomes the
administrator.**

---

## Deploying to Streamlit Community Cloud

1. Push this folder to a public GitHub repository.
2. At <https://share.streamlit.io>, create an app pointing at your repo.
3. Set **Main file path** to `app.py`.
4. Open **Advanced settings → Secrets** and paste:

```toml
OPENAI_API_KEY = "sk-your-key"
# optional
SPEAKMATE_CHAT_MODEL = "gpt-4o-mini"
SPEAKMATE_ADMIN_PASSWORD = "a-strong-password"
```

5. Deploy.

**Storage caveat.** Community Cloud containers have an ephemeral filesystem, so the SQLite
file is wiped whenever the app restarts or redeploys. That is fine for a demo. For
anything persistent, set `SPEAKMATE_DB_URL` to a hosted Postgres instance — SQLAlchemy
handles the rest, and the only extra requirement is adding `psycopg2-binary` to
`requirements.txt`.

Microphone capture requires HTTPS, which Community Cloud provides. On `localhost` browsers
also allow it. On any other plain-HTTP host the recorder will not start, and the upload or
typed-answer paths are the fallback.

---

### If Streamlit Cloud says `ModuleNotFoundError`

The traceback points at the first local import in `app.py`. Almost always the cause is a
missing package folder in the repository rather than a code problem. Check three things:

1. **`__init__.py` files.** Each of `components/`, `database/`, `pages/`, `services/` and
   `utils/` needs one. GitHub's drag-and-drop web uploader silently skips zero-byte files,
   which is why every `__init__.py` here carries a docstring. Push from the command line
   with `git add -A` if you are unsure.
2. **Where `app.py` sits.** In the app settings, **Main file path** must match the file's
   real location in the repo. If `app.py` is inside a `speakmate/` folder, the path is
   `speakmate/app.py`, and the package folders must sit beside it in that same folder.
3. **Run the checker.** From the folder holding `app.py`:

   ```bash
   python check_setup.py
   ```

   It lists any missing or empty file and exits non-zero. Run it locally before pushing.

After fixing the repository, click **Reboot app** in Streamlit Cloud — a redeploy alone
sometimes serves a cached build.

---

## Database

SQLite through SQLAlchemy 2.0, created at `data/speakmate.db` on first run. Nine tables:
`users`, `profiles`, `practice_sessions`, `feedback`, `grammar_corrections`,
`vocabulary`, `progress`, `practice_topics`, `settings`, with foreign keys and cascade
deletes throughout. All access goes through the ORM, so values are parameterised and
string-built SQL never appears.

To start over, stop the app and delete `data/speakmate.db`.

---

## Testing

```bash
pip install pytest
pytest -q
```

The suite redirects the app to a temporary database and covers password hashing,
registration, authentication, authorization, schema creation, vocabulary operations,
progress totals, streak increment and reset, free-plan limits, Pydantic validation of
model output (including malformed and out-of-range values), the grammar and fluency
heuristics, practice history, and cross-account access attempts.

---

## Security

Passwords are hashed with PBKDF2-SHA256, 240,000 iterations and a per-password salt, and
compared with a constant-time check. Every input is validated and length-capped before it
reaches the database. Admin screens re-read the role from the database on each action
rather than trusting the session, so hiding a menu item is never the control. Audio is
size-checked and held in memory only for the length of the analysis unless the user turns
on recording storage. Transcripts sent to the model are truncated to a configured
maximum. Exceptions are logged server-side; users see a plain message, never a traceback.

---

## Cost control

Prompts are short and ask for a fixed JSON shape. Transcripts are truncated. Each analysis
is one chat call plus one transcription call, and the free plan caps that at five a day
per account, counted in the `progress` table. Topic generation is optional and only fires
when the user asks for it.

---

## What this version does not do

Streamlit has no native real-time multiplayer video, and none is faked here. There are no
live rooms, no peer matching and no simulated partners. Human-to-human conversation needs
WebRTC infrastructure — LiveKit or similar, with a Next.js or comparable frontend — which
is Version 3 on the roadmap below, not a feature hidden behind a coming-soon label.

Pronunciation is handled the same way. Volume and pausing are measurable from the
waveform, so those are shown. Phoneme accuracy is not, so no number is invented for it.

---

## Roadmap

**Version 1 (this release)** — AI speaking practice, voice recording, transcription, AI
feedback, grammar correction, vocabulary, progress, history, authentication.

**Version 2** — AI conversational voice mode (multi-turn spoken dialogue), more target
languages, advanced pronunciation scoring, fuller IELTS and TOEFL modes.

**Version 3** — human-to-human matching, WebRTC/LiveKit live conversation rooms,
messaging. This is the point at which the frontend moves off Streamlit.

**Version 4** — subscriptions through Stripe, mobile application, advanced analytics.

The `plan` field on `users` and the usage counters in `progress` already exist, so adding
billing is a matter of wiring a payment webhook to flip `plan` and raise the cap.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `streamlit: command not found` | Activate the virtual environment, then reinstall requirements. |
| The recorder never starts | Allow microphone access for the site, use HTTPS or localhost, or use the upload / typed-answer path. |
| "Transcription needs an API key" | Add `OPENAI_API_KEY` to `.env` or to Streamlit secrets and restart. |
| "The API key was rejected" | The key is wrong, revoked, or out of credit. |
| Report says "offline analyser" | No key is configured, or the AI call failed; the app scored your answer locally. |
| "You've reached today's free practice limit" | Five analyses per account per day. The counter resets at midnight UTC. |
| `ModuleNotFoundError` on Cloud | A package folder or its `__init__.py` is missing from the repo. Run `python check_setup.py`, then push and reboot. |
| Database errors on start | Make sure `data/` is writable, or delete `data/speakmate.db` to rebuild. |
| Data disappeared after redeploy | Expected on Community Cloud. Use a hosted database via `SPEAKMATE_DB_URL`. |
