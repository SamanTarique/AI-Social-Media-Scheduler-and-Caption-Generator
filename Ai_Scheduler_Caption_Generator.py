import os
import re
import time
import datetime
import pandas as pd
from Gemni_Services import client, generate_caption
from Rag import search_knowledge

DEFAULTS = dict(platform="Instagram", goal="Increase Engagement", audience="Students", emoji="Yes", language="English")
SECONDS_BETWEEN_CALLS = 13  
FALLBACK_TOPICS = [
    "Restaurant Spotlight", "Weekend Cravings", "Free Delivery Reminder",
    "Fan Engagement Poll", "Customer Favorite Dish", "Seasonal Special", "General Engagement Post",
]


def generate_weekly_topics(market="Pakistan", num_days=7) -> list[str]:
    if client is None:
        topics = FALLBACK_TOPICS
    else:
        try:
            context = "\n\n".join(d.page_content for d in search_knowledge("Common Campaign Types Foodpanda weekly content calendar"))
            prompt = (
                f"Suggest exactly {num_days} short (max 8 words), non-repeating Foodpanda {market} "
                f"social media post topics, based only on real campaign types found here:\n{context}\n"
                "Cover a mix of types across the week. Return ONLY a numbered list, one topic per line."
            )
            text = client.models.generate_content(model="gemini-flash-latest", contents=prompt).text
            topics = [re.sub(r"^\d+[\.\)]\s*", "", line).strip() for line in text.splitlines() if line.strip()]
            topics = [t for t in topics if t] or FALLBACK_TOPICS
        except Exception:
            topics = FALLBACK_TOPICS

    return (topics * ((num_days // len(topics)) + 1))[:num_days]


def parse_caption_output(text: str) -> tuple[str, str, str]:
    def grab(pattern):
        m = re.search(pattern, text, re.S | re.I)
        return m.group(1).strip() if m else ""

    caption = grab(r"Caption\s*:\s*(.*?)(?=\n\s*CTA\s*:|\Z)")
    cta = grab(r"CTA\s*:\s*(.*?)(?=\n\s*Hashtags\s*:|\Z)")
    hashtags = grab(r"Hashtags\s*:\s*(.*)")
    return caption, cta, hashtags


def build_weekly_calendar(market="Pakistan", start_date=None, **overrides) -> list[dict]:
    opts = {**DEFAULTS, **overrides}
    topics = generate_weekly_topics(market)
    start = datetime.date.fromisoformat(start_date) if start_date else datetime.date.today()

    rows = []
    for i, topic in enumerate(topics):
        day = start + datetime.timedelta(days=i)
        raw = generate_caption(topic=topic, market=market, **opts)
        caption, cta, hashtags = parse_caption_output(raw)

        rows.append({
            "date": day.isoformat(), "day": day.strftime("%A"), "platform": opts["platform"],
            "topic": topic, "caption": caption, "cta": cta, "hashtags": hashtags,
        })

        if i < len(topics) - 1:
            time.sleep(SECONDS_BETWEEN_CALLS)

    return rows


def save_calendar(rows: list[dict], path: str = "output/weekly_calendar.csv") -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


if __name__ == "__main__":
    print("Generating this week's AI-planned content calendar...\n")

    rows = build_weekly_calendar(market="Pakistan")
    path = save_calendar(rows)
    print(f"Saved to: {path}\n")

    for r in rows:
        print(f"{r['date']} ({r['day']}) - {r['platform']} - Topic: {r['topic']}")
        print(f"  Caption : {r['caption']}")
        print(f"  CTA     : {r['cta']}")
        print(f"  Hashtags: {r['hashtags']}\n")