---
layout: default
title: AI Integration
parent: Technical Documentation
nav_order: 4
---

# AI Integration Architecture
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

FeedForward's AI integration provides sophisticated, multi-model feedback generation with a focus on educational effectiveness, consistency, and privacy. The system orchestrates multiple AI providers, aggregates their outputs, and ensures pedagogically sound feedback aligned with instructor-defined rubrics.

## Architecture Overview

### High-Level Flow

```
Student Submission
       ↓
┌─────────────────────────────┐
│   Feedback Generator        │
│  ┌────────────────────┐     │
│  │ Prompt Engineering │     │
│  └────────┬───────────┘     │
│           ↓                 │
│  ┌────────────────────┐     │
│  │ Model Orchestrator │     │
│  └────────┬───────────┘     │
│           ↓                 │
│  ┌────────────────────┐     │
│  │ Response Parsing   │     │
│  └────────┬───────────┘     │
│           ↓                 │
│  ┌────────────────────┐     │
│  │ Result Aggregation │     │
│  └────────┬───────────┘     │
└───────────┼─────────────────┘
            ↓
    Instructor Review
            ↓
    Student Receives Feedback
```

### Core Components

```yaml
AI Integration Stack:
  Provider Layer:
    - LiteLLM (unified interface)
    - Provider-specific configs
    - API key management
    
  Orchestration Layer:
    - FeedbackGenerator service
    - Async task processing
    - Concurrent model execution
    
  Intelligence Layer:
    - Prompt templates
    - Response parsing
    - Result aggregation
    
  Storage Layer:
    - Model configurations
    - Feedback results
    - Audit logging
```

## Provider Integration

### Supported Providers

FeedForward integrates with multiple LLM providers through LiteLLM:

```python
SUPPORTED_PROVIDERS = {
    'openai': {
        'models': ['gpt-4', 'gpt-3.5-turbo'],
        'config_fields': ['api_key', 'organization'],
        'capabilities': ['text', 'vision']
    },
    'anthropic': {
        'models': ['claude-3-opus', 'claude-3-sonnet'],
        'config_fields': ['api_key'],
        'capabilities': ['text', 'vision']
    },
    'google': {
        'models': ['gemini-pro', 'gemini-pro-vision'],
        'config_fields': ['api_key'],
        'capabilities': ['text', 'vision']
    },
    'ollama': {
        'models': ['llama3', 'mixtral', 'phi3'],
        'config_fields': ['base_url'],
        'capabilities': ['text']
    }
}
```

### Provider Configuration

Each provider requires specific configuration:

```python
# OpenAI Configuration
{
    'api_key': 'sk-...',  # Required
    'organization': 'org-...',  # Optional
    'api_base': 'https://api.openai.com/v1',  # Optional proxy
    'api_version': '2024-02-01'  # For Azure OpenAI
}

# Anthropic Configuration
{
    'api_key': 'sk-ant-...',  # Required
    'max_retries': 3,  # Optional
    'timeout': 30  # Optional
}

# Ollama Configuration
{
    'base_url': 'http://localhost:11434',  # Required
    'timeout': 120  # Longer for local models
}
```

### Model Selection

Models are selected based on:
1. Assignment configuration
2. Provider availability
3. Cost considerations
4. Performance requirements

```python
# Assignment model configuration
assignment_models = [
    {
        'model_id': 'gpt-4',
        'runs': 3,
        'temperature': 0.7,
        'max_tokens': 2000
    },
    {
        'model_id': 'claude-3-opus',
        'runs': 2,
        'temperature': 0.6,
        'max_tokens': 2500
    }
]
```

## Prompt Engineering

### Prompt Template System

The system uses sophisticated prompt templates that incorporate:

```python
# Core prompt components
prompt_components = {
    'role_definition': "Expert educator providing constructive feedback",
    'task_description': "Analyze student submission against rubric",
    'output_format': "Structured JSON with scores and feedback",
    'constraints': "Be encouraging, specific, and actionable"
}
```

### Dynamic Prompt Generation

Prompts are dynamically generated based on:

```python
def generate_feedback_prompt(
    assignment: Assignment,
    student_submission: str,
    draft_version: int,
    previous_feedback: Optional[str] = None,
    feedback_style: str = "balanced"
) -> str:
    
    # Build context
    context = {
        'assignment_title': assignment.title,
        'instructions': assignment.description,
        'draft_number': draft_version,
        'max_drafts': assignment.max_drafts,
        'rubric': format_rubric(assignment.rubric),
        'style_guide': FEEDBACK_STYLES[feedback_style]
    }
    
    # Include iteration context
    if previous_feedback:
        context['previous_feedback'] = previous_feedback
        context['focus'] = "improvement from previous draft"
    
    return render_prompt(context)
```

### Rubric Integration

Rubrics are formatted for AI comprehension:

```json
{
  "rubric_criteria": [
    {
      "name": "Thesis Statement",
      "weight": 20,
      "description": "Clear, arguable thesis that previews main points",
      "excellent": "Thesis is compelling, specific, and perfectly positioned",
      "good": "Thesis is clear and arguable with minor improvements needed",
      "satisfactory": "Thesis present but could be more specific or clear",
      "needs_improvement": "Thesis is unclear, too broad, or missing"
    }
  ]
}
```

