import os, random, requests, time, hashlib
from datetime import datetime, timedelta
from urllib.parse import quote

# ── CREDENTIALS ───────────────────────────────────────────────────────────────
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

# ── KEYWORD CLUSTERS (rotated daily — prevents tag repetition) ────────────────
KEYWORD_CLUSTERS = [
    # Cluster 1 — Spa discovery
    ["spa ads Sri Lanka", "find spa Colombo", "Ceylon spa deals", "luxury spa listings",
     "book spa online Sri Lanka", "spa services Colombo", "Sri Lanka wellness guide",
     "spa treatments Sri Lanka", "Colombo beauty spa", "wellness booking Sri Lanka"],

    # Cluster 2 — Classified ads angle
    ["Sri Lanka classified ads", "ads-sl spa", "sl ads wellness", "lanka ad beauty",
     "post spa ads Sri Lanka", "wellness business ads", "Sri Lanka ad platform",
     "spa business listing", "online ads Sri Lanka", "classified beauty ads"],

    # Cluster 3 — Wellness & lifestyle
    ["spa and wellness Sri Lanka", "Ceylon wellness retreat", "ayurvedic spa Sri Lanka",
     "herbal spa treatments", "wellness tourism Sri Lanka", "relaxation spa Kandy",
     "Galle spa resort", "Negombo wellness center", "couples spa Sri Lanka",
     "traditional spa treatments Ceylon"],

    # Cluster 4 — Business & marketing
    ["advertise spa Sri Lanka", "spa marketing Sri Lanka", "sl spa business",
     "grow spa business online", "spa ads platform", "wellness ads Sri Lanka",
     "beauty salon ads", "spa listings online", "local spa advertising",
     "spa promotion Sri Lanka"],

    # Cluster 5 — Niche specific
    ["badu ads Sri Lanka", "VIP spa Sri Lanka", "premium wellness ads",
     "luxury spa packages", "spa gift packages Sri Lanka", "anti-aging spa",
     "body massage Sri Lanka", "facial treatment Colombo", "home spa service",
     "spa deals online Sri Lanka"],

    # Cluster 6 — Location based
    ["Colombo spa guide", "Kandy wellness center", "Galle spa retreat",
     "Negombo beach spa", "Nuwara Eliya wellness", "Mirissa spa resort",
     "Hikkaduwa beauty spa", "Ella wellness retreat", "Sigiriya spa hotel",
     "Bentota spa resort"],
]

# ── TOPIC BANK (expanded & varied) ───────────────────────────────────────────
TOPIC_BANK = [
    # Discovery & booking
    "how to find the best spa deals in Sri Lanka online",
    "complete guide to booking spa services in Colombo",
    "top luxury spa experiences available in Sri Lanka",
    "best ayurvedic wellness centers in Sri Lanka",
    "affordable spa packages for couples in Sri Lanka",
    "hidden gem spas in Kandy and Galle you should visit",
    "how to compare spa services before booking in Sri Lanka",
    "best beachside spa resorts in Negombo and Bentota",

    # Ceylon & traditional angle
    "traditional Ceylon spa rituals you must experience",
    "how ancient Sri Lankan herbs are used in modern spas",
    "authentic ayurvedic treatments available in Sri Lanka",
    "Ceylon spa vs international spa what makes it unique",
    "best herbal massage treatments in Sri Lanka",
    "traditional oil treatments at Ceylon wellness centers",

    # Business & advertising angle
    "how to advertise your spa business online in Sri Lanka",
    "best platforms to post spa ads in Sri Lanka",
    "how online classified ads help spa businesses grow",
    "why spa businesses need digital advertising in Sri Lanka",
    "how to create effective spa ads that attract customers",
    "growing your wellness business with online listings",

    # Lifestyle & wellness
    "wellness tourism guide for visitors to Sri Lanka",
    "best spa retreats for stress relief in Sri Lanka",
    "how spa treatments improve mental health and wellbeing",
    "complete body wellness routines available in Sri Lanka",
    "best anti-aging spa treatments available in Colombo",
    "couples wellness retreats available across Sri Lanka",
    "top skin care treatments at Sri Lanka beauty spas",

    # Niche & trending
    "home spa services you can book through Sri Lankan ads",
    "how to find VIP spa services in Sri Lanka discreetly",
    "luxury spa packages available at five star hotels Sri Lanka",
    "best day spa vs wellness resort in Sri Lanka",
    "how to verify authentic spa listings before booking",
    "spa gift packages perfect for gifting in Sri Lanka",
    "trending wellness treatments in Sri Lanka right now",
    "how digital platforms are changing Sri Lanka spa industry",

    # Location specific
    "best spas in Colombo for a quick relaxation break",
    "top wellness centers in Kandy for tourists",
    "spa and wellness options near Galle Fort Sri Lanka",
    "best beach resort spas in southern Sri Lanka",
    "Nuwara Eliya hill country spa retreats guide",
]

