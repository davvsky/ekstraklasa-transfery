import json
import re

# Read scraped data
with open('transfers.json', 'r', encoding='utf-8') as f:
    transfers = json.load(f)

# Read current HTML
with open('simple.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find and replace the transfers array
js_array = 'const transfers = ' + json.dumps(transfers, ensure_ascii=False, indent=2) + ';'

# Replace the transfers array in HTML
pattern = r'const transfers = \[.*?\];'
new_html = re.sub(pattern, js_array, html_content, flags=re.DOTALL)

# Write updated HTML
with open('simple.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

# Also update index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f'Updated HTML with {len(transfers)} transfers')