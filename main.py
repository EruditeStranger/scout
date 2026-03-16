"""
Scout: Career opportunity scraper for Project Asago-to-the-Moon.
Scrapes job boards, scores listings against Sumika's profile, and
posts high-value leads to Discord via webhook.
"""

import requests
from bs4 import BeautifulSoup
import os
import json
import re
import datetime
import random

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
HEARTBEAT_WEBHOOK_URL = os.getenv("HEARTBEAT_WEBHOOK_URL", WEBHOOK_URL)
HYPE_WEBHOOK_URL = os.getenv("HYPE_WEBHOOK_URL", WEBHOOK_URL)
DB_FILE = "seen_jobs.json"
TARGETS_FILE = "targets.json"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# ---------------------------------------------------------------------------
# Ferrari Score: keyword weights (higher = more relevant to Sumika's profile)
# ---------------------------------------------------------------------------
KEYWORD_WEIGHTS = {
    # Japanese keywords
    "国際": 3,
    "海外": 3,
    "危機管理": 5,
    "調整": 2,
    "コーディネーター": 4,
    "修士": 4,
    "修士歓迎": 5,
    "運営": 2,
    "外交": 4,
    "交流": 3,
    "姉妹都市": 5,
    "ボランティア": 2,
    "多文化": 4,
    "異文化": 4,
    "英語": 3,
    "通訳": 3,
    "翻訳": 3,
    "プログラム管理": 4,
    "リスク管理": 5,
    "安全管理": 4,
    "渡航": 3,
    "大学院": 4,
    # English keywords
    "international": 3,
    "coordinator": 4,
    "crisis management": 5,
    "risk management": 5,
    "exchange": 3,
    "diplomatic": 4,
    "intercultural": 4,
    "cross-cultural": 4,
    "master": 4,
    "global": 3,
    "bilingual": 3,
    "program manager": 4,
    "operations": 2,
}

MAX_SCORE = 10


def compute_ferrari_score(text: str) -> int:
    """Score a job listing 1-10 based on keyword relevance to Sumika's profile."""
    text_lower = text.lower()
    raw = 0
    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword.lower() in text_lower:
            raw += weight
    # Normalize: cap at MAX_SCORE. A raw score of 15+ maps to 10.
    score = min(MAX_SCORE, max(1, round(raw * MAX_SCORE / 15)))
    return score


def score_emoji(score: int) -> str:
    if score >= 8:
        return "🔥🔥🔥"
    elif score >= 5:
        return "🔥"
    else:
        return "📍"


# ---------------------------------------------------------------------------
# Scrapers — one per source
# ---------------------------------------------------------------------------

def scrape_jica_partner() -> list[dict]:
    """Scrape JICA PARTNER job listings (the main board with ~300 listings)."""
    url = "https://partner.jica.go.jp/Recruit/Search"
    jobs = []
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Job cards use class "for-clawler" (their typo)
        for card in soup.select(".for-clawler"):
            # Extract text and link from the card
            link_elem = card.select_one("a")
            if not link_elem:
                continue

            title = link_elem.get_text(strip=True)
            href = link_elem.get("href", "")
            if not href.startswith("http"):
                href = "https://partner.jica.go.jp" + href

            # Get surrounding text for scoring context
            description = card.get_text(strip=True)
            full_text = f"{title} {description}"

            jobs.append({
                "title": title,
                "link": href,
                "description": description[:300],
                "source": "JICA PARTNER",
                "score": compute_ferrari_score(full_text),
            })

        # Also try pagination if available
        if not jobs:
            # Fallback: try the results container directly
            container = soup.select_one("#partialViewContainer")
            if container:
                for link_elem in container.select("a[href*='/Recruit/']"):
                    title = link_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    href = link_elem.get("href", "")
                    if not href.startswith("http"):
                        href = "https://partner.jica.go.jp" + href
                    jobs.append({
                        "title": title,
                        "link": href,
                        "description": "",
                        "source": "JICA PARTNER",
                        "score": compute_ferrari_score(title),
                    })

    except requests.RequestException as e:
        print(f"[WARN] JICA PARTNER scrape failed: {e}")
    return jobs


