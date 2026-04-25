import cloudscraper
from bs4 import BeautifulSoup
import re
import os
import time
import io
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, "images")
TEX_FILE = os.path.join(SCRIPT_DIR, "san.tex")

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def clean_for_latex(text):
    if not text: return ""
    
    junk = [
        r"View Answer", r"Sanfoundry Global Education.*", r"To practice all areas.*",
        r"here is complete set.*", r"For weekly automata theory.*", r"Sanfoundry’s official.*",
        r"Next -.*", r"🔥.*", r"⚡.*", r"advertisement", r"Enroll for Free.*", r"Free Data Structure.*",
        r"🎓.*", r"👉.*", "📌.*"
    ]
    for pattern in junk:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

    replacements = {
        '\\': r'\textbackslash ', '&': r'\&', '%': r'\%', '$': r'\$', '{': r'\{', '}': r'\}',
        '_': r'\_', '#': r'\#', 'ϵ': r'$\epsilon$', '∑': r'$\Sigma$', 'Σ': r'$\Sigma$',
        'δ': r'$\delta$', 'ε': r'$\epsilon$', 'Φ': r'$\Phi$', 'Γ': r'$\Gamma$',
        '>': r'$>$', '<': r'$<$', '≠': r'$\neq$', '∈': r'$\in$', '∩': r'$\cap$',
        '∆': r'$\Delta$', 'Δ': r'$\Delta$', '₵': r'\textcent ', '’': "'", '“': '"', '”': '"',
        '≥': r'$\geq$',
        '^': r'\textasciicircum{}',
        'Φ': r'$\Phi$', 'Ф': r'$\Phi$', 'λ': r'$\Lambda$', '∗': r'$\ast$', '′': r'$^\prime$', 'γ': r'$\gamma$', 'Ε': r'E', '∈': r'$\in$', '∉': r'$\notin$', 'Ґ': r'$\Gamma$'
    }
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    
    return text.strip()

def download_image(img_url, scraper, page_url):
    try:
        if not img_url or "sanfoundry.com" not in img_url: return None
        filename = re.sub(r'[^\w\-_.]', '_', img_url.split('/')[-1])
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')): filename += ".png"
        local_path = os.path.join(IMG_DIR, filename)
        
        if not os.path.exists(local_path):
            r = scraper.get(img_url, headers={'Referer': page_url})
            if r.status_code == 200:
                try:
                    img_data = io.BytesIO(r.content)
                    with Image.open(img_data) as img:
                        img.convert("RGB").save(local_path, "PNG")
                except:
                    with open(local_path, 'wb') as f: f.write(r.content)
        return filename
    except: return None

def process_page(url, scraper, topic_title):
    res = scraper.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    entry = soup.find('div', class_='entry-content')
    if not entry: return ""

    for ns in entry.find_all('noscript'): ns.decompose()

    for img in entry.find_all('img'):
        img_url = img.get('data-src') or img.get('src')
        if img_url:
            fname = download_image(img_url, scraper, url)
            if fname: img.replace_with(f" IMGTAG{fname}IMGTAG ")

    full_text = entry.get_text(separator="\n")
    
    safe_title = clean_for_latex(topic_title)
    
    parts = re.split(r'\n(\d+)\.', "\n" + full_text)
    output = f"\\newtopic{{{safe_title}}}\n\n"

    for i in range(1, len(parts), 2):
        q_num = parts[i]
        q_body = parts[i+1]
        
        ans_match = re.search(r'(Answer:.*)', q_body, re.DOTALL | re.IGNORECASE)
        raw_q = q_body[:ans_match.start()] if ans_match else q_body
        raw_ans = ans_match.group(1) if ans_match else "Answer not found."

        q_clean = clean_for_latex(raw_q)
        ans_clean = clean_for_latex(raw_ans)

        def make_img(match):
            return f"\n\\begin{{center}}\\includegraphics[width=0.5\\textwidth]{{{match.group(1)}}}\\end{{center}}\n"

        q_final = re.sub(r'IMGTAG(.*?)IMGTAG', make_img, q_clean)
        ans_final = re.sub(r'IMGTAG(.*?)IMGTAG', make_img, ans_clean)

        if q_final.strip():
            output += r"\begin{mdframed}[linewidth=1pt, roundcorner=5pt, linecolor=gray!30, backgroundcolor=gray!5]" + "\n"
            output += f"\\textbf{{Question {q_num}}} \n\n"
            output += q_final.strip() + "\n"
            output += r"\vspace{5pt} \par" + "\n"
            output += r"\begin{tcolorbox}[colback=green!5, colframe=green!40!black, title=Solution]" + "\n"
            output += ans_final.strip() + "\n"
            output += r"\end{tcolorbox}" + "\n"
            output += r"\end{mdframed}" + "\n"
            output += r"\newpage" + "\n\n"
    return output

