"""
Rubric generation service using AI to extract or create rubrics from assignment specifications
"""

import json
from typing import Dict, List, Optional, Tuple

from app.utils.ai_client import get_ai_client


def generate_rubric_from_spec(
    assignment_title: str,
    assignment_instructions: str,
    spec_content: Optional[str] = None,
    assignment_type: str = "essay"
) -> Tuple[bool, List[Dict[str, any]], str]:
    """
    Generate a rubric from assignment specification using AI.
    
    Args:
        assignment_title: Title of the assignment
        assignment_instructions: Brief instructions
        spec_content: Full specification text content (if uploaded)
        assignment_type: Type of assignment (essay, research, presentation, etc.)
    
    Returns:
        Tuple of (success, rubric_categories, error_message)
        rubric_categories is a list of dicts with 'name', 'description', 'weight'
    """
    
    # Combine all available information
    context = f"Assignment Title: {assignment_title}\n\n"
    context += f"Instructions: {assignment_instructions}\n\n"
    
    if spec_content:
        context += f"Full Specification:\n{spec_content}\n\n"
    
    # Create the prompt for rubric generation
    prompt = f"""
    You are an educational assessment expert. Based on the following assignment information, 
    generate a comprehensive rubric for evaluating student submissions.
    
    {context}
    
    Create a rubric with 4-6 categories that cover the essential aspects of this assignment.
    Each category should have:
    - A clear, concise name (2-3 words)
    - A detailed description of what is being evaluated
    - A weight percentage (all weights should sum to 100%)
    
    Focus on academic criteria relevant to the assignment type and learning objectives.
    
    Return ONLY a valid JSON array of rubric categories in this exact format:
    [
        {{
            "name": "Category Name",
            "description": "Detailed description of what this category evaluates...",
            "weight": 25
        }},
        ...
    ]
    
    Ensure the weights sum to exactly 100.
    """
    
    try:
        # Get AI client
        ai_client = get_ai_client()
        
        # Generate rubric
        response = ai_client.generate(
            prompt=prompt,
            system_prompt="You are an expert educator creating assessment rubrics. Return only valid JSON.",
            max_tokens=1500,
            temperature=0.7
        )
        
        # Parse the JSON response
        # Clean response - remove any markdown code blocks
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        # Parse JSON
        rubric_categories = json.loads(cleaned_response)
        
        # Validate the rubric
        if not isinstance(rubric_categories, list):
            return False, [], "Invalid rubric format: expected a list of categories"
        
        if len(rubric_categories) < 3:
            return False, [], "Rubric must have at least 3 categories"
        
        if len(rubric_categories) > 8:
            return False, [], "Rubric should not have more than 8 categories"
        
        # Validate each category and check weights
        total_weight = 0
        for category in rubric_categories:
            if not all(key in category for key in ['name', 'description', 'weight']):
                return False, [], "Each category must have name, description, and weight"
            
            if not isinstance(category['weight'], (int, float)):
                return False, [], f"Invalid weight for category {category['name']}"
            
            total_weight += category['weight']
        
        # Adjust weights if they don't sum to 100 (allow small rounding errors)
        if abs(total_weight - 100) > 0.1:
            # Normalize weights to sum to 100
            for category in rubric_categories:
                category['weight'] = round((category['weight'] / total_weight) * 100, 1)
        
        return True, rubric_categories, ""
        
    except json.JSONDecodeError as e:
        return False, [], f"Failed to parse AI response as JSON: {str(e)}"
    except Exception as e:
        return False, [], f"Error generating rubric: {str(e)}"


