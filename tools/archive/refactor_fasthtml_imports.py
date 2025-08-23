#!/usr/bin/env python3
"""
Automated refactoring tool for FastHTML imports
Converts star imports to namespace imports (fh.Component pattern)
"""

import argparse
import ast
import difflib
import sys
from pathlib import Path
from typing import ClassVar, Optional

from rich.console import Console
from rich.progress import track
from rich.prompt import Confirm


class FastHTMLImportRefactorer:
    """Refactor FastHTML star imports to namespace imports"""

    # Common FastHTML components and functions
    FASTHTML_COMPONENTS: ClassVar[set[str]] = {
        # HTML elements
        'Html', 'Head', 'Body', 'Title', 'Meta', 'Link', 'Script', 'Style',
        'Div', 'P', 'Span', 'A', 'Img', 'Hr', 'Br',
        'H1', 'H2', 'H3', 'H4', 'H5', 'H6',
        'Ul', 'Ol', 'Li', 'Dl', 'Dt', 'Dd',
        'Table', 'Thead', 'Tbody', 'Tfoot', 'Tr', 'Th', 'Td',
        'Form', 'Input', 'Textarea', 'Select', 'Option', 'Button', 'Label',
        'Fieldset', 'Legend', 'Datalist', 'Output', 'Progress', 'Meter',
        'Details', 'Summary', 'Dialog',
        'Nav', 'Main', 'Header', 'Footer', 'Article', 'Section', 'Aside',
        'Figure', 'Figcaption', 'Mark', 'Time',
        'Canvas', 'Video', 'Audio', 'Source', 'Track',
        'Iframe', 'Embed', 'Object', 'Param',
        'Code', 'Pre', 'Kbd', 'Samp', 'Var',
        'B', 'I', 'U', 'S', 'Small', 'Strong', 'Em', 'Cite', 'Q',
        'Blockquote', 'Address',

        # FastHTML specific
        'Titled', 'Card', 'Container', 'Group', 'Grid', 'NotStr',
        'Safe', 'Hidden', 'Fragment',

        # Common utilities
        'fast_app', 'FastHTML', 'Route', 'APIRouter',
        'serve', 'setup_toasts',

        # Response types
        'HTMLResponse', 'RedirectResponse', 'FileResponse',

        # Form utilities
        'File', 'UploadFile', 'Beforeware',

        # UI Components
        'Toast', 'Modal', 'Dropdown', 'Accordion', 'Tab', 'Tabs',

        # Icons and special
        'Icon', 'Favicon', 'SvgIcon',

        # HTMX related
        'HtmxResponseHeaders',
    }

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.console = Console()
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'imports_refactored': 0,
            'components_prefixed': 0,
            'errors': 0
        }

    def find_fasthtml_usage(self, tree: ast.AST) -> set[str]:
        """Find all FastHTML components used in the file"""
        used_components = set()

        class ComponentVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                if node.id in FastHTMLImportRefactorer.FASTHTML_COMPONENTS:
                    used_components.add(node.id)
                self.generic_visit(node)

            def visit_Attribute(self, node):
                # Skip if already namespaced (e.g., fh.Div)
                self.generic_visit(node)

        ComponentVisitor().visit(tree)
        return used_components

    def has_star_import(self, tree: ast.AST) -> bool:
        """Check if file has star import from fasthtml.common"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and 'fasthtml' in node.module and any(alias.name == '*' for alias in node.names):
                return True
        return False

    def refactor_imports(self, source: str) -> tuple[str, list[str]]:
        """Refactor FastHTML imports in source code"""
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            return source, [f"Syntax error: {e}"]

        if not self.has_star_import(tree):
            return source, []

        # Find used components
        used_components = self.find_fasthtml_usage(tree)
        if not used_components and not self.has_star_import(tree):
            return source, []

        lines = source.splitlines(keepends=True)
        changes = []

        # Find and replace import statements
        import_line_idx = None
        for _i, node in enumerate(tree.body):
            if isinstance(node, ast.ImportFrom) and node.module and 'fasthtml' in node.module and any(alias.name == '*' for alias in node.names):
                import_line_idx = node.lineno - 1
                # Replace star import with namespace import
                new_line = "from fasthtml import common as fh\n"
                lines[import_line_idx] = new_line
                changes.append(f"Line {node.lineno}: Replaced star import")
                self.stats['imports_refactored'] += 1
                break

        # Now prefix all component usage
        if import_line_idx is not None:
            # Parse again to get accurate positions
            modified_source = ''.join(lines)

            # Use regex for more accurate replacement
            import re

            # Build pattern for all used components
            for component in used_components:
                # Match component usage but not when already prefixed or in strings
                pattern = r'\b(?<!fh\.)(?<!["\'])(' + re.escape(component) + r')(?=\s*\()'
                replacement = r'fh.\1'

                new_source, count = re.subn(pattern, replacement, modified_source)
                if count > 0:
                    modified_source = new_source
                    changes.append(f"Prefixed {count} instances of {component}")
                    self.stats['components_prefixed'] += count

            return modified_source, changes

        return source, []

    def process_file(self, file_path: Path) -> bool:
        """Process a single Python file"""
        try:
            with open(file_path, encoding='utf-8') as f:
                original_source = f.read()

            refactored_source, changes = self.refactor_imports(original_source)

            if changes:
                if self.verbose or self.dry_run:
                    self.console.print(f"\n[cyan]File: {file_path}[/cyan]")
                    for change in changes:
                        self.console.print(f"  • {change}")

                if not self.dry_run:
                    # Show diff if verbose
                    if self.verbose:
                        diff = difflib.unified_diff(
                            original_source.splitlines(keepends=True),
                            refactored_source.splitlines(keepends=True),
                            fromfile=str(file_path),
                            tofile=str(file_path) + ' (refactored)',
                            n=3
                        )
                        self.console.print("\n[yellow]Diff:[/yellow]")
                        for line in diff:
                            if line.startswith('+'):
                                self.console.print(f"[green]{line.rstrip()}[/green]")
                            elif line.startswith('-'):
                                self.console.print(f"[red]{line.rstrip()}[/red]")
                            else:
                                self.console.print(line.rstrip())

                    # Write back
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(refactored_source)

                    self.stats['files_modified'] += 1
                    return True

            return False

        except Exception as e:
            self.console.print(f"[red]Error processing {file_path}: {e}[/red]")
            self.stats['errors'] += 1
            return False

    def process_directory(self, directory: Path, exclude: Optional[list[str]] = None) -> None:
        """Process all Python files in directory"""
        exclude = exclude or ['.venv', '__pycache__', '.git']

        python_files = []
        for file_path in directory.rglob("*.py"):
            if not any(exc in str(file_path) for exc in exclude):
                python_files.append(file_path)

        self.console.print(f"\n[bold]Found {len(python_files)} Python files to process[/bold]")

        if not python_files:
            return

        for file_path in track(python_files, description="Processing files..."):
            self.stats['files_processed'] += 1
            self.process_file(file_path)

    def print_summary(self) -> None:
        """Print processing summary"""
        self.console.print("\n[bold cyan]Refactoring Summary[/bold cyan]")
        self.console.print(f"Files processed: {self.stats['files_processed']}")
        self.console.print(f"Files modified: {self.stats['files_modified']}")
        self.console.print(f"Imports refactored: {self.stats['imports_refactored']}")
        self.console.print(f"Components prefixed: {self.stats['components_prefixed']}")

        if self.stats['errors'] > 0:
            self.console.print(f"[red]Errors: {self.stats['errors']}[/red]")

        if self.dry_run:
            self.console.print("\n[yellow]This was a dry run. No files were modified.[/yellow]")


def create_backup(directory: Path) -> Path:
    """Create a backup of the codebase before refactoring"""
    import shutil
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = directory.parent / f"{directory.name}_backup_{timestamp}"

    console = Console()
    console.print(f"[yellow]Creating backup at {backup_dir}...[/yellow]")

    shutil.copytree(directory, backup_dir, ignore=shutil.ignore_patterns(
        '.git', '.venv', '__pycache__', '*.pyc', '.mypy_cache', '.ruff_cache'
    ))

    console.print("[green]Backup created successfully[/green]")
    return backup_dir


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Refactor FastHTML star imports to namespace imports'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to file or directory to refactor'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output including diffs'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup'
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        default=['.venv', '__pycache__', '.git'],
        help='Directories to exclude'
    )

    args = parser.parse_args()

    path = Path(args.path)
    console = Console()

    if not path.exists():
        console.print(f"[red]Path {path} does not exist[/red]")
        sys.exit(1)

    # Create backup unless skipped
    if not args.dry_run and not args.no_backup and path.is_dir() and Confirm.ask("[yellow]Create backup before refactoring?[/yellow]", default=True):
        backup_path = create_backup(path)
        console.print(f"[green]Backup created at: {backup_path}[/green]")

    # Create refactorer
    refactorer = FastHTMLImportRefactorer(
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    # Process files
    if path.is_file():
        refactorer.stats['files_processed'] = 1
        if refactorer.process_file(path):
            console.print(f"[green]Successfully refactored {path}[/green]")
    else:
        refactorer.process_directory(path, exclude=args.exclude)

    # Print summary
    refactorer.print_summary()

    # Show next steps
    if not args.dry_run and refactorer.stats['files_modified'] > 0:
        console.print("\n[bold]Next Steps:[/bold]")
        console.print("1. Run tests to ensure functionality: pytest")
        console.print("2. Run type checker: mypy app/")
        console.print("3. Run linter: ruff check .")
        console.print("4. Commit changes: git add -A && git commit -m 'Refactor FastHTML imports'")


if __name__ == '__main__':
    main()
