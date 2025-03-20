"""
Script to clean up draft content for privacy
Run this as a scheduled task to ensure student submissions are not stored long-term
"""
import sys
import os

# Make sure app is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app.utils.privacy import cleanup_drafts_after_feedback

if __name__ == "__main__":
    count = cleanup_drafts_after_feedback()
    print(f"Cleaned up {count} drafts to protect student privacy.")