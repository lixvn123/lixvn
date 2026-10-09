#!/usr/bin/env python3
"""
AgentPulse Startup Kit Configurator
SOLID-compliant utility to customize project details across all kit templates.
"""

import sys
import os
import argparse
from typing import Dict

DEFAULT_TARGET_FILES = [
    "index.html",
    "README.md",
    "APPLICATION_PITCH.md",
    "SETUP_GUIDE.md"
]

class ProjectConfigurator:
    def __init__(self, base_dir: str):
        self.base_dir = os.path.abspath(base_dir)

    def apply_configuration(
        self,
        project_name: str,
        domain: str,
        contact_email: str,
        github_repo: str,
        files=None
    ) -> Dict[str, int]:
        target_files = files or DEFAULT_TARGET_FILES
        replacements = {
            "AgentPulse": project_name,
            "agentpulse.dev": domain,
            "contact@agentpulse.dev": contact_email,
            "your-username/agentpulse": github_repo,
        }

        sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)

        stats = {}
        for filename in target_files:
            file_path = os.path.join(self.base_dir, filename)
            if not os.path.isfile(file_path):
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            modified = content
            total_file_replacements = 0
            for old_val, new_val in sorted_replacements:
                if old_val in modified and old_val != new_val:
                    count = modified.count(old_val)
                    modified = modified.replace(old_val, new_val)
                    total_file_replacements += count

            if total_file_replacements > 0:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(modified)

            stats[filename] = total_file_replacements

        return stats


def main():
    parser = argparse.ArgumentParser(description="Customize Claude for Startups Kit")
    parser.add_argument("--name", default="AgentPulse", help="Project / Startup Name")
    parser.add_argument("--domain", default="agentpulse.dev", help="Custom domain (e.g., myapp.dev)")
    parser.add_argument("--email", default="contact@agentpulse.dev", help="Custom contact email")
    parser.add_argument("--github", default="your-username/agentpulse", help="GitHub repo path (e.g. user/repo)")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    configurator = ProjectConfigurator(base_dir)
    results = configurator.apply_configuration(
        project_name=args.name,
        domain=args.domain,
        contact_email=args.email,
        github_repo=args.github
    )

    print("Configuration updated successfully:")
    for file, count in results.items():
        print(f"  - {file}: {count} replacements")


if __name__ == "__main__":
    main()
