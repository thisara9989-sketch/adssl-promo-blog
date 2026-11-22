import os, re, random, requests, time, hashlib
from datetime import datetime, timedelta
from urllib.parse import quote

GROQ_KEY      = os.environ["GROQ_API_KEY"]
REFRESH_TOKEN = os.environ["BLOGGER_REFRESH_TOKEN"]
CLIENT_ID     = os.environ["BLOGGER_CLIENT_ID"]
CLIENT_SECRET = os.environ["BLOGGER_CLIENT_SECRET"]
BLOG_ID       = os.environ["BLOGGER_BLOG_ID"]
PEXELS_KEY    = os.environ.get("PEXELS_API_KEY", "")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS  = {"Authorization": "Bearer " + GROQ_KEY, "Content-Type": "application/json"}

# Model is configurable: set GROQ_MODEL in the workflow to switch without editing code.
# If the first model is gone, the script automatically tries the next one.
MODELS = [m for m in [
    os.environ.get("GROQ_MODEL", "").strip(),
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
] if m]
MODELS = list(dict.fromkeys(MODELS))

SITE_URL = "https://www.ads-sl.com/"

KEYWORD_CLUSTERS = [
    ["sl ads", "ads sl", "lanka ads", "hela ads", "spa ads", "ceylon ads",
     "sl spa", "ads-sl.com", "Sri Lanka ads", "classified ads Sri Lanka"],
    ["spa ads Sri Lanka", "Ceylon spa deals", "luxury spa listings",
     "book spa online Sri Lanka", "spa services Colombo", "wellness Sri Lanka",
     "spa treatments Sri Lanka", "Colombo beauty spa", "sl ads spa", "lanka ads wellness"],
    ["hela ads spa", "ceylon ads wellness", "ads sl spa", "lanka ad beauty",
     "post spa ads Sri Lanka", "wellness business ads", "Sri Lanka ad platform",
     "spa business listing", "sl ads online", "ceylon classified ads"],
    ["spa and wellness Sri Lanka", "Ceylon wellness retreat", "ayurvedic spa Sri Lanka",
     "herbal spa treatments", "wellness tourism Sri Lanka", "relaxation spa Kandy",
     "Galle spa resort", "Negombo wellness center", "hela ads beauty", "sl spa deals"],
    ["advertise spa Sri Lanka", "spa marketing Sri Lanka", "sl spa business",
     "grow spa business online", "ceylon spa ads", "wellness ads Sri Lanka",
     "beauty salon ads", "spa listings online", "lanka ads spa", "ads sl wellness"],
    ["Colombo spa guide", "Kandy wellness center", "Galle spa retreat",
     "Negombo beach spa", "Nuwara Eliya wellness", "Mirissa spa resort",
     "sl ads Colombo", "lanka ads Kandy", "hela ads Galle", "ceylon ads spa"],
]

TOPIC_BANK = [
    "how to find the best spa deals in Sri Lanka using sl ads",
    "complete guide to booking spa services in Colombo through lanka ads",
    "top luxury spa experiences available in Sri Lanka on ads-sl",
    "best ayurvedic wellness centers in Sri Lanka listed on ceylon ads",
    "affordable spa packages for couples in Sri Lanka via hela ads",
    "hidden gem spas in Kandy and Galle found through sl ads",
    "how to compare spa services before booking using Sri Lanka ads",
    "best beachside spa resorts in Negombo and Bentota on lanka ads",
    "traditional Ceylon spa rituals you must experience in Sri Lanka",
    "how ancient Sri Lankan herbs are used in modern spas",
    "authentic ayurvedic treatments available in Sri Lanka",
    "Ceylon spa vs international spa what makes it unique",
    "best herbal massage treatments in Sri Lanka",
    "how to advertise your spa business online using ads sl",
    "best platforms to post spa ads in Sri Lanka",
    "how online classified ads help spa businesses grow in Sri Lanka",
    "why spa businesses need hela ads to reach more customers",
    "how to create effective spa ads that attract customers on sl ads",
    "growing your wellness business with ceylon ads online listings",
    "wellness tourism guide for visitors to Sri Lanka",
    "best spa retreats for stress relief in Sri Lanka",
    "complete body wellness routines available in Sri Lanka",
    "best anti-aging spa treatments available in Colombo",
    "couples wellness retreats available across Sri Lanka",
    "top skin care treatments at Sri Lanka beauty spas",
    "home spa services you can book through Sri Lankan ads",
    "luxury spa packages at five star hotels Sri Lanka",
    "best day spa vs wellness resort in Sri Lanka",
    "how to verify authentic spa listings on sl ads before booking",
    "spa gift packages perfect for gifting in Sri Lanka",
    "trending wellness treatments in Sri Lanka right now",
    "how digital platforms like ads-sl are changing Sri Lanka spa industry",
    "best spas in Colombo for a quick relaxation break",
    "top wellness centers in Kandy for tourists",
    "spa and wellness options near Galle Fort Sri Lanka",
    "best beach resort spas in southern Sri Lanka",
    "Nuwara Eliya hill country spa retreats guide",
    "how hela ads connects spa businesses with customers in Sri Lanka",
    "finding VIP spa services in Sri Lanka through ceylon ads",
    "top rated massage centers listed on lanka ads Sri Lanka",
]


