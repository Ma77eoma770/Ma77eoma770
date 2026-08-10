# generate_badge.py
import requests
import datetime
import os

# USERNAME GITHUB
USERNAME = "Ma77eoma770"

TOKEN = os.getenv("GH_PAT")
print(TOKEN)
HEADERS = {}
if TOKEN:
    HEADERS["Authorization"] = f"token {TOKEN}"

def fetch_github_profile_data(username):
    print(f"[*] Connessione alle API di GitHub per l'utente: {username}...")
    
    user_url = f"https://api.github.com/users/{username}"
    user_resp = requests.get(user_url, headers=HEADERS)
    
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
    repos_resp = requests.get(repos_url, headers=HEADERS)
    
    languages_bytes = {}
    total_stars = 0

    if repos_resp.status_code == 200:
        repos = repos_resp.json()
        print(f"[+] Trovati {len(repos)} repository da analizzare.")
        
        for repo in repos:
            repo_name = repo.get("name")
            is_fork = repo.get("fork")
            stars = repo.get("stargazers_count", 0)
            
            if is_fork:
                print(f"    - Salto il repo '{repo_name}' perché è un fork.")
                continue
                
            total_stars += stars
            print(f"    - Analizzo il repo: '{repo_name}' (Stelle: {stars})")
            
            langs_url = repo.get("languages_url")
            if langs_url:
                langs_resp = requests.get(langs_url, headers=HEADERS)
                if langs_resp.status_code == 200:
                    langs_data = langs_resp.json()
                    for lang, count in langs_data.items():
                        languages_bytes[lang] = languages_bytes.get(lang, 0) + count
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
    for lang, count in sorted_langs[:5]:
        percentage = round((count / total_bytes) * 100)
        print(f"    > {lang}: {count} byte ({percentage}%)")
        top_languages.append({"name": lang, "pct": percentage})

    return {
        "name": name,
        "repos": public_repos_count,
        "followers": followers,
        "stars": total_stars,
        "languages": top_languages
    }

print("--------------------------------------------------")
data = fetch_github_profile_data(USERNAME)
print("--------------------------------------------------")
print("[*] Avvio orchestrazione dinamica dei container SVG...")

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
    "Rust": "#fab387"
}

# --- SISTEMA DINAMICO A CONTAINER ---
# Spaziature e dimensioni ottimizzate per stile Interstellare e Catppuccin
padding_top = 34
about_height = 76          # Spazio occupato dalla sezione About Me (più spazio sotto il nome)
separator_margin = 10      # Spazio ridotto prima e dopo la linea di separazione
skills_header_height = 26  # Spazio per il titolo "LANGUAGE STACK"
row_height = 26            # Altezza riga di ciascun linguaggio
padding_bottom = 32        # Margine inferiore bilanciato

num_langs = len(data["languages"])
skills_list_height = num_langs * row_height

# Posizione Y dinamica della linea di separazione
separator_y = padding_top + about_height + separator_margin

# Posizione Y dinamica del blocco delle skill
skills_start_y = separator_y + separator_margin

# Altezza totale calcolata interamente a monte in modo dinamico
svg_height = skills_start_y + skills_header_height + skills_list_height + padding_bottom


# Generazione dinamica delle righe SVG per i linguaggi con layout a scorrimento
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

# Generazione dinamica delle stelle nello sfondo (Cielo Stellato)
import random
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

svg_content = f"""<svg width="800" height="{svg_height}" viewBox="0 0 800 {svg_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Font Google Interstellar / Futuristic Style -->
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;family=Orbitron:wght@600;800&amp;display=swap');
    </style>

    <clipPath id="card-clip">
      <rect x="10" y="10" width="780" height="{svg_height - 20}" rx="20" />
    </clipPath>

    <!-- Gradiente Bordo Interstellare (Catppuccin Mauve -> Pink -> Peach -> Sapphire) -->
    <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#cba6f7" />
      <stop offset="40%" stop-color="#f5c2e7" />
      <stop offset="75%" stop-color="#fab387" />
      <stop offset="100%" stop-color="#74c7ec" />
    </linearGradient>

    <!-- Gradiente Testo Titolo Interstellare -->
    <linearGradient id="title-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f5c2e7" />
      <stop offset="50%" stop-color="#cba6f7" />
      <stop offset="100%" stop-color="#89b4fa" />
    </linearGradient>

    <!-- Gradiente Separatore cosmico -->
    <linearGradient id="sep-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#313244" stop-opacity="0.1" />
      <stop offset="20%" stop-color="#cba6f7" stop-opacity="0.6" />
      <stop offset="50%" stop-color="#89b4fa" stop-opacity="0.8" />
      <stop offset="80%" stop-color="#cba6f7" stop-opacity="0.6" />
      <stop offset="100%" stop-color="#313244" stop-opacity="0.1" />
    </linearGradient>

    <!-- Gradiente di sfondo Catppuccin Deep Space -->
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f0f17" />
      <stop offset="45%" stop-color="#181825" />
      <stop offset="80%" stop-color="#1e1e2e" />
      <stop offset="100%" stop-color="#282338" />
    </linearGradient>

    <!-- Gradienti per la stella cadente interstellare -->
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

    <!-- Soft Glow Filter per elementi interstellari -->
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

    /* Animazione Stelle Brillanti dello Sfondo */
    @keyframes twinkle {{
      0%, 100% {{ opacity: 0.12; transform: scale(0.8); }}
      50% {{ opacity: 0.95; transform: scale(1.3); }}
    }}
    .star {{
      animation: twinkle var(--duration, 3s) infinite ease-in-out var(--delay, 0s);
      transform-box: fill-box;
      transform-origin: center;
    }}

    /* Animazione Stella Cadente Minimale Rallentata */
    @keyframes shootingStar1 {{
      0% {{
        transform: translate(320px, -30px);
        opacity: 0;
      }}
      10% {{
        opacity: 0.95;
      }}
      55% {{
        transform: translate(820px, 180px);
        opacity: 0;
      }}
      100% {{
        transform: translate(820px, 180px);
        opacity: 0;
      }}
    }}

    @keyframes shootingStar2 {{
      0%, 40% {{
        transform: translate(250px, -40px);
        opacity: 0;
      }}
      50% {{
        opacity: 0.75;
      }}
      85% {{
        transform: translate(750px, 190px);
        opacity: 0;
      }}
      100% {{
        transform: translate(750px, 190px);
        opacity: 0;
      }}
    }}

    .shooting-star-1 {{
      animation: shootingStar1 14s infinite ease-out;
    }}
    .shooting-star-2 {{
      animation: shootingStar2 14s infinite ease-out;
    }}
  </style>

  <!-- Sfondo dimensionato dinamicamente con i margini -->
  <rect class="card-bg" x="10" y="10" width="780" height="{svg_height - 20}" />

  <!-- LIVELLO SFONDO ANIMATO (CIELO STELLATO E STELLE CADENTI MINIMALI PASSA DIETRO IL TESTO) -->
  <g clip-path="url(#card-clip)">
    <!-- Cielo Stellato -->
    {stars_svg}

    <!-- Prima Stella Cadente Minimale -->
    <g class="shooting-star-1">
      <line x1="0" y1="0" x2="65" y2="32" stroke="url(#star-trail-1)" stroke-width="1.3" stroke-linecap="round" />
      <circle cx="65" cy="32" r="1.6" fill="#ffffff" />
    </g>

    <!-- Seconda Stella Cadente Minimale -->
    <g class="shooting-star-2">
      <line x1="0" y1="0" x2="50" y2="25" stroke="url(#star-trail-2)" stroke-width="1.1" stroke-linecap="round" />
      <circle cx="50" cy="25" r="1.3" fill="#ffffff" />
    </g>
  </g>

  <!-- CONTAINER 1: ABOUT ME -->
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

  <!-- LINEA DI SEPARAZIONE COSMICA CON SFUMATURA -->
  <line x1="42" y1="{separator_y}" x2="758" y2="{separator_y}" stroke="url(#sep-grad)" stroke-width="1.5" />

  <!-- CONTAINER 2: LANGUAGE STACK -->
  <g transform="translate(42, {skills_start_y})">
    <text class="section-label" x="0" y="0">✦ LANGUAGE STACK</text>

    <!-- Lista delle skill posizionata in modo fluido sotto il titolo del container -->
    <g transform="translate(0, 18)">
      {languages_svg_rows}
    </g>
  </g>
</svg>
"""

with open("dynamic_card.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"[+] File 'dynamic_card.svg' generato con successo! Altezza dinamica calcolata: {svg_height}px")