### Feedback Styles

Four feedback styles adapt AI responses:

```python
FEEDBACK_STYLES = {
    'balanced': {
        'tone': 'Professional and constructive',
        'emphasis': 'Equal focus on strengths and improvements',
        'detail_level': 'Moderate'
    },
    'encouraging': {
        'tone': 'Warm and supportive',
        'emphasis': 'Highlight strengths, gentle on improvements',
        'detail_level': 'High on positives'
    },
    'critical': {
        'tone': 'Direct and analytical',
        'emphasis': 'Focus on areas needing improvement',
        'detail_level': 'Detailed on issues'
    },
    'detailed': {
        'tone': 'Comprehensive and thorough',
        'emphasis': 'Everything analyzed in depth',
        'detail_level': 'Very high'
    }
}
```

## Model Orchestration

### Asynchronous Execution

Models run concurrently for efficiency:

```python
async def run_models_concurrently(models, prompt):
    tasks = []
    for model in models:
        for run in range(model.runs):
            task = asyncio.create_task(
                execute_model_run(model, prompt, run)
            )
            tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]
```

### Retry Mechanism

Robust retry logic handles transient failures:

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(APIError)
)
async def call_model_with_retry(model_config, prompt):
    try:
        response = await litellm.acompletion(
            model=model_config['model_id'],
            messages=[{"role": "user", "content": prompt}],
            temperature=model_config.get('temperature', 0.7),
            max_tokens=model_config.get('max_tokens', 2000),
            response_format={"type": "json_object"}
        )
        return response
    except Exception as e:
        logger.error(f"Model call failed: {e}")
        raise
```

### Response Parsing

Structured response parsing with fallbacks:

```python
def parse_model_response(raw_response: str) -> FeedbackResult:
    try:
        # Primary: Parse as JSON
        data = json.loads(raw_response)
        return FeedbackResult(
            overall_score=data['overall_score'],
            overall_feedback=data['overall_feedback'],
            category_scores=data['category_scores'],
            category_feedback=data['category_feedback']
        )
    except json.JSONDecodeError:
        # Fallback: Extract using regex patterns
        return parse_with_patterns(raw_response)
    except Exception:
        # Final fallback: Basic extraction
        return create_minimal_feedback(raw_response)
```

## Result Aggregation

### Aggregation Methods

Four aggregation strategies for combining model outputs:

#### 1. Mean (Average)
Simple arithmetic mean of all scores:
```python
def aggregate_mean(scores: List[float]) -> float:
    return sum(scores) / len(scores)
```

#### 2. Weighted Mean
Weights based on model confidence or priority:
```python
def aggregate_weighted_mean(
    scores: List[float], 
    weights: List[float]
) -> float:
    total_weight = sum(weights)
    weighted_sum = sum(s * w for s, w in zip(scores, weights))
    return weighted_sum / total_weight
