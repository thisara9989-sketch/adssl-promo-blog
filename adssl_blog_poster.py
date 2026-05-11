import os, random, requests, time, json
from datetime import datetime, timedelta
from urllib.parse import quote

# ── CREDENTIALS ──────────────────────────────────────────────────────────────
GROQ_KEY      = os.environ["GROQ_API_KEY"]
REFRESH_TOKEN = os.environ["BLOGGER_REFRESH_TOKEN"]
CLIENT_ID     = os.environ["BLOGGER_CLIENT_ID"]
CLIENT_SECRET = os.environ["BLOGGER_CLIENT_SECRET"]
BLOG_ID       = os.environ["BLOGGER_BLOG_ID"]

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS  = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
MODEL    = "llama-3.3-70b-versatile"

SITE_URL  = "https://www.ads-sl.com/"
SITE_NAME = "Ads-SL"

# ── TARGET KEYWORDS ──────────────────────────────────────────────────────────
PRIMARY_KEYWORDS = [
    "spa ads", "sl spa", "spa and wellness", "Ceylon spa",
    "ads sl", "sl ads", "Sri Lankan ads", "lanka ad",
    "Sri Lanka spa", "Colombo spa", "wellness Sri Lanka",
    "Sri Lanka classified ads", "spa listings Sri Lanka",
    "beauty ads Sri Lanka", "wellness ads Sri Lanka",
]

# ── TOPIC BANK ───────────────────────────────────────────────────────────────
TOPIC_BANK = [
    "best spa deals in Sri Lanka you can find online",
    "how to find luxury spa services in Colombo",
    "top wellness centers in Sri Lanka for relaxation",
    "Ceylon spa traditions and modern wellness treatments",
    "how to advertise your spa business in Sri Lanka",
    "best classified ads sites in Sri Lanka for spa listings",
    "affordable spa packages available in Sri Lanka",
    "how to book a spa appointment online in Sri Lanka",
    "Sri Lanka wellness tourism guide for visitors",
    "best beauty and wellness services in Colombo",
    "traditional Ceylon spa treatments you must try",
    "how to find trusted spa ads in Sri Lanka",
    "top massage and wellness centers in Sri Lanka",
    "guide to Sri Lanka spa and beauty industry",
    "how online ads help spa businesses grow in Sri Lanka",
    "best places to post spa ads in Sri Lanka",
    "wellness retreats available in Sri Lanka",
    "how to find authentic spa services through Sri Lankan ads",
    "top ayurvedic wellness centers in Sri Lanka",
    "complete guide to spa services in Sri Lanka",
    "how Sri Lankan classified ads help wellness businesses",
    "best spa gift packages in Sri Lanka",
    "benefits of booking spa services through online ads",
    "top rated beauty salons and spas in Sri Lanka",
    "how to choose the right spa in Sri Lanka",
    "spa and wellness trends in Sri Lanka 2025",
    "couples spa packages available in Sri Lanka",
    "how to list your wellness business on Sri Lankan ad sites",
    "best herbal spa treatments in Sri Lanka",
    "day spa vs wellness resort which is right for you in Sri Lanka",
    "how to find budget spa deals through online ads in Sri Lanka",
    "Sri Lanka beauty industry growth and online advertising",
    "best anti-aging spa treatments available in Sri Lanka",
    "how local spas use online classified ads to grow",
    "top facial and skin care centers in Colombo Sri Lanka",
    "body massage services available through Sri Lanka ads",
    "how to verify spa listings before booking in Sri Lanka",
    "luxury wellness experiences in Sri Lanka",
    "home spa services available through Sri Lankan classified ads",
    "how digital advertising is transforming Sri Lanka spa industry",
]

IMAGE_PROMPTS = [
    "luxury spa Sri Lanka tropical wellness",
    "Ceylon spa massage relaxation",
    "wellness center Colombo Sri Lanka",
    "tropical spa treatment flowers candles",
    "Sri Lanka ayurvedic spa herbs",
    "luxury hotel spa swimming pool tropical",
    "beauty salon wellness treatment",
    "spa massage stones flowers calm",
    "tropical wellness resort Sri Lanka",
    "herbal spa treatment natural oils",
]

# ── POST TIMES (Sri Lanka = UTC+5:30) ────────────────────────────────────────
# 10 posts scheduled across the day
def get_publish_times():
    now = datetime.utcnow()
    # Start from next hour, space posts randomly 1.5-3 hours apart
    times = []
    current = now + timedelta(hours=1)
    for _ in range(10):
        times.append(current)
        gap = random.uniform(1.5, 2.5)
        current = current + timedelta(hours=gap)
    return times

# ── AI HELPER ─────────────────────────────────────────────────────────────────
def ask_ai(prompt, max_tokens=4000):
    resp = requests.post(GROQ_URL,
        headers=HEADERS,
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.82
        },
        timeout=90
    )
    data = resp.json()
    if "choices" not in data:
        print("Groq error:", data)
        raise Exception("Groq API failed")
    return data["choices"][0]["message"]["content"]

