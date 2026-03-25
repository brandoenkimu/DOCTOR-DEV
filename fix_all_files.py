#!C:\Program Files\Python313\python.exe
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sys

def fix_file(filename):
    """Add compatibility import to Python file"""
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return False
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    shebang_found = False
    compatibility_added = False
    
    for line in lines:
        new_lines.append(line)
        
        # After shebang and encoding line, add compatibility import
        if not shebang_found and line.startswith('#!'):
            shebang_found = True
        elif shebang_found and not compatibility_added and line.strip() and not line.startswith('#!'):
            # Add compatibility import after the first non-shebang, non-encoding line
            if not line.startswith('# -*-'):
                new_lines.insert(len(new_lines)-1, 'import sys')
                new_lines.insert(len(new_lines)-1, 'import os')
                new_lines.insert(len(new_lines)-1, 'sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))')
                new_lines.insert(len(new_lines)-1, 'import cgi_compat  # This handles cgi/cgitb for Python 3.13')
                new_lines.insert(len(new_lines)-1, '')
                compatibility_added = True
    
    if compatibility_added:
        # Remove any existing cgi imports that might cause issues
        new_content = '\n'.join(new_lines)
        # Comment out any direct cgi imports that might remain
        import re
        new_content = re.sub(r'^import cgi\b', '# import cgi  # Handled by cgi_compat', new_content, flags=re.MULTILINE)
        new_content = re.sub(r'^from cgi import', '# from cgi import  # Handled by cgi_compat', new_content, flags=re.MULTILINE)
        new_content = re.sub(r'^import cgitb\b', '# import cgitb  # Handled by cgi_compat', new_content, flags=re.MULTILINE)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Fixed: {filename}")
        return True
    else:
        print(f"⚠️  Could not fix: {filename} (no shebang line?)")
        return False

# List all Python files to fix
files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'cgi_compat.py' and f != 'fix_all_files.py']

print("=" * 50)
print("Fixing Python files for Python 3.13 compatibility")
print("=" * 50)

fixed = 0
for file in files:
    if fix_file(file):
        fixed += 1

print("=" * 50)
print(f"Fixed {fixed} out of {len(files)} files")
print("=" * 50)