def get_todays_cluster():
    day_index = datetime.now().timetuple().tm_yday
    return KEYWORD_CLUSTERS[day_index % len(KEYWORD_CLUSTERS)]


def get_publish_times():
    """3 random times per day: one morning, one afternoon, one evening (Sri Lanka time)."""
    now_utc = datetime.utcnow()
    sl_offset = timedelta(hours=5, minutes=30)
    sl_today = (now_utc + sl_offset).replace(hour=0, minute=0, second=0, microsecond=0)
    windows = [(8, 11), (13, 16), (18, 22)]  # SL hours
    times = []
    for start_h, end_h in windows:
        minutes = random.randint(start_h * 60, end_h * 60 - 1)
        t_utc = sl_today + timedelta(minutes=minutes) - sl_offset
        if t_utc < now_utc + timedelta(minutes=15):  # window already passed -> tomorrow
            t_utc += timedelta(days=1)
        times.append(t_utc)
    return sorted(times)


# ---------------------------------------------------------------- Groq
def ask_ai(prompt, max_tokens=4000):
    """Try each model in MODELS. Skips to the next model if one no longer exists."""
    last_error = None
    for model in MODELS:
        use_reasoning_param = model.startswith("openai/gpt-oss")
        for attempt in range(3):
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.83,
            }
            if use_reasoning_param:
                payload["reasoning_effort"] = "low"
            try:
                resp = requests.post(GROQ_URL, headers=HEADERS, json=payload, timeout=120)
                data = resp.json()
                if "choices" in data:
                    text = (data["choices"][0]["message"].get("content") or "").strip()
                    if text:
                        return text
                    print("Empty reply from " + model + " (attempt " + str(attempt + 1) + "), retrying")
                    max_tokens = int(max_tokens * 1.5)
                    time.sleep(5)
                    continue

                err      = data.get("error", {}) if isinstance(data, dict) else {}
                err_code = str(err.get("code", ""))
                err_msg  = str(err.get("message", ""))
                last_error = data
                print("Groq error [" + model + "] attempt " + str(attempt + 1) + ":", data)

                if err_code == "model_not_found":
                    break  # go to next model immediately
                if "reasoning_effort" in err_msg:
                    use_reasoning_param = False
                    continue
                if err_code == "rate_limit_exceeded" or resp.status_code == 429:
                    time.sleep(40)
                else:
                    time.sleep(10)
            except Exception as e:
                last_error = str(e)
                print("Request error [" + model + "] attempt " + str(attempt + 1) + ": " + str(e))
                time.sleep(10)
    raise Exception("Groq API failed on all models: " + str(last_error))


# ---------------------------------------------------------------- Blogger
def get_access_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type":    "refresh_token"
    }, timeout=30)
    data = r.json()
    if "access_token" not in data:
        raise Exception("Blogger auth failed: " + str(data))
    return data["access_token"]


def get_recent_titles(token, limit=50):
    """Titles of recent live + scheduled posts, so we don't repeat topics."""
    try:
        r = requests.get(
            "https://www.googleapis.com/blogger/v3/blogs/" + BLOG_ID + "/posts",
            headers={"Authorization": "Bearer " + token},
            params=[("maxResults", limit), ("fetchBodies", "false"),
                    ("status", "live"), ("status", "scheduled")],
            timeout=30
        )
        items = r.json().get("items", [])
        return [i.get("title", "") for i in items if i.get("title")]
    except Exception as e:
        print("Could not load recent titles: " + str(e))
        return []


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
        "https://www.googleapis.com/blogger/v3/blogs/" + BLOG_ID + "/posts/?isDraft=false",
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        json=body,
        timeout=60
    )
    data = r.json()
    if "error" in data:
        raise Exception("Blogger publish failed: " + str(data["error"]))
    return data