# ── PICK 10 TOPICS ────────────────────────────────────────────────────────────
def pick_topics():
    month = datetime.now().strftime("%B %Y")
    sample = random.sample(TOPIC_BANK, min(20, len(TOPIC_BANK)))
    listed = "\n".join(f"- {t}" for t in sample)
    kw_list = ", ".join(PRIMARY_KEYWORDS[:8])

    prompt = f"""You are an SEO strategist for a Sri Lankan classified ads website called Ads-SL (ads-sl.com).

Month: {month}
Target keywords: {kw_list}

From this topic list, pick 10 BEST blog post titles that:
1. Naturally include target keywords
2. Have high Google search potential in Sri Lanka
3. Help promote a classified ads website for spa/wellness services
4. Cover different angles (how-to, guides, lists, comparisons)
5. Are relevant for {month}

Topics:
{listed}

Rewrite each title to be SEO-powerful with keywords naturally included.
Return ONLY numbered list:
1.
2.
3.
4.
5.
6.
7.
8.
9.
10."""

    text = ask_ai(prompt, 600)
    topics = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line and line[0].isdigit() and "." in line:
            t = line.split(".", 1)[-1].strip()
            if t:
                topics.append(t)
    return topics[:10]

# ── GET AI IMAGE URL ──────────────────────────────────────────────────────────
def get_image_url(topic):
    prompt = random.choice(IMAGE_PROMPTS)
    encoded = quote(f"{prompt} professional photography")
    return f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=450&nologo=true&seed={random.randint(1,9999)}"

# ── GENERATE BLOG POST ────────────────────────────────────────────────────────
def generate_post(topic, img_url):
    month_year = datetime.now().strftime("%B %Y")
    kw_str = ", ".join(random.sample(PRIMARY_KEYWORDS, 6))

    # Promotional blocks with link to ads-sl.com
    promo_top = f"""
<div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:18px 20px;border-radius:12px;margin:0 0 24px 0;text-align:center;">
  <p style="color:#fff;font-size:15px;margin:0 0 10px 0;">🌟 <strong>Looking for trusted spa and wellness ads in Sri Lanka?</strong></p>
  <a href="{SITE_URL}" target="_blank" rel="noopener" style="background:#fff;color:#764ba2;padding:10px 24px;border-radius:25px;font-weight:700;font-size:14px;text-decoration:none;display:inline-block;">Visit Ads-SL.com →</a>
</div>"""

    promo_mid = f"""
<div style="background:#f0f9ff;border:2px solid #0ea5e9;border-radius:12px;padding:18px 20px;margin:28px 0;text-align:center;">
  <p style="color:#0369a1;font-size:15px;font-weight:700;margin:0 0 8px 0;">📢 Find or Post Spa & Wellness Ads in Sri Lanka</p>
  <p style="color:#475569;font-size:13px;margin:0 0 12px 0;">Sri Lanka's leading classified ads platform — browse hundreds of spa, wellness and beauty listings.</p>
  <a href="{SITE_URL}" target="_blank" rel="noopener" style="background:#0ea5e9;color:#fff;padding:10px 24px;border-radius:25px;font-weight:700;font-size:14px;text-decoration:none;display:inline-block;">Browse Ads on Ads-SL.com →</a>
</div>"""

    promo_bottom = f"""
<div style="background:#f8fafc;border-left:4px solid #764ba2;border-radius:0 12px 12px 0;padding:18px 20px;margin:28px 0 0 0;">
  <p style="color:#334155;font-size:14px;margin:0 0 10px 0;">🔗 <strong>Ready to find the best spa deals or advertise your wellness business in Sri Lanka?</strong></p>
  <p style="color:#64748b;font-size:13px;margin:0 0 12px 0;"><a href="{SITE_URL}" target="_blank" rel="noopener" style="color:#764ba2;font-weight:700;">Ads-SL.com</a> is Sri Lanka's trusted platform for spa ads, wellness listings, beauty services and more. Join thousands of Sri Lankan businesses and customers today.</p>
  <a href="{SITE_URL}" target="_blank" rel="noopener" style="background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:10px 24px;border-radius:25px;font-weight:700;font-size:14px;text-decoration:none;display:inline-block;">Post or Find Ads on Ads-SL.com →</a>
</div>"""

    prompt = f"""You are an expert Sri Lankan digital marketing blogger writing for {month_year}.

Topic: "{topic}"
Target keywords to include naturally: {kw_str}
Website to promote: {SITE_URL} ({SITE_NAME})

Write a complete SEO-optimized blog post. Follow EXACT format:

TITLE: [SEO title with main keyword — max 65 characters]
META: [155 character meta description with keyword]
TAGS: [10 comma-separated tags mixing: spa ads, sl spa, ads-sl, Sri Lanka wellness, Ceylon spa, sl ads, classified ads Sri Lanka, spa Sri Lanka, lanka ad, wellness ads]
---
[TOP_PROMO]

<img src="{img_url}" alt="[relevant alt text with keyword]" style="width:100%;border-radius:12px;margin:0 0 24px 0;" loading="lazy"/>

[Write full HTML blog post here]

[MID_PROMO]

[Continue blog post here]

[BOTTOM_PROMO]

WRITING REQUIREMENTS:
- Total: 1,200–1,500 words (excluding promo blocks)
- Tone: friendly, knowledgeable, helpful — like a local Sri Lankan expert
- 5 main sections with <h2> headings
- Each section: 2-3 paragraphs + <h3> subtopics + <blockquote> tip
- Target keywords used 6-8 times naturally throughout
- Include: specific Sri Lankan locations (Colombo, Kandy, Galle, Negombo)
- Reference ads-sl.com as THE place to find/post spa ads in Sri Lanka
- FAQ section at end: 3 questions people search on Google
- End with reader engagement question
- NO clichés: "In today's world", "Game changer", "Dive in"
- Sound 100% human, vary sentence length

IMPORTANT: Keep [TOP_PROMO], [MID_PROMO], [BOTTOM_PROMO] as exact placeholders — they will be replaced."""

    raw = ask_ai(prompt, 4000)

    # Replace placeholders with actual promo HTML
    raw = raw.replace("[TOP_PROMO]", promo_top)
    raw = raw.replace("[MID_PROMO]", promo_mid)
    raw = raw.replace("[BOTTOM_PROMO]", promo_bottom)

    return raw

