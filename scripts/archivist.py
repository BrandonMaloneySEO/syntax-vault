import os
import re
import sys

# Flush output immediately so logs are real-time
sys.stdout.reconfigure(line_buffering=True)

print("1. [INIT] Script starting...")

MARKER_START = ""
MARKER_END = ""
EXCLUDE = {'.git', '.github', 'scripts', 'css', 'img', 'index.html', '404.html', 'CNAME'}

def get_clean_title(filepath):
    print(f"   > [READING] {filepath}...")  # DIAGNOSTIC PRINT
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(5000) # Only read first 5000 chars to prevent memory hang
            match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip().replace('| Standard Syntax Entity Verified', '')
    except Exception as e:
        print(f"   [!] Error reading file: {e}")
    return os.path.basename(filepath)

def scan_folder(path):
    print(f"2. [SCANNING] Folder: {path}")
    files = []
    folders = []
    
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.name.startswith('.') or entry.name in EXCLUDE:
                    print(f"   - [IGNORING] {entry.name}")
                    continue
                
                if entry.is_file() and entry.name.endswith('.html'):
                    print(f"   ? [FOUND FILE] {entry.name}")
                    title = get_clean_title(entry.path)
                    files.append((entry.name, title))
                
                elif entry.is_dir():
                    print(f"   ? [FOUND DIR] {entry.name}")
                    # Recursion
                    update_index_file(entry.path)
                    folders.append((entry.name, entry.name.capitalize()))
    except Exception as e:
        print(f"   [!] Error scanning folder: {e}")
        
    files.sort(key=lambda x: x[1])
    folders.sort(key=lambda x: x[1])
    return files, folders

def make_link(name, title, is_dir=False):
    if is_dir:
        return f'<li><span class="dir-badge" style="background:#005f87;color:#fff;padding:2px 6px;font-size:10px;text-transform:uppercase;margin-right:10px">Collection</span><a href="{name}/index.html" style="text-decoration:none;color:#111;font-weight:700;display:inline-block">📂 {title} Vault</a></li>'
    return f'<li><span class="badge" style="background:#000;color:#fff;padding:2px 6px;font-size:10px;text-transform:uppercase;margin-right:10px">Entity</span><a href="{name}" style="text-decoration:none;color:#111;font-weight:500;display:inline-block">{title}</a></li>'

def update_index_file(directory):
    target = os.path.join(directory, 'index.html')
    files, folders = scan_folder(directory)
    
    print(f"3. [BUILDING] List for {directory}")
    html_items = []
    for f_name, f_title in folders:
        html_items.append(make_link(f_name, f_title, is_dir=True))
    for f_name, f_title in files:
        html_items.append(make_link(f_name, f_title))
    
    list_content = "\n        ".join(html_items) or "<li>No verified entities found.</li>"

    # Create if missing
    if not os.path.exists(target):
        print(f"   + [CREATING] New index at {target}")
        with open(target, 'w', encoding='utf-8') as f:
            f.write(f"<!DOCTYPE html><html><head><title>Index</title></head><body><ul>{MARKER_START}\n{MARKER_END}</ul></body></html>")

    # Update
    print(f"4. [UPDATING] {target}")
    try:
        with open(target, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = re.compile(f'({re.escape(MARKER_START)})(.*?)({re.escape(MARKER_END)})', re.DOTALL)
        if pattern.search(content):
            new_content = pattern.sub(f'\\1\n        {list_content}\n        \\3', content)
            if new_content != content:
                with open(target, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"   ✅ [SUCCESS] Updated {target}")
            else:
                print(f"   - [SKIP] No changes needed for {target}")
        else:
            print(f"   ⚠️ [FAIL] Markers missing in {target}")
    except Exception as e:
        print(f"   [!] Error writing file: {e}")

if __name__ == "__main__":
    update_index_file('.')
    print("5. [DONE] Script finished.")