# ---------------------------------------------------------------- Topics
RESEARCH_SEEDS = [
    "spa sri lanka", "spa colombo", "massage sri lanka", "ayurvedic spa sri lanka",
    "wellness sri lanka", "beauty salon colombo", "spa kandy", "spa galle",
    "sl ads", "ads sl", "hela ads", "lanka ads", "ceylon ads", "spa ads",
]
RELEVANT_WORDS = ["spa", "massage", "wellness", "ayurved", "salon", "beauty", "ads", "classified"]


def research_queries():
    """Real Google autocomplete suggestions for Sri Lanka = what people actually type.
    Unofficial endpoint: if it fails, the script just falls back to the topic bank."""
    found = []
    seeds = random.sample(RESEARCH_SEEDS, min(8, len(RESEARCH_SEEDS)))
    for seed in seeds:
        for suffix in ["", " best", " near", " price", " a"]:
            try:
                r = requests.get(
                    "https://suggestqueries.google.com/complete/search",
                    params={"client": "firefox", "q": seed + suffix, "hl": "en", "gl": "lk"},
                    timeout=15
                )
                for sug in r.json()[1]:
                    low = sug.lower()
                    if sug not in found and any(w in low for w in RELEVANT_WORDS):
                        found.append(sug)
            except Exception:
                pass
        time.sleep(0.3)
    print("  Research queries found: " + str(len(found)))
    return found[:60]


def pick_topics(recent_titles, research):
    """Returns 3 tuples: (topic, primary_keyword)."""
    today   = datetime.now().strftime("%B %d, %Y")
    month   = datetime.now().strftime("%B %Y")
    cluster = get_todays_cluster()
    kw_list = ", ".join(cluster[:6])
    sample  = random.sample(TOPIC_BANK, min(15, len(TOPIC_BANK)))
    bank    = "\n".join("- " + t for t in sample)
    searches = ""
    if research:
        searches = ("Real Google searches from Sri Lanka (search demand signals):\n"
                    + "\n".join("- " + q for q in research) + "\n\n")
    avoid = ""
    if recent_titles:
        avoid = ("Already published (do NOT repeat or closely copy):\n"
                 + "\n".join("- " + t for t in recent_titles[:30]) + "\n\n")
    prompt = (
        "You are a senior SEO strategist for ads-sl.com, a Sri Lankan classified ads platform "
        "with a strong spa and wellness category.\n\n"
        "Today: " + today + "\n"
        "Brand keywords to weave in: " + kw_list + "\n\n"
        + searches + avoid +
        "Backup topic ideas:\n" + bank + "\n\n"
        "Choose the 3 best blog topics for " + month + ". Prefer topics that match the real searches above "
        "(people clearly want this) and are not already published. Cover 3 different angles: "
        "one how-to, one list, one guide.\n\n"
        "For each topic also give ONE primary search keyword (2-5 words) that people really type.\n"
        "Topic max 65 characters.\n\n"
        "Return ONLY this format, nothing else:\n"
        "1. Topic title | primary keyword\n2. Topic title | primary keyword\n3. Topic title | primary keyword"
    )
    text   = ask_ai(prompt, 2500)
    topics = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line and line[0].isdigit() and "." in line:
            body = line.split(".", 1)[-1].strip().strip("*").strip()
            if "|" in body:
                t, k = body.split("|", 1)
            else:
                t, k = body, cluster[0]
            t = t.strip().strip('"').strip("'").strip("*").strip()
            k = k.strip().strip('"').strip("'").strip("*").strip() or cluster[0]
            if t:
                topics.append((t, k))
    if len(topics) < 3:  # safety net: fill from the bank
        for t in random.sample(TOPIC_BANK, len(TOPIC_BANK)):
            if t not in [x[0] for x in topics]:
                topics.append((t, cluster[0]))
            if len(topics) >= 3:
                break
    return topics[:3]


# ---------------------------------------------------------------- Images
def image_query_for(topic):
    t = topic.lower()
    if any(w in t for w in ["ayurved", "herb", "ancient", "ritual", "traditional"]):
        return ["ayurveda spa treatment", "herbal massage spa", "spa herbs wellness"]
    if any(w in t for w in ["beach", "resort", "negombo", "bentota", "mirissa", "galle", "southern"]):
        return ["tropical beach resort spa", "spa resort pool", "luxury resort wellness"]
    if any(w in t for w in ["couple", "gift", "romantic"]):
        return ["couples spa massage", "spa candles flowers", "romantic spa"]
    if any(w in t for w in ["skin", "anti-aging", "facial", "beauty"]):
        return ["facial spa treatment", "skin care spa", "beauty salon treatment"]
    if any(w in t for w in ["advertis", "business", "platform", "marketing", "grow", "post", "listing"]):
        return ["spa reception", "spa interior", "wellness center interior"]
    return ["spa massage", "wellness spa relaxation", "spa treatment room"]


