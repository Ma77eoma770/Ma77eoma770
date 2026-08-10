# generate_badge.py
import requests
import datetime
import os
import random
import textwrap

# USERNAME GITHUB
USERNAME = "Ma77eoma770"

TOKEN = os.getenv("GH_PAT")
HEADERS = {}
if TOKEN:
    HEADERS["Authorization"] = f"bearer {TOKEN}"

lang_colors = {
    "TypeScript": "#89b4fa",
    "Python": "#74c7ec",
    "JavaScript": "#f9e2af",
    "HTML": "#fab387",
    "CSS": "#cba6f7",
    "C++": "#eba0ac",
    "C": "#94e2d5",
    "Java": "#f38ba8",
    "Go": "#89dceb",
    "Rust": "#fab387",
    "Shell": "#a6e3a1",
    "Vue": "#a6e3a1",
    "React": "#89b4fa"
}

def format_description(desc, max_chars_per_line=60):
    if not desc:
        desc = "No description provided."
    lines = textwrap.wrap(desc, width=max_chars_per_line)
    line1 = lines[0] if len(lines) > 0 else ""
    line2 = lines[1] if len(lines) > 1 else ""
    if len(lines) > 2:
        line2 = line2[:max_chars_per_line - 3].strip() + "..."
    return line1, line2

def fetch_github_contributions_graphql(username):
    print(f"[*] Recupero calendario dei contributi reali via GitHub GraphQL API...")
    query = """
    query($username: String!) {
      user(login: $username) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
                color
              }
            }
          }
        }
      }
    }
    """
    url = "https://api.github.com/graphql"
    if TOKEN:
        try:
            resp = requests.post(url, json={"query": query, "variables": {"username": username}}, headers=HEADERS)
            if resp.status_code == 200:
                res_data = resp.json()
                calendar = res_data.get("data", {}).get("user", {}).get("contributionsCollection", {}).get("contributionCalendar", {})
                if calendar:
                    total_cnt = calendar.get("totalContributions", 0)
                    print(f"[+] Heatmap REALE recuperata con successo! Totale contributi anno: {total_cnt}")
                    return calendar
            else:
                print(f"[!] GraphQL status code: {resp.status_code}. Risposta: {resp.text[:150]}")
        except Exception as e:
            print(f"[!] Eccezione durante la chiamata GraphQL: {e}")
    else:
        print("[!] Nessun GH_PAT trovato. Chiamata GraphQL non autenticata non consentita da GitHub.")
    
    return None

def fetch_github_profile_data(username):
    print(f"[*] Connessione alle API REST di GitHub per l'utente: {username}...")
    
    rest_headers = {}
    if TOKEN:
        rest_headers["Authorization"] = f"token {TOKEN}"

    user_url = f"https://api.github.com/users/{username}"
    user_resp = requests.get(user_url, headers=rest_headers)
    
    if user_resp.status_code == 200:
        user_data = user_resp.json()
        print(f"[+] Dati utente recuperati con successo per: {user_data.get('name', username)}")
    else:
        print(f"[!] Errore nel recupero dati utente (Status code: {user_resp.status_code})")
        user_data = {}
    
    name = user_data.get("name", username)
    public_repos_count = user_data.get("public_repos", 0)
    followers = user_data.get("followers", 0)

    print(f" -> Nome: {name}")
    print(f" -> Repository pubblici: {public_repos_count}")
    print(f" -> Followers: {followers}")

    print("[*] Recupero della lista dei repository pubblici...")
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
    repos_resp = requests.get(repos_url, headers=rest_headers)
    
    languages_bytes = {}
    total_stars = 0
    all_projects = []

    if repos_resp.status_code == 200:
        repos = repos_resp.json()
        print(f"[+] Trovati {len(repos)} repository da analizzare.")
        
        for repo in repos:
            repo_name = repo.get("name")
            is_fork = repo.get("fork")
            stars = repo.get("stargazers_count", 0)
            forks = repo.get("forks_count", 0)
            lang = repo.get("language") or "Code"
            desc = repo.get("description") or "No description provided."
            url = repo.get("html_url", f"https://github.com/{username}/{repo_name}")
            
            if is_fork:
                print(f"    - Salto il repo '{repo_name}' per le statistiche perché è un fork.")
                continue
                
            total_stars += stars
            print(f"    - Analizzo il repo: '{repo_name}' (Stelle: {stars})")
            
            all_projects.append({
                "name": repo_name,
                "description": desc,
                "language": lang,
                "stars": stars,
                "forks": forks,
                "url": url
            })

            langs_url = repo.get("languages_url")
            if langs_url:
                langs_resp = requests.get(langs_url, headers=rest_headers)
                if langs_resp.status_code == 200:
                    langs_data = langs_resp.json()
                    for l_name, count in langs_data.items():
                        languages_bytes[l_name] = languages_bytes.get(l_name, 0) + count
    else:
        print(f"[!] Errore nel recupero dei repository (Status code: {repos_resp.status_code})")

    print(f"[+] Totale stelle accumulate nei repo originali: {total_stars}")

    if not languages_bytes:
        print("[!] Nessun linguaggio trovato, applico i valori di fallback.")
        languages_bytes = {"Python": 1000, "TypeScript": 1000}

    total_bytes = sum(languages_bytes.values())
    sorted_langs = sorted(languages_bytes.items(), key=lambda x: x[1], reverse=True)
    
    print("[*] Calcolo delle percentuali dei linguaggi...")
    top_languages = []
    for l_name, count in sorted_langs[:5]:
        percentage = round((count / total_bytes) * 100)
        print(f"    > {l_name}: {count} byte ({percentage}%)")
        top_languages.append({"name": l_name, "pct": percentage})

    all_projects.sort(key=lambda x: (x["stars"], x["forks"], x["name"]), reverse=True)
    top_4_projects = all_projects[:4]

    default_projects = [
        {"name": "Awesome-App", "description": "High performance application built with modern architecture and interstellar aesthetic.", "language": "Python", "stars": 12, "forks": 3, "url": f"https://github.com/{username}"},
        {"name": "Cosmic-Engine", "description": "Lightweight graphics and animation toolkit for dark mode SVG generation.", "language": "TypeScript", "stars": 8, "forks": 2, "url": f"https://github.com/{username}"},
        {"name": "Neural-Net-Lab", "description": "Deep learning experiments and modular neural network implementations.", "language": "C++", "stars": 5, "forks": 1, "url": f"https://github.com/{username}"},
        {"name": "Quantum-Shield", "description": "Security and cryptographic utility library for modern cloud applications.", "language": "Rust", "stars": 4, "forks": 0, "url": f"https://github.com/{username}"},
    ]

    while len(top_4_projects) < 4:
        top_4_projects.append(default_projects[len(top_4_projects)])

    contributions_calendar = fetch_github_contributions_graphql(username)

    daily_events = {}
    events_url = f"https://api.github.com/users/{username}/events?per_page=100"
    events_resp = requests.get(events_url, headers=rest_headers)
    if events_resp.status_code == 200:
        events = events_resp.json()
        for ev in events:
            created_at = ev.get("created_at")
            if created_at:
                date_str = created_at.split("T")[0]
                daily_events[date_str] = daily_events.get(date_str, 0) + 1

    return {
        "name": name,
        "repos": public_repos_count,
        "followers": followers,
        "stars": total_stars,
        "languages": top_languages,
        "top_projects": top_4_projects,
        "daily_events": daily_events,
        "contributions_calendar": contributions_calendar
    }

