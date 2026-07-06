import re, json

with open(r'D:\project\Lexiword\Lexiword.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'const DAYBOOK_DATA = (\{[\s\S]*?\n\};)', content)
if not match:
    print("NOT FOUND")
    exit()

js_data = match.group(1).rstrip(';').strip()
js_data = re.sub(r',(\s*[}\]])', r'\1', js_data)
js_data = re.sub(r'(\s)(\d+):', r'\1"\2":', js_data)
data = json.loads(js_data)

lines = []
for day_key in sorted(data.keys(), key=int):
    words = data[day_key]
    lines.append(f'        "{day_key}": [')
    for w in words:
        w_text = w['w'].replace('\\', '\\\\').replace("'", "\\'")
        m_text = w['m'].replace('\\', '\\\\').replace("'", "\\'")
        lines.append(f"            {{'w':'{w_text}','m':'{m_text}'}},")
    lines.append('        ],')

with open(r'D:\project\Lexiword\daybook_data.py', 'w', encoding='utf-8') as f:
    f.write('DAYBOOK_DATA = {\n')
    for line in lines:
        f.write(line + '\n')
    f.write('}\n')

print(f"Written daybook_data.py - {sum(len(data[d]) for d in data)} words, {len(data)} days")
