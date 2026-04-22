from __future__ import annotations

"""
Socrates Maturity Tracking System

A pure, standalone library for calculating and tracking project maturity
across four phases (discovery, analysis, design, implementation) and five
quality categories (code_quality, testing, documentation, architecture, performance).

The maturity calculation uses a smart algorithm that:
- Averages scores of phases being worked on
- Never penalizes advancing to new phases
- Drives agent coordination through phase-aware skill generation

Key Classes:
    - MaturityCalculator: Pure calculation engine
    - CategoryScore: Per-category maturity score
    - PhaseMaturity: Complete phase maturity information
    - MaturityEvent: Historical maturity change event

Example:
    >>> from socrates_maturity import MaturityCalculator
    >>>
    >>> # Calculate overall maturity from phase scores
    >>> phase_scores = {"discovery": 1.0, "analysis": 0.3}
    >>> overall = MaturityCalculator.calculate_overall_maturity(phase_scores)
    >>> # overall = 0.65 (65%)
    >>>
    >>> # Estimate current phase
    >>> current_phase = MaturityCalculator.estimate_current_phase(overall)
    >>> # current_phase = "design"
    >>>
    >>> # Find weak categories
    >>> weak = MaturityCalculator.identify_weak_categories({
    ...     "code_quality": 0.4,
    ...     "testing": 0.8,
    ...     "documentation": 0.3
    ... })
    >>> # weak = ["code_quality", "documentation"]
"""

from socrates_maturity.calculator import MaturityCalculator
from socrates_maturity.models import CategoryScore, MaturityEvent, PhaseMaturity
from socrates_maturity.workflows import (
    LearningVelocityWorkflow,
    MaturityTransitionWorkflow,
    PhaseProgressionWorkflow,
    SkillRecommendationWorkflow,
    WorkflowState,
    WorkflowType,
)

__version__ = "0.1.0"

__all__ = [
    "MaturityCalculator",
    "CategoryScore",
    "PhaseMaturity",
    "MaturityEvent",
    "PhaseProgressionWorkflow",
    "SkillRecommendationWorkflow",
    "MaturityTransitionWorkflow",
    "LearningVelocityWorkflow",
    "WorkflowType",
    "WorkflowState",
]
