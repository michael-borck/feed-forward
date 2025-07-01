#!/usr/bin/env python3
"""
Test script for AI integration
Tests the complete feedback pipeline with sample data
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.assignment import assignments, rubric_categories
from app.models.feedback import ai_models, drafts
from app.utils.feedback_pipeline import feedback_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_ai_configuration():
    """Test AI model configuration"""
    print("\n=== Testing AI Configuration ===")

    models = ai_models()
    if not models:
        print("❌ No AI models configured")
        return False

    print(f"✅ Found {len(models)} AI models:")
    for model in models:
        print(
            f"  - {model.name} ({model.provider}/{model.model_id}) - Active: {model.active}"
        )

    return True


def test_assignment_rubric():
    """Test assignment and rubric data"""
    print("\n=== Testing Assignment & Rubric Data ===")

    all_assignments = assignments()
    if not all_assignments:
        print("❌ No assignments found")
        return False

    # Get first assignment
    assignment = all_assignments[0]
    print(f"✅ Found assignment: {assignment.title}")

    # Get rubric categories
    categories = rubric_categories()
    assignment_categories = [
        cat for cat in categories if cat.assignment_id == assignment.id
    ]

    if not assignment_categories:
        print("❌ No rubric categories found for assignment")
        return False

    print(f"✅ Found {len(assignment_categories)} rubric categories:")
    for cat in assignment_categories:
        print(f"  - {cat.name} (Weight: {cat.weight}%)")

    return assignment, assignment_categories


def create_test_draft(assignment_id: int) -> int:
    """Create a test draft submission"""
    print("\n=== Creating Test Draft ===")

    test_content = """
    This is a sample student submission for testing the AI feedback system.
    
    The submission demonstrates several key concepts including clear structure,
    argumentation, and evidence-based reasoning. The student has attempted to
    address the assignment requirements through a well-organized approach.
    
    However, there are areas that could be improved, such as deeper analysis
    and stronger conclusion. The writing style is generally clear but could
    benefit from more sophisticated vocabulary and varied sentence structure.
    
    Overall, this represents a solid effort that shows understanding of the
    material while leaving room for enhancement in future drafts.
    """

    from app.models.feedback import Draft
    from app.utils.privacy import calculate_word_count

    # Create test draft
    new_draft = Draft(
        id=next((d.id for d in drafts()), 0) + 1,
        assignment_id=assignment_id,
        student_email="test@example.com",
        version=1,
        content=test_content,
        content_preserved=True,  # Preserve for testing
        submission_date=datetime.now().isoformat(),
        word_count=calculate_word_count(test_content),
        status="submitted",
        content_removed_date="",
    )

    draft_id = drafts.insert(new_draft)
    print(f"✅ Created test draft {draft_id} with {new_draft.word_count} words")

    return draft_id


async def test_feedback_processing(draft_id: int):
    """Test the complete feedback processing pipeline"""
    print("\n=== Testing Feedback Processing ===")

    try:
        # Process feedback synchronously for testing
        result = await feedback_pipeline._process_draft_async(draft_id)

        if result.success:
            print("✅ Feedback processing completed successfully")
            print(f"   Models run: {result.successful_runs}/{result.total_models_run}")
            print(f"   Categories processed: {len(result.aggregated_scores)}")

            for score in result.aggregated_scores:
                print(
                    f"   - {score.category_name}: {score.final_score}/100 (confidence: {score.confidence})"
                )
        else:
            print(f"❌ Feedback processing failed: {result.error_message}")
            return False

    except Exception as e:
        print(f"❌ Error during feedback processing: {e!s}")
        logger.exception("Feedback processing error")
        return False

    return True


def test_status_checking(draft_id: int):
    """Test status checking functionality"""
    print("\n=== Testing Status Checking ===")

    status = feedback_pipeline.get_processing_status(draft_id)
    print(f"Draft Status: {status}")

    return True


async def main():
    """Run all tests"""
    print("🚀 Starting AI Integration Tests")

    # Test 1: AI Configuration
    if not test_ai_configuration():
        print("❌ AI configuration test failed")
        return

    # Test 2: Assignment & Rubric
    assignment_data = test_assignment_rubric()
    if not assignment_data:
        print("❌ Assignment/rubric test failed")
        return

    assignment, categories = assignment_data

    # Test 3: Create Test Draft
    try:
        draft_id = create_test_draft(assignment.id)
    except Exception as e:
        print(f"❌ Failed to create test draft: {e!s}")
        return

    # Test 4: Process Feedback
    if not await test_feedback_processing(draft_id):
        print("❌ Feedback processing test failed")
        return

    # Test 5: Status Checking
    test_status_checking(draft_id)

    print("\n🎉 All AI integration tests completed successfully!")
    print("\nNext steps:")
    print("1. Configure AI model API keys in admin interface")
    print("2. Test with real AI providers (OpenAI, Anthropic, etc.)")
    print("3. Submit a real draft through the web interface")
    print("4. Monitor logs for background processing")


if __name__ == "__main__":
    asyncio.run(main())
