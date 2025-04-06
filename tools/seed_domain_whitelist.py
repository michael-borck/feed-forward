#!/usr/bin/env python3
"""
Seed the domain whitelist table with initial values
"""
from datetime import datetime
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.config import domain_whitelist

def seed_domain_whitelist():
    """Seed the domain whitelist table with initial values"""
    # Check if there are existing records
    existing = list(domain_whitelist())
    if existing:
        print(f"Domain whitelist already contains {len(existing)} entries.")
        print("Current domains:")
        for domain in existing:
            print(f"- {domain['domain']} (auto-approve: {domain['auto_approve_instructor']})")
        choice = input("Do you want to add more domains? (y/n): ")
        if choice.lower() != 'y':
            return

    # Define initial domains
    initial_domains = [
        {"domain": "curtin.edu.au", "auto_approve_instructor": True},
        {"domain": "ecu.edu.au", "auto_approve_instructor": True},
        {"domain": "uwa.edu.au", "auto_approve_instructor": True},
        {"domain": "murdoch.edu.au", "auto_approve_instructor": True},
        {"domain": "notre-dame.edu.au", "auto_approve_instructor": False}
    ]

    # Add timestamp fields
    now = datetime.now().isoformat()
    for domain in initial_domains:
        domain["created_at"] = now
        domain["updated_at"] = now

    # Check for duplicates and insert new domains
    existing_domains = set(d["domain"] for d in existing)
    domains_added = 0
    
    for domain in initial_domains:
        if domain["domain"] not in existing_domains:
            # Generate a new ID
            if existing:
                max_id = max(d["id"] for d in existing)
                domain_id = max_id + 1 + domains_added
            else:
                domain_id = 1 + domains_added
            
            domain["id"] = domain_id
            domain_whitelist.insert(domain)
            print(f"Added domain: {domain['domain']} (auto-approve: {domain['auto_approve_instructor']})")
            domains_added += 1
        else:
            print(f"Domain {domain['domain']} already exists, skipping.")

    print(f"Added {domains_added} new domains to the whitelist.")

if __name__ == "__main__":
    seed_domain_whitelist()