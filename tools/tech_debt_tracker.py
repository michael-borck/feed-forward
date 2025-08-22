#!/usr/bin/env python3
"""
Technical Debt Tracker for FeedForward
Scans codebase for suppressed warnings and technical debt markers
"""

import ast
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import ClassVar, Optional

from rich import box
from rich.console import Console
from rich.table import Table


@dataclass
class TechDebtItem:
    """Represents a single technical debt item"""
    file_path: str
    line_number: int
    debt_type: str
    message: str
    severity: str  # low, medium, high, critical
    category: str  # type-ignore, noqa, todo, fixme, hack, etc.
    date_added: Optional[str] = None
    assigned_to: Optional[str] = None
    ticket: Optional[str] = None


class TechDebtTracker:
    """Track and manage technical debt in the codebase"""

    # Patterns to detect technical debt
    DEBT_PATTERNS: ClassVar[dict] = {
        # Type checking suppressions
        r'#\s*type:\s*ignore(?:\[([^\]]+)\])?': ('type-ignore', 'type-checking'),
        r'#\s*mypy:\s*ignore-errors': ('mypy-ignore', 'type-checking'),
        r'#\s*pyright:\s*ignore(?:\[([^\]]+)\])?': ('pyright-ignore', 'type-checking'),

        # Linting suppressions
        r'#\s*noqa(?::\s*([A-Z0-9, ]+))?': ('noqa', 'linting'),
        r'#\s*pylint:\s*disable=([a-z-]+)': ('pylint-disable', 'linting'),
        r'#\s*ruff:\s*noqa(?::\s*([A-Z0-9, ]+))?': ('ruff-noqa', 'linting'),

        # Development markers
        r'#\s*TODO(?::\s*(.*))?': ('todo', 'development'),
        r'#\s*FIXME(?::\s*(.*))?': ('fixme', 'development'),
        r'#\s*HACK(?::\s*(.*))?': ('hack', 'development'),
        r'#\s*XXX(?::\s*(.*))?': ('xxx', 'development'),
        r'#\s*BUG(?::\s*(.*))?': ('bug', 'development'),
        r'#\s*REFACTOR(?::\s*(.*))?': ('refactor', 'development'),

        # Technical debt markers
        r'#\s*TECH[_-]?DEBT(?::\s*(.*))?': ('tech-debt', 'debt'),
        r'#\s*DEPRECATED(?::\s*(.*))?': ('deprecated', 'debt'),
        r'#\s*LEGACY(?::\s*(.*))?': ('legacy', 'debt'),

        # Security markers
        r'#\s*SECURITY(?::\s*(.*))?': ('security', 'security'),
        r'#\s*nosec': ('nosec', 'security'),
    }

    # Severity mapping
    SEVERITY_MAP: ClassVar[dict] = {
        'todo': 'low',
        'hack': 'medium',
        'fixme': 'high',
        'bug': 'high',
        'xxx': 'high',
        'deprecated': 'medium',
        'legacy': 'medium',
        'security': 'critical',
        'nosec': 'critical',
        'type-ignore': 'medium',
        'noqa': 'low',
        'tech-debt': 'medium',
        'refactor': 'medium',
    }

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.console = Console()
        self.debt_items: list[TechDebtItem] = []
        self.stats: dict[str, int] = defaultdict(int)

    def scan_file(self, file_path: Path) -> list[TechDebtItem]:
        """Scan a single Python file for technical debt"""
        items = []

        try:
            with open(file_path, encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                for pattern, (debt_type, category) in self.DEBT_PATTERNS.items():
                    match = re.search(pattern, line)
                    if match:
                        message = match.group(1) if match.groups() else ""

                        # Extract metadata from message if present
                        ticket = None
                        assigned = None
                        date = None

                        # Look for ticket reference (e.g., JIRA-123)
                        ticket_match = re.search(r'\b([A-Z]+-\d+)\b', message)
                        if ticket_match:
                            ticket = ticket_match.group(1)

                        # Look for assignment (@username)
                        assign_match = re.search(r'@(\w+)', message)
                        if assign_match:
                            assigned = assign_match.group(1)

                        # Look for date (YYYY-MM-DD)
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', message)
                        if date_match:
                            date = date_match.group(1)

                        item = TechDebtItem(
                            file_path=str(file_path.relative_to(self.root_dir)),
                            line_number=line_num,
                            debt_type=debt_type,
                            message=message.strip() if message else "",
                            severity=self.SEVERITY_MAP.get(debt_type, 'low'),
                            category=category,
                            date_added=date,
                            assigned_to=assigned,
                            ticket=ticket
                        )
                        items.append(item)
                        self.stats[debt_type] += 1
                        self.stats[f"severity_{item.severity}"] += 1

        except Exception as e:
            self.console.print(f"[red]Error scanning {file_path}: {e}[/red]")

        return items

    def scan_directory(self, directory: Path, exclude_patterns: Optional[list[str]] = None) -> None:
        """Scan directory recursively for Python files"""
        exclude_patterns = exclude_patterns or [
            '__pycache__', '.venv', 'venv', '.git', '.mypy_cache', '.ruff_cache'
        ]

        for file_path in directory.rglob("*.py"):
            # Skip excluded directories
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue

            items = self.scan_file(file_path)
            self.debt_items.extend(items)

    def analyze_ast_complexity(self, file_path: Path) -> dict:
        """Analyze AST for complexity metrics"""
        try:
            with open(file_path, encoding='utf-8') as f:
                tree = ast.parse(f.read())

            # Count various complexity indicators
            metrics = {
                'functions': 0,
                'classes': 0,
                'max_function_length': 0,
                'deeply_nested': [],  # Functions with nesting > 3
                'too_many_args': [],  # Functions with > 5 args
                'too_many_returns': [],  # Functions with > 3 returns
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics['functions'] += 1

                    # Count lines in function
                    if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                        func_length = node.end_lineno - node.lineno
                        metrics['max_function_length'] = max(
                            metrics['max_function_length'], func_length
                        )

                    # Count arguments
                    num_args = len(node.args.args)
                    if num_args > 5:
                        metrics['too_many_args'].append((node.name, num_args))

                    # Count returns
                    returns = sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))
                    if returns > 3:
                        metrics['too_many_returns'].append((node.name, returns))

                elif isinstance(node, ast.ClassDef):
                    metrics['classes'] += 1

            return metrics

        except Exception as e:
            return {'error': str(e)}

    def generate_report(self, output_format: str = "console") -> None:
        """Generate technical debt report"""
        if output_format == "console":
            self._console_report()
        elif output_format == "json":
            self._json_report()
        elif output_format == "markdown":
            self._markdown_report()
        elif output_format == "csv":
            self._csv_report()

    def _console_report(self) -> None:
        """Generate console report with rich formatting"""
        self.console.print("\n[bold cyan]🔍 Technical Debt Report[/bold cyan]\n")

        # Summary statistics
        summary_table = Table(title="Summary Statistics", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Count", justify="right", style="yellow")

        summary_table.add_row("Total Items", str(len(self.debt_items)))
        summary_table.add_row("Critical Severity", str(self.stats.get('severity_critical', 0)))
        summary_table.add_row("High Severity", str(self.stats.get('severity_high', 0)))
        summary_table.add_row("Medium Severity", str(self.stats.get('severity_medium', 0)))
        summary_table.add_row("Low Severity", str(self.stats.get('severity_low', 0)))

        self.console.print(summary_table)

        # Debt by category
        category_table = Table(title="\nDebt by Category", box=box.ROUNDED)
        category_table.add_column("Category", style="cyan")
        category_table.add_column("Count", justify="right", style="yellow")

        categories = defaultdict(int)
        for item in self.debt_items:
            categories[item.category] += 1

        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            category_table.add_row(category.title(), str(count))

        self.console.print(category_table)

        # Debt by type
        type_table = Table(title="\nDebt by Type", box=box.ROUNDED)
        type_table.add_column("Type", style="cyan")
        type_table.add_column("Count", justify="right", style="yellow")

        types = defaultdict(int)
        for item in self.debt_items:
            types[item.debt_type] += 1

        for debt_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True)[:10]:
            type_table.add_row(debt_type, str(count))

        self.console.print(type_table)

        # Files with most debt
        file_debt = defaultdict(list)
        for item in self.debt_items:
            file_debt[item.file_path].append(item)

        worst_files = sorted(file_debt.items(), key=lambda x: len(x[1]), reverse=True)[:10]

        if worst_files:
            files_table = Table(title="\nFiles with Most Technical Debt", box=box.ROUNDED)
            files_table.add_column("File", style="cyan")
            files_table.add_column("Items", justify="right", style="yellow")
            files_table.add_column("Critical", justify="right", style="red")
            files_table.add_column("High", justify="right", style="orange1")

            for file_path, items in worst_files:
                critical = sum(1 for i in items if i.severity == 'critical')
                high = sum(1 for i in items if i.severity == 'high')
                files_table.add_row(
                    file_path,
                    str(len(items)),
                    str(critical) if critical else "",
                    str(high) if high else ""
                )

            self.console.print(files_table)

        # Critical items details
        critical_items = [i for i in self.debt_items if i.severity == 'critical']
        if critical_items:
            self.console.print("\n[bold red]⚠️  Critical Items[/bold red]")
            for item in critical_items[:10]:
                self.console.print(
                    f"  • {item.file_path}:{item.line_number} - "
                    f"[yellow]{item.debt_type}[/yellow]: {item.message or 'No message'}"
                )

    def _json_report(self) -> None:
        """Generate JSON report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_items": len(self.debt_items),
                "by_severity": {
                    "critical": self.stats.get('severity_critical', 0),
                    "high": self.stats.get('severity_high', 0),
                    "medium": self.stats.get('severity_medium', 0),
                    "low": self.stats.get('severity_low', 0),
                },
                "by_category": {},
                "by_type": {}
            },
            "items": []
        }

        # Aggregate by category and type
        for item in self.debt_items:
            report["summary"]["by_category"][item.category] = \
                report["summary"]["by_category"].get(item.category, 0) + 1
            report["summary"]["by_type"][item.debt_type] = \
                report["summary"]["by_type"].get(item.debt_type, 0) + 1

            report["items"].append({
                "file": item.file_path,
                "line": item.line_number,
                "type": item.debt_type,
                "category": item.category,
                "severity": item.severity,
                "message": item.message,
                "metadata": {
                    "ticket": item.ticket,
                    "assigned_to": item.assigned_to,
                    "date_added": item.date_added
                }
            })

        print(json.dumps(report, indent=2))

    def _markdown_report(self) -> None:
        """Generate Markdown report"""
        print("# Technical Debt Report\n")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print("## Summary\n")
        print(f"- **Total Items**: {len(self.debt_items)}")
        print(f"- **Critical**: {self.stats.get('severity_critical', 0)}")
        print(f"- **High**: {self.stats.get('severity_high', 0)}")
        print(f"- **Medium**: {self.stats.get('severity_medium', 0)}")
        print(f"- **Low**: {self.stats.get('severity_low', 0)}")
        print()

        # Group by file
        file_debt = defaultdict(list)
        for item in self.debt_items:
            file_debt[item.file_path].append(item)

        print("## By File\n")
        for file_path, items in sorted(file_debt.items()):
            print(f"### `{file_path}` ({len(items)} items)\n")
            for item in sorted(items, key=lambda x: x.line_number):
                severity_emoji = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(item.severity, '⚪')

                print(f"- Line {item.line_number}: {severity_emoji} **{item.debt_type}**")
                if item.message:
                    print(f"  - {item.message}")
            print()

    def _csv_report(self) -> None:
        """Generate CSV report"""
        import csv

        writer = csv.writer(sys.stdout)
        writer.writerow([
            'File', 'Line', 'Type', 'Category', 'Severity',
            'Message', 'Ticket', 'Assigned To', 'Date Added'
        ])

        for item in self.debt_items:
            writer.writerow([
                item.file_path,
                item.line_number,
                item.debt_type,
                item.category,
                item.severity,
                item.message,
                item.ticket or '',
                item.assigned_to or '',
                item.date_added or ''
            ])


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Track technical debt in Python codebase')
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to scan (default: current directory)'
    )
    parser.add_argument(
        '--format',
        choices=['console', 'json', 'markdown', 'csv'],
        default='console',
        help='Output format'
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        help='Patterns to exclude from scanning'
    )
    parser.add_argument(
        '--severity',
        choices=['all', 'critical', 'high', 'medium', 'low'],
        default='all',
        help='Minimum severity to report'
    )
    parser.add_argument(
        '--save',
        help='Save report to file'
    )

    args = parser.parse_args()

    # Create tracker
    tracker = TechDebtTracker(args.path)

    # Scan codebase
    console = Console()
    with console.status("[yellow]Scanning codebase for technical debt...[/yellow]"):
        tracker.scan_directory(Path(args.path), args.exclude)

    # Filter by severity if requested
    if args.severity != 'all':
        severity_order = ['low', 'medium', 'high', 'critical']
        min_severity_index = severity_order.index(args.severity)
        tracker.debt_items = [
            item for item in tracker.debt_items
            if severity_order.index(item.severity) >= min_severity_index
        ]

    # Generate report
    if args.save:
        # Redirect stdout to file
        import sys
        original_stdout = sys.stdout
        with open(args.save, 'w') as f:
            sys.stdout = f
            tracker.generate_report(args.format)
        sys.stdout = original_stdout
        console.print(f"[green]Report saved to {args.save}[/green]")
    else:
        tracker.generate_report(args.format)

    # Exit with error code if critical items found
    critical_count = tracker.stats.get('severity_critical', 0)
    if critical_count > 0:
        console.print(f"\n[red]⚠️  Found {critical_count} critical items![/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
