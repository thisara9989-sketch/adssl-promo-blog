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
    ["spa ads Sri Lanka", "find spa Colombo", "Ceylon spa deals", "luxury spa listings",
     "book spa online Sri Lanka", "spa services Colombo", "Sri Lanka wellness guide",
     "spa treatments Sri Lanka", "Colombo beauty spa", "wellness booking Sri Lanka"],
    ["Sri Lanka classified ads", "ads-sl spa", "sl ads wellness", "lanka ad beauty",
     "post spa ads Sri Lanka", "wellness business ads", "Sri Lanka ad platform",
     "spa business listing", "online ads Sri Lanka", "classified beauty ads"],
    ["spa and wellness Sri Lanka", "Ceylon wellness retreat", "ayurvedic spa Sri Lanka",
     "herbal spa treatments", "wellness tourism Sri Lanka", "relaxation spa Kandy",
     "Galle spa resort", "Negombo wellness center", "couples spa Sri Lanka",
     "traditional spa treatments Ceylon"],
    ["advertise spa Sri Lanka", "spa marketing Sri Lanka", "sl spa business",
     "grow spa business online", "spa ads platform", "wellness ads Sri Lanka",
     "beauty salon ads", "spa listings online", "local spa advertising",
     "spa promotion Sri Lanka"],
    ["badu ads Sri Lanka", "VIP spa Sri Lanka", "premium wellness ads",
     "luxury spa packages", "spa gift packages Sri Lanka", "anti-aging spa",
     "body massage Sri Lanka", "facial treatment Colombo", "home spa service",
     "spa deals online Sri Lanka"],
    ["Colombo spa guide", "Kandy wellness center", "Galle spa retreat",
     "Negombo beach spa", "Nuwara Eliya wellness", "Mirissa spa resort",
     "Hikkaduwa beauty spa", "Ella wellness retreat", "Sigiriya spa hotel",
     "Bentota spa resort"],
]