def run():
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','desktop': True})
    
    my_topics = [
        # Done "Finite Automata – Basics", "Deterministic Finite Automata-Introduction and Definition",
        # Done "DFA Processing Strings", "Simpler Notations", "The Language of DFA",
        # Done "Finite Automata", "Non Deterministic Finite Automata-Introduction",
        # Done ""The Language of NFA", "Equivalence of NFA and DFA", 
        # Done "Applications of DFA", "Union, Intersection & Complement",
        # Done "Regular Expression – Introduction", "Operators of Regular Expression",
        # Done "Building Regular Expressions", "DFA to Regular Expressions",
        # Done "Conversion by Eliminating states", "Regular Language & Expression – 1",
        # Done "Regular Language & Expression – 2", "Converting Regular Expressions to Automata",
        # Done "Finding Patterns in Text, Algebric Laws and Derivatives",
        # Done "Pumping Lemma for Regular Language", "Applications of Pumping Lemma", "Closure Properties under Boolean Operations",
        # Done "Context Free Grammar-Derivations and Definitions", "The Language of a Grammar, Inferences and Ambiguity", 
        # "Sentential Forms", "Construction and Yield of a Parse Tree", "Inferences to Trees and Trees to Derivations", "Ambiguous Grammar",
        # Done "PDA-Acceptance by Final State", "PDA-Acceptance by Empty Stack", "From Grammars to Push Down Automata", "From PDA to Grammars",
        # Done "CFG-Eliminating Useless Symbols", "Eliminating Epsilon Productions", "Eliminating Unit Productions",
        # Done "Chomsky Normal Form", "Pumping Lemma for Context Free Language",
        # Done "CFL- Closure Properties", "Intersection with Regular Languages",
        # Done "Turing Machine – Notation and Transition Diagrams", "The Language of Turing Machine-1",
        # Done "The Language of Turing Machine-2", "Turing Machine and Halting"
    ]
    
    print("Fetching index...")
    res = scraper.get("https://www.sanfoundry.com/1000-automata-theory-questions-answers/")
    soup = BeautifulSoup(res.text, 'html.parser')
    
    final_latex = ""
    processed = 0
    content_div = soup.find('div', class_='entry-content')
    
    for a in content_div.find_all('a'):
        raw_web_title = a.get_text().replace('\xa0', ' ').strip()
        compare_web = raw_web_title.replace('–', '-').replace('—', '-')
        href = a.get('href')

        if not href or href.startswith('#'): continue

        for topic in my_topics:
            compare_target = topic.replace('–', '-').replace('—', '-')
            if "sanfoundry.com" in href and compare_web == compare_target:
                print(f"Scraping: {raw_web_title}")
                content = process_page(href, scraper, raw_web_title)
                if content:
                    final_latex += content
                    processed += 1
                time.sleep(1)
                break

    if os.path.exists(TEX_FILE):
        with open(TEX_FILE, "r", encoding="utf-8") as f:
            template = f.read()
        if "% INSERT_CONTENT_HERE" in template:
            with open(TEX_FILE, "w", encoding="utf-8") as f:
                f.write(template.replace("% INSERT_CONTENT_HERE", final_latex))
            print(f"\nSUCCESS: {processed} topics written to san.tex!")

if __name__ == "__main__":
    run()