print("--------------------------------------------------")
data = fetch_github_profile_data(USERNAME)
print("--------------------------------------------------")

# ==========================================
# 1. GENERAZIONE dynamic_card.svg (PROFILE BADGE)
# ==========================================
print("[*] Avvio orchestrazione dinamica del Badge Profilo...")

padding_top = 34
about_height = 76
separator_margin = 10
skills_header_height = 26
row_height = 26
padding_bottom = 32

num_langs = len(data["languages"])
skills_list_height = num_langs * row_height

separator_y = padding_top + about_height + separator_margin
skills_start_y = separator_y + separator_margin
svg_height = skills_start_y + skills_header_height + skills_list_height + padding_bottom

languages_svg_rows = ""
for i, lang_info in enumerate(data["languages"]):
    l_name = lang_info["name"]
    l_pct = lang_info["pct"]
    l_width = int((l_pct / 100) * 340)
    color = lang_colors.get(l_name, "#cba6f7")
    
    row_y = i * row_height
    languages_svg_rows += f"""
    <g transform="translate(0, {row_y})">
      <circle cx="6" cy="7" r="4" fill="{color}" filter="url(#glow-dot)" />
      <text class="skill-text" x="22" y="11">{l_name}</text>
      <text class="percentage" x="250" y="11">{l_pct}%</text>
      <rect class="track" x="290" y="3" width="340" height="8" rx="4" />
      <rect class="animated-bar" style="--target-width: {l_width}px;" x="290" y="3" height="8" rx="4" fill="{color}" width="0" />
    </g>
    """

random.seed(42)
stars_svg = ""
num_stars = 30
for s in range(num_stars):
    sx = random.randint(20, 770)
    sy = random.randint(20, max(40, svg_height - 30))
    sr = round(random.uniform(0.8, 2.2), 1)
    duration = round(random.uniform(2.0, 4.5), 1)
    delay = round(random.uniform(0.0, 3.5), 1)
    stars_svg += f'<circle class="star" cx="{sx}" cy="{sy}" r="{sr}" fill="#cdd6f4" style="--duration: {duration}s; --delay: {delay}s;" />\n    '

badge_svg_content = f"""<svg width="800" height="{svg_height}" viewBox="0 0 800 {svg_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;family=Orbitron:wght@600;800&amp;display=swap');
    </style>

    <clipPath id="card-clip">
      <rect x="10" y="10" width="780" height="{svg_height - 20}" rx="20" />
    </clipPath>

    <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#cba6f7" />
      <stop offset="40%" stop-color="#f5c2e7" />
      <stop offset="75%" stop-color="#fab387" />
      <stop offset="100%" stop-color="#74c7ec" />
    </linearGradient>

    <linearGradient id="title-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f5c2e7" />
      <stop offset="50%" stop-color="#cba6f7" />
      <stop offset="100%" stop-color="#89b4fa" />
    </linearGradient>

    <linearGradient id="sep-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#313244" stop-opacity="0.1" />
      <stop offset="20%" stop-color="#cba6f7" stop-opacity="0.6" />
      <stop offset="50%" stop-color="#89b4fa" stop-opacity="0.8" />
      <stop offset="80%" stop-color="#cba6f7" stop-opacity="0.6" />
      <stop offset="100%" stop-color="#313244" stop-opacity="0.1" />
    </linearGradient>

    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f0f17" />
      <stop offset="45%" stop-color="#181825" />
      <stop offset="80%" stop-color="#1e1e2e" />
      <stop offset="100%" stop-color="#282338" />
    </linearGradient>

    <linearGradient id="star-trail-1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#cba6f7" stop-opacity="0" />
      <stop offset="70%" stop-color="#f5c2e7" stop-opacity="0.6" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="1" />
    </linearGradient>

    <linearGradient id="star-trail-2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#89b4fa" stop-opacity="0" />
      <stop offset="75%" stop-color="#cba6f7" stop-opacity="0.5" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.9" />
    </linearGradient>

    <filter id="glow-dot" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <style>
    .card-bg {{
      fill: url(#bg-grad);
      stroke: url(#border-grad);
      stroke-width: 1.75;
      rx: 20px;
    }}
    .section-label {{
      font-family: 'Orbitron', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      fill: #f5e0dc;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 2px;
      opacity: 0.9;
    }}
    .main-title {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      fill: #cdd6f4;
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.3px;
    }}
    .hero-name {{
      fill: url(#title-grad);
    }}
    .sub-stats {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      fill: #a6adc8;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.2px;
    }}
    .stat-val {{
      font-weight: 700;
    }}
    .skill-text {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      fill: #cdd6f4;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.1px;
    }}
    .percentage {{
      font-family: 'Orbitron', 'Inter', sans-serif;
      fill: #bac2de;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.5px;
    }}
    .track {{
      fill: #313244;
      opacity: 0.7;
    }}
    @keyframes loadBar {{
      from {{ width: 0px; }}
      to {{ width: var(--target-width); }}
    }}
    .animated-bar {{
      animation: loadBar 1.5s cubic-bezier(0.1, 1, 0.1, 1) forwards;
      filter: drop-shadow(0px 0px 2px rgba(203, 166, 247, 0.4));
    }}
    @keyframes twinkle {{
      0%, 100% {{ opacity: 0.12; transform: scale(0.8); }}
      50% {{ opacity: 0.95; transform: scale(1.3); }}
    }}
    .star {{
      animation: twinkle var(--duration, 3s) infinite ease-in-out var(--delay, 0s);
      transform-box: fill-box;
      transform-origin: center;
    }}
    @keyframes shootingStar1 {{
      0% {{ transform: translate(120px, -40px); opacity: 0; }}
      10% {{ opacity: 0.95; }}
      45% {{ transform: translate(620px, 210px); opacity: 0; }}
      100% {{ transform: translate(620px, 210px); opacity: 0; }}
    }}
    @keyframes shootingStar2 {{
      0%, 30% {{ transform: translate(350px, -40px); opacity: 0; }}
      40% {{ opacity: 0.85; }}
      75% {{ transform: translate(850px, 210px); opacity: 0; }}
      100% {{ transform: translate(850px, 210px); opacity: 0; }}
    }}
    @keyframes shootingStar3 {{
      0%, 60% {{ transform: translate(50px, -30px); opacity: 0; }}
      68% {{ opacity: 0.9; }}
      92% {{ transform: translate(550px, 220px); opacity: 0; }}
      100% {{ transform: translate(550px, 220px); opacity: 0; }}
    }}
    .shooting-star-1 {{ animation: shootingStar1 8s infinite ease-out; }}
    .shooting-star-2 {{ animation: shootingStar2 9s infinite ease-out; }}
    .shooting-star-3 {{ animation: shootingStar3 7s infinite ease-out; }}
  </style>

  <rect class="card-bg" x="10" y="10" width="780" height="{svg_height - 20}" />

  <g clip-path="url(#card-clip)">
    {stars_svg}
    <g class="shooting-star-1">
      <line x1="0" y1="0" x2="65" y2="32" stroke="url(#star-trail-1)" stroke-width="1.4" stroke-linecap="round" />
      <circle cx="65" cy="32" r="1.6" fill="#ffffff" />
    </g>
    <g class="shooting-star-2">
      <line x1="0" y1="0" x2="50" y2="25" stroke="url(#star-trail-2)" stroke-width="1.2" stroke-linecap="round" />
      <circle cx="50" cy="25" r="1.3" fill="#ffffff" />
    </g>
    <g class="shooting-star-3">
      <line x1="0" y1="0" x2="55" y2="27" stroke="url(#star-trail-1)" stroke-width="1.3" stroke-linecap="round" />
      <circle cx="55" cy="27" r="1.4" fill="#ffffff" />
    </g>
  </g>

  <g transform="translate(42, {padding_top})">
    <text class="section-label" x="0" y="0">✦ ABOUT ME</text>
    <text class="main-title" x="0" y="26">Hi, I'm <tspan class="hero-name">{data["name"]}</tspan> 👋</text>
    <text class="sub-stats" x="0" y="58">
      <tspan fill="#bac2de">Repos:</tspan> <tspan class="stat-val" fill="#89b4fa">{data["repos"]}</tspan>
      <tspan fill="#585b70" dx="10">|</tspan> 
      <tspan fill="#bac2de" dx="10">Stars:</tspan> <tspan class="stat-val" fill="#f9e2af">{data["stars"]}</tspan>
      <tspan fill="#585b70" dx="10">|</tspan> 
      <tspan fill="#bac2de" dx="10">Followers:</tspan> <tspan class="stat-val" fill="#a6e3a1">{data["followers"]}</tspan>
    </text>
  </g>

  <line x1="42" y1="{separator_y}" x2="758" y2="{separator_y}" stroke="url(#sep-grad)" stroke-width="1.5" />

  <g transform="translate(42, {skills_start_y})">
    <text class="section-label" x="0" y="0">✦ LANGUAGE STACK</text>
    <g transform="translate(0, 18)">
      {languages_svg_rows}
    </g>
  </g>
</svg>
"""