# ── PARSE POST ────────────────────────────────────────────────────────────────
def parse_post(raw):
    lines = raw.strip().splitlines()
    title = f"Sri Lanka Spa & Wellness Guide — {datetime.now().strftime('%B %d %Y')}"
    tags  = ["spa ads","sl spa","ads-sl","Sri Lanka wellness","Ceylon spa",
             "sl ads","classified ads Sri Lanka","spa Sri Lanka","lanka ad","wellness ads"]
    content_lines = []
    in_content = False

    for line in lines:
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.startswith("TAGS:"):
            tags = [t.strip() for t in line.replace("TAGS:", "").split(",") if t.strip()]
        elif line.strip() == "---":
            in_content = True
        elif in_content:
            content_lines.append(line)

    if not content_lines:
        content_lines = [l for l in lines if not l.startswith(("TITLE:","META:","TAGS:","---"))]

    return title, "\n".join(content_lines), tags

# ── BLOGGER AUTH ──────────────────────────────────────────────────────────────
def get_access_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    })
    data = r.json()
    if "access_token" not in data:
        raise Exception(f"Blogger auth failed: {data}")
    return data["access_token"]

# ── PUBLISH TO BLOGGER ────────────────────────────────────────────────────────
def publish_post(title, content, tags, token, publish_time=None):
    body = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "labels": tags
    }
    # Schedule post for future time if provided
    if publish_time:
        body["published"] = publish_time.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        body["status"] = "SCHEDULED"

    r = requests.post(
        f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/?isDraft=false",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=body
    )
    return r.json()

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*60}")
    print(f"  Ads-SL Auto Blog — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Promoting: {SITE_URL}")
    print(f"{'='*60}\n")

    # Get publish schedule
    publish_times = get_publish_times()
    print(f"📅 Scheduled post times (UTC):")
    for i, t in enumerate(publish_times, 1):
        print(f"   Post {i}: {t.strftime('%H:%M')}")

    # Pick topics
    print(f"\n🔍 Researching best topics...")
    topics = pick_topics()
    if not topics:
        print("ERROR: No topics generated")
        return
    print(f"   Found {len(topics)} topics:")
    for i, t in enumerate(topics, 1):
        print(f"   {i}. {t}")

    # Get token
    token = get_access_token()
    print(f"\n✍️  Generating & scheduling {len(topics)} posts...\n")

    success = 0
    for i, topic in enumerate(topics, 1):
        print(f"[{i}/10] {topic[:60]}...")
        try:
            img_url = get_image_url(topic)
            raw = generate_post(topic, img_url)
            title, content, tags = parse_post(raw)
            pub_time = publish_times[i-1] if i <= len(publish_times) else None
            result = publish_post(title, content, tags, token, pub_time)
            url = result.get("url", "scheduled")
            sched = publish_times[i-1].strftime('%H:%M UTC') if pub_time else "now"
            print(f"      ✅ Scheduled for {sched}: {url}\n")
            success += 1
        except Exception as e:
            print(f"      ❌ Error: {e}\n")

        if i < len(topics):
            wait = random.randint(15, 25)
            print(f"      ⏳ Waiting {wait}s...\n")
            time.sleep(wait)

    print(f"\n{'='*60}")
    print(f"  ✅ {success}/10 posts scheduled successfully")
    print(f"  🔗 All posts promote: {SITE_URL}")
    print(f"  📅 Posts will publish throughout today")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
