#!/usr/bin/env python3
"""
Test script for the prompt template system
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.assignment import Assignment, Rubric, RubricCategory
from app.models.config import FeedbackStyle
from app.services.prompt_templates import (
    generate_feedback_prompt, 
    PromptContext, 
    create_prompt_template
)


def test_prompt_generation():
    """Test the prompt generation system"""
    print("=== Testing Prompt Template System ===\n")
    
    # Create mock assignment
    assignment = Assignment(
        id=1,
        course_id=1,
        title="Critical Analysis Essay",
        description="Write a 1000-word critical analysis of a contemporary social issue, demonstrating clear argumentation and evidence-based reasoning.",
        due_date="2024-12-31",
        max_drafts=3,
        created_by="instructor@example.com",
        status="active",
        created_at="2024-01-01",
        updated_at="2024-01-01"
    )
    
    # Create mock rubric categories
    categories = [
        RubricCategory(
            id=1,
            rubric_id=1,
            name="Thesis and Argumentation",
            description="Clear thesis statement and logical flow of arguments with supporting evidence",
            weight=30.0
        ),
        RubricCategory(
            id=2,
            rubric_id=1,
            name="Critical Analysis",
            description="Depth of analysis, consideration of multiple perspectives, and original insights",
            weight=30.0
        ),
        RubricCategory(
            id=3,
            rubric_id=1,
            name="Evidence and Sources",
            description="Use of credible sources, proper citations, and integration of evidence",
            weight=25.0
        ),
        RubricCategory(
            id=4,
            rubric_id=1,
            name="Writing Quality",
            description="Grammar, clarity, organization, and academic writing conventions",
            weight=15.0
        )
    ]
    
    # Create mock feedback style
    feedback_style = FeedbackStyle(
        id=1,
        name="Encouraging",
        description="Positive and supportive tone",
        is_active=True
    )
    
    # Mock student submission
    student_submission = """
    The Impact of Social Media on Mental Health

    In recent years, social media has become an integral part of daily life for billions of people worldwide. While these platforms offer unprecedented connectivity and information sharing, growing evidence suggests they may have significant negative impacts on mental health, particularly among young adults and teenagers.

    Social media platforms are designed to be addictive. Features like infinite scroll, push notifications, and variable reward schedules trigger dopamine responses similar to those seen in gambling addiction. Users find themselves checking their phones compulsively, seeking the next "like" or comment. This constant engagement creates a cycle of dependency that can interfere with real-world activities and relationships.

    Research has shown strong correlations between heavy social media use and increased rates of anxiety and depression. A study by the University of Pennsylvania found that limiting social media use to 30 minutes per day led to significant reductions in loneliness and depression after just three weeks. The constant comparison with others' curated online personas creates unrealistic expectations and feelings of inadequacy.

    Furthermore, social media has fundamentally altered how people communicate and form relationships. While it allows for maintaining connections across distances, it often replaces face-to-face interactions with superficial online exchanges. This shift has been linked to decreased empathy and increased social isolation, despite being more "connected" than ever.

    In conclusion, while social media offers benefits, its impact on mental health cannot be ignored. As a society, we must develop healthier relationships with these technologies and implement safeguards to protect vulnerable populations from their potentially harmful effects.
    """
    
    # Test 1: Overall feedback only
    print("Test 1: Generating prompt for overall feedback only")
    print("-" * 50)
    
    context1 = PromptContext(
        assignment=assignment,
        rubric_categories=categories,
        student_submission=student_submission,
        draft_version=1,
        max_drafts=3,
        feedback_style=feedback_style,
        feedback_level="overall",
        word_count=len(student_submission.split())
    )
    
    template1 = create_prompt_template("iterative")
    prompt1 = template1.generate_prompt(context1)
    print(prompt1[:500] + "...\n")
    
    # Test 2: Criterion-specific feedback
    print("\nTest 2: Generating prompt for criterion-specific feedback")
    print("-" * 50)
    
    context2 = PromptContext(
        assignment=assignment,
        rubric_categories=categories,
        student_submission=student_submission,
        draft_version=2,
        max_drafts=3,
        feedback_style=feedback_style,
        feedback_level="criterion",
        word_count=len(student_submission.split())
    )
    
    template2 = create_prompt_template("iterative")
    prompt2 = template2.generate_prompt(context2)
    print(prompt2[:500] + "...\n")
    
    # Test 3: Combined feedback (both overall and criterion)
    print("\nTest 3: Generating prompt for combined feedback")
    print("-" * 50)
    
    context3 = PromptContext(
        assignment=assignment,
        rubric_categories=categories,
        student_submission=student_submission,
        draft_version=3,
        max_drafts=3,
        feedback_style=None,  # No specific style
        feedback_level="both",
        word_count=len(student_submission.split())
    )
    
    template3 = create_prompt_template("standard")
    prompt3 = template3.generate_prompt(context3)
    
    # Show the JSON format instructions
    print("\nJSON Format Instructions:")
    print("-" * 50)
    json_instructions = template3._get_json_format_instructions(context3)
    print(json_instructions)
    
    print("\n✅ Prompt template system test complete!")


if __name__ == "__main__":
    test_prompt_generation()