import os
import re

# --- CONFIG ---
MARKER_START = ""
MARKER_END = ""
# Add any other folder names you want to ignore here
EXCLUDE_DIRS = {'.git', '.github', 'scripts', 'css', 'img', 'node_modules', '__pycache__'}
EXCLUDE_FILES = {'index.html', '404.html', 'CNAME', 'README.md'}

# Track visited paths to prevent infinite loops
VISITED = set()

def get_clean_title(filepath):
    """Reads file and grabs <title> content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip().replace('| Standard Syntax Entity Verified', '')
    except Exception as e:
        print(f"   [!] Error reading {filepath}: {e}")
    return os.path.basename(filepath)

def make_link(name, title, is_dir=False):
    """Returns the HTML string for the list item."""
    if is_dir:
        return f'<li><span class="dir-badge" style="background:#005f87;color:#fff;padding:2px 6px;font-size:10px;text-transform:uppercase;margin-right:10px">Collection</span><a href="{name}/index.html" style="text-decoration:none;color:#111;font-weight:700;display:inline-block">📂 {title} Vault</a></li>'
    return f'<li><span class="badge" style="background:#000;color:#fff;padding:2px 6px;font-size:10px;text-transform:uppercase;margin-right:10px">Entity</span><a href="{name}" style="text-decoration:none;color:#111;font-weight:500;display:inline-block">{title}</a></li>'

def process_directory(current_path):
    # 1. Safety Check: Have we been here?
    abs_path = os.path.abspath(current_path)
    if abs_path in VISITED:
        print(f"Skipping loop: {current_path}")
        return
    VISITED.add(abs_path)
    
    print(f"📂 Scanning: {current_path}")

    files = []
    folders = []
    
    # 2. Scan content
    try:
        with os.scandir(current_path) as entries:
            for entry in entries:
                # Skip excluded stuff
                if entry.name.startswith('.') or entry.name in EXCLUDE_DIRS or entry.name in EXCLUDE_FILES:
                    continue
                
                # Handle Files
                if entry.is_file() and entry.name.endswith('.html'):
                    title = get_clean_title(entry.path)
                    files.append((entry.name, title))
                
                # Handle Directories
                elif entry.is_dir():
                    # RECURSION: Dive into subfolder first
                    process_directory(entry.path)
                    folders.append((entry.name, entry.name.capitalize()))
    except OSError as e:
        print(f"   [!] Could not access {current_path}: {e}")
        return

    # 3. Sort lists
    files.sort(key=lambda x: x[1])
    folders.sort(key=lambda x: x[1])

    # 4. Generate HTML
    html_items = []
    for f_name, f_title in folders:
        html_items.append(make_link(f_name, f_title, is_dir=True))
    for f_name, f_title in files:
        html_items.append(make_link(f_name, f_title))

    list_content = "\n        ".join(html_items)
    if not list_content:
        list_content = "<li>No verified entities found.</li>"

    # 5. Write to index.html
    target_file = os.path.join(current_path, 'index.html')
    
    # If index doesn't exist, create it (only if not root, root must exist)
    if not os.path.exists(target_file) and current_path != '.':
        print(f"   + Creating new index for {current_path}")
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(f"<!DOCTYPE html><html><head><title>Index</title></head><body><ul>{MARKER_START}\n{MARKER_END}</ul></body></html>")

    # Update existing index
    if os.path.exists(target_file):
        update_file_content(target_file, list_content)

def update_file_content(filepath, new_list_html):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = re.compile(f'({re.escape(MARKER_START)})(.*?)({re.escape(MARKER_END)})', re.DOTALL)
        
        if pattern.search(content):
            new_content = pattern.sub(f'\\1\n        {new_list_html}\n        \\3', content)
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"   ✅ Updated: {filepath}")
            else:
                print(f"   - No changes needed: {filepath}")
        else:
            print(f"   ⚠️ Markers missing in: {filepath}")
    except Exception as e:
        print(f"   [!] Failed to write {filepath}: {e}")

if __name__ == "__main__":
    print("--- STANDARD SYNTAX ARCHIVIST STARTED ---")
    process_directory('.')
    print("--- ARCHIVE COMPLETE ---")