def image_from_pexels(topic, seed):
    if not PEXELS_KEY:
        return None
    for q in image_query_for(topic):
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 15, "orientation": "landscape"},
                timeout=30
            )
            photos = r.json().get("photos", [])
            if photos:
                p = photos[seed % len(photos)]
                return {
                    "url":    p["src"]["large"],
                    "credit": p.get("photographer", "Pexels"),
                    "link":   p.get("url", "https://www.pexels.com"),
                }
        except Exception as e:
            print("  Pexels error: " + str(e))
    return None


def image_from_pollinations(topic, seed):
    prompt = "professional photo, spa and wellness in Sri Lanka, " + topic + ", soft natural light, no text"
    url = ("https://image.pollinations.ai/prompt/" + quote(prompt)
           + "?width=1200&height=630&nologo=true&seed=" + str(seed))
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
            return {"url": url, "credit": None, "link": None}
        print("  Pollinations returned " + str(r.status_code))
    except Exception as e:
        print("  Pollinations error: " + str(e))
    return None


def get_image_block(topic):
    """Returns ready-to-insert HTML for the post image, or '' if no image could be found."""
    seed = int(hashlib.md5((topic + datetime.now().strftime("%Y%m%d")).encode()).hexdigest()[:8], 16)
    img = image_from_pexels(topic, seed) or image_from_pollinations(topic, seed)
    if not img:
        print("  No image available, posting without one")
        return ""
    alt = topic.replace('"', "'")
    html = ('<img src="' + img["url"] + '" alt="' + alt
            + '" style="width:100%;border-radius:12px;margin:0 0 8px 0;" />')
    if img["credit"]:
        html += ('<p style="font-size:11px;color:#6b7280;margin:0 0 24px 0;">Photo by '
                 + img["credit"] + ' on <a href="' + img["link"]
                 + '" target="_blank" rel="nofollow">Pexels</a></p>')
    else:
        html += '<div style="margin:0 0 24px 0;"></div>'
    return html


# ---------------------------------------------------------------- Content
def get_promo_block():
    styles = [
        '<div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:20px;border-radius:12px;margin:0 0 24px 0;text-align:center;">'
        + '<p style="color:#fff;font-size:16px;font-weight:700;margin:0 0 10px 0;">Sri Lanka\'s #1 Spa and Wellness Ads Platform</p>'
        + '<p style="color:rgba(255,255,255,0.9);font-size:13px;margin:0 0 14px 0;">Find trusted spa listings on <strong>ads-sl.com</strong> — Sri Lanka\'s leading platform for sl ads, spa ads, lanka ads and hela ads.</p>'
        + '<a href="' + SITE_URL + '" target="_blank" style="background:#fff;color:#764ba2;padding:10px 24px;border-radius:25px;font-weight:700;font-size:14px;text-decoration:none;display:inline-block;">Visit Ads-SL.com</a>'
        + '</div>',

        '<div style="background:#fff;border:2px solid #764ba2;border-radius:12px;padding:20px;margin:0 0 24px 0;">'
        + '<p style="color:#764ba2;font-size:15px;font-weight:700;margin:0 0 8px 0;">Looking for Spa Ads in Sri Lanka?</p>'
        + '<p style="color:#374151;font-size:13px;margin:0 0 12px 0;">Browse verified <strong>sl ads</strong>, <strong>spa ads</strong>, <strong>ceylon ads</strong> and <strong>lanka ads</strong> at ads-sl.com — Sri Lanka\'s most trusted classified ads platform.</p>'
        + '<a href="' + SITE_URL + '" target="_blank" style="background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:10px 24px;border-radius:25px;font-weight:700;font-size:13px;text-decoration:none;display:inline-block;">Browse Ads-SL.com</a>'
        + '</div>',

        '<div style="background:#f0fdf4;border-left:5px solid #22c55e;padding:18px 20px;margin:0 0 24px 0;border-radius:0 12px 12px 0;">'
        + '<p style="color:#166534;font-size:15px;font-weight:700;margin:0 0 6px 0;">Sponsored by Ads-SL.com</p>'
        + '<p style="color:#374151;font-size:13px;margin:0 0 12px 0;"><strong>Ads-SL.com</strong> is Sri Lanka\'s leading platform for <strong>hela ads</strong>, <strong>spa ads</strong>, <strong>sl ads</strong> and <strong>ceylon ads</strong>. Find or post wellness listings today.</p>'
        + '<a href="' + SITE_URL + '" target="_blank" style="background:#22c55e;color:#fff;padding:10px 22px;border-radius:25px;font-weight:700;font-size:13px;text-decoration:none;display:inline-block;">Post Free Ads Now</a>'
        + '</div>',
    ]
    return random.choice(styles)


