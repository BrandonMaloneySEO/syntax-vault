import os
import sys

# Flush output immediately
sys.stdout.reconfigure(line_buffering=True)

print("--- ARCHIVIST: STRING SPLIT PROTOCOL ---")

MARKER_START = ""
MARKER_END = ""
EXCLUDE = {'.git', '.github', 'scripts', 'css', 'img', 'index.html', '404.html', 'CNAME'}

def get_clean_title(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(2000) # Read header only
            start = content.find('<title>')
            end = content.find('</title>')
            if start != -1 and end != -1:
                return content[start+7:end].strip().replace('| Standard Syntax Entity Verified', '')
    except:
        pass
    return os.path.basename(filepath)

def make_link(name, title, is_dir=False):
    if is_dir:
        return f'<li><span class="dir-badge" style="background:#005f87;color:#fff;padding:2px 6px;font-size:10px;text-transform:uppercase;margin-right:10px">Collection</span><a href="{name}/index.html" style="text-decoration:none;color:#111;font-weight:700;display:inline-block">📂 {title} Vault</a></li>'
    return f'<li><span class="badge" style="background:#000;color:#fff;padding:2px 6px;font-size:10px;text-transform:uppercase;margin-right:10px">Entity</span><a href="{name}" style="text-decoration:none;color:#111;font-weight:500;display:inline-block">{title}</a></li>'

def scan_and_build(path):
    print(f"📂 Scanning: {path}")
    files = []
    folders = []
    
    # 1. Gather Data
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.name.startswith('.') or entry.name in EXCLUDE: continue
                
                if entry.is_file() and entry.name.endswith('.html'):
                    files.append((entry.name, get_clean_title(entry.path)))
                elif entry.is_dir():
                    # Recurse immediately
                    scan_and_build(entry.path)
                    folders.append((entry.name, entry.name.capitalize()))
    except Exception as e:
        print(f"   [!] Access Denied: {path} ({e})")
        return

    # 2. Sort
    files.sort(key=lambda x: x[1])
    folders.sort(key=lambda x: x[1])

    # 3. Build HTML
    html_items = []
    for f_name, f_title in folders:
        html_items.append(make_link(f_name, f_title, is_dir=True))
    for f_name, f_title in files:
        html_items.append(make_link(f_name, f_title))
    
    list_content = "\n        ".join(html_items) or "<li>No verified entities found.</li>"

    # 4. Write to File (The Knife Method)
    target = os.path.join(path, 'index.html')
    
    # Create if missing
    if not os.path.exists(target):
        if path == '.': return # Should exist for root
        print(f"   + Creating {target}")
        with open(target, 'w', encoding='utf-8') as f:
            f.write(f"<!DOCTYPE html><html><head><title>Index</title></head><body><ul>{MARKER_START}\n{MARKER_END}</ul></body></html>")

    # Update
    try:
        with open(target, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # FIND THE MARKERS
        start_idx = content.find(MARKER_START)
        end_idx = content.find(MARKER_END)
        
        if start_idx != -1 and end_idx != -1:
            # Slicing the string (Impossible to hang)
            pre_content = content[:start_idx + len(MARKER_START)]
            post_content = content[end_idx:]
            
            new_full_content = pre_content + "\n        " + list_content + "\n        " + post_content
            
            if new_full_content != content:
                with open(target, 'w', encoding='utf-8') as f:
                    f.write(new_full_content)
                print(f"   ✅ Updated {target}")
            else:
                print(f"   - Clean {target}")
        else:
            print(f"   ⚠️ MARKERS MISSING in {target}")

    except Exception as e:
        print(f"   [!] Write failed for {target}: {e}")

if __name__ == "__main__":
    scan_and_build('.')
    print("--- MISSION COMPLETE ---")