# ── PICK TODAY'S KEYWORD CLUSTER ─────────────────────────────────────────────
def get_todays_cluster():
    day_index = datetime.now().timetuple().tm_yday
    return KEYWORD_CLUSTERS[day_index % len(KEYWORD_CLUSTERS)]

# ── RANDOM PUBLISH TIMES (3 posts, random gaps 2-5 hours) ────────────────────
def get_publish_times():
    now = datetime.utcnow()
    times = []
    # First post 1-2 hours from now
    current = now + timedelta(hours=random.uniform(1, 2))
    for _ in range(3):
        times.append(current)
        gap = random.uniform(2.5, 5.0)   # 2.5–5 hour random gap
        current += timedelta(hours=gap)
    return times

# ── AI HELPER ─────────────────────────────────────────────────────────────────
def ask_ai(prompt, max_tokens=4000):
    for attempt in range(3):
        try:
            resp = requests.post(GROQ_URL,
                headers=HEADERS,
                json={
                    "model": MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.83
                },
                timeout=90
            )
            data = resp.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            print(f"Groq error (attempt {attempt+1}):", data)
            time.sleep(10)
        except Exception as e:
            print(f"Request error (attempt {attempt+1}): {e}")
            time.sleep(10)
    raise Exception("Groq API failed after 3 attempts")

# ── PICK 3 BEST TOPICS (AI researches from bank) ──────────────────────────────
def pick_topics():
    today     = datetime.now().strftime("%B %d, %Y")
    month     = datetime.now().strftime("%B %Y")
    cluster   = get_todays_cluster()
    kw_list   = ", ".join(cluster[:6])
    sample    = random.sample(TOPIC_BANK, min(20, len(TOPIC_BANK)))
    listed    = "\n".join(f"- {t}" for t in sample)

    prompt = f"""You are a senior SEO content strategist for Ads-SL (ads-sl.com), Sri Lanka's leading classified ads platform for spa and wellness services.

Today: {today}
Focus keywords for today: {kw_list}

From these topics, choose the 3 BEST for {month} that:
1. Have high Google search volume potential in Sri Lanka
2. Naturally fit today's keywords
3. Cover DIFFERENT content angles (e.g. one guide, one list, one how-to)
4. Will genuinely help readers AND promote ads-sl.com

Topics to choose from:
{listed}

Rewrite each chosen title to be:
- SEO powerful (include a number or power word where natural)
- Max 65 characters
- Specific and searchable

Return ONLY a numbered list of 3 titles:
1.
2.
3."""

    text   = ask_ai(prompt, 400)
    topics = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line and line[0].isdigit() and "." in line:
            t = line.split(".", 1)[-1].strip().strip('"').strip("'")
            if t:
                topics.append(t)
    return topics[:3]

