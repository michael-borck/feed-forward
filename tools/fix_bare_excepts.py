#!/usr/bin/env python3
"""
Fix bare except clauses (E722) in the codebase
Replaces bare 'except:' with 'except Exception:'
"""

import re
from pathlib import Path


def fix_bare_excepts(file_path: Path) -> bool:
    """Fix bare except clauses in a Python file"""
    try:
        content = file_path.read_text()
        original_content = content

        # Pattern to match bare except clauses
        # This regex looks for 'except:' with optional whitespace
        pattern = r'^(\s*)except\s*:\s*$'
        replacement = r'\1except Exception:'

        # Replace bare excepts
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        # Check if we made any changes
        if content != original_content:
            file_path.write_text(content)
            return True
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Fix bare excepts in all Python files"""
    root = Path(__file__).parent.parent

    # Find all Python files
    python_files = list(root.glob("**/*.py"))

    # Exclude venv and other directories
    excluded_dirs = {'.venv', '__pycache__', '.git', 'node_modules'}
    python_files = [
        f for f in python_files
        if not any(excluded in f.parts for excluded in excluded_dirs)
    ]

    fixed_count = 0
    for file_path in python_files:
        if fix_bare_excepts(file_path):
            print(f"Fixed: {file_path.relative_to(root)}")
            fixed_count += 1

    print(f"\nFixed {fixed_count} files with bare except clauses")

    # Now add TECH-DEBT comments where needed
    print("\nAdding TECH-DEBT comments for specific exception handling...")

    # Files that need more specific exception handling
    files_needing_specific_exceptions = [
        'app/services/feedback_generator.py',
        'tools/test_tos_privacy.py',
        'tools/test_instructor_feedback_ui.py',
    ]

    for file_name in files_needing_specific_exceptions:
        file_path = root / file_name
        if file_path.exists():
            try:
                content = file_path.read_text()
                # Add TECH-DEBT comment after Exception
                content = re.sub(
                    r'^(\s*)except Exception:(\s*)$',
                    r'\1except Exception:  # TECH-DEBT: Use specific exception types\2',
                    content,
                    flags=re.MULTILINE
                )
                file_path.write_text(content)
                print(f"Added TECH-DEBT comment to: {file_name}")
            except Exception as e:
                print(f"Error adding TECH-DEBT to {file_name}: {e}")


if __name__ == '__main__':
    main()
