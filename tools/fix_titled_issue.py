#!/usr/bin/env python3
"""
Fix the fh.Titled issue that causes titles to appear as visible text on pages
"""

import re
from pathlib import Path


def fix_titled_in_file(file_path):
    """Fix fh.Titled usage in a single file"""
    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    # Pattern to match return fh.Titled(..., content)
    # This captures the title and the content
    pattern = r'return fh\.Titled\(\s*([^,]+),\s*(.+?)\s*\)'

    def replacement(match):
        # Just return the content without the fh.Titled wrapper
        return f'return {match.group(2)}'

    modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if modified_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        return True
    return False

def main():
    """Fix fh.Titled in all affected files"""
    app_dir = Path(__file__).parent.parent / 'app'

    # Files that need fixing based on grep search results
    files_to_fix = [
        'routes/docs.py',
        'routes/student/assignments.py',
        'routes/student/submissions.py',
        'routes/student/courses.py',
        'routes/admin/models.py',
        'routes/admin/instructors.py',
        'routes/admin/domains.py',
        'routes/instructor/models.py',
        'app.py',  # Main app file
    ]

    print("Fixing fh.Titled issue across all files...")

    fixed_count = 0
    for file_name in files_to_fix:
        file_path = app_dir / file_name
        if file_path.exists():
            if fix_titled_in_file(file_path):
                print(f"✅ Fixed: {file_name}")
                fixed_count += 1
            else:
                print(f"⏭️  No changes needed: {file_name}")
        else:
            print(f"❌ File not found: {file_name}")

    print(f"\n✅ Done! Fixed {fixed_count} files.")
    print("The visible title issue should now be resolved across the application.")

if __name__ == '__main__':
    main()