def get_rubric_template(template_type: str) -> List[Dict[str, any]]:
    """
    Get a pre-defined rubric template for common assignment types.
    
    Args:
        template_type: Type of template (essay, research, presentation, code)
    
    Returns:
        List of rubric categories with name, description, weight
    """
    
    templates = {
        "essay": [
            {
                "name": "Thesis & Argument",
                "description": "Clear thesis statement, logical argument development, and persuasive reasoning throughout the essay",
                "weight": 25
            },
            {
                "name": "Evidence & Support",
                "description": "Use of relevant evidence, examples, and citations to support claims. Quality and integration of sources",
                "weight": 25
            },
            {
                "name": "Organization & Structure",
                "description": "Clear introduction, body paragraphs with topic sentences, smooth transitions, and effective conclusion",
                "weight": 20
            },
            {
                "name": "Writing Quality",
                "description": "Grammar, spelling, sentence variety, word choice, and overall clarity of expression",
                "weight": 20
            },
            {
                "name": "Critical Thinking",
                "description": "Depth of analysis, original insights, consideration of counterarguments, and sophistication of thought",
                "weight": 10
            }
        ],
        "research": [
            {
                "name": "Research Question",
                "description": "Clear, focused, and significant research question or hypothesis that guides the investigation",
                "weight": 15
            },
            {
                "name": "Literature Review",
                "description": "Comprehensive review of relevant sources, synthesis of existing knowledge, and identification of gaps",
                "weight": 25
            },
            {
                "name": "Methodology",
                "description": "Appropriate research methods, clear explanation of approach, and justification of choices",
                "weight": 20
            },
            {
                "name": "Analysis & Results",
                "description": "Thorough analysis of data/findings, clear presentation of results, and accurate interpretation",
                "weight": 25
            },
            {
                "name": "Conclusions",
                "description": "Well-supported conclusions, acknowledgment of limitations, and suggestions for future research",
                "weight": 15
            }
        ],
        "presentation": [
            {
                "name": "Content & Knowledge",
                "description": "Accuracy of information, depth of understanding, and relevance to topic",
                "weight": 30
            },
            {
                "name": "Organization",
                "description": "Logical flow, clear introduction and conclusion, smooth transitions between sections",
                "weight": 20
            },
            {
                "name": "Delivery",
                "description": "Eye contact, voice projection, pace, enthusiasm, and engagement with audience",
                "weight": 20
            },
            {
                "name": "Visual Aids",
                "description": "Quality and effectiveness of slides, handouts, or other visual materials",
                "weight": 15
            },
            {
                "name": "Q&A Handling",
                "description": "Ability to answer questions clearly and demonstrate deeper understanding",
                "weight": 15
            }
        ],
        "code": [
            {
                "name": "Functionality",
                "description": "Code runs correctly, meets all requirements, handles edge cases appropriately",
                "weight": 35
            },
            {
                "name": "Code Quality",
                "description": "Clean, readable code with proper naming conventions, appropriate comments, and good structure",
                "weight": 25
            },
            {
                "name": "Algorithm Design",
                "description": "Efficient algorithms, appropriate data structures, and optimization where relevant",
                "weight": 20
            },
            {
                "name": "Testing",
                "description": "Comprehensive test cases, error handling, and validation of inputs",
                "weight": 10
            },
            {
                "name": "Documentation",
                "description": "Clear README, inline comments, and explanation of design decisions",
                "weight": 10
            }
        ]
    }
    
    return templates.get(template_type, templates["essay"])


def extract_rubric_from_text(text: str) -> Tuple[bool, List[Dict[str, any]], str]:
    """
    Try to extract an existing rubric from assignment specification text.
    
    Args:
        text: The assignment specification text
    
    Returns:
        Tuple of (success, rubric_categories, error_message)
    """
    
    # Check if text seems to contain a rubric
    rubric_indicators = [
        "rubric", "grading criteria", "evaluation criteria", 
        "assessment criteria", "scoring guide", "grading scale"
    ]
    
    has_rubric = any(indicator in text.lower() for indicator in rubric_indicators)
    
    if not has_rubric:
        return False, [], "No rubric found in specification"
    
    # Use AI to extract the rubric
    prompt = f"""
    Extract the grading rubric from the following assignment specification.
    Look for sections that describe evaluation criteria, point distributions, or grading categories.
    
    Text:
    {text}
    
    If a rubric is found, convert it to a JSON array with categories.
    Each category should have: name, description, and weight (as a percentage).
    
    If percentages/points are given, convert to percentages that sum to 100.
    If no weights are given, distribute evenly.
    
    Return ONLY a valid JSON array in this format:
    [
        {{
            "name": "Category Name",
            "description": "What this category evaluates",
            "weight": 25
        }}
    ]
    
    If no clear rubric is found, return: {{"error": "No rubric found"}}
    """
    
    try:
        ai_client = get_ai_client()
        
        response = ai_client.generate(
            prompt=prompt,
            system_prompt="You are an expert at extracting rubrics from academic documents. Return only valid JSON.",
            max_tokens=1500,
            temperature=0.3  # Lower temperature for extraction task
        )
        
        # Clean and parse response
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        parsed = json.loads(cleaned_response)
        
        # Check if it's an error response
        if isinstance(parsed, dict) and "error" in parsed:
            return False, [], parsed["error"]
        
        # Validate as rubric categories
        if isinstance(parsed, list) and len(parsed) > 0:
            # Ensure weights sum to 100
            total_weight = sum(cat.get('weight', 0) for cat in parsed)
            if total_weight > 0 and abs(total_weight - 100) > 0.1:
                for cat in parsed:
                    cat['weight'] = round((cat.get('weight', 100/len(parsed)) / total_weight) * 100, 1)
            
            return True, parsed, ""
        
        return False, [], "Could not extract valid rubric structure"
        
    except Exception as e:
        return False, [], f"Error extracting rubric: {str(e)}"