def scrape_jetro() -> list[dict]:
    """Scrape JETRO recruitment sub-pages for active openings."""
    base = "https://www.jetro.go.jp"
    sub_pages = [
        "/jetro/recruit/",            # Main recruitment portal
        "/jetro/recruit/career/",     # Experienced hire
        "/jetro/recruit/staff-1.html",  # Full-time contract
        "/jetro/recruit/staff.html",    # Part-time contract
        "/jetro/recruit/advisor.html",  # Advisors/specialists
        "/jetro/recruit/ninkitsuki.html",  # Fixed-term
    ]
    jobs = []
    seen_links = set()

    for path in sub_pages:
        url = base + path
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            for link_elem in soup.select("a"):
                title = link_elem.get_text(strip=True)
                href = link_elem.get("href", "")
                # Look for active recruitment announcements
                if any(kw in title for kw in ["募集", "採用", "職員", "スタッフ", "求人", "応募"]):
                    if not href.startswith("http"):
                        href = base + href
                    if href not in seen_links:
                        seen_links.add(href)
                        jobs.append({
                            "title": title,
                            "link": href,
                            "description": "",
                            "source": "JETRO",
                            "score": compute_ferrari_score(title),
                        })
        except requests.RequestException as e:
            print(f"[WARN] JETRO scrape failed for {path}: {e}")
    return jobs


# Registry of all scrapers
SCRAPERS = [
    scrape_jica_partner,
    scrape_jetro,
]


# ---------------------------------------------------------------------------
# Persistence — seen jobs with metadata
# ---------------------------------------------------------------------------