with open("dynamic_card.svg", "w", encoding="utf-8") as f:
    f.write(badge_svg_content)

print(f"[+] File 'dynamic_card.svg' generato con successo! Altezza: {svg_height}px")

# ==========================================
# 2. GENERAZIONE projects_carousel.svg (TOP PROJECTS CAROUSEL)
# ==========================================
print("[*] Avvio orchestrazione dinamica del Carosello Progetti Top...")

carousel_width = 800
carousel_height = 310
viewport_width = 720

project_cards_svg = ""
for idx, proj in enumerate(data["top_projects"]):
    p_name = proj["name"]
    p_lang = proj["language"]
    p_stars = proj["stars"]
    p_forks = proj["forks"]
    p_url = proj["url"]
    p_color = lang_colors.get(p_lang, "#cba6f7")
    
    line1, line2 = format_description(proj["description"])
    card_x = idx * viewport_width
    
    project_cards_svg += f"""
    <g transform="translate({card_x}, 0)">
      <rect x="0" y="0" width="716" height="210" rx="16" fill="#181825" fill-opacity="0.75" stroke="#313244" stroke-width="1.2" />
      <g transform="translate(24, 34)">
        <path d="M4 1.75C4 .783 4.783 0 5.75 0h8.5C15.217 0 16 .783 16 1.75v12.5c0 .098-.015.192-.042.281H16V17.25C16 18.217 15.217 19 14.25 19h-11A1.75 1.75 0 0 1 1.5 17.25V4.75C1.5 3.783 2.283 3 3.25 3H4V1.75Zm1.75 1.25a.25.25 0 0 0-.25.25V17.25c0 .138.112.25.25.25h11a.25.25 0 0 0 .25-.25V14.5H5.75A1.75 1.75 0 0 1 4 12.75V3H5.75ZM3.25 4.5a.25.25 0 0 0-.25.25v8c0 .138.112.25.25.25H4V4.5h-.75Z" fill="#cba6f7" transform="scale(1.2)" />
        <text class="project-title" x="28" y="16">{p_name}</text>
      </g>
      <g transform="translate(370, 24)">
        <rect x="0" y="0" width="105" height="26" rx="13" fill="#1e1e2e" stroke="#313244" />
        <circle cx="14" cy="13" r="4" fill="{p_color}" />
        <text class="badge-text" x="25" y="17">{p_lang}</text>
        <rect x="113" y="0" width="75" height="26" rx="13" fill="#1e1e2e" stroke="#313244" />
        <text class="badge-icon" x="124" y="17" fill="#f9e2af">★</text>
        <text class="badge-text" x="138" y="17">{p_stars}</text>
        <rect x="194" y="0" width="75" height="26" rx="13" fill="#1e1e2e" stroke="#313244" />
        <text class="badge-icon" x="205" y="17" fill="#89b4fa">⑂</text>
        <text class="badge-text" x="219" y="17">{p_forks}</text>
      </g>
      <line x1="24" y1="68" x2="692" y2="68" stroke="#313244" stroke-width="1" opacity="0.6" />
      <text class="proj-desc" x="24" y="100">{line1}</text>
      <text class="proj-desc" x="24" y="124">{line2}</text>
      <g transform="translate(24, 154)">
        <rect x="0" y="0" width="165" height="30" rx="15" fill="url(#title-grad)" opacity="0.12" stroke="#cba6f7" stroke-width="1" />
        <text class="cta-text" x="14" y="19">VIEW PROJECT →</text>
      </g>
    </g>
    """

carousel_stars_svg = ""
for s in range(25):
    sx = random.randint(20, 770)
    sy = random.randint(20, carousel_height - 30)
    sr = round(random.uniform(0.8, 2.0), 1)
    duration = round(random.uniform(2.5, 4.5), 1)
    delay = round(random.uniform(0.0, 3.0), 1)
    carousel_stars_svg += f'<circle class="star" cx="{sx}" cy="{sy}" r="{sr}" fill="#cdd6f4" style="--duration: {duration}s; --delay: {delay}s;" />\n    '

