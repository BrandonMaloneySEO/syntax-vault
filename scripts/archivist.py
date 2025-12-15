import os
import sys

# Flush output immediately
sys.stdout.reconfigure(line_buffering=True)

print("--- ARCHIVIST: HIGH FIDELITY PROTOCOL ---")

MARKER_START = ""
MARKER_END = ""
EXCLUDE_DIRS = {'.git', '.github', 'scripts', 'css', 'img', 'node_modules', '_site'}
EXCLUDE_FILES = {'index.html', '404.html', 'CNAME', 'README.md', 'LICENSE'}

# --- THE VISUAL IDENTITY (The "Good Looking" Template) ---
CSS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Standard Syntax | {dir_name} Vault</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{ --bg-color: #f0f0f0; --card-bg: #ffffff; --text-main: #111111; --text-muted: #666666; --folder-color: #005f87; --font-stack: 'Space Grotesk', sans-serif; }}
        * {{ box-sizing: border-box; }}
        body {{ font-family: var(--font-stack); background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 40px 20px; min-height: 100vh; display: flex; justify-content: center; }}
        .vault-container {{ max-width: 800px; width: 100%; }}
        .terminal-header {{ background: var(--text-main); color: #fff; padding: 20px; border-radius: 4px 4px 0 0; display: flex; justify-content: space-between; align-items: center; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }}
        .status-light {{ height: 8px; width: 8px; background-color: #00ff41; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 5px #00ff41; }}
        .index-card {{ background: var(--card-bg); border: 1px solid #ddd; border-top: none; border-radius: 0 0 4px 4px; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }}
        h1 {{ font-size: 32px; margin: 0 0 10px 0; letter-spacing: -1px; font-weight: 700; }}
        .subtitle {{ color: var(--text-muted); margin-bottom: 40px; font-size: 16px; line-height: 1.5; border-bottom: 2px solid #000; padding-bottom: 20px; }}
        ul {{ list-style: none; padding: 0; margin: 0; }}
        li {{ margin-bottom: 12px; background: #fff; border: 1px solid #e0e0e0; padding: 15px 20px; border-radius: 4px; transition: all 0.2s ease; display: flex; align-items: center; }}
        li:hover {{ transform: translateX(5px); border-color: #000; box-shadow: 2px 2px 0px rgba(0,0,0,0.1); }}
        a {{ text-decoration: none; color: var(--text-main); font-weight: 500; font-size: 16px; width: 100%; }}
        .badge, .dir-badge {{ font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; padding: 4px 8px; border-radius: 2px; margin-right: 15px; min-width: 80px; text-align: center; display: inline-block; }}
        .badge {{ background: #000; color: #fff; }}
        .dir-badge {{ background: var(--folder-color); color: #fff; }}
        .footer {{ margin-top: 40px; text-align: center; font-size: 12px; color: #999; }}
    </style>
</head>
<body>
    <div class="vault-container">
        <div class="terminal-header"><div><span class="status-light"></span>Vault System</div><div>Sector: {dir_name}</div></div>
        <div class="index-card">
            <h1>{dir_name} Index</h1>
            <div class="subtitle">Verified Data Sector. Double-Geo Anchored.</div>
            <ul id="entity-list">
                {marker_start}
                {content}
                {marker_end}
            </ul>
            <div class="footer">&copy; Standard Syntax Protocol</div>
        </div>
    </div>
</body>
</html>
"""

def get_clean_title(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(2000)
            start = content.find('<title>')
            end = content.find('</title>')
            if start != -1 and end != -1:
                return content[start+7:end].strip().replace('| Standard Syntax Entity Verified', '')
    except: pass
    return os.path.basename(filepath)

def make_link(name, title, is_dir=False):
    if is_dir:
        return f'<li><span class="dir-badge">Collection</span><a href="{name}/index.html">📂 {title} Vault</a></li>'
    return f'<li><span class="badge">Entity</span><a href="{name}">{title}</a></li>'

def scan_and_build(path):
    print(f"📂 Scanning: {path}")
    files = []
    folders = []
    
    # SCANNING
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.name.startswith('.') or entry.name in EXCLUDE_DIRS or entry.name in EXCLUDE_FILES: continue
                if entry.is_file() and entry.name.endswith('.html'):
                    files.append((entry.name, get_clean_title(entry.path)))
                elif entry.is_dir():
                    scan_and_build(entry.path) # Recurse
                    folders.append((entry.name, entry.name.capitalize()))
    except Exception as e:
        print(f"   [!] Error: {e}")
        return

    # SORTING
    files.sort(key=lambda x: x[1])
    folders.sort(key=lambda x: x[1])

    # BUILDING HTML LIST
    html_items = []
    for f_name, f_title in folders:
        html_items.append(make_link(f_name, f_title, is_dir=True))
    for f_name, f_title in files:
        html_items.append(make_link(f_name, f_title))
    
    list_content = "\n                ".join(html_items) or "<li>No verified entities found.</li>"

    # WRITING TO FILE
    target = os.path.join(path, 'index.html')
    
    # 1. CREATE NEW (If missing, use Beautiful Template)
    if not os.path.exists(target):
        if path == '.': return # Should exist for root
        print(f"   + Creating BEAUTIFUL index for {target}")
        dir_name = os.path.basename(path).capitalize()
        new_html = CSS_TEMPLATE.format(dir_name=dir_name, marker_start=MARKER_START, marker_end=MARKER_END, content=list_content)
        with open(target, 'w', encoding='utf-8') as f:
            f.write(new_html)
            
    # 2. UPDATE EXISTING (Inject into markers)
    else:
        try:
            with open(target, 'r', encoding='utf-8') as f:
                content = f.read()
            
            start_idx = content.find(MARKER_START)
            end_idx = content.find(MARKER_END)
            
            if start_idx != -1 and end_idx != -1:
                # Splice safely
                new_full = content[:start_idx + len(MARKER_START)] + "\n                " + list_content + "\n                " + content[end_idx:]
                with open(target, 'w', encoding='utf-8') as f:
                    f.write(new_full)
                print(f"   ✅ Updated {target}")
            else:
                print(f"   ⚠️ MARKERS MISSING in {target}")
        except Exception as e:
            print(f"   [!] Update failed: {e}")

if __name__ == "__main__":
    scan_and_build('.')
    print("--- MISSION COMPLETE ---")
