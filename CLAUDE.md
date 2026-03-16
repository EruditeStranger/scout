# Project: Asago-to-the-Moon 🚀

A career transition toolkit built by her boyfriend (engineer) to help Sumika Moriwaki pivot from Japanese local administration to the globalized "Japan B" market — and to feel less alone while doing it.

---

## 1. Mission

Stop "plowing a rice field with a Ferrari." Move the search to highways — organizations that value an M.A. from Boston University and 6.5 years of international crisis management experience.

## 2. Candidate Profile: Sumika Moriwaki

- **Academic:** M.A. International Relations, Boston University (Pardee School, 2025); B.A. Intercultural Studies, Yamaguchi Prefectural University
- **Experience:** 6.5 years as International Exchange Program Coordinator at Himeji Cultural and International Exchange Foundation
- **Highlights:** 4-country Duty of Care (Belgium, Australia, South Korea, Singapore), 11-country program portfolio, 1,000+ annual participants, 50+ volunteer network, 7-language newsletter, sister-city diplomacy
- **Certifications:** Johns Hopkins International Travel Safety, TESOL, Japanese Language Teacher, Tea Ceremony Instructor, Goodwill Guide
- **Languages:** Japanese (native), English (advanced)
- **Location:** Hyogo Prefecture (Asago/Ikuno), Japan

## 3. Architecture Decisions

### Delivery layers (decided 2026-03-16)

| Layer | Tool | Rationale |
|---|---|---|
| Job scraping + scoring | **GitHub Actions** cron → `main.py` | Free, stateless, already working |
| Real-time alerts & hype | **Discord** webhooks | She has notifications on, it's their shared project space |
| Structured job management | **Vercel app** (planned) | Search, filter, track applications, story coaching — things Discord can't do |
| Personal communication | **LINE** (no automation) | Keep their intimate channel free of bots |

### Why not LINE for notifications?
LINE Notify shut down March 2025. LINE Messaging API requires a business account (feels impersonal). She already gets Discord notifications. Don't fix what works.

### Token optimization protocol
- **Opus 4.6:** Planning, architecture decisions, ideation, CLAUDE.md updates
- **Sonnet 4.6:** Code execution, file edits, implementation tasks
- Keep CLAUDE.md updated at decision points so either model has full context

## 4. Repository Structure

```
scout/
├── main.py                  # Scraper: multi-source, Ferrari Score (1-10), Discord alerts + heartbeat + hype
├── requirements.txt         # requests, beautifulsoup4
├── targets.json             # Curated "highway" organizations
├── seen_jobs.json           # Tracked jobs with metadata (auto-generated)
├── CLAUDE.md                # This file — project context for AI agents
├── SKILLS.md                # Reusable skill definitions for implementation
├── .github/workflows/
│   └── scrape.yaml          # Cron: scrape 9AM/9PM JST, hype 3PM JST
├── docs/
│   ├── resume_master.md     # Full resume in markdown (from PDF)
│   ├── stories_bank.md      # STAR-method narratives (EN + JP)
│   ├── Sumika_Moriwaki_BU_Grad_Resume.pdf
│   └── sample_cover_letter.txt  # Two sample cover letters
└── prompts/
    └── tailor_cover_letter.txt  # LLM prompt for cover letter generation
```

## 5. Discord Setup ("Asago-to-the-Moon" server)

| Channel | Webhook secret | Purpose |
|---|---|---|
| `#🚨-scout-alerts` | `DISCORD_WEBHOOK_URL` | Job leads with Ferrari Score + framing angle |
| `#🛠-system-status` | `HEARTBEAT_WEBHOOK_URL` | Scraper heartbeat after each run |
| `#📍-the-north-star` | `HYPE_WEBHOOK_URL` | Daily motivational messages (3 PM JST) |
| `#📝-resume-lab` | — | Manual: iterate on CV versions |

All three secrets can point to the same webhook during development.

## 6. Scraper (`main.py`)

- **Sources:** JICA PARTNER, JICA Careers, JETRO, Hyogo International Association
- **Scoring:** Weighted JP/EN keyword matching → normalized 1-10 "Ferrari Score"
- **Alerts:** Discord embeds with score, source, and contextual "Framing Angle" (suggests how to position her experience for each role)
- **Hype mode:** `python main.py --hype` sends a motivational message drawn from her real accomplishments
- **Pluggable:** Add a new source by writing a function that returns `list[dict]` and appending to `SCRAPERS`

## 7. Vercel App (planned — not yet built)

Target features:
- **Job dashboard:** View/filter/sort scraped leads by score, source, status
- **Application tracker:** Mark jobs as "interested" / "applied" / "rejected" / "blacklisted"
- **Organization management:** Radar list, blacklist, notes
- **Keyword search:** Custom keyword entry for manual searches
- **Story coaching:** STAR method practice tool sourced from stories_bank.md
- **Hype section:** Motivational content she can visit when she needs it

Tech stack TBD — likely Next.js + Vercel KV or similar lightweight persistence.

## 8. Content Pipeline

- `docs/resume_master.md` — canonical resume, reframed as "Global Program & Risk Lead"
- `docs/stories_bank.md` — STAR narratives (currently 2, expand to cover all 4 countries + pandemic pivot)
- `prompts/` — LLM instructions for tailoring cover letters, Self-PR statements, LinkedIn outreach
- Target orgs: Sysmex, P&G Japan (Kobe), Nestlé Japan (Kobe), AstraZeneca Osaka, JICA, JETRO, Hyogo Intl Association, international NGOs in Kansai

## 9. Empathy Guideline

All generated content must emphasize her immense responsibility (4-country safety oversight, 1,000+ participant programs, diplomatic liaison work). Combat the "unemployable" / "overqualified" mindset. She is underdeployed, not underqualified. The right organizations will see that.
