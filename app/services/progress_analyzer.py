"""
Draft progress analysis and comparison service.
Analyzes improvements between drafts and generates progress insights.
"""

import json
from typing import Any, Optional

from app.models.feedback import AggregatedFeedback, Draft


class ProgressAnalyzer:
    """Analyzes student progress across multiple drafts."""

    def __init__(self, drafts: list[Draft], feedback_list: list[AggregatedFeedback]):
        """
        Initialize the progress analyzer.

        Args:
            drafts: List of student drafts for an assignment
            feedback_list: List of aggregated feedback for the drafts
        """
        self.drafts = sorted(drafts, key=lambda d: d.version)
        self.feedback_by_draft = self._organize_feedback(feedback_list)

    def _organize_feedback(self, feedback_list: list[AggregatedFeedback]) -> dict[int, AggregatedFeedback]:
        """Organize feedback by draft ID for easy lookup."""
        feedback_dict = {}
        for feedback in feedback_list:
            if feedback.draft_id not in feedback_dict:
                feedback_dict[feedback.draft_id] = feedback
        return feedback_dict

    def get_score_progression(self) -> list[dict[str, Any]]:
        """
        Get score progression across all drafts.

        Returns:
            List of dictionaries containing draft version, score, and submission date
        """
        progression = []
        for draft in self.drafts:
            feedback = self.feedback_by_draft.get(draft.id)
            if feedback:
                try:
                    score = float(getattr(feedback, 'overall_score', 0))
                except (ValueError, TypeError):
                    score = 0
            else:
                score = 0

            progression.append({
                'version': draft.version,
                'score': score,
                'submission_date': draft.submission_date,
                'word_count': getattr(draft, 'word_count', 0),
                'has_feedback': feedback is not None
            })
        return progression

    def get_category_progression(self, rubric_categories: list[Any]) -> dict[str, list[dict[str, Any]]]:
        """
        Get score progression for each rubric category.

        Args:
            rubric_categories: List of rubric category objects

        Returns:
            Dictionary mapping category names to their score progression
        """
        category_progression: dict[str, list[dict[str, Any]]] = {cat.name: [] for cat in rubric_categories}

        for draft in self.drafts:
            feedback = self.feedback_by_draft.get(draft.id)
            if feedback and hasattr(feedback, 'category_scores'):
                try:
                    if isinstance(feedback.category_scores, str):
                        category_scores = json.loads(feedback.category_scores)
                    else:
                        category_scores = feedback.category_scores or {}
                except (json.JSONDecodeError, TypeError):
                    category_scores = {}

                for cat in rubric_categories:
                    cat_score_data = category_scores.get(cat.name, {})
                    if isinstance(cat_score_data, dict):
                        score = cat_score_data.get('score', 0)
                    else:
                        score = float(cat_score_data) if cat_score_data else 0

                    category_progression[cat.name].append({
                        'version': draft.version,
                        'score': score,
                        'has_feedback': True
                    })
            else:
                # No feedback for this draft
                for cat in rubric_categories:
                    category_progression[cat.name].append({
                        'version': draft.version,
                        'score': 0,
                        'has_feedback': False
                    })

        return category_progression

    def compare_drafts(self, draft1_version: int, draft2_version: int) -> dict[str, Any]:
        """
        Compare two specific draft versions.

        Args:
            draft1_version: Version number of first draft
            draft2_version: Version number of second draft

        Returns:
            Dictionary containing comparison data
        """
        draft1 = next((d for d in self.drafts if d.version == draft1_version), None)
        draft2 = next((d for d in self.drafts if d.version == draft2_version), None)

        if not draft1 or not draft2:
            return {'error': 'One or both drafts not found'}

        feedback1 = self.feedback_by_draft.get(draft1.id)
        feedback2 = self.feedback_by_draft.get(draft2.id)

        # Get scores
        score1 = 0.0
        score2 = 0.0
        if feedback1:
            try:
                score1 = float(getattr(feedback1, 'overall_score', 0))
            except (ValueError, TypeError):
                score1 = 0
        if feedback2:
            try:
                score2 = float(getattr(feedback2, 'overall_score', 0))
            except (ValueError, TypeError):
                score2 = 0

        # Calculate changes
        score_change = score2 - score1
        word_count_change = (getattr(draft2, 'word_count', 0) or 0) - (getattr(draft1, 'word_count', 0) or 0)

        # Extract key changes from feedback
        changes_summary = self._extract_changes_summary(feedback1, feedback2)

        return {
            'draft1': {
                'version': draft1.version,
                'score': score1,
                'word_count': getattr(draft1, 'word_count', 0),
                'submission_date': draft1.submission_date
            },
            'draft2': {
                'version': draft2.version,
                'score': score2,
                'word_count': getattr(draft2, 'word_count', 0),
                'submission_date': draft2.submission_date
            },
            'changes': {
                'score_change': score_change,
                'score_change_percent': (score_change / score1 * 100) if score1 > 0 else 0,
                'word_count_change': word_count_change,
                'improvement_areas': changes_summary.get('improvements', []),
                'regression_areas': changes_summary.get('regressions', []),
                'maintained_strengths': changes_summary.get('maintained', [])
            }
        }

    def _extract_changes_summary(self, feedback1: Optional[AggregatedFeedback],
                                  feedback2: Optional[AggregatedFeedback]) -> dict[str, list[str]]:
        """
        Extract a summary of changes between two feedback instances.

        Args:
            feedback1: First feedback instance
            feedback2: Second feedback instance

        Returns:
            Dictionary with improvements, regressions, and maintained strengths
        """
        summary: dict[str, list[str]] = {
            'improvements': [],
            'regressions': [],
            'maintained': []
        }

        if not feedback1 or not feedback2:
            return summary

        # Parse category scores for both drafts
        try:
            if hasattr(feedback1, 'category_scores'):
                if isinstance(feedback1.category_scores, str):
                    cat_scores1 = json.loads(feedback1.category_scores)
                else:
                    cat_scores1 = feedback1.category_scores or {}
            else:
                cat_scores1 = {}

            if hasattr(feedback2, 'category_scores'):
                if isinstance(feedback2.category_scores, str):
                    cat_scores2 = json.loads(feedback2.category_scores)
                else:
                    cat_scores2 = feedback2.category_scores or {}
            else:
                cat_scores2 = {}
        except (json.JSONDecodeError, TypeError):
            return summary

        # Compare category scores
        for category, score_data2 in cat_scores2.items():
            score_data1 = cat_scores1.get(category, {})

            if isinstance(score_data1, dict):
                score1 = score_data1.get('score', 0)
            else:
                score1 = float(score_data1) if score_data1 else 0

            if isinstance(score_data2, dict):
                score2 = score_data2.get('score', 0)
            else:
                score2 = float(score_data2) if score_data2 else 0

            change = score2 - score1
            if change > 5:  # Significant improvement
                summary['improvements'].append(f"{category}: +{change:.1f} points")
            elif change < -5:  # Significant regression
                summary['regressions'].append(f"{category}: {change:.1f} points")
            elif score2 >= 80:  # Maintained strength
                summary['maintained'].append(f"{category}: {score2:.0f}/100")

        return summary

    def get_improvement_metrics(self) -> dict[str, Any]:
        """
        Calculate overall improvement metrics across all drafts.

        Returns:
            Dictionary containing various improvement metrics
        """
        if len(self.drafts) < 2:
            return {
                'total_improvement': 0,
                'average_improvement_per_draft': 0,
                'best_improvement': 0,
                'consistency_score': 0,
                'drafts_submitted': len(self.drafts)
            }

        progression = self.get_score_progression()
        scores = [p['score'] for p in progression if p['has_feedback']]

        if len(scores) < 2:
            return {
                'total_improvement': 0,
                'average_improvement_per_draft': 0,
                'best_improvement': 0,
                'consistency_score': 0,
                'drafts_submitted': len(self.drafts)
            }

        # Calculate metrics
        total_improvement = scores[-1] - scores[0]
        average_improvement = total_improvement / (len(scores) - 1)

        # Find best single improvement
        best_improvement = 0
        for i in range(1, len(scores)):
            improvement = scores[i] - scores[i-1]
            if improvement > best_improvement:
                best_improvement = improvement

        # Calculate consistency (lower variance = more consistent)
        improvements = [scores[i] - scores[i-1] for i in range(1, len(scores))]
        if improvements:
            avg_imp = sum(improvements) / len(improvements)
            variance = sum((imp - avg_imp) ** 2 for imp in improvements) / len(improvements)
            # Convert variance to a 0-100 consistency score (lower variance = higher score)
            consistency_score = max(0, 100 - variance)
        else:
            consistency_score = 0

        return {
            'total_improvement': total_improvement,
            'average_improvement_per_draft': average_improvement,
            'best_improvement': best_improvement,
            'consistency_score': consistency_score,
            'drafts_submitted': len(self.drafts),
            'drafts_with_feedback': len(scores),
            'current_score': scores[-1] if scores else 0,
            'initial_score': scores[0] if scores else 0
        }

    def get_next_steps_recommendations(self, latest_feedback: Optional[AggregatedFeedback],
                                        rubric_categories: list[Any]) -> list[dict[str, Any]]:
        """
        Generate prioritized recommendations for the next draft.

        Args:
            latest_feedback: The most recent feedback
            rubric_categories: List of rubric categories

        Returns:
            List of prioritized recommendations
        """
        recommendations: list[dict[str, Any]] = []

        if not latest_feedback:
            return recommendations

        # Parse category scores
        try:
            if hasattr(latest_feedback, 'category_scores'):
                if isinstance(latest_feedback.category_scores, str):
                    category_scores = json.loads(latest_feedback.category_scores)
                else:
                    category_scores = latest_feedback.category_scores or {}
            else:
                category_scores = {}
        except (json.JSONDecodeError, TypeError):
            category_scores = {}

        # Analyze each category and generate recommendations
        for cat in rubric_categories:
            cat_score_data = category_scores.get(cat.name, {})
            if isinstance(cat_score_data, dict):
                score = cat_score_data.get('score', 0)
                cat_score_data.get('feedback', '')
            else:
                score = float(cat_score_data) if cat_score_data else 0

            # Generate recommendations based on score
            if score < 60:
                priority = 'high'
                action = 'Critical improvement needed'
            elif score < 75:
                priority = 'medium'
                action = 'Focus area for improvement'
            elif score < 90:
                priority = 'low'
                action = 'Minor refinements suggested'
            else:
                continue  # Skip categories with excellent scores

            recommendations.append({
                'category': cat.name,
                'current_score': score,
                'weight': cat.weight,
                'priority': priority,
                'action': action,
                'potential_impact': cat.weight * ((100 - score) / 100),  # How much this could improve overall score
                'description': cat.description
            })

        # Sort by potential impact (highest first)
        recommendations.sort(key=lambda x: x['potential_impact'], reverse=True)

        return recommendations[:5]  # Return top 5 recommendations
