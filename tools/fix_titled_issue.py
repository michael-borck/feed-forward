#!/usr/bin/env python3
"""
Fix the fh.Titled issue that causes titles to appear as visible text on pages
"""

import re
from pathlib import Path


def fix_titled_in_file(file_path):
    """Fix fh.Titled usage in a single file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match return fh.Titled(..., dashboard_layout(...))
    # This captures the title and the dashboard_layout call
    pattern = r'return fh\.Titled\(\s*([^,]+),\s*(dashboard_layout\([^)]*\)[^)]*\))\s*\)'
    
    def replacement(match):
        # Just return the dashboard_layout call without the fh.Titled wrapper
        # The title parameter is already passed to dashboard_layout
        return f'return {match.group(2)}'
    
    modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if modified_content != content:
        with open(file_path, 'w') as f:
            f.write(modified_content)
        return True
    return False


def main():
    """Fix fh.Titled in all affected files"""
    app_dir = Path(__file__).parent.parent / 'app'
    
    files_to_fix = [
        app_dir / 'routes' / 'instructor' / 'dashboard.py',
        app_dir / 'routes' / 'instructor' / 'models.py',
        app_dir / 'routes' / 'student' / 'dashboard.py',
        app_dir / 'routes' / 'student' / 'courses.py',
        app_dir / 'routes' / 'student' / 'submissions.py',
        app_dir / 'routes' / 'student' / 'assignments.py',
        app_dir / 'routes' / 'admin' / 'dashboard.py',
        app_dir / 'routes' / 'admin' / 'models.py',
        app_dir / 'routes' / 'admin' / 'domains.py',
        app_dir / 'routes' / 'admin' / 'instructors.py',
    ]
    
    print("Fixing fh.Titled issue in dashboard pages...")
    
    for file_path in files_to_fix:
        if file_path.exists():
            if fix_titled_in_file(file_path):
                print(f"✅ Fixed: {file_path.relative_to(app_dir.parent)}")
            else:
                print(f"⏭️  No changes needed: {file_path.relative_to(app_dir.parent)}")
        else:
            print(f"❌ File not found: {file_path}")
    
    # Special handling for docs.py since it doesn't use dashboard_layout
    docs_file = app_dir / 'routes' / 'docs.py'
    print(f"\n⚠️  {docs_file.relative_to(app_dir.parent)} needs manual review - it doesn't use dashboard_layout")
    
    print("\n✅ Done! The visible title issue should be fixed for dashboard pages.")
    print("Note: The docs.py file may need separate handling as it doesn't use dashboard_layout.")


if __name__ == '__main__':
    main()