# ── GENERATE SMART IMAGE URL ──────────────────────────────────────────────────
def get_image_url(topic):
    """Generate a unique, topic-relevant AI image via Pollinations.ai"""
    # Ask AI for a good image description for this topic
    img_prompt_raw = ask_ai(
        f"""Create a short 8-12 word image description for a professional blog post about: "{topic}"
The image should look like a real photograph of a luxury Sri Lanka spa or wellness scene.
Return ONLY the image description, nothing else. No quotes.""",
        max_tokens=50
    ).strip().replace('"', '').replace('\n', ' ')

    # Create unique seed from topic so same topic always gets same image
    seed = int(hashlib.md5(topic.encode()).hexdigest()[:8], 16) % 10000
    encoded = quote(img_prompt_raw[:200])
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1200&height=630&nologo=true&seed={seed}&model=flux"

# ── TOP-ONLY PROMO BLOCK ──────────────────────────────────────────────────────
def get_promo_block():
    # Rotate between 3 different promo styles to avoid looking repetitive
    styles = [
        f"""<div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:20px 24px;border-radius:14px;margin:0 0 28px 0;text-align:center;box-shadow:0 4px 15px rgba(102,126,234,0.3);">
  <p style="color:#fff;font-size:16px;font-weight:600;margin:0 0 12px 0;">🌟 Sri Lanka's #1 Spa & Wellness Ads Platform</p>
  <p style="color:rgba(255,255,255,0.85);font-size:13px;margin:0 0 14px 0;">Find trusted spa listings, wellness centers and beauty services across Sri Lanka — all in one place.</p>
  <a href="{SITE_URL}" target="_blank" rel="noopener" style="background:#fff;color:#764ba2;padding:11px 28px;border-radius:30px;font-weight:700;font-size:14px;text-decoration:none;display:inline-block;box-shadow:0 2px 8px rgba(0,0,0,0.15);">Explore Ads-SL.com →</a>
</div>""",

        f"""<div style="background:#fff;border:2px solid #e2e8f0;border-radius:14px;padding:20px 24px;margin:0 0 28px 0;display:flex;align-items:center;gap:16px;box-shadow:0 2px 10px rgba(0,0,0,0.06);">
  <div style="font-size:36px;flex-shrink:0;">💆</div>
  <div style="flex:1;">
    <p style="color:#1e293b;font-size:15px;font-weight:700;margin:0 0 4px 0;">Looking for spa services in Sri Lanka?</p>
    <p style="color:#64748b;font-size:13px;margin:0 0 10px 0;">Browse verified spa ads, wellness centers and beauty listings at <strong>Ads-SL.com</strong> — Sri Lanka's trusted ad platform.</p>
    <a href="{SITE_URL}" target="_blank" rel="noopener" style="background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:8px 20px;border-radius:20px;font-weight:700;font-size:13px;text-decoration:none;display:inline-block;">Visit Ads-SL.com →</a>
  </div>
</div>""",

        f"""<div style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-left:5px solid #22c55e;border-radius:0 14px 14px 0;padding:18px 22px;margin:0 0 28px 0;">
  <p style="color:#166534;font-size:15px;font-weight:700;margin:0 0 6px 0;">📢 Advertised on <a href="{SITE_URL}" target="_blank" rel="noopener" style="color:#15803d;">Ads-SL.com</a></p>
  <p style="color:#374151;font-size:13px;margin:0 0 12px 0;">This post is brought to you by <strong>Ads-SL.com</strong> — Sri Lanka's leading platform for spa, wellness, and beauty classified ads. Find the best local listings or advertise your business today.</p>
  <a href="{SITE_URL}" target="_blank" rel="noopener" style="background:#22c55e;color:#fff;padding:9px 22px;border-radius:20px;font-weight:700;font-size:13px;text-decoration:none;display:inline-block;">Browse All Ads →</a>
</div>""",
    ]
    return random.choice(styles)