```

#### 3. Median
Middle value, resistant to outliers:
```python
def aggregate_median(scores: List[float]) -> float:
    sorted_scores = sorted(scores)
    n = len(sorted_scores)
    if n % 2 == 0:
        return (sorted_scores[n//2-1] + sorted_scores[n//2]) / 2
    return sorted_scores[n//2]
```

#### 4. Trimmed Mean
Remove extremes before averaging:
```python
def aggregate_trimmed_mean(
    scores: List[float], 
    trim_percent: float = 0.1
) -> float:
    sorted_scores = sorted(scores)
    trim_count = int(len(sorted_scores) * trim_percent)
    trimmed = sorted_scores[trim_count:-trim_count or None]
    return sum(trimmed) / len(trimmed)
```

### Feedback Aggregation

Textual feedback aggregation uses frequency analysis:

```python
def aggregate_feedback_items(
    feedback_items: List[FeedbackItem],
    category_id: int
) -> AggregatedFeedback:
    # Group similar feedback
    grouped = group_similar_feedback(feedback_items)
    
    # Extract most frequent themes
    themes = extract_common_themes(grouped, min_frequency=0.6)
    
    # Combine into coherent feedback
    combined_text = synthesize_feedback(themes)
    
    return AggregatedFeedback(
        category_id=category_id,
        feedback_text=combined_text,
        confidence=calculate_agreement_score(feedback_items)
    )
```

## Background Processing

### Task Queue Architecture

Feedback generation runs asynchronously:

```python
# Task creation
task_id = await create_background_task(
    task_type="generate_feedback",
    params={
        "draft_id": draft.id,
        "assignment_id": assignment.id,
        "priority": "normal"
    }
)

# Task processing
async def process_feedback_task(task):
    try:
        # Update draft status
        await update_draft_status(task.draft_id, "processing")
        
        # Generate feedback
        result = await generate_feedback(task.draft_id)
        
        # Store results
        await store_feedback_results(result)
        
        # Update status
        await update_draft_status(task.draft_id, "feedback_ready")
        
    except Exception as e:
        await handle_task_failure(task, e)
```

### Task Monitoring

Track task progress and performance:

```yaml
Task Metrics:
  Queue Length: Current tasks waiting
  Processing Time: Average per task
  Success Rate: Completed vs failed
  Retry Count: Tasks requiring retry
  
Performance Targets:
  Queue Time: < 30 seconds
  Processing Time: < 2 minutes
  Success Rate: > 95%
  Max Retries: 3
```

## Privacy & Security

### Data Handling

Privacy-first approach to AI processing:

```python
class PrivacyAwareFeedbackGenerator:
    async def generate_feedback(self, draft_id: int):
        # Load submission
        draft = await load_draft(draft_id)
        
        try:
            # Generate feedback
            feedback = await self._process_with_ai(draft.content)
            
            # Store results
            await store_feedback(feedback)
            
        finally:
            # Always clean up
            if not draft.content_preserved:
                await remove_draft_content(draft_id)
                await log_content_removal(draft_id)
```

### API Key Security

Encrypted storage and secure access:

```python
class SecureModelConfig:
    def __init__(self, encrypted_config: str):
        self._cipher = Fernet(self._get_key())
        self._config = json.loads(
            self._cipher.decrypt(encrypted_config.encode())
        )
    
    def get_api_key(self) -> str:
        # Decrypt only when needed
        return self._config.get('api_key')
    
    def __del__(self):
        # Clear sensitive data
        self._config = None
```

## Performance Optimization

### Caching Strategy

Reduce redundant AI calls:

```python
# Cache rubric interpretations
@lru_cache(maxsize=100)
def get_rubric_prompt_section(rubric_id: int) -> str:
    rubric = load_rubric(rubric_id)
    return format_rubric_for_ai(rubric)

# Cache model configurations
@ttl_cache(ttl=3600)  # 1 hour
def get_model_config(model_id: int) -> dict:
    return load_and_decrypt_model_config(model_id)
```

### Batch Processing

Efficient handling of multiple submissions:

```python
async def batch_process_submissions(submissions: List[Draft]):
    # Group by assignment for rubric reuse
    grouped = group_by_assignment(submissions)
    
    for assignment_id, drafts in grouped.items():
        # Load shared resources once
        rubric = await load_rubric(assignment_id)
        models = await load_models(assignment_id)
        
        # Process in parallel batches
        batch_size = 5
        for batch in chunks(drafts, batch_size):
            await asyncio.gather(*[
                generate_feedback(d.id, rubric, models)
                for d in batch
            ])
```

## Monitoring & Analytics

### AI Usage Tracking

Monitor model performance and costs:

```sql
-- Track per-model metrics
CREATE VIEW ai_model_metrics AS
SELECT 
    model_id,
    COUNT(*) as total_calls,
    AVG(response_time) as avg_response_time,
    SUM(token_count) as total_tokens,
    SUM(estimated_cost) as total_cost,
    AVG(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_rate
FROM model_runs
GROUP BY model_id;
```

### Quality Metrics

Track feedback effectiveness:

```python
class FeedbackQualityAnalyzer:
    def analyze_feedback_quality(self, feedback_id: int):
        metrics = {
            'specificity': self.measure_specificity(feedback.text),
            'actionability': self.measure_actionability(feedback.text),
            'alignment': self.measure_rubric_alignment(feedback),
            'sentiment': self.analyze_sentiment(feedback.text),
            'length': len(feedback.text.split()),
            'readability': self.calculate_readability_score(feedback.text)
        }
        return metrics
```

## Configuration Management

### Assignment-Level Settings

Fine-grained control per assignment:

```yaml
Assignment AI Configuration:
  Models:
    - Model: gpt-4
      Runs: 3
      Temperature: 0.7
      Weight: 0.6
    - Model: claude-3
      Runs: 2
      Temperature: 0.6
      Weight: 0.4
      
  Aggregation:
    Method: weighted_mean
    Trim: 0.1
    
  Feedback:
    Level: both  # overall + criterion
    Style: encouraging
    Max_length: 2000
    
  Review:
    Required: true
    Auto_release: false
```

### System Defaults

Global defaults for consistency:

```python
DEFAULT_AI_CONFIG = {
    'primary_model': 'gpt-4',
    'fallback_model': 'gpt-3.5-turbo',
    'temperature': 0.7,
    'max_tokens': 2000,
    'runs_per_model': 3,
    'aggregation_method': 'mean',
    'feedback_style': 'balanced',
    'require_instructor_review': True
}
```

## Future Enhancements

### Planned Improvements

1. **Adaptive Prompting**
   - Learn from instructor edits
   - Personalize to student level
   - Context-aware adjustments

2. **Multi-Modal Support**
   - Image analysis for visual assignments
   - Code evaluation for programming
   - Audio feedback generation

3. **Advanced Analytics**
   - Predictive scoring models
   - Improvement trajectory analysis
   - Cohort comparison insights

4. **Real-Time Features**
   - Streaming feedback generation
   - Progressive result display
   - Live collaboration tools

---

{: .note }
> The AI integration is designed to be educator-first, ensuring that technology enhances rather than replaces human judgment in the educational process.