TOPIC_BANK = [
    "how to find the best spa deals in Sri Lanka online",
    "complete guide to booking spa services in Colombo",
    "top luxury spa experiences available in Sri Lanka",
    "best ayurvedic wellness centers in Sri Lanka",
    "affordable spa packages for couples in Sri Lanka",
    "hidden gem spas in Kandy and Galle you should visit",
    "how to compare spa services before booking in Sri Lanka",
    "best beachside spa resorts in Negombo and Bentota",
    "traditional Ceylon spa rituals you must experience",
    "how ancient Sri Lankan herbs are used in modern spas",
    "authentic ayurvedic treatments available in Sri Lanka",
    "Ceylon spa vs international spa what makes it unique",
    "best herbal massage treatments in Sri Lanka",
    "traditional oil treatments at Ceylon wellness centers",
    "how to advertise your spa business online in Sri Lanka",
    "best platforms to post spa ads in Sri Lanka",
    "how online classified ads help spa businesses grow",
    "why spa businesses need digital advertising in Sri Lanka",
    "how to create effective spa ads that attract customers",
    "growing your wellness business with online listings",
    "wellness tourism guide for visitors to Sri Lanka",
    "best spa retreats for stress relief in Sri Lanka",
    "how spa treatments improve mental health and wellbeing",
    "complete body wellness routines available in Sri Lanka",
    "best anti-aging spa treatments available in Colombo",
    "couples wellness retreats available across Sri Lanka",
    "top skin care treatments at Sri Lanka beauty spas",
    "home spa services you can book through Sri Lankan ads",
    "how to find VIP spa services in Sri Lanka discreetly",
    "luxury spa packages available at five star hotels Sri Lanka",
    "best day spa vs wellness resort in Sri Lanka",
    "how to verify authentic spa listings before booking",
    "spa gift packages perfect for gifting in Sri Lanka",
    "trending wellness treatments in Sri Lanka right now",
    "how digital platforms are changing Sri Lanka spa industry",
    "best spas in Colombo for a quick relaxation break",
    "top wellness centers in Kandy for tourists",
    "spa and wellness options near Galle Fort Sri Lanka",
    "best beach resort spas in southern Sri Lanka",
    "Nuwara Eliya hill country spa retreats guide",
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
        "You are a senior SEO content strategist for Ads-SL (ads-sl.com), "
        "Sri Lanka's leading classified ads platform for spa and wellness services.\n\n"
        "Today: " + today + "\n"
        "Focus keywords for today: " + kw_list + "\n\n"
        "From these topics, choose the 3 BEST for " + month + " that:\n"
        "1. Have high Google search volume potential in Sri Lanka\n"
        "2. Naturally fit today's keywords\n"
        "3. Cover DIFFERENT content angles (one guide, one list, one how-to)\n"
        "4. Will genuinely help readers AND promote ads-sl.com\n\n"
        "Topics to choose from:\n" + listed + "\n\n"
        "Rewrite each title to be SEO powerful, max 65 characters.\n"
        "Return ONLY a numbered list:\n1.\n2.\n3."
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
    img_desc = ask_ai(
        "Create a short 8-12 word image description for a blog post about: " + topic + "\n"
        "Should look like a real photo of a luxury Sri Lanka spa.\n"
        "Return ONLY the description, no quotes.",
        max_tokens=50
    ).strip().replace('"', '').replace('\n', ' ')
    seed    = int(hashlib.md5(topic.encode()).hexdigest()[:8], 16) % 10000
    encoded = quote(img_desc[:200])
    return "https://image.pollinations.ai/prompt/" + encoded + "?width=1200&height=630&nologo=true&seed=" + str(seed) + "&model=flux"

def get_promo_block():
    styles = [
        '<div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:20px 24px;border-radius:14px;margin:0 0 28px 0;text-align:center;">'
        '<p style="color:#fff;font-size:16px;font-weight:600;margin:0 0 12px 0;">Sri Lanka\'s #1 Spa and Wellness Ads Platform</p>'
        '<p style="color:rgba(255,255,255,0.85);font-size:13px;margin:0 0 14px 0;">Find trusted spa listings, wellness centers and beauty services across Sri Lanka.</p>'
        '<a href="' + SITE_URL + '" target="_blank" rel="noopener" style="background:#fff;color:#764ba2;padding:11px 28px;border-radius:30px;font-weight:700;font-size:14px;text-decoration:none;display:inline-block;">Explore Ads-SL.com</a>'
        '</div>',

        '<div style="background:#fff;border:2px solid #e2e8f0;border-radius:14px;padding:20px 24px;margin:0 0 28px 0;box-shadow:0 2px 10px rgba(0,0,0,0.06);">'
        '<p style="color:#1e293b;font-size:15px;font-weight:700;margin:0 0 4px 0;">Looking for spa services in Sri Lanka?</p>'
        '<p style="color:#64748b;font-size:13px;margin:0 0 10px 0;">Browse verified spa ads, wellness centers and beauty listings at Ads-SL.com - Sri Lanka\'s trusted ad platform.</p>'
        '<a href="' + SITE_URL + '" target="_blank" rel="noopener" style="background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:8px 20px;border-radius:20px;font-weight:700;font-size:13px;text-decoration:none;display:inline-block;">Visit Ads-SL.com</a>'
        '</div>',

        '<div style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-left:5px solid #22c55e;border-radius:0 14px 14px 0;padding:18px 22px;margin:0 0 28px 0;">'
        '<p style="color:#166534;font-size:15px;font-weight:700;margin:0 0 6px 0;">Advertised on Ads-SL.com</p>'
        '<p style="color:#374151;font-size:13px;margin:0 0 12px 0;">Sri Lanka\'s leading platform for spa, wellness and beauty classified ads. Find listings or advertise your business today.</p>'
        '<a href="' + SITE_URL + '" target="_blank" rel="noopener" style="background:#22c55e;color:#fff;padding:9px 22px;border-radius:20px;font-weight:700;font-size:13px;text-decoration:none;display:inline-block;">Browse All Ads</a>'
        '</div>',
    ]
    return random.choice(styles)

def generate_post(topic, img_url, tags):
    month_year  = datetime.now().strftime("%B %Y")
    cluster     = get_todays_cluster()
    kw_sample   = random.sample(cluster, min(5, len(cluster)))
    kw_str      = ", ".join(kw_sample)
    promo_block = get_promo_block()
    tag_str     = ", ".join(tags[:6])

    prompt = (
        "You are an expert Sri Lankan lifestyle and wellness blogger for " + month_year + ".\n\n"
        "Topic: " + topic + "\n"
        "Keywords to use naturally: " + kw_str + "\n"
        "Promote this website: " + SITE_URL + "\n"
        "Post tags: " + tag_str + "\n\n"
        "Write a complete SEO blog post. EXACT format:\n\n"
        "TITLE: [SEO title max 65 chars with main keyword]\n"
        "META: [155-char meta description]\n"
        "---\n"
        "[PROMO_BLOCK]\n\n"
        '<figure style="margin:0 0 28px 0;">\n'
        '<img src="' + img_url + '" alt="[alt text with keyword]" style="width:100%;border-radius:14px;" loading="lazy"/>\n'
        '<figcaption style="text-align:center;color:#94a3b8;font-size:12px;margin-top:8px;">[image caption]</figcaption>\n'
        "</figure>\n\n"
        "BLOG POST STRUCTURE:\n"
        "- Opening hook paragraph with bold first sentence\n"
        "- 5 sections each with H2 heading, 2-3 paragraphs, H3 subtopic, blockquote tip\n"
        "- FAQ section with 3 common Google questions and answers\n"
        "- Closing paragraph mentioning ads-sl.com naturally\n"
        "- Final question to invite comments\n\n"
        "RULES:\n"
        "- 1300 to 1600 words total\n"
        "- Warm friendly tone like a local Sri Lankan expert\n"
        "- Mention Colombo, Kandy, Galle, Negombo, Bentota, Mirissa\n"
        "- Use keywords 5-7 times naturally\n"
        "- Reference ads-sl.com 2-3 times in body naturally\n"
        "- NO cliches: no 'In today's world', 'Game changer', 'Dive in'\n"
        "- Sound 100 percent human\n"
        "- Use HTML tags: h2, h3, p, blockquote, ul, li, strong\n\n"
        "IMPORTANT: Write [PROMO_BLOCK] as exact placeholder text."
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
    print("=" * 60)
    print("Ads-SL Smart Blog - " + datetime.now().strftime("%Y-%m-%d %H:%M UTC"))
    print("Promoting: " + SITE_URL)
    print("Today keyword cluster: " + cluster[0])
    print("=" * 60)

    publish_times = get_publish_times()
    print("Post schedule (UTC):")
    for i, t in enumerate(publish_times, 1):
        sl_time = t + timedelta(hours=5, minutes=30)
        print("  Post " + str(i) + ": " + t.strftime("%H:%M") + " UTC / " + sl_time.strftime("%H:%M") + " SL")

    print("\nAI researching best topics...")
    topics = pick_topics()
    if not topics:
        print("ERROR: Topic generation failed")
        return

    print("Selected topics:")
    for i, t in enumerate(topics, 1):
        print("  " + str(i) + ". " + t)

    token   = get_access_token()
    success = 0

    print("\nWriting " + str(len(topics)) + " posts...\n")

    for i, topic in enumerate(topics, 1):
        print("[" + str(i) + "/3] " + topic[:65])

        shuffled  = cluster.copy()
        random.shuffle(shuffled)
        post_tags = shuffled[:10]

        try:
            print("  Generating image...")
            img_url = get_image_url(topic)

            print("  Writing post...")
            raw = generate_post(topic, img_url, post_tags)

            title, content, tags = parse_post(raw, post_tags)

            pub_time = publish_times[i - 1]
            result   = publish_post(title, content, tags, token, pub_time)
            url      = result.get("url", "scheduled")
            sl_time  = pub_time + timedelta(hours=5, minutes=30)

            print("  OK - Scheduled: " + pub_time.strftime("%H:%M") + " UTC / " + sl_time.strftime("%H:%M") + " SL")
            print("  URL: " + str(url) + "\n")
            success += 1

        except Exception as e:
            print("  ERROR: " + str(e) + "\n")

        if i < len(topics):
            wait = random.randint(20, 35)
            print("  Waiting " + str(wait) + "s...\n")
            time.sleep(wait)

    print("=" * 60)
    print("Done: " + str(success) + "/3 posts scheduled")
    print("All linking to: " + SITE_URL)
    print("Tomorrow uses different keyword cluster automatically")
    print("=" * 60)


if __name__ == "__main__":
    main()