# ── GENERATE FULL BLOG POST ────────────────────────────────────────────────────
def generate_post(topic, img_url, tags):
    month_year  = datetime.now().strftime("%B %Y")
    kw_sample   = random.sample(get_todays_cluster(), min(5, len(get_todays_cluster())))
    kw_str      = ", ".join(kw_sample)
    promo_block = get_promo_block()
    tag_str     = ", ".join(tags[:6])

    prompt = f"""You are an expert Sri Lankan lifestyle and wellness blogger for {month_year}.

Topic: "{topic}"
Keywords to use naturally: {kw_str}
Promote this website: {SITE_URL}
Post tags: {tag_str}

Write a complete, high-quality SEO blog post following this EXACT format:

TITLE: [Compelling SEO title — max 65 chars, include main keyword]
META: [155-char meta description — include keyword, make it click-worthy]
---
[PROMO_BLOCK]

<figure style="margin:0 0 28px 0;">
<img src="{img_url}" alt="[8-word descriptive alt text with keyword]" style="width:100%;border-radius:14px;box-shadow:0 4px 20px rgba(0,0,0,0.1);" loading="lazy"/>
<figcaption style="text-align:center;color:#94a3b8;font-size:12px;margin-top:8px;">[Short relevant image caption]</figcaption>
</figure>

[WRITE THE FULL BLOG POST IN HTML BELOW]

POST STRUCTURE:
<p><strong>[Opening hook — a bold relatable statement or surprising fact. NOT "Are you..." or "In today's world"]</strong> [2 more engaging sentences. Include main keyword naturally.]</p>

<p>[Second paragraph — what reader will learn + why it matters. Build excitement about the topic.]</p>

<h2>[Section 1 — informative heading with keyword variation]</h2>
<p>[2-3 detailed paragraphs with specific info, locations, examples]</p>
<h3>[Specific subtopic]</h3>
<p>[Detailed paragraph with numbers, facts, practical advice]</p>
<blockquote style="border-left:4px solid #764ba2;padding:12px 18px;background:#f8f7ff;border-radius:0 8px 8px 0;margin:16px 0;"><strong>💡 Expert Tip:</strong> [One specific actionable tip]</blockquote>

[Repeat H2 → paragraphs → H3 → blockquote pattern for 4 more sections]

<h2>Frequently Asked Questions</h2>
<div style="background:#f8fafc;border-radius:12px;padding:20px;">
<h3 style="color:#1e293b;">[Common Google question about this topic]</h3>
<p>[Clear 2-3 sentence answer]</p>
<h3 style="color:#1e293b;">[Another common question]</h3>
<p>[Clear answer]</p>
<h3 style="color:#1e293b;">[Third question]</h3>
<p>[Clear answer]</p>
</div>

<p style="margin-top:28px;">[Warm closing paragraph — reinforce main benefit, mention ads-sl.com naturally as the resource to find/post spa ads in Sri Lanka]</p>
<p><em>[End with an engaging question inviting readers to share their experience in comments]</em></p>

WRITING RULES:
- 1,300–1,600 words total
- Tone: warm, knowledgeable, like a trusted local Sri Lankan friend
- Mention specific cities: Colombo, Kandy, Galle, Negombo, Bentota, Mirissa
- Use keywords 5-7 times naturally — NEVER forced or stuffed
- Reference ads-sl.com naturally 2-3 times in body content (not just promo)
- Include real-sounding tips with specific numbers and timeframes
- Vary sentence length — mix short punchy sentences with longer ones
- AVOID: "In today's world", "Game changer", "Dive in", "In conclusion", "Unleash"
- Sound 100% human — no AI-sounding phrases

IMPORTANT: Write [PROMO_BLOCK] as the EXACT placeholder text — it will be replaced automatically."""

    raw = ask_ai(prompt, 4000)

    # Inject promo block
    raw = raw.replace("[PROMO_BLOCK]", promo_block)

    return raw

