import os, random, requests, time, hashlib
from datetime import datetime, timedelta
from urllib.parse import quote

GROQ_KEY      = os.environ["GROQ_API_KEY"]
REFRESH_TOKEN = os.environ["BLOGGER_REFRESH_TOKEN"]
CLIENT_ID     = os.environ["BLOGGER_CLIENT_ID"]
CLIENT_SECRET = os.environ["BLOGGER_CLIENT_SECRET"]
BLOG_ID       = os.environ["BLOGGER_BLOG_ID"]

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS  = {"Authorization": "Bearer " + GROQ_KEY, "Content-Type": "application/json"}
MODEL    = "llama-3.3-70b-versatile"
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
    now = datetime.utcnow()
    times = []
    current = now + timedelta(hours=random.uniform(1, 2))
    for _ in range(3):
        times.append(current)
        gap = random.uniform(2.5, 5.0)
        current += timedelta(hours=gap)
    return times

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
            print("Groq error attempt " + str(attempt+1) + ":", data)
            time.sleep(10)
        except Exception as e:
            print("Request error attempt " + str(attempt+1) + ": " + str(e))
            time.sleep(10)
    raise Exception("Groq API failed after 3 attempts")

def pick_topics():
    today   = datetime.now().strftime("%B %d, %Y")
    month   = datetime.now().strftime("%B %Y")
    cluster = get_todays_cluster()
    kw_list = ", ".join(cluster[:6])
    sample  = random.sample(TOPIC_BANK, min(20, len(TOPIC_BANK)))
    listed  = "\n".join("- " + t for t in sample)
    prompt = (
        "You are a senior SEO strategist for ads-sl.com, Sri Lanka's top classified ads platform.\n\n"
        "Today: " + today + "\n"
        "Target keywords: " + kw_list + "\n\n"
        "Pick 3 BEST blog topics from this list for " + month + ":\n"
        + listed + "\n\n"
        "Rules:\n"
        "1. Each topic must naturally include keywords like: sl ads, lanka ads, hela ads, ads sl, spa ads, ceylon ads\n"
        "2. Cover different angles: one how-to, one list, one guide\n"
        "3. Max 65 characters per title\n"
        "4. High Google search potential in Sri Lanka\n\n"
        "Return ONLY numbered list:\n1.\n2.\n3."
    )
    text   = ask_ai(prompt, 400)
    topics = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line and line[0].isdigit() and "." in line:
            t = line.split(".", 1)[-1].strip().strip('"').strip("'")
            if t:
                topics.append(t)
    return topics[:3]

def get_image_url(topic):
    seed    = int(hashlib.md5(topic.encode()).hexdigest()[:8], 16) % 9999
    prompts = [
        "luxury spa treatment Sri Lanka tropical flowers candles",
        "beautiful Ceylon spa massage room relaxing atmosphere",
        "Sri Lanka wellness center ayurvedic herbs treatment",
        "Colombo spa beauty salon professional treatment",
        "tropical spa resort Sri Lanka pool relaxation",
        "herbal spa treatment Sri Lanka natural ingredients",
        "couples spa retreat Sri Lanka beach resort",
        "traditional Ceylon massage therapy wellness center",
    ]
    img_prompt = random.choice(prompts)
    encoded = quote(img_prompt)
    return "https://image.pollinations.ai/prompt/" + encoded + "?width=1200&height=630&nologo=true&seed=" + str(seed) + "&model=flux"

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

