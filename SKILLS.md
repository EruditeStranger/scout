# Skills Reference for Scout

Reusable patterns and domain knowledge for building this project. Intended for AI agents (primarily Sonnet 4.6 during execution).

---

## Skill: Discord Webhook Messaging

**When:** Sending alerts, heartbeats, or hype messages from GitHub Actions or scripts.

**Pattern:**
```python
import requests

def send_discord_embed(webhook_url: str, title: str, description: str, color: int, fields: list[dict] = None):
    payload = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "fields": fields or [],
        }]
    }
    requests.post(webhook_url, json=payload, timeout=10)
```

**Color conventions in this project:**
- `0xFF4500` — hot lead (score 8+)
- `0xFFA500` — warm lead (score 5-7)
- `0x808080` — low score
- `0x00FF00` — heartbeat OK
- `0xFF0000` — heartbeat error
- `0xFFD700` — hype message

**Limits:** Discord webhooks allow 30 requests/60s. Batch if needed.

---

## Skill: Ferrari Score Computation

**When:** Evaluating a job listing's relevance to Sumika's profile.

**Logic:** Weighted keyword matching against JP and EN terms. Raw score normalized to 1-10 (15+ raw → 10). See `KEYWORD_WEIGHTS` in `main.py`.

**High-weight keywords (5):** 危機管理, 修士歓迎, 姉妹都市, crisis management, risk management
**Medium-weight keywords (3-4):** 国際, 海外, コーディネーター, 修士, 外交, intercultural, coordinator, bilingual, program manager

**Framing angles by keyword cluster:**
- Safety/crisis → "Lead with 4-country Duty of Care & Johns Hopkins cert"
- International/global → "Emphasize 11-country portfolio & BU M.A."
- Coordination → "6.5 yrs coordinating 20+ annual programs, 1000+ participants"
- Diplomatic → "Sister-city diplomacy across multiple continents"
- Volunteer/community → "50+ volunteer network, 7-language newsletter"
- Language → "Native JP + Advanced EN, TESOL certified"

---

## Skill: Adding a New Scraper Source

**When:** Expanding job coverage to a new site.

**Steps:**
1. Write a function `scrape_<source>() -> list[dict]` in `main.py`
2. Each job dict must have: `title`, `link`, `description`, `source`, `score`
3. Use `compute_ferrari_score(full_text)` for scoring
4. Wrap HTTP calls in try/except, print warnings on failure
5. Append function to `SCRAPERS` list
6. Add the org to `targets.json` if not already there

**Template:**
```python
def scrape_new_source() -> list[dict]:
    """Scrape [Source Name] for job listings."""
    url = "https://..."
    jobs = []
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # ... parse jobs ...
        for item in soup.select("..."):
            title = item.get_text(strip=True)
            link = item.get("href", "")
            jobs.append({
                "title": title,
                "link": link,
                "description": "",
                "source": "Source Name",
                "score": compute_ferrari_score(title),
            })
    except requests.RequestException as e:
        print(f"[WARN] Source Name scrape failed: {e}")
    return jobs
```

---

## Skill: Tailoring Content for Sumika

**When:** Generating cover letters, LinkedIn messages, Self-PR, or story coaching.

**Rules:**
1. Never use "assistant" or "secretary" — use "coordinator," "liaison," "program lead"
2. Frame admin work as "operations management" and "diplomatic support"
3. Always quantify: 20+ programs/year, 1,000+ participants, 11 countries, 50+ volunteers, 7 languages
4. The 4-country chaperone duty = "International Risk Management & Field Operations"
5. M.A. from BU = "evidence of high-level analytical capacity and resilience in global contexts"
6. Tea ceremony / crochet / teaching certs = cultural depth, not hobbies
7. Bilingual in JP/EN with content: position as "High-Context Intercultural Liaison"
8. All content should combat her "overqualified = unemployable" mindset

**Target audience for Kansai outreach:**
- JAC Recruitment (Osaka/Kobe)
- Robert Walters Japan
- Hays Japan
- Global HQs: Sysmex, P&G Japan (Kobe), Nestlé Japan (Kobe), AstraZeneca (Osaka)
- International orgs: JICA, JETRO, Hyogo International Association

---

## Skill: STAR Story Generation

**When:** Expanding stories_bank.md or coaching interview preparation.

**Existing stories:** Singapore crisis management, Himeji sister-city diplomacy.

**Untold stories to develop (from resume):**
- Pandemic pivot: creating online exchange programs when travel stopped
- 7-language newsletter: managing multilingual communication at scale
- 1,000-person festival: coordinating 30+ volunteer groups for the international friendship festival
- Elementary school program: designing global awareness curriculum for 30 students
- BosMUN 2025: recent US-based international conference logistics

**Format:** Always dual-language (EN + JP). English version should be "High-Impact Professional Storytelling" — not direct translation, but reframed for global employers.

---

## Skill: Vercel App Development (future)

**Stack (proposed):** Next.js 14+ (App Router), Vercel KV or Postgres for persistence, Tailwind CSS.

**Data flow:**
1. GitHub Actions runs `main.py` → writes scored jobs to a data store (Vercel KV, or push to a Vercel API route)
2. Vercel app reads from data store → renders dashboard
3. Sumika interacts (filter, mark status, search) → writes back to data store

**Key pages (planned):**
- `/` — Dashboard: latest leads sorted by Ferrari Score
- `/jobs` — Full job list with filters (source, score, status, blacklist)
- `/tracker` — Application tracker (interested → applied → interview → result)
- `/stories` — STAR coaching tool
- `/hype` — Motivational content on demand

**Auth:** Simple password or magic link — this is a private tool for one person.
