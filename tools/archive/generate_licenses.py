#!/usr/bin/env python3
"""
Script to generate third-party license acknowledgments from requirements.txt
"""

import json
from pathlib import Path

import requests

# Common license mappings
LICENSE_URLS = {
    "MIT": "https://opensource.org/licenses/MIT",
    "Apache-2.0": "https://www.apache.org/licenses/LICENSE-2.0",
    "BSD": "https://opensource.org/licenses/BSD-3-Clause",
    "BSD-3-Clause": "https://opensource.org/licenses/BSD-3-Clause",
    "BSD-2-Clause": "https://opensource.org/licenses/BSD-2-Clause",
    "GPL-3.0": "https://www.gnu.org/licenses/gpl-3.0.en.html",
    "LGPL-3.0": "https://www.gnu.org/licenses/lgpl-3.0.en.html",
    "ISC": "https://opensource.org/licenses/ISC",
}


def get_package_info(package_name):
    """Get package information from PyPI"""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            info = data.get("info", {})
            return {
                "name": info.get("name", package_name),
                "version": info.get("version", "unknown"),
                "license": info.get("license", "Unknown"),
                "author": info.get("author", "Unknown"),
                "home_page": info.get("home_page", "") or info.get("project_url", ""),
                "summary": info.get("summary", ""),
            }
    except Exception as e:
        print(f"Warning: Could not fetch info for {package_name}: {e}")

    return {
        "name": package_name,
        "version": "unknown",
        "license": "Unknown",
        "author": "Unknown",
        "home_page": "",
        "summary": "",
    }


def parse_requirements():
    """Parse requirements.txt and get package information"""
    requirements_path = Path(__file__).parent.parent / "requirements.txt"
    packages = []

    if not requirements_path.exists():
        print("Error: requirements.txt not found")
        return packages

    with open(requirements_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Extract package name (handle ==, >=, <= etc)
                for separator in ["==", ">=", "<=", "~=", ">"]:
                    if separator in line:
                        package_name = line.split(separator)[0].strip()
                        break
                else:
                    package_name = line.strip()

                if package_name:
                    print(f"Fetching info for {package_name}...")
                    info = get_package_info(package_name)
                    packages.append(info)

    return packages


def categorize_packages(packages):
    """Categorize packages by their purpose"""
    categories = {
        "Core Framework": [
            "fasthtml",
            "fastapi",
            "starlette",
            "uvicorn",
            "fastcore",
            "fastlite",
        ],
        "AI/ML Libraries": ["litellm", "openai", "anthropic"],
        "Database": ["python-fasthtml", "databases"],
        "Document Processing": ["pypdf", "python-docx", "python-multipart", "aiofiles"],
        "Authentication & Security": [
            "passlib",
            "python-jose",
            "cryptography",
            "bcrypt",
            "python-dotenv",
        ],
        "Email": ["aiosmtplib", "email-validator"],
        "HTTP & Networking": ["httpx", "requests", "urllib3", "certifi"],
        "Utilities": [
            "pydantic",
            "python-dateutil",
            "six",
            "typing-extensions",
            "click",
        ],
        "Development": ["pytest", "mypy", "black", "flake8"],
    }

    categorized = {cat: [] for cat in categories}
    categorized["Other"] = []

    for package in packages:
        placed = False
        for category, keywords in categories.items():
            if any(keyword in package["name"].lower() for keyword in keywords):
                categorized[category].append(package)
                placed = True
                break

        if not placed:
            categorized["Other"].append(package)

    # Remove empty categories
    return {k: v for k, v in categorized.items() if v}


def generate_license_markdown(packages):
    """Generate markdown content for licenses"""
    categorized = categorize_packages(packages)

    content = """# Third-Party Licenses and Acknowledgments

FeedForward is built upon the work of many open source projects. We gratefully acknowledge the following projects and their contributors.

## Python Dependencies

"""

    for category, category_packages in categorized.items():
        if category_packages:
            content += f"### {category}\n\n"

            for pkg in sorted(category_packages, key=lambda x: x["name"].lower()):
                content += f"- **{pkg['name']}** "

                if pkg["version"] != "unknown":
                    content += f"v{pkg['version']} "

                if pkg["license"] and pkg["license"] != "Unknown":
                    content += f"- {pkg['license']}\n"
                else:
                    content += "- License not specified\n"

                if pkg["author"] and pkg["author"] != "Unknown":
                    content += f"  - Copyright (c) {pkg['author']}\n"

                if pkg["home_page"]:
                    content += f"  - {pkg['home_page']}\n"

                if pkg["summary"]:
                    content += f"  - {pkg['summary']}\n"

                content += "\n"

    content += """## Frontend Dependencies

### CSS Framework
- **Tailwind CSS** - MIT License
  - Copyright (c) Tailwind Labs, Inc.
  - https://tailwindcss.com/

### JavaScript Libraries
- **HTMX** - BSD 2-Clause License
  - Copyright (c) 2020 Big Sky Software
  - https://htmx.org/

## License Compliance

This software complies with all third-party licenses. The full text of each license can be found at the links provided or in the respective package repositories.

## Acknowledgments

Special thanks to all the contributors of these open source projects that make FeedForward possible.

If you believe we've inadvertently omitted acknowledgment of your project, please contact us via our GitHub repository.

---

*This document was automatically generated from our requirements.txt file.*
*Last updated: {date}*
"""

    from datetime import datetime

    content = content.replace("{date}", datetime.now().strftime("%Y-%m-%d"))

    return content


def main():
    """Main function"""
    print("Generating third-party license acknowledgments...")

    packages = parse_requirements()
    print(f"\nFound {len(packages)} packages")

    markdown_content = generate_license_markdown(packages)

    # Save to docs/legal/third-party-licenses.md
    output_path = (
        Path(__file__).parent.parent / "docs" / "legal" / "third-party-licenses.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(markdown_content)

    print(f"\nLicense acknowledgments written to {output_path}")

    # Also create a JSON file for future reference
    json_path = output_path.with_suffix(".json")
    with open(json_path, "w") as f:
        json.dump(packages, f, indent=2)

    print(f"Package data saved to {json_path}")


if __name__ == "__main__":
    main()
