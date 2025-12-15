import os
import re

# CONFIGURATION
MARKER_START = ""
MARKER_END = ""
EXCLUDE_DIRS = {'.git', '.github', 'scripts', 'css', 'img'}
EXCLUDE_FILES = {'index.html', '404.html', 'CNAME'}

def get_title(filepath):
    """Extracts the <title> content from an HTML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip().replace('| Standard Syntax Entity Verified', '')
    except Exception:
        pass
    return os.path.basename(filepath)

def generate_list_item(filename, title, is_collection=False):
    """Generates the HTML list item."""
    if is_collection:
        return f'<li><span class="dir-badge" style="background:#005f87;color:#fff;padding:2px 6px;font-size:10px;text-transform:uppercase;margin-right:10px">Collection</span><a href="{filename}/index.html" style="text-decoration:none;color:#111;font-weight:700;display:inline-block">📂 {title} Vault</a></li>'
    else:
        return f'<li><span class="badge" style="background:#000;color:#fff;padding:2px 6px;font-size:10px;text-transform:uppercase;margin-right:10px">Entity</span><a href="{filename}" style="text-decoration:none;color:#111;font-weight:500;display:inline-block">{title}</a></li>'

def update_index(directory):
    """Updates or creates the index.html in the given directory."""
    index_path = os.path.join(directory, 'index.html')
    
    # 1. Scan for Files and Folders
    files = []
    folders = []
    
    # Scan the directory
    if os.path.isdir(directory):
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.name in EXCLUDE_FILES or entry.name.startswith('.'):
                    continue
                
                if entry.is_file() and entry.name.endswith('.html'):
                    title = get_title(entry.path)
                    files.append((entry.name, title))
                
                elif entry.is_dir() and entry.name not in EXCLUDE_DIRS:
                    # Recursively update the subfolder first
                    update_index(entry.path)
                    # Then add it to this list
                    folders.append((entry.name, entry.name.capitalize()))

    # Sort them
    files.sort(key=lambda x: x[1])
    folders.sort(key=lambda x: x[1])

    # 2. Build the HTML Content
    html_lines = []
    
    # Add Folders first (if any)
    for folder_name, folder_title in folders:
        html_lines.append(generate_list_item(folder_name, folder_title, is_collection=True))
        
    # Add Files second
    for file_name, file_title in files:
        html_lines.append(generate_list_item(file_name, file_title))

    new_list_content = "\n        ".join(html_lines)
    if not new_list_content:
        new_list_content = "<li>No verified entities found in this sector.</li>"

    # 3. Read or Create index.html
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
            
        # 4. Inject the Content
        pattern = re.compile(f'({re.escape(MARKER_START)})(.*?)({re.escape(MARKER_END)})', re.DOTALL)
        
        if pattern.search(original_content):
            updated_content = pattern.sub(f'\\1\\n        {new_list_content}\\n        \\3', original_content)
            
            # Only write if changed
            if updated_content != original_content:
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"✅ Updated: {index_path}")
        else:
            print(f"⚠️ Skipped: {index_path} (Missing Markers)")
            
    else:
        # Create a new index.html if one doesn't exist (Sub-folder auto-creation)
        dir_name = os.path.basename(directory).capitalize() or "Root"
        new_file_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Standard Syntax | {dir_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>body{{font-family:'Space Grotesk',sans-serif;padding:40px;background:#f4f4f4;color:#111;max-width:800px;margin:0 auto}}h1{{border-bottom:2px solid #000;padding-bottom:10px;margin-bottom:20px}}ul{{list-style:none;padding:0}}li{{margin-bottom:10px;background:#fff;border:1px solid #ddd;padding:15px;border-radius:4px;transition:transform .2s}}li:hover{{transform:translateX(5px);border-color:#000}}a{{text-decoration:none;color:#111;font-weight:500;display:block}}.badge{{background:#000;color:#fff;padding:2px 6px;font-size:10px;text-transform:uppercase;margin-right:10px}}.dir-badge{{background:#005f87;color:#fff;padding:2px 6px;font-size:10px;text-transform:uppercase;margin-right:10px}}</style>
</head>
<body>
    <h1>{dir_name} Index</h1>
    <ul id="entity-list">
        {MARKER_START}
        {new_list_content}
        {MARKER_END}
    </ul>
</body>
</html>"""
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(new_file_content)
        print(f"✅ Created New Index: {index_path}")

# Run the script from the current working directory
if __name__ == "__main__":
    print("Starting Standard Syntax Archivist...")
    update_index('.')