# ── PARSE POST ─────────────────────────────────────────────────────────────────
def parse_post(raw, fallback_tags):
    lines         = raw.strip().splitlines()
    title         = f"Sri Lanka Spa Guide — {datetime.now().strftime('%B %d %Y')}"
    tags          = fallback_tags
    content_lines = []
    in_content    = False

    for line in lines:
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip().strip('"')
        elif line.strip() == "---":
            in_content = True
        elif in_content:
            content_lines.append(line)

    if not content_lines:
        content_lines = [l for l in lines if not l.startswith(("TITLE:", "META:", "---"))]

    return title, "\n".join(content_lines), tags

# ── BLOGGER AUTH ───────────────────────────────────────────────────────────────
def get_access_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type":    "refresh_token"
    })
    data = r.json()
    if "access_token" not in data:
        raise Exception(f"Blogger auth failed: {data}")
    return data["access_token"]

# ── PUBLISH WITH SCHEDULED TIME ────────────────────────────────────────────────
def publish_post(title, content, tags, token, publish_time):
    body = {
        "kind":      "blogger#post",
        "title":     title,
        "content":   content,
        "labels":    tags,
        "published": publish_time.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "status":    "SCHEDULED"
    }
    r = requests.post(
        f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/?isDraft=false",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=body
    )
    return r.json()

# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    today_str = datetime.now().strftime("%Y-%m-%d")
    cluster   = get_todays_cluster()

    print(f"\n{'='*60}")
    print(f"  Ads-SL Smart Blog — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Promoting: {SITE_URL}")
    print(f"  Today's keyword cluster: {cluster[0]}, {cluster[1]}...")
    print(f"{'='*60}\n")

    # Schedule 3 posts at random times
    publish_times = get_publish_times()
    print("📅 Post schedule (UTC):")
    for i, t in enumerate(publish_times, 1):
        # Convert to Sri Lanka time (UTC+5:30)
        sl_time = t + timedelta(hours=5, minutes=30)
        print(f"   Post {i}: {t.strftime('%H:%M')} UTC  ({sl_time.strftime('%H:%M')} Sri Lanka)")

    # Research 3 best topics
    print("\n🔍 AI researching best topics for today...")
    topics = pick_topics()
    if not topics:
        print("ERROR: Topic generation failed")
        return
    print(f"   Selected topics:")
    for i, t in enumerate(topics, 1):
        print(f"   {i}. {t}")

    token   = get_access_token()
    success = 0

    print(f"\n✍️  Writing {len(topics)} high-quality posts...\n")

    for i, topic in enumerate(topics, 1):
        print(f"[{i}/3] {topic[:65]}")

        # Each post gets unique tags from today's cluster
        # Shuffle cluster and pick 10 unique tags per post
        shuffled = cluster.copy()
        random.shuffle(shuffled)
        post_tags = shuffled[:10]

        try:
            # Generate smart image
            print(f"      🖼️  Generating image...")
            img_url = get_image_url(topic)

            # Generate post
            print(f"      ✍️  Writing post...")
            raw = generate_post(topic, img_url, post_tags)

            # Parse
            title, content, tags = parse_post(raw, post_tags)

            # Publish scheduled
            pub_time = publish_times[i-1]
            result   = publish_post(title, content, tags, token, pub_time)
            url      = result.get("url", "scheduled")
            sl_time  = pub_time + timedelta(hours=5, minutes=30)

            print(f"      ✅ Scheduled: {pub_time.strftime('%H:%M')} UTC / {sl_time.strftime('%H:%M')} SL")
            print(f"      🔗 {url}\n")
            success += 1

        except Exception as e:
            print(f"      ❌ Error: {e}\n")

        if i < len(topics):
            wait = random.randint(20, 35)
            print(f"      ⏳ Cooling down {wait}s before next post...\n")
            time.sleep(wait)

    print(f"{'='*60}")
    print(f"  ✅ {success}/3 posts scheduled for today")
    print(f"  🔗 All linking to: {SITE_URL}")
    print(f"  🏷️  Cluster used: {cluster[0][:30]}...")
    print(f"  📅 Tomorrow uses different keyword cluster automatically")
    print(f"{'='*60}\n")

if __name__ =