TIP = ('<blockquote style="border-left:4px solid #764ba2;padding:12px 16px;background:#f8f7ff;'
       'margin:16px 0;border-radius:0 8px 8px 0;"><strong>Expert Tip:</strong> [One specific actionable tip]</blockquote>\n\n')


def generate_post(topic, keyword, img_block):
    month_year = datetime.now().strftime("%B %Y")
    cluster    = get_todays_cluster()
    kw_sample  = random.sample(cluster, min(6, len(cluster)))
    kw_str     = ", ".join(kw_sample)

    prompt = (
        "You are an expert Sri Lankan spa and wellness blogger writing for " + month_year + ".\n\n"
        "Topic: " + topic + "\n"
        "PRIMARY KEYWORD: " + keyword + " (must appear in the TITLE, the first paragraph, at least one H2, and the closing paragraph)\n"
        "MUST include these keywords naturally: sl ads, ads sl, lanka ads, hela ads, spa ads, ceylon ads, " + kw_str + "\n"
        "Promote: " + SITE_URL + "\n\n"
        "CRITICAL: Write ONLY in pure HTML. NO markdown. NO ## symbols. NO ** symbols. NO > symbols.\n\n"
        "OUTPUT FORMAT:\n"
        "TITLE: [SEO title max 65 chars]\n"
        "---\n"
        "[PROMO_BLOCK]\n\n"
        "[IMAGE_BLOCK]\n\n"
        "<p><strong>[Opening hook sentence about " + topic + "]</strong> [2 more sentences with sl ads or spa ads keyword naturally.]</p>\n\n"
        "<p>[Second paragraph about what reader will learn. Mention ads-sl.com naturally.]</p>\n\n"
        "<h2>[Section 1 heading with keyword]</h2>\n"
        "<p>[Paragraph 1 with practical info and locations: Colombo, Kandy, Galle]</p>\n"
        "<p>[Paragraph 2 with tips and hela ads or ceylon ads keyword]</p>\n"
        "<h3>[Subtopic of section 1]</h3>\n"
        "<p>[Detailed paragraph with specific advice]</p>\n"
        + TIP +
        "<h2>[Section 2 heading with lanka ads or sl ads keyword]</h2>\n"
        "<p>[Paragraph with info about finding services through sl ads or ads sl]</p>\n"
        "<p>[Paragraph 2]</p>\n"
        "<h3>[Subtopic]</h3>\n"
        "<p>[Paragraph]</p>\n"
        + TIP +
        "<h2>[Section 3 heading]</h2>\n"
        "<p>[Content mentioning Negombo, Bentota or Mirissa]</p>\n"
        "<p>[Paragraph 2 with ceylon ads or hela ads keyword]</p>\n"
        "<h3>[Subtopic]</h3>\n"
        "<p>[Paragraph]</p>\n"
        + TIP +
        "<h2>[Section 4 heading]</h2>\n"
        "<p>[Content]</p>\n"
        "<ul>\n<li>[Tip 1]</li>\n<li>[Tip 2]</li>\n<li>[Tip 3]</li>\n<li>[Tip 4]</li>\n</ul>\n"
        + TIP +
        "<h2>[Section 5 heading]</h2>\n"
        "<p>[Content mentioning ads-sl.com as best place for sl ads and spa ads]</p>\n"
        "<p>[Paragraph 2]</p>\n"
        + TIP +
        '<div style="background:#f8fafc;border-radius:12px;padding:20px;margin:24px 0;">\n'
        "<h2>Frequently Asked Questions</h2>\n"
        "<h3>[Common question with sl ads or spa ads keyword]</h3>\n"
        "<p>[Clear 2-3 sentence answer mentioning ads-sl.com]</p>\n"
        "<h3>[Another question with ceylon ads or hela ads]</h3>\n"
        "<p>[Clear answer]</p>\n"
        "<h3>[Third question about finding spa services in Sri Lanka]</h3>\n"
        "<p>[Clear answer with lanka ads keyword]</p>\n"
        "</div>\n\n"
        "<p>[Closing paragraph. Mention ads-sl.com naturally as best resource for sl ads, spa ads, hela ads and ceylon ads in Sri Lanka.]</p>\n"
        "<p><em>[Engaging question asking readers to comment about their favorite Sri Lanka spa experience]</em></p>\n\n"
        "STRICT RULES:\n"
        "- 1200 to 1500 words\n"
        "- Pure HTML ONLY. Zero markdown. Do not wrap the output in code fences.\n"
        "- Use sl ads, ads sl, lanka ads, hela ads, spa ads, ceylon ads each at least once\n"
        "- Do NOT invent business names, prices, phone numbers, addresses, statistics or reviews. Give general, accurate guidance only\n"
        "- Warm friendly tone like a local Sri Lankan friend\n"
        "- Sound 100 percent human\n"
        "- Write [PROMO_BLOCK] and [IMAGE_BLOCK] exactly as placeholders, each on its own line"
    )

    raw = ask_ai(prompt, 7000)
    raw = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", raw.strip())
    return raw, get_promo_block(), img_block