carousel_svg_content = f"""<svg width="800" height="{carousel_height}" viewBox="0 0 800 {carousel_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;family=Orbitron:wght@600;800&amp;display=swap');
    </style>

    <clipPath id="carousel-clip">
      <rect x="10" y="10" width="780" height="{carousel_height - 20}" rx="20" />
    </clipPath>

    <clipPath id="viewport-clip">
      <rect x="0" y="0" width="716" height="210" rx="16" />
    </clipPath>

    <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#cba6f7" />
      <stop offset="40%" stop-color="#f5c2e7" />
      <stop offset="75%" stop-color="#fab387" />
      <stop offset="100%" stop-color="#74c7ec" />
    </linearGradient>

    <linearGradient id="title-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f5c2e7" />
      <stop offset="50%" stop-color="#cba6f7" />
      <stop offset="100%" stop-color="#89b4fa" />
    </linearGradient>

    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f0f17" />
      <stop offset="45%" stop-color="#181825" />
      <stop offset="80%" stop-color="#1e1e2e" />
      <stop offset="100%" stop-color="#282338" />
    </linearGradient>

    <linearGradient id="star-trail-1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#cba6f7" stop-opacity="0" />
      <stop offset="70%" stop-color="#f5c2e7" stop-opacity="0.6" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="1" />
    </linearGradient>
  </defs>

  <style>
    .card-bg {{
      fill: url(#bg-grad);
      stroke: url(#border-grad);
      stroke-width: 1.75;
      rx: 20px;
    }}
    .section-label {{
      font-family: 'Orbitron', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      fill: #f5e0dc;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 2px;
      opacity: 0.9;
    }}
    .project-title {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      fill: #cdd6f4;
      font-size: 17px;
      font-weight: 800;
      letter-spacing: -0.2px;
    }}
    .proj-desc {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      fill: #a6adc8;
      font-size: 13px;
      font-weight: 500;
      line-height: 1.4;
    }}
    .badge-text {{
      font-family: 'Inter', sans-serif;
      fill: #cdd6f4;
      font-size: 11px;
      font-weight: 600;
    }}
    .badge-icon {{
      font-family: 'Inter', sans-serif;
      font-size: 12px;
      font-weight: 700;
    }}
    .cta-text {{
      font-family: 'Orbitron', 'Inter', sans-serif;
      fill: #cba6f7;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 1px;
    }}

    @keyframes twinkle {{
      0%, 100% {{ opacity: 0.12; transform: scale(0.8); }}
      50% {{ opacity: 0.95; transform: scale(1.3); }}
    }}
    .star {{
      animation: twinkle var(--duration, 3s) infinite ease-in-out var(--delay, 0s);
      transform-box: fill-box;
      transform-origin: center;
    }}

    @keyframes shootingStarCarousel1 {{
      0% {{ transform: translate(780px, 20px); opacity: 0; }}
      15% {{ opacity: 0.9; }}
      60% {{ transform: translate(380px, 310px); opacity: 0; }}
      100% {{ transform: translate(380px, 310px); opacity: 0; }}
    }}
    @keyframes shootingStarCarousel2 {{
      0%, 40% {{ transform: translate(520px, -20px); opacity: 0; }}
      52% {{ opacity: 0.85; }}
      88% {{ transform: translate(120px, 280px); opacity: 0; }}
      100% {{ transform: translate(120px, 280px); opacity: 0; }}
    }}
    .shooting-star-1 {{ animation: shootingStarCarousel1 8s infinite ease-out; }}
    .shooting-star-2 {{ animation: shootingStarCarousel2 10s infinite ease-out; }}

    @keyframes slideCarousel {{
      0%, 20% {{ transform: translateX(0px); }}
      25%, 45% {{ transform: translateX(-720px); }}
      50%, 70% {{ transform: translateX(-1440px); }}
      75%, 95% {{ transform: translateX(-2160px); }}
      100% {{ transform: translateX(0px); }}
    }}
    .carousel-track {{
      animation: slideCarousel 16s cubic-bezier(0.77, 0, 0.175, 1) infinite;
    }}

    @keyframes dot1 {{
      0%, 20%, 100% {{ fill: #cba6f7; opacity: 1; transform: scale(1.25); }}
      25%, 95% {{ fill: #585b70; opacity: 0.4; transform: scale(1); }}
    }}
    @keyframes dot2 {{
      0%, 20%, 70%, 100% {{ fill: #585b70; opacity: 0.4; transform: scale(1); }}
      25%, 45% {{ fill: #cba6f7; opacity: 1; transform: scale(1.25); }}
    }}
    @keyframes dot3 {{
      0%, 45%, 95%, 100% {{ fill: #585b70; opacity: 0.4; transform: scale(1); }}
      50%, 70% {{ fill: #cba6f7; opacity: 1; transform: scale(1.25); }}
    }}
    @keyframes dot4 {{
      0%, 70% {{ fill: #585b70; opacity: 0.4; transform: scale(1); }}
      75%, 95% {{ fill: #cba6f7; opacity: 1; transform: scale(1.25); }}
      100% {{ fill: #585b70; opacity: 0.4; transform: scale(1); }}
    }}

    .dot-1 {{ animation: dot1 16s infinite; transform-box: fill-box; transform-origin: center; }}
    .dot-2 {{ animation: dot2 16s infinite; transform-box: fill-box; transform-origin: center; }}
    .dot-3 {{ animation: dot3 16s infinite; transform-box: fill-box; transform-origin: center; }}
    .dot-4 {{ animation: dot4 16s infinite; transform-box: fill-box; transform-origin: center; }}
  </style>

  <rect class="card-bg" x="10" y="10" width="780" height="{carousel_height - 20}" />

  <g clip-path="url(#carousel-clip)">
    {carousel_stars_svg}
    <g class="shooting-star-1">
      <line x1="45" y1="-33" x2="0" y2="0" stroke="url(#star-trail-1)" stroke-width="1.3" stroke-linecap="round" />
      <circle cx="0" cy="0" r="1.5" fill="#ffffff" />
    </g>
    <g class="shooting-star-2">
      <line x1="45" y1="-33" x2="0" y2="0" stroke="url(#star-trail-1)" stroke-width="1.1" stroke-linecap="round" />
      <circle cx="0" cy="0" r="1.3" fill="#ffffff" />
    </g>
  </g>

  <g transform="translate(42, 34)">
    <text class="section-label" x="0" y="0">✦ FEATURED PROJECTS</text>
    <g transform="translate(670, -6)">
      <circle class="dot-1" cx="0" cy="0" r="4.5" fill="#585b70" />
      <circle class="dot-2" cx="14" cy="0" r="4.5" fill="#585b70" />
      <circle class="dot-3" cx="28" cy="0" r="4.5" fill="#585b70" />
      <circle class="dot-4" cx="42" cy="0" r="4.5" fill="#585b70" />
    </g>
  </g>

  <g transform="translate(42, 58)" clip-path="url(#viewport-clip)">
    <g class="carousel-track">
      {project_cards_svg}
    </g>
  </g>
</svg>
"""