def load_seen_jobs() -> dict:
    """Load seen jobs. Returns dict of link -> metadata."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Migration: old format was a flat list of links
            if isinstance(data, list):
                return {link: {"seen_at": "unknown"} for link in data}
            return data
    return {}


def save_seen_jobs(seen: dict):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Discord notifications
# ---------------------------------------------------------------------------

def notify_discord(job: dict):
    """Post a scored job alert to Discord."""
    if not WEBHOOK_URL:
        print(f"[DRY RUN] {job['source']} | {job['title']} | Score: {job['score']}")
        return

    score = job["score"]
    emoji = score_emoji(score)
    framing = suggest_framing(job)

    embed = {
        "embeds": [{
            "title": f"{emoji} Ferrari Score: {score}/10",
            "description": f"**{job['title']}**",
            "url": job["link"],
            "color": 0xFF4500 if score >= 8 else 0xFFA500 if score >= 5 else 0x808080,
            "fields": [
                {"name": "Source", "value": job["source"], "inline": True},
                {"name": "Score", "value": f"{'🟢' * min(score, 10)}", "inline": True},
                {"name": "Framing Angle", "value": framing, "inline": False},
            ],
            "footer": {"text": f"Scout | {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"},
        }]
    }

    try:
        requests.post(WEBHOOK_URL, json=embed, timeout=10)
    except requests.RequestException as e:
        print(f"[WARN] Discord notify failed: {e}")


def suggest_framing(job: dict) -> str:
    """Suggest how Sumika should frame her experience for this role."""
    text = f"{job['title']} {job.get('description', '')}".lower()

    angles = []
    if any(kw in text for kw in ["危機", "crisis", "risk", "安全", "safety"]):
        angles.append("Lead with 4-country Duty of Care & Johns Hopkins safety cert")
    if any(kw in text for kw in ["国際", "international", "global", "海外"]):
        angles.append("Emphasize 11-country program portfolio & BU M.A.")
    if any(kw in text for kw in ["調整", "coordinator", "コーディネーター", "運営"]):
        angles.append("Highlight 6.5 yrs coordinating 20+ annual programs, 1000+ participants")
    if any(kw in text for kw in ["外交", "diplomatic", "姉妹", "sister"]):
        angles.append("Sister-city diplomacy across multiple continents")
    if any(kw in text for kw in ["ボランティア", "volunteer", "community"]):
        angles.append("50+ volunteer network management & 7-language newsletter")
    if any(kw in text for kw in ["英語", "english", "bilingual", "通訳", "翻訳"]):
        angles.append("Native JP + Advanced EN, TESOL certified")

    if not angles:
        angles.append("Frame as 'International Ops & Cross-Cultural Program Management'")

    return "\n".join(f"• {a}" for a in angles[:3])


def send_heartbeat(stats: dict):
    """Post a system status heartbeat to Discord."""
    webhook = HEARTBEAT_WEBHOOK_URL
    if not webhook:
        print(f"[DRY RUN] Heartbeat: {stats}")
        return

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    embed = {
        "embeds": [{
            "title": "💓 Scout Heartbeat",
            "color": 0x00FF00 if stats.get("errors", 0) == 0 else 0xFF0000,
            "fields": [
                {"name": "Sources Scraped", "value": str(stats.get("sources", 0)), "inline": True},
                {"name": "New Leads", "value": str(stats.get("new_jobs", 0)), "inline": True},
                {"name": "Errors", "value": str(stats.get("errors", 0)), "inline": True},
                {"name": "Total Tracked", "value": str(stats.get("total_tracked", 0)), "inline": True},
            ],
            "footer": {"text": f"Scout | {now}"},
        }]
    }

    try:
        requests.post(webhook, json=embed, timeout=10)
    except requests.RequestException as e:
        print(f"[WARN] Heartbeat failed: {e}")


# ---------------------------------------------------------------------------
# Hype system — motivational messages for #the-north-star
# ---------------------------------------------------------------------------

HYPE_MESSAGES = [
    "**Remember:** You managed international safety logistics across 4 countries. Most people never even get a passport. You're not unemployable — you're *underdeployed*. 🚀",
    "**Fact check:** You have an M.A. from Boston University, 6.5 years of diplomatic experience, and certifications most hiring managers can only dream of listing. The right door hasn't opened yet. That's all. 🔑",
    "**You coordinated programs for 1,000+ people.** That's not 'just admin.' That's operations leadership at scale. Own it. 💪",
    "**They said 'overqualified.'** Translation: *they couldn't afford you.* The highway is where you belong, not the rice field. 🏎️",
    "**11 countries. 7 languages. 50+ volunteers. 20+ annual programs.** Read that again. That's your resume. You built that. ✨",
    "**The Ferrari doesn't belong in a typewriter shop.** Today might feel slow, but you're heading for the highway. 🛣️",
    "**Quick reminder:** Johns Hopkins safety cert + BU M.A. + 6.5 years of real crisis management = a profile most global orgs would fight over. The search is temporary. Your skills are permanent. 🌏",
    "**You facilitated cross-cultural programs during a global pandemic.** When the whole world stopped, you found a way to keep connecting people. That's leadership. 🌟",
    "**Tea ceremony instructor. TESOL certified. Crochet artist.** You're not just qualified — you're interesting. The right team will see that. 🍵",
    "**好香ちゃん、大丈夫。ボストン大学の修士号を持って、4カ国の安全管理をやり遂げた人が「使えない」わけがない。世界はあなたを必要としている。今日も一歩前へ。** 🌸",
]


def send_hype():
    """Post a motivational message to the hype channel."""
    webhook = HYPE_WEBHOOK_URL
    if not webhook:
        print("[DRY RUN] Hype message would be sent")
        return

    message = random.choice(HYPE_MESSAGES)
    embed = {
        "embeds": [{
            "title": "🌟 Daily Hype from Captain Hook",
            "description": message,
            "color": 0xFFD700,
            "footer": {"text": "You've got this. — Project Asago-to-the-Moon 🚀"},
        }]
    }

    try:
        requests.post(webhook, json=embed, timeout=10)
    except requests.RequestException as e:
        print(f"[WARN] Hype message failed: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    seen = load_seen_jobs()
    stats = {"sources": 0, "new_jobs": 0, "errors": 0, "total_tracked": len(seen)}

    all_jobs = []
    for scraper in SCRAPERS:
        stats["sources"] += 1
        try:
            jobs = scraper()
            all_jobs.extend(jobs)
        except Exception as e:
            stats["errors"] += 1
            print(f"[ERROR] {scraper.__name__}: {e}")

    # Deduplicate, notify new, sort by score (highest first)
    all_jobs.sort(key=lambda j: j["score"], reverse=True)

    new_found = False
    for job in all_jobs:
        if job["link"] not in seen:
            notify_discord(job)
            seen[job["link"]] = {
                "title": job["title"],
                "source": job["source"],
                "score": job["score"],
                "seen_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
            stats["new_jobs"] += 1
            new_found = True

    if new_found:
        stats["total_tracked"] = len(seen)
        save_seen_jobs(seen)

    send_heartbeat(stats)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--hype":
        send_hype()
    else:
        main()
