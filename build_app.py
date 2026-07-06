"""Build complete app.py with full vocabulary from Lexiword.html DAYBOOK_DATA."""
import os

# Read the generated daybook data
daybook_path = os.path.join(os.path.dirname(__file__), 'daybook_data.py')
with open(daybook_path, 'r', encoding='utf-8') as f:
    daybook_data = f.read()

# Read the original app.py to extract the routes and footer
app_path = os.path.join(os.path.dirname(__file__), 'deploy_backend', 'app.py')
with open(app_path, 'r', encoding='utf-8') as f:
    full = f.read()

# Find the start of the old DAYBOOK_DATA and the end of seed_daybook
# We replace lines from '# inline DAYBOOK_DATA' to '    db.commit()' right after the loop
import re
# Match from '    # inline DAYBOOK_DATA' through the end of seed_daybook's db.commit()
pattern = r'    # inline DAYBOOK_DATA.*?    db\.commit\(\)'
# Actually simpler: just find where old seed_daybook ends and routes begin
# After seed_daybook comes '# ── JWT helpers'
idx_start_routes = full.index("def encode_token(user_id):")
# Before that, find '# inline DAYBOOK_DATA' or the start of old DAYBOOK_DATA
idx_old_data_start = full.index('    # inline DAYBOOK_DATA')

# Build: header (up to seed_daybook def) + new DAYBOOK_DATA + seed loop + rest
header = full[:idx_old_data_start].rstrip() + '\n\n'
# Now we need the seed_daybook function that uses DAYBOOK_DATA
# The seed function body after the data loading loop comes after '    db.commit()'
# Let's find where the old DAYBOOK_DATA block ends
idx_after_old_dblock = full.index('\n    for day_str, words in DAYBOOK_DATA.items():')
idx_routes = full.index('\n\n# ── JWT helpers')
# The seed loop + db.commit + closing function
seed_end = '\n    for day_str, words in DAYBOOK_DATA.items():\n        day_num = int(day_str)\n        for entry in words:\n            db.execute(\n                "INSERT OR IGNORE INTO daybook_words (day, word, meaning) VALUES (?, ?, ?)",\n                (day_num, entry[\'w\'], entry[\'m\']))\n    db.commit()\n'
routes = full[idx_routes:]

# Indent daybook_data (4 spaces) to be inside seed_daybook() function
indented_data = '\n'.join('    ' + line for line in daybook_data.split('\n'))
output = header + indented_data + '\n' + seed_end + '\n' + routes.strip()

# Write output
output_path = os.path.join(os.path.dirname(__file__), 'deploy_backend', 'app_full.py')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(output)

print(f'Written {output_path}')
print(f'Size: {len(output)} bytes, {output.count(chr(10))} lines')

# Verify syntax
import py_compile
try:
    py_compile.compile(output_path, doraise=True)
    print('Syntax check: PASSED')
except py_compile.PyCompileError as e:
    print(f'Syntax check: FAILED - {e}')