with open("projects_carousel.svg", "w", encoding="utf-8") as f:
    f.write(carousel_svg_content)

print(f"[+] File 'projects_carousel.svg' generato con successo!")

# ==========================================
# 3. GENERAZIONE contribution_heatmap.svg (MATHEMATICALLY PERFECT SPACE INVADERS SYNCHRONIZATION)
# ==========================================
print("[*] Avvio orchestrazione dinamica della Heatmap & Space Defender...")

heatmap_height = 275
today = datetime.date.today()

weeks_count = 52
heatmap_squares_svg = ""

catppuccin_levels = {
    0: {"fill": "#1e1e2e", "stroke": "#313244"},
    1: {"fill": "#45475a", "stroke": "#585b70"},
    2: {"fill": "#74c7ec", "stroke": "#89b4fa"},
    3: {"fill": "#cba6f7", "stroke": "#f5c2e7"},
    4: {"fill": "#a6e3a1", "stroke": "#94e2d5"}
}

calendar_data = data.get("contributions_calendar")
daily_events = data.get("daily_events", {})

real_daily_map = {}
total_contributions_cnt = 0

# Costruiamo la lista ordinata delle settimane restituite da GitHub se disponibili
github_weeks = []
if calendar_data:
    total_contributions_cnt = calendar_data.get("totalContributions", 0)
    github_weeks = calendar_data.get("weeks", [])
    for week in github_weeks:
        for day_info in week.get("contributionDays", []):
            d_str = day_info.get("date")
            c_cnt = day_info.get("contributionCount", 0)
            real_daily_map[d_str] = c_cnt
else:
    total_contributions_cnt = sum(daily_events.values())
    real_daily_map = daily_events

# Costruzione griglia Heatmap INGRANDITA (52 settimane x 7 giorni, step 13.8px, celle 11.5x11.5px)
step_x = 13.8
step_y = 13.8

if github_weeks and len(github_weeks) >= 52:
    weeks_to_render = github_weeks[-52:]
    for w, week_info in enumerate(weeks_to_render):
        col_x = w * step_x
        days_in_week = week_info.get("contributionDays", [])
        for d, day_info in enumerate(days_in_week):
            if d >= 7:
                break
            events_cnt = day_info.get("contributionCount", 0)
            
            if events_cnt == 0:
                level = 0
            elif events_cnt <= 2:
                level = 1
            elif events_cnt <= 4:
                level = 2
            elif events_cnt <= 7:
                level = 3
            else:
                level = 4
                
            row_y = d * step_y
            style_info = catppuccin_levels[level]
            fill_color = style_info["fill"]
            stroke_color = style_info["stroke"]
            glow_attr = ' filter="url(#glow-dot)"' if level >= 3 else ''
            
            cell_class = f'cell-w{w}-d{d}'
            heatmap_squares_svg += f'<rect x="{col_x:.1f}" y="{row_y:.1f}" width="11.5" height="11.5" rx="3.0" fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.9"{glow_attr} class="{cell_class}" />\n      '
else:
    for w in range(weeks_count):
        col_x = w * step_x
        for d in range(7):
            day_offset = (weeks_count - 1 - w) * 7 + (6 - d)
            date_obj = today - datetime.timedelta(days=day_offset)
            date_str = date_obj.strftime("%Y-%m-%d")
            
            events_cnt = real_daily_map.get(date_str, 0)
            if events_cnt == 0:
                level = 0
            elif events_cnt <= 2:
                level = 1
            elif events_cnt <= 4:
                level = 2
            elif events_cnt <= 7:
                level = 3
            else:
                level = 4
            
            row_y = d * step_y
            style_info = catppuccin_levels[level]
            fill_color = style_info["fill"]
            stroke_color = style_info["stroke"]
            glow_attr = ' filter="url(#glow-dot)"' if level >= 3 else ''
            
            cell_class = f'cell-w{w}-d{d}'
            heatmap_squares_svg += f'<rect x="{col_x:.1f}" y="{row_y:.1f}" width="11.5" height="11.5" rx="3.0" fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.9"{glow_attr} class="{cell_class}" />\n      '

# --- CALCOLO POSIZIONAMENTO REALE DEI MESI NELLE 52 SETTIMANE ---
months_labels_svg = ""
prev_month = None

if github_weeks and len(github_weeks) >= 52:
    weeks_to_render = github_weeks[-52:]
    for w, week_info in enumerate(weeks_to_render):
        days_in_week = week_info.get("contributionDays", [])
        if days_in_week:
            first_day_date = days_in_week[0].get("date")
            if first_day_date:
                month_num = int(first_day_date.split("-")[1])
                month_name = datetime.date(2020, month_num, 1).strftime("%b")
                if month_name != prev_month:
                    col_x = w * step_x
                    months_labels_svg += f'<text class="axis-label" x="{col_x:.1f}" y="0">{month_name}</text>\n    '
                    prev_month = month_name
else:
    for w in range(weeks_count):
        day_offset = (weeks_count - 1 - w) * 7 + 6
        date_obj = today - datetime.timedelta(days=day_offset)
        month_name = date_obj.strftime("%b")
        if month_name != prev_month:
            col_x = w * step_x
            months_labels_svg += f'<text class="axis-label" x="{col_x:.1f}" y="0">{month_name}</text>\n    '
            prev_month = month_name

random.seed(2026)
heatmap_stars_svg = ""
for s in range(30):
    sx = random.randint(20, 770)
    sy = random.randint(20, heatmap_height - 30)
    sr = round(random.uniform(0.8, 2.0), 1)
    duration = round(random.uniform(2.5, 4.5), 1)
    delay = round(random.uniform(0.0, 3.0), 1)
    heatmap_stars_svg += f'<circle class="star" cx="{sx}" cy="{sy}" r="{sr}" fill="#cdd6f4" style="--duration: {duration}s; --delay: {delay}s;" />\n    '

# Bersagli per la pattuglia di ANDATA (10 celle colpite a raffica veloce)
shots_forward = [
    {"w": 2,  "d": 5},
    {"w": 7,  "d": 2},
    {"w": 12, "d": 6},
    {"w": 17, "d": 1},
    {"w": 22, "d": 4},
    {"w": 27, "d": 0},
    {"w": 32, "d": 3},
    {"w": 37, "d": 6},
    {"w": 42, "d": 2},
    {"w": 47, "d": 5}
]

# Bersagli per la pattuglia di RITORNO (10 celle colpite a raffica veloce)
shots_return = [
    {"w": 49, "d": 3},
    {"w": 44, "d": 1},
    {"w": 39, "d": 5},
    {"w": 34, "d": 0},
    {"w": 29, "d": 4},
    {"w": 24, "d": 2},
    {"w": 19, "d": 6},
    {"w": 14, "d": 1},
    {"w": 9,  "d": 4},
    {"w": 4,  "d": 3}
]

total_anim_time = 24.0
num_cols = 52

laser_keyframes = ["0% { transform: translateY(0px); opacity: 0; }"]
cell_css_rules = []

# Processa spari di andata (navicella ancorata a Y=205px, celle a Y=62px + d*13.8px)
# Altezza di volo dal muso Y=205: travel_y = (62 + d*13.8) - 205 = -143 + d*13.8
for shot in shots_forward:
    w = shot["w"]
    d = shot["d"]
    
    t_hit = (w / float(num_cols - 1)) * 50.0
    travel_y = -143.0 + (d * 13.8)

    t_start = max(0.0, t_hit - 0.7)
    t_end = t_hit
    t_hide = t_hit + 0.01

    laser_keyframes.append(f"{t_start - 0.01:.2f}% {{ transform: translateY(0px); opacity: 0; }}")
    laser_keyframes.append(f"{t_start:.2f}% {{ transform: translateY(0px); opacity: 1; }}")
    laser_keyframes.append(f"{t_end:.2f}% {{ transform: translateY({travel_y:.1f}px); opacity: 1; }}")
    laser_keyframes.append(f"{t_hide:.2f}% {{ transform: translateY({travel_y:.1f}px); opacity: 0; }}")
    laser_keyframes.append(f"{t_hide + 0.01:.2f}% {{ transform: translateY(0px); opacity: 0; }}")

    cell_css = f"""
    @keyframes cellErase_w{w}_d{d} {{
      0%, {t_hit - 0.1:.2f}% {{ opacity: 1; transform: scale(1); }}
      {t_hit:.2f}% {{ opacity: 1; transform: scale(2.2); fill: #ffffff; stroke: #f38ba8; filter: drop-shadow(0 0 10px #f5c2e7); }}
      {t_hit + 0.4:.2f}% {{ opacity: 0; transform: scale(0); }}
      98% {{ opacity: 0; transform: scale(0); }}
      99.5%, 100% {{ opacity: 1; transform: scale(1); }}
    }}
    .cell-w{w}-d{d} {{
      animation: cellErase_w{w}_d{d} {total_anim_time}s linear infinite;
      transform-box: fill-box;
      transform-origin: center;
    }}
    """
    cell_css_rules.append(cell_css)

# Processa spari di ritorno
for shot in shots_return:
    w = shot["w"]
    d = shot["d"]
    
    t_hit = 50.0 + ((num_cols - 1 - w) / float(num_cols - 1)) * 50.0
    travel_y = -143.0 + (d * 13.8)

    t_start = max(50.0, t_hit - 0.7)
    t_end = t_hit
    t_hide = t_hit + 0.01

    laser_keyframes.append(f"{t_start - 0.01:.2f}% {{ transform: translateY(0px); opacity: 0; }}")
    laser_keyframes.append(f"{t_start:.2f}% {{ transform: translateY(0px); opacity: 1; }}")
    laser_keyframes.append(f"{t_end:.2f}% {{ transform: translateY({travel_y:.1f}px); opacity: 1; }}")
    laser_keyframes.append(f"{t_hide:.2f}% {{ transform: translateY({travel_y:.1f}px); opacity: 0; }}")
    laser_keyframes.append(f"{t_hide + 0.01:.2f}% {{ transform: translateY(0px); opacity: 0; }}")

    cell_css = f"""
    @keyframes cellErase_w{w}_d{d} {{
      0%, {t_hit - 0.1:.2f}% {{ opacity: 1; transform: scale(1); }}
      {t_hit:.2f}% {{ opacity: 1; transform: scale(2.2); fill: #ffffff; stroke: #f38ba8; filter: drop-shadow(0 0 10px #f5c2e7); }}
      {t_hit + 0.4:.2f}% {{ opacity: 0; transform: scale(0); }}
      98% {{ opacity: 0; transform: scale(0); }}
      99.5%, 100% {{ opacity: 1; transform: scale(1); }}
    }}
    .cell-w{w}-d{d} {{
      animation: cellErase_w{w}_d{d} {total_anim_time}s linear infinite;
      transform-box: fill-box;
      transform-origin: center;
    }}
    """
    cell_css_rules.append(cell_css)

laser_keyframes.append("100% { transform: translateY(0px); opacity: 0; }")

laser_css = f"""
@keyframes laserShotSync {{
  {"\n  ".join(laser_keyframes)}
}}
.synced-laser-bolt {{
  animation: laserShotSync {total_anim_time}s linear infinite;
  filter: url(#laser-glow);
  transform-box: fill-box;
  transform-origin: bottom center;
}}
"""

all_cell_animations_css = laser_css + "\n" + "\n".join(cell_css_rules)

