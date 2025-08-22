"""
Instructor analytics and performance dashboard routes
"""

import statistics

from fasthtml.common import *
from fastlite import NotFoundError
from starlette.responses import RedirectResponse

from app import instructor_required, rt
from app.models.assignment import assignments, rubric_categories
from app.models.config import ai_models
from app.models.course import courses
from app.models.feedback import aggregated_feedback, category_scores, drafts, model_runs
from app.models.user import Role, users
from app.utils.ui import dashboard_layout


@rt("/instructor/assignments/{assignment_id}/analytics")
@instructor_required
def instructor_assignment_analytics(session, assignment_id: int):
    """Analytics dashboard for assignment performance and LLM effectiveness"""
    # Get current user and verify access
    user = users[session["auth"]]

    try:
        assignment = assignments[assignment_id]
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return RedirectResponse("/instructor/dashboard", status_code=303)

    # Get all drafts for this assignment
    all_drafts = drafts()
    assignment_drafts = [d for d in all_drafts if d.assignment_id == assignment_id]

    # Get rubric categories
    rubric_cats = rubric_categories()
    assignment_rubric = [
        cat for cat in rubric_cats if cat.assignment_id == assignment_id
    ]

    # Get all model runs
    all_runs = model_runs()
    assignment_runs = [
        run for run in all_runs if any(d.id == run.draft_id for d in assignment_drafts)
    ]

    # Get all AI models
    all_ai_models = ai_models()
    models_map = {model.id: model for model in all_ai_models}

    # Get scores and aggregated feedback
    all_scores = category_scores()
    aggregated_feedback()

    # Calculate submission statistics
    total_submissions = len(assignment_drafts)
    completed_feedback = len(
        [d for d in assignment_drafts if d.status == "feedback_ready"]
    )
    processing = len([d for d in assignment_drafts if d.status == "processing"])
    errors = len([d for d in assignment_drafts if d.status == "error"])

    # Calculate LLM performance statistics
    llm_stats = {}
    for run in assignment_runs:
        model = models_map.get(run.model_id)
        if not model:
            continue

        model_key = f"{model.name} ({model.provider})"
        if model_key not in llm_stats:
            llm_stats[model_key] = {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "avg_response_time": 0,
                "scores": [],
            }

        llm_stats[model_key]["total_runs"] += 1
        if run.status == "complete":
            llm_stats[model_key]["successful_runs"] += 1

            # Get scores for this run
            run_scores = [score for score in all_scores if score.model_run_id == run.id]
            if run_scores:
                avg_score = statistics.mean([score.score for score in run_scores])
                llm_stats[model_key]["scores"].append(avg_score)
        else:
            llm_stats[model_key]["failed_runs"] += 1

    # Calculate category performance
    category_performance = {}
    for category in assignment_rubric:
        category_scores_list = [
            score.score
            for score in all_scores
            if score.category_id == category.id
            and any(
                run.id == score.model_run_id and run.status == "complete"
                for run in assignment_runs
            )
        ]

        if category_scores_list:
            category_performance[category.name] = {
                "avg_score": statistics.mean(category_scores_list),
                "min_score": min(category_scores_list),
                "max_score": max(category_scores_list),
                "std_dev": statistics.stdev(category_scores_list)
                if len(category_scores_list) > 1
                else 0,
                "count": len(category_scores_list),
            }

    # Build LLM comparison table
    llm_comparison_rows = []
    for model_name, stats in llm_stats.items():
        success_rate = (
            (stats["successful_runs"] / stats["total_runs"] * 100)
            if stats["total_runs"] > 0
            else 0
        )
        avg_score = statistics.mean(stats["scores"]) if stats["scores"] else 0

        # Success rate color coding
        if success_rate >= 90:
            rate_color = "text-green-600"
        elif success_rate >= 70:
            rate_color = "text-yellow-600"
        else:
            rate_color = "text-red-600"

        llm_comparison_rows.append(
            Tr(
                Td(model_name, cls="px-4 py-3 font-medium"),
                Td(f"{stats['total_runs']}", cls="px-4 py-3 text-center"),
                Td(
                    f"{success_rate:.1f}%",
                    cls=f"px-4 py-3 text-center {rate_color} font-semibold",
                ),
                Td(
                    f"{avg_score:.1f}/100" if avg_score > 0 else "—",
                    cls="px-4 py-3 text-center",
                ),
                Td(
                    f"{len(stats['scores'])}", cls="px-4 py-3 text-center text-gray-600"
                ),
            )
        )

    llm_comparison_table = (
        Div(
            H3("AI Model Performance Comparison", cls="text-lg font-semibold mb-4"),
            Table(
                Thead(
                    Tr(
                        Th(
                            "Model",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase",
                        ),
                        Th(
                            "Total Runs",
                            cls="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase",
                        ),
                        Th(
                            "Success Rate",
                            cls="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase",
                        ),
                        Th(
                            "Avg Score",
                            cls="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase",
                        ),
                        Th(
                            "Scored Runs",
                            cls="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase",
                        ),
                    )
                ),
                Tbody(*llm_comparison_rows, cls="bg-white divide-y divide-gray-200"),
                cls="min-w-full divide-y divide-gray-200",
            ),
            cls="bg-white rounded-lg shadow overflow-hidden mb-8",
        )
        if llm_comparison_rows
        else Div(
            P(
                "No model performance data available yet.",
                cls="text-gray-500 text-center py-8",
            ),
            cls="bg-white rounded-lg shadow mb-8",
        )
    )

    # Build category performance chart
    category_chart_bars = []
    for category_name, perf in category_performance.items():
        # Calculate bar width based on score (0-100 -> 0-100%)
        bar_width = perf["avg_score"]

        # Color coding based on score
        if bar_width >= 80:
            bar_color = "bg-green-500"
        elif bar_width >= 60:
            bar_color = "bg-yellow-500"
        else:
            bar_color = "bg-red-500"

        category_chart_bars.append(
            Div(
                Div(
                    Div(
                        P(category_name, cls="font-medium text-gray-900"),
                        P(
                            f"{perf['avg_score']:.1f}/100 avg ({perf['count']} submissions)",
                            cls="text-sm text-gray-600",
                        ),
                        cls="mb-2",
                    ),
                    Div(
                        Div(
                            cls=f"h-4 {bar_color} rounded", style=f"width: {bar_width}%"
                        ),
                        cls="w-full bg-gray-200 rounded-full h-4",
                    ),
                    cls="mb-4",
                ),
                cls="bg-white p-4 rounded-lg",
            )
        )

    category_performance_section = Div(
        H3("Rubric Category Performance", cls="text-lg font-semibold mb-4"),
        Div(*category_chart_bars, cls="space-y-4")
        if category_chart_bars
        else P(
            "No category performance data available.",
            cls="text-gray-500 text-center py-8",
        ),
        cls="mb-8",
    )

    # Summary statistics cards
    stats_cards = Div(
        Div(
            Div(
                P("Total Submissions", cls="text-sm font-medium text-gray-500"),
                P(str(total_submissions), cls="text-3xl font-bold text-gray-900"),
                P("Student drafts", cls="text-sm text-gray-600"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        Div(
            Div(
                P("Feedback Complete", cls="text-sm font-medium text-gray-500"),
                P(str(completed_feedback), cls="text-3xl font-bold text-green-600"),
                P(
                    f"{(completed_feedback / total_submissions * 100):.1f}% complete"
                    if total_submissions > 0
                    else "0% complete",
                    cls="text-sm text-gray-600",
                ),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        Div(
            Div(
                P("Processing", cls="text-sm font-medium text-gray-500"),
                P(str(processing), cls="text-3xl font-bold text-blue-600"),
                P("Currently running", cls="text-sm text-gray-600"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        Div(
            Div(
                P("Errors", cls="text-sm font-medium text-gray-500"),
                P(str(errors), cls="text-3xl font-bold text-red-600"),
                P("Need attention", cls="text-sm text-gray-600"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8",
    )

    # Main content
    main_content = Div(
        # Header
        Div(
            Div(
                H1(
                    f"Analytics: {assignment.title}",
                    cls="text-2xl font-bold text-gray-900",
                ),
                P(f"Course: {course.name}", cls="text-gray-600"),
                cls="flex-1",
            ),
            Div(
                A(
                    "← Back to Assignment",
                    href=f"/instructor/assignments/{assignment_id}",
                    cls="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors",
                ),
                A(
                    "View Submissions",
                    href=f"/instructor/assignments/{assignment_id}/submissions",
                    cls="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors ml-3",
                ),
                cls="flex items-center",
            ),
            cls="flex items-center justify-between mb-6",
        ),
        # Summary stats
        stats_cards,
        # LLM performance comparison
        llm_comparison_table,
        # Category performance
        category_performance_section,
        cls="max-w-7xl mx-auto px-4 py-6",
    )

    # Sidebar content with insights
    top_model = None
    if llm_stats:
        # Find top performing model
        sorted_models = sorted(
            llm_stats.items(),
            key=lambda x: (
                x[1]["successful_runs"] / x[1]["total_runs"]
                if x[1]["total_runs"] > 0
                else 0,
                statistics.mean(x[1]["scores"]) if x[1]["scores"] else 0,
            ),
            reverse=True,
        )
        if sorted_models:
            top_model_name, top_model_stats = sorted_models[0]
            success_rate = (
                (
                    top_model_stats["successful_runs"]
                    / top_model_stats["total_runs"]
                    * 100
                )
                if top_model_stats["total_runs"] > 0
                else 0
            )
            top_model = f"{top_model_name} ({success_rate:.0f}% success)"

    # Find category insights
    strong_categories = []
    weak_categories = []
    if category_performance:
        for cat_name, perf in category_performance.items():
            if perf["avg_score"] >= 75:
                strong_categories.append(cat_name)
            elif perf["avg_score"] < 60:
                weak_categories.append(cat_name)

    sidebar_content = Div(
        H3("Insights", cls="text-lg font-semibold text-gray-900 mb-4"),
        Div(
            H4("Top Performing Model", cls="font-semibold text-gray-700 mb-2"),
            P(top_model or "No data yet", cls="text-sm text-gray-600 mb-4"),
            H4("Category Insights", cls="font-semibold text-gray-700 mb-2"),
            (
                Div(
                    P("Strong Areas:", cls="text-sm font-medium text-gray-700"),
                    Ul(
                        *[
                            Li(cat, cls="text-sm text-gray-600")
                            for cat in strong_categories[:3]
                        ],
                        cls="list-disc list-inside mb-2",
                    )
                    if strong_categories
                    else P("None identified", cls="text-sm text-gray-500 mb-2"),
                    P(
                        "Areas for Improvement:",
                        cls="text-sm font-medium text-gray-700",
                    ),
                    Ul(
                        *[
                            Li(cat, cls="text-sm text-gray-600")
                            for cat in weak_categories[:3]
                        ],
                        cls="list-disc list-inside mb-4",
                    )
                    if weak_categories
                    else P("None identified", cls="text-sm text-gray-500 mb-4"),
                )
                if category_performance
                else P("No data yet", cls="text-sm text-gray-600 mb-4")
            ),
            H4("Recommendations", cls="font-semibold text-gray-700 mb-2"),
            Ul(
                Li(
                    "Consider adjusting rubric weights"
                    if category_performance
                    else "Collect more submissions",
                    cls="text-sm text-gray-600 mb-1",
                ),
                Li(
                    "Review low-performing models"
                    if llm_stats
                    else "Configure AI models",
                    cls="text-sm text-gray-600 mb-1",
                ),
                Li(
                    "Provide targeted feedback guidance"
                    if weak_categories
                    else "Monitor performance trends",
                    cls="text-sm text-gray-600",
                ),
                cls="list-disc list-inside",
            ),
        ),
    )

    return dashboard_layout(
        f"Analytics: {assignment.title} | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/assignments/{assignment_id}/analytics",
    )