def generate_post(topic, img_url, tags):
    month_year  = datetime.now().strftime("%B %Y")
    cluster     = get_todays_cluster()
    kw_sample   = random.sample(cluster, min(6, len(cluster)))
    kw_str      = ", ".join(kw_sample)
    promo_block = get_promo_block()
    tag_str     = ", ".join(tags[:6])

    prompt = (
        "You are an expert Sri Lankan spa and wellness blogger writing for " + month_year + ".\n\n"
        "Topic: " + topic + "\n"
        "MUST include these keywords naturally: sl ads, ads sl, lanka ads, hela ads, spa ads, ceylon ads, " + kw_str + "\n"
        "Promote: " + SITE_URL + "\n\n"
        "CRITICAL: Write ONLY in pure HTML. NO markdown. NO ## symbols. NO ** symbols. NO > symbols.\n\n"
        "OUTPUT FORMAT:\n"
        "TITLE: [SEO title max 65 chars]\n"
        "---\n"
        "[PROMO_BLOCK]\n\n"
        '<img src="' + img_url + '" alt="' + topic + '" style="width:100%;border-radius:12px;margin:0 0 24px 0;" />\n\n'
        "<p><strong>[Opening hook sentence about " + topic + "]</strong> [2 more sentences with sl ads or spa ads keyword naturally.]</p>\n\n"
        "<p>[Second paragraph about what reader will learn. Mention ads-sl.com naturally.]</p>\n\n"
        "<h2>[Section 1 heading with keyword]</h2>\n"
        "<p>[Paragraph 1 with practical info and locations: Colombo, Kandy, Galle]</p>\n"
        "<p>[Paragraph 2 with tips and hela ads or ceylon ads keyword]</p>\n"
        "<h3>[Subtopic of section 1]</h3>\n"
        "<p>[Detailed paragraph with specific numbers and advice]</p>\n"
        '<blockquote style="border-left:4px solid #764ba2;padding:12px 16px;background:#f8f7ff;margin:16px 0;border-radius:0 8px 8px 0;"><strong>Expert Tip:</strong> [One specific actionable tip]</blockquote>\n\n'
        "<h2>[Section 2 heading with lanka ads or sl ads keyword]</h2>\n"
        "<p>[Paragraph with info about finding services through sl ads or ads sl]</p>\n"
        "<p>[Paragraph 2]</p>\n"
        "<h3>[Subtopic]</h3>\n"
        "<p>[Paragraph]</p>\n"
        '<blockquote style="border-left:4px solid #764ba2;padding:12px 16px;background:#f8f7ff;margin:16px 0;border-radius:0 8px 8px 0;"><strong>Expert Tip:</strong> [Tip]</blockquote>\n\n'
        "<h2>[Section 3 heading]</h2>\n"
        "<p>[Content mentioning Negombo, Bentota or Mirissa]</p>\n"
        "<p>[Paragraph 2 with ceylon ads or hela ads keyword]</p>\n"
        "<h3>[Subtopic]</h3>\n"
        "<p>[Paragraph]</p>\n"
        '<blockquote style="border-left:4px solid #764ba2;padding:12px 16px;background:#f8f7ff;margin:16px 0;border-radius:0 8px 8px 0;"><strong>Expert Tip:</strong> [Tip]</blockquote>\n\n'
        "<h2>[Section 4 heading]</h2>\n"
        "<p>[Content]</p>\n"
        "<ul>\n<li>[Tip 1]</li>\n<li>[Tip 2]</li>\n<li>[Tip 3]</li>\n<li>[Tip 4]</li>\n</ul>\n"
        '<blockquote style="border-left:4px solid #764ba2;padding:12px 16px;background:#f8f7ff;margin:16px 0;border-radius:0 8px 8px 0;"><strong>Expert Tip:</strong> [Tip]</blockquote>\n\n'
        "<h2>[Section 5 heading]</h2>\n"
        "<p>[Content mentioning ads-sl.com as best place for sl ads and spa ads]</p>\n"
        "<p>[Paragraph 2]</p>\n"
        '<blockquote style="border-left:4px solid #764ba2;padding:12px 16px;background:#f8f7ff;margin:16px 0;border-radius:0 8px 8px 0;"><strong>Expert Tip:</strong> [Tip]</blockquote>\n\n'
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
        "- Pure HTML ONLY. Zero markdown.\n"
        "- Use sl ads, ads sl, lanka ads, hela ads, spa ads, ceylon ads each at least once\n"
        "- Warm friendly tone like a local Sri Lankan friend\n"
        "- Sound 100 percent human\n"
        "- Write [PROMO_BLOCK] as exact placeholder"
    )

    raw = ask_ai(prompt, 4000)
    raw = raw.replace("[PROMO_BLOCK]", promo_block)
    return raw

def parse_post(raw, fallback_tags):
    lines         = raw.strip().splitlines()
    title         = "Sri Lanka Spa Guide " + datetime.now().strftime("%B %d %Y")
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

def get_access_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type":    "refresh_token"
    })
    data = r.json()
    if "access_token" not in data:
        raise Exception("Blogger auth failed: " + str(data))
    return data["access_token"]

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
        json=body
    )
    return r.json()

def main():
    cluster = get_todays_cluster()
    print("=" * 55)
    print("Ads-SL Blog - " + datetime.now().strftime("%Y-%m-%d %H:%M UTC"))
    print("Site: " + SITE_URL)
    print("Keywords: " + cluster[0] + ", " + cluster[1])
    print("=" * 55)

    publish_times = get_publish_times()
    print("Schedule:")
    for i, t in enumerate(publish_times, 1):
        sl = t + timedelta(hours=5, minutes=30)
        print("  Post " + str(i) + ": " + t.strftime("%H:%M") + " UTC / " + sl.strftime("%H:%M") + " SL")

    print("\nResearching topics...")
    topics = pick_topics()
    if not topics:
        print("ERROR: No topics")
        return
    for i, t in enumerate(topics, 1):
        print("  " + str(i) + ". " + t)

    token   = get_access_token()
    success = 0
    print("\nWriting posts...\n")

    for i, topic in enumerate(topics, 1):
        print("[" + str(i) + "/3] " + topic[:60])
        shuffled  = cluster.copy()
        random.shuffle(shuffled)
        post_tags = shuffled[:10]
        try:
            print("  Getting image...")
            img_url = get_image_url(topic)
            print("  Writing post...")
            raw = generate_post(topic, img_url, post_tags)
            title, content, tags = parse_post(raw, post_tags)
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
            wait = random.randint(20, 35)
            print("  Waiting " + str(wait) + "s...\n")
            time.sleep(wait)

    print("=" * 55)
    print("Done: " + str(success) + "/3 posts scheduled")
    print("All promoting: " + SITE_URL)
    print("=" * 55)


if __name__ == "__main__":
    main()