heatmap_svg_content = f"""<svg width="800" height="{heatmap_height}" viewBox="0 0 800 {heatmap_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;family=Orbitron:wght@600;800&amp;display=swap');
    </style>

    <clipPath id="heatmap-clip">
      <rect x="10" y="10" width="780" height="{heatmap_height - 20}" rx="20" />
    </clipPath>

    <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#cba6f7" />
      <stop offset="40%" stop-color="#f5c2e7" />
      <stop offset="75%" stop-color="#fab387" />
      <stop offset="100%" stop-color="#74c7ec" />
    </linearGradient>

    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f0f17" />
      <stop offset="45%" stop-color="#181825" />
      <stop offset="80%" stop-color="#1e1e2e" />
      <stop offset="100%" stop-color="#282338" />
    </linearGradient>

    <linearGradient id="laser-grad" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" stop-color="#a6e3a1" stop-opacity="1" />
      <stop offset="50%" stop-color="#74c7ec" stop-opacity="1" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="1" />
    </linearGradient>

    <filter id="glow-dot" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="1.8" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="laser-glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="3.0" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <style>
    .card-bg {{
      fill: url(#bg-grad);
      stroke: url(#border-grad);
      stroke-width: 1.75;
      rx: 20px;
    }}
    .section-label {{
      font-family: 'Orbitron', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      fill: #f5e0dc;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 2px;
      opacity: 0.9;
    }}
    .legend-text {{
      font-family: 'Inter', sans-serif;
      fill: #a6adc8;
      font-size: 10px;
      font-weight: 600;
    }}
    .axis-label {{
      font-family: 'Inter', sans-serif;
      fill: #6c7086;
      font-size: 10px;
      font-weight: 600;
    }}

    @keyframes twinkle {{
      0%, 100% {{ opacity: 0.12; transform: scale(0.8); }}
      50% {{ opacity: 0.95; transform: scale(1.3); }}
    }}
    .star {{
      animation: twinkle var(--duration, 3s) infinite ease-in-out var(--delay, 0s);
      transform-box: fill-box;
      transform-origin: center;
    }}

    /* PATTUGLIA NAVICELLA IN SCORRIMENTO ORIZZONTALE SUL FONDO (24 SECONDI) */
    @keyframes defenderPatrolHorizontal {{
      0% {{ transform: translateX(50px); }}
      49% {{ transform: translateX(730px); }}
      50% {{ transform: translateX(730px); }}
      99% {{ transform: translateX(50px); }}
      100% {{ transform: translateX(50px); }}
    }}
    .defender-ship-patrol {{
      animation: defenderPatrolHorizontal {total_anim_time}s linear infinite;
    }}

    {all_cell_animations_css}

    @keyframes flamePulse {{
      0%, 100% {{ transform: scaleY(1); opacity: 0.85; }}
      50% {{ transform: scaleY(1.6); opacity: 1; }}
    }}
    .thruster-flame {{
      animation: flamePulse 0.2s infinite alternate ease-in-out;
      transform-origin: top center;
    }}
  </style>

  <rect class="card-bg" x="10" y="10" width="780" height="{heatmap_height - 20}" />

  <g clip-path="url(#heatmap-clip)">
    {heatmap_stars_svg}
  </g>

  <!-- HEADER HEATMAP -->
  <g transform="translate(42, 30)">
    <text class="section-label" x="0" y="0">✦ CONTRIBUTIONS</text>
    
    <g transform="translate(540, -8)">
      <text class="legend-text" x="0" y="9">Less</text>
      <rect x="32" y="0" width="10" height="10" rx="2.5" fill="#1e1e2e" stroke="#313244" />
      <rect x="46" y="0" width="10" height="10" rx="2.5" fill="#45475a" stroke="#585b70" />
      <rect x="60" y="0" width="10" height="10" rx="2.5" fill="#74c7ec" stroke="#89b4fa" />
      <rect x="74" y="0" width="10" height="10" rx="2.5" fill="#cba6f7" stroke="#f5c2e7" filter="url(#glow-dot)" />
      <rect x="88" y="0" width="10" height="10" rx="2.5" fill="#a6e3a1" stroke="#94e2d5" filter="url(#glow-dot)" />
      <text class="legend-text" x="104" y="9">More</text>
    </g>
  </g>

  <!-- ETICHETTE MESI -->
  <g transform="translate(50, 48)">
    {months_labels_svg}
  </g>

  <!-- ETICHETTE GIORNI (Mon, Wed, Fri) -->
  <g transform="translate(20, 75)">
    <text class="axis-label" x="0" y="0">Mon</text>
    <text class="axis-label" x="0" y="27.6">Wed</text>
    <text class="axis-label" x="0" y="55.2">Fri</text>
  </g>

  <!-- MATRICE HEATMAP REALE (52 SETTIMANE x 7 GIORNI) -->
  <g transform="translate(50, 62)">
    {heatmap_squares_svg}
  </g>

  <!-- LINEA SEPARATRICE COSMICA COMPATTA -->
  <line x1="42" y1="175" x2="758" y2="175" stroke="#313244" stroke-width="1.2" stroke-dasharray="4,4" opacity="0.6" />

  <!-- CONTAINER NAVICELLA COMPATTO ANCORATO IN BASSO A Y=205px -->
  <g transform="translate(0, 205)">
    <g class="defender-ship-patrol">
      
      <!-- PROIETTILE LASER ALLINEATO CON LA CANNA DELLA NAVICELLA -->
      <g class="synced-laser-bolt" transform="translate(28, 0)">
        <line x1="0" y1="0" x2="0" y2="18" stroke="url(#laser-grad)" stroke-width="3.5" stroke-linecap="round" />
        <circle cx="0" cy="-2" r="2.5" fill="#ffffff" filter="url(#glow-dot)" />
      </g>

      <!-- PROPULSORE DEL MOTORE -->
      <g transform="translate(24, 30)">
        <polygon points="0,0 8,0 4,14" fill="#fab387" class="thruster-flame" />
        <polygon points="2,0 6,0 4,9" fill="#f9e2af" />
      </g>

      <!-- DESIGN STARFIGHTER DEFENDER -->
      <g transform="translate(0, 0)">
        <path d="M 28 0 L 34 10 L 52 22 L 56 28 L 44 28 L 38 23 L 28 18 L 18 23 L 12 28 L 0 28 L 4 22 L 22 10 Z" fill="#181825" stroke="#cba6f7" stroke-width="1.75" filter="url(#glow-dot)" />
        <rect x="4" y="2" width="4" height="12" rx="2" fill="#89b4fa" />
        <rect x="48" y="2" width="4" height="12" rx="2" fill="#89b4fa" />
        <path d="M 28 4 L 38 16 L 18 16 Z" fill="#89b4fa" opacity="0.85" />
        <ellipse cx="28" cy="10" rx="4.5" ry="5.5" fill="#f5c2e7" filter="url(#glow-dot)" />
        <rect x="20" y="24" width="16" height="4" rx="2" fill="#a6e3a1" />
      </g>
    </g>
  </g>
</svg>
"""

with open("contribution_heatmap.svg", "w", encoding="utf-8") as f:
    f.write(heatmap_svg_content)

print(f"[+] File 'contribution_heatmap.svg' generato con successo! Altezza totale: {heatmap_height}px")

# ==========================================
# GENERAZIONE CARD WALL-E SPAZIALE (walle_card.svg)
# ==========================================
print(f"[*] Avvio orchestrazione della Card WALL-E Spaziale...")

walle_gif_path = "walle.gif"
if os.path.exists(walle_gif_path):
    import base64
    with open(walle_gif_path, "rb") as gif_file:
        walle_b64 = base64.b64encode(gif_file.read()).decode("utf-8")
    walle_img_href = f"data:image/gif;base64,{walle_b64}"
else:
    print(f"[!] Warning: {walle_gif_path} non trovato!")
    walle_img_href = ""

# Generazione stelle casuali per lo sfondo di WALL-E
walle_stars = []
for _ in range(35):
    sx = random.randint(20, 780)
    sy = random.randint(20, 260)
    r = random.uniform(0.6, 1.8)
    dur = round(random.uniform(1.8, 4.0), 2)
    delay = round(random.uniform(0, 3.0), 2)
    color = random.choice(["#89b4fa", "#cba6f7", "#b4befe", "#f5c2e7", "#ffffff"])
    walle_stars.append(f'<circle class="star" cx="{sx}" cy="{sy}" r="{r:.2f}" fill="{color}" style="--duration: {dur}s; --delay: {delay}s;" />')

walle_stars_svg = "\n    ".join(walle_stars)