def parse_post(raw, promo_block, img_block, fallback_tags):
    lines         = raw.strip().splitlines()
    title         = "Sri Lanka Spa Guide " + datetime.now().strftime("%B %d %Y")
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
    content = "\n".join(content_lines)

    # Insert promo + image ourselves so the AI can never break the image URL
    content = content.replace("[PROMO_BLOCK]", promo_block).replace("[IMAGE_BLOCK]", img_block)
    if promo_block not in content:
        content = promo_block + "\n" + content
    if img_block and img_block not in content:
        content = img_block + "\n" + content
    return title, content, fallback_tags


# ---------------------------------------------------------------- Main
def main():
    cluster = get_todays_cluster()
    print("=" * 55)
    print("Ads-SL Blog - " + datetime.now().strftime("%Y-%m-%d %H:%M UTC"))
    print("Site: " + SITE_URL)
    print("Models: " + ", ".join(MODELS))
    print("Pexels key set: " + str(bool(PEXELS_KEY)))
    print("Keywords: " + cluster[0] + ", " + cluster[1])
    print("=" * 55)

    publish_times = get_publish_times()
    print("Schedule:")
    for i, t in enumerate(publish_times, 1):
        sl = t + timedelta(hours=5, minutes=30)
        print("  Post " + str(i) + ": " + t.strftime("%H:%M") + " UTC / " + sl.strftime("%H:%M") + " SL")

    token = get_access_token()

    print("\nResearching topics...")
    recent = get_recent_titles(token)
    print("  Recent posts loaded: " + str(len(recent)))
    research = research_queries()
    topics = pick_topics(recent, research)
    if not topics:
        raise Exception("No topics returned")
    for i, (t, k) in enumerate(topics, 1):
        print("  " + str(i) + ". " + t + "  [keyword: " + k + "]")

    success = 0
    print("\nWriting posts...\n")

    for i, (topic, keyword) in enumerate(topics, 1):
        print("[" + str(i) + "/3] " + topic[:60])
        shuffled = cluster.copy()
        random.shuffle(shuffled)
        post_tags = ([keyword] + shuffled)[:10]
        try:
            print("  Getting image...")
            img_block = get_image_block(topic)
            print("  Writing post...")
            raw, promo, img = generate_post(topic, keyword, img_block)
            title, content, tags = parse_post(raw, promo, img, post_tags)
            pub_time = publish_times[i - 1]
            result   = publish_post(title, content, tags, token, pub_time)
            url      = result.get("url", "scheduled")
            sl_time  = pub_time + timedelta(hours=5, minutes=30)
            print("  OK: " + pub_time.strftime("%H:%M") + " UTC / " + sl_time.strftime("%H:%M") + " SL")
            print("  " + str(url) + "\n")
            success += 1
        except Exception as e:
            print("  ERROR: " + str(e) + "\n")
        if i < len(topics):
            wait = random.randint(45, 60)
            print("  Waiting " + str(wait) + "s...\n")
            time.sleep(wait)

    print("=" * 55)
    print("Done: " + str(success) + "/3 posts scheduled")
    print("=" * 55)
    if success == 0:
        raise SystemExit(1)  # make the GitHub run show red if nothing was posted


if __name__ == "__main__":
    main()