walle_card_svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 800 280" width="100%" height="280">
  <defs>
    <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#cba6f7" />
      <stop offset="40%" stop-color="#f5c2e7" />
      <stop offset="75%" stop-color="#fab387" />
      <stop offset="100%" stop-color="#74c7ec" />
    </linearGradient>

    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&amp;display=swap');
      
      .card-bg {{
        fill: #11111b;
        stroke: url(#border-grad);
        stroke-width: 1.75;
        rx: 16px;
      }}
      .badge-title {{
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        font-weight: 800;
        fill: #cba6f7;
        letter-spacing: 1.5px;
      }}
      .badge-subtitle {{
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        font-weight: 500;
        fill: #a6adc8;
      }}
      .quote-text {{
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-style: italic;
        font-weight: 600;
        fill: #89b4fa;
      }}
      .hud-line {{
        stroke: #cba6f7;
        stroke-width: 1.5;
        opacity: 0.6;
      }}
      .hud-accent {{
        fill: #f5c2e7;
      }}
      @keyframes twinkle {{
        0%, 100% {{ opacity: 0.15; transform: scale(0.8); }}
        50% {{ opacity: 0.95; transform: scale(1.3); }}
      }}
      .star {{
        animation: twinkle var(--duration, 3s) infinite ease-in-out var(--delay, 0s);
        transform-box: fill-box;
        transform-origin: center;
      }}
      @keyframes orbitScan {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
      }}
      .orbit-ring {{
        animation: orbitScan 20s linear infinite;
        transform-origin: 155px 140px;
      }}
      @keyframes floatAnim {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-5px); }}
      }}
      .floating-group {{
        animation: floatAnim 4s ease-in-out infinite;
      }}
    </style>

    <!-- Filtri Glow per stile cosmico -->
    <filter id="glow-purple" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
    <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>

    <!-- Gradienti per HUD -->
    <linearGradient id="hud-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#cba6f7" stop-opacity="0.8" />
      <stop offset="50%" stop-color="#89b4fa" stop-opacity="0.5" />
      <stop offset="100%" stop-color="#f5c2e7" stop-opacity="0.8" />
    </linearGradient>

    <!-- Porthole / Oblò Clip Path (cerchio perfetto per inquadrare WALL-E) -->
    <clipPath id="porthole-clip">
      <circle cx="155" cy="140" r="92" />
    </clipPath>
    <clipPath id="card-clip">
      <rect x="10" y="10" width="780" height="260" rx="16" />
    </clipPath>
  </defs>

  <!-- BACKGROUND CARD CON STELLE -->
  <rect class="card-bg" x="10" y="10" width="780" height="260" />
  
  <g clip-path="url(#card-clip)">
    {walle_stars_svg}
  </g>

  <!-- SEZIONE OBLÒ WALL-E (SINISTRA) -->
  <g class="floating-group">
    <!-- Neon Outer Ring -->
    <circle cx="155" cy="140" r="102" fill="none" stroke="url(#hud-grad)" stroke-width="2" filter="url(#glow-purple)" opacity="0.7" />
    <circle cx="155" cy="140" r="98" fill="#181825" stroke="#313244" stroke-width="3" />
    
    <!-- Anello di Scansione Orbital (Tratteggiato) -->
    <circle class="orbit-ring" cx="155" cy="140" r="96" fill="none" stroke="#89b4fa" stroke-width="1.5" stroke-dasharray="8, 25, 4, 15" opacity="0.8" />

    <!-- IMMAGINE GIF DI WALL-E CLIPPPATA NELL'OBLÒ -->
    <g clip-path="url(#porthole-clip)">
      <!-- Sfondo interno dell'oblò -->
      <rect x="50" y="35" width="210" height="210" fill="#0d0e15" />
      <!-- WALL-E GIF -->
      <image href="{walle_img_href}" x="40" y="25" width="230" height="230" preserveAspectRatio="xMidYMid slice" />
    </g>

    <!-- Cornice Interna Vetrata Oblò HUD -->
    <circle cx="155" cy="140" r="92" fill="none" stroke="#cba6f7" stroke-width="2.5" opacity="0.85" filter="url(#glow-cyan)" />

    <!-- Dettagli Tattici HUD attorno all'oblò -->
    <!-- Tacche agli angoli -->
    <line x1="155" y1="36" x2="155" y2="44" stroke="#f5c2e7" stroke-width="2" />
    <line x1="155" y1="236" x2="155" y2="244" stroke="#f5c2e7" stroke-width="2" />
    <line x1="51" y1="140" x2="59" y2="140" stroke="#f5c2e7" stroke-width="2" />
    <line x1="251" y1="140" x2="259" y2="140" stroke="#f5c2e7" stroke-width="2" />

    <!-- Etichetta HUD vicino all'oblò -->
    <rect x="110" y="234" width="90" height="18" rx="4" fill="#181825" stroke="#cba6f7" stroke-width="1" />
    <text x="155" y="246" text-anchor="middle" font-family="'Inter', sans-serif" font-size="9.5" font-weight="700" fill="#a6e3a1" letter-spacing="1">WALL-E // 01</text>
  </g>

  <!-- SEZIONE TESTO / PANNELLO DI BORDO (DESTRA) -->
  <g transform="translate(290, 45)">
    <!-- Header Badge -->
    <text class="badge-title" x="0" y="15">✦ WALL•E // CODE COMPANION</text>
    <text class="badge-subtitle" x="0" y="38">Solar-Powered Bug Compactor • 700 Years of Refactoring</text>

    <!-- Separatore HUD -->
    <line x1="0" y1="52" x2="460" y2="52" stroke="#313244" stroke-width="1.5" stroke-dasharray="6,4" />

    <!-- Citazione / Messaggio -->
    <text class="quote-text" x="0" y="82">"Pressing [Ctrl+S]... *happy robot noises* 🤖📦"</text>
    
    <!-- Descrizione / Status Box -->
    <rect x="0" y="102" width="460" height="72" rx="10" fill="#181825" stroke="#313244" stroke-width="1.2" />
    
    <!-- Dettagli Status HUD -->
    <g transform="translate(18, 124)">
      <!-- Indicatore di stato verde -->
      <circle cx="6" cy="6" r="4" fill="#a6e3a1" filter="url(#glow-cyan)" />
      <text font-family="'Inter', sans-serif" font-size="11" font-weight="700" fill="#cdd6f4" x="20" y="10">DIRECTIVE:</text>
      <text font-family="'Inter', sans-serif" font-size="11" font-weight="500" fill="#a6e3a1" x="96" y="10">COMPACT BUGS &amp; COLLECT CODE</text>

      <circle cx="6" cy="30" r="4" fill="#89b4fa" />
      <text font-family="'Inter', sans-serif" font-size="11" font-weight="700" fill="#cdd6f4" x="20" y="34">BATTERY:</text>
      <text font-family="'Inter', sans-serif" font-size="11" font-weight="500" fill="#89b4fa" x="88" y="34">CHARGING VIA SOLAR PANELS &amp; TEA 🍵</text>
    </g>
  </g>
</svg>
"""

with open("walle_card.svg", "w", encoding="utf-8") as f:
    f.write(walle_card_svg_content)

print(f"[+] File 'walle_card.svg' generato con successo!")