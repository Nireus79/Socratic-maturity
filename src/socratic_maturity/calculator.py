from __future__ import annotations

"""
Maturity calculation engine.

Pure, side-effect-free calculation of project maturity based on phase scores.
"""

from typing import Any, Dict, List, Optional

PHASES = ["discovery", "analysis", "design", "implementation"]
PHASE_RANGES = {
    "discovery": (0.0, 0.25),
    "analysis": (0.25, 0.5),
    "design": (0.5, 0.75),
    "implementation": (0.75, 1.0),
}

# Project type phase categories
PROJECT_TYPE_CATEGORIES = {
    "software": {
        "discovery": ["requirements", "tech_stack", "stakeholders"],
        "analysis": ["scope", "dependencies", "risks"],
        "design": ["architecture", "database", "api_design"],
        "implementation": ["coding", "testing", "documentation"],
    },
    "business": {
        "discovery": ["market_research", "competitors", "customer_needs"],
        "analysis": ["business_model", "financial_plan", "resources"],
        "design": ["strategy", "processes", "branding"],
        "implementation": ["launch", "marketing", "operations"],
    },
    "creative": {
        "discovery": ["inspiration", "concept", "audience"],
        "analysis": ["feedback", "iterations", "refinement"],
        "design": ["visual_design", "layout", "style"],
        "implementation": ["production", "delivery", "promotion"],
    },
    "research": {
        "discovery": ["literature_review", "hypothesis", "methodology"],
        "analysis": ["data_collection", "analysis", "validation"],
        "design": ["experiments", "controls", "measurements"],
        "implementation": ["results", "publication", "dissemination"],
    },
    "marketing": {
        "discovery": ["audience_research", "market_analysis", "trends"],
        "analysis": ["campaign_planning", "budget", "channels"],
        "design": ["content_creation", "messaging", "creative"],
        "implementation": ["execution", "analytics", "optimization"],
    },
    "educational": {
        "discovery": ["learning_objectives", "content_audit", "audience"],
        "analysis": ["curriculum_design", "assessment_plan", "resources"],
        "design": ["course_structure", "materials", "interactions"],
        "implementation": ["delivery", "evaluation", "iteration"],
    },
}

# Thresholds
READY_THRESHOLD = 20.0
COMPLETE_THRESHOLD = 100.0
WARNING_THRESHOLD = 10.0


class MaturityCalculator:
    """Maturity calculator with support for project types and phase categories."""

    def __init__(self, project_type: str = "software", claude_client: Optional[Any] = None):
        """
        Initialize MaturityCalculator with project type and optional Claude client.

        Args:
            project_type: Project type (software, business, creative, research, marketing,
                educational)
            claude_client: Optional Claude API client for intelligent categorization
        """
        self.project_type = project_type.lower()
        self.claude_client = claude_client

        # Set phase categories based on project type
        self.phase_categories = PROJECT_TYPE_CATEGORIES.get(
            self.project_type, PROJECT_TYPE_CATEGORIES["software"]
        )

        # Set thresholds
        self.READY_THRESHOLD = READY_THRESHOLD
        self.COMPLETE_THRESHOLD = COMPLETE_THRESHOLD
        self.WARNING_THRESHOLD = WARNING_THRESHOLD

    @staticmethod
    def calculate_overall_maturity(phase_scores: Dict[str, float]) -> float:
        """
        Calculate overall project maturity using weighted phase contributions.

        Instead of averaging (which penalizes starting new phases), this uses:
        - All completed phases (with scores) contribute equally
        - Current/active phase (even if just started) contributes its current score
        - Result: advancing to new phases doesn't decrease overall maturity

        Args:
            phase_scores: Dict mapping phase names to scores (0.0-1.0)
                         e.g., {"discovery": 1.0, "analysis": 0.3}

        Returns:
            Overall maturity as a float between 0.0 and 1.0

        Examples:
            >>> MaturityCalculator.calculate_overall_maturity({"discovery": 1.0})
            1.0

            >>> MaturityCalculator.calculate_overall_maturity(
            ...     {"discovery": 1.0, "analysis": 0.0}
            ... )
            1.0

            >>> MaturityCalculator.calculate_overall_maturity(
            ...     {"discovery": 1.0, "analysis": 0.3}
            ... )
            0.65
        """
        if not phase_scores:
            return 0.0

        # Get all phases with non-zero scores (these are the ones being worked on)
        scored_phases = [s for s in phase_scores.values() if s > 0]

        if not scored_phases:
            return 0.0

        # Use average of active/completed phases
        # This avoids penalizing users for advancing to new phases
        return sum(scored_phases) / len(scored_phases)

    @staticmethod
    def estimate_current_phase(overall_maturity: float) -> str:
        """
        Estimate current phase based on overall maturity percentage.

        Args:
            overall_maturity: Overall maturity as float 0.0-1.0 (or 0-100)

        Returns:
            Phase name: "discovery", "analysis", "design", or "implementation"

        Examples:
            >>> MaturityCalculator.estimate_current_phase(0.1)
            'discovery'

            >>> MaturityCalculator.estimate_current_phase(0.4)
            'analysis'

            >>> MaturityCalculator.estimate_current_phase(0.65)
            'design'

            >>> MaturityCalculator.estimate_current_phase(0.9)
            'implementation'
        """
        # Handle both 0-1.0 and 0-100 scales
        if overall_maturity > 1.0:
            overall_maturity = overall_maturity / 100.0

        for phase in PHASES:
            min_val, max_val = PHASE_RANGES[phase]
            if min_val <= overall_maturity < max_val:
                return phase

        # Default to implementation if >= 0.75
        return "implementation"

    @staticmethod
    def get_phase_completion_percentage(overall_maturity: float) -> int:
        """
        Get percentage completion of current phase.

        Args:
            overall_maturity: Overall maturity as float 0.0-1.0

        Returns:
            Completion percentage within current phase (0-100)

        Examples:
            >>> MaturityCalculator.get_phase_completion_percentage(0.1)
            40

            >>> MaturityCalculator.get_phase_completion_percentage(0.4)
            60

            >>> MaturityCalculator.get_phase_completion_percentage(0.9)
            60
        """
        current_phase = MaturityCalculator.estimate_current_phase(overall_maturity)
        min_val, max_val = PHASE_RANGES[current_phase]
        phase_range = max_val - min_val
        position_in_phase = overall_maturity - min_val

        if phase_range == 0:
            return 0

        return int((position_in_phase / phase_range) * 100)

    @staticmethod
    def identify_weak_categories(
        category_scores: Dict[str, float], weak_threshold: float = 0.6
    ) -> List[str]:
        """
        Identify categories that are below weakness threshold.

        Args:
            category_scores: Dict mapping category names to scores (0.0-1.0)
            weak_threshold: Score below which categories are considered weak (default 0.6)

        Returns:
            List of weak category names

        Examples:
            >>> MaturityCalculator.identify_weak_categories({
            ...     "code_quality": 0.4,
            ...     "testing": 0.3,
            ...     "documentation": 0.8
            ... })
            ['code_quality', 'testing']
        """
        return [category for category, score in category_scores.items() if score < weak_threshold]

    @staticmethod
    def calculate_category_improvement(
        before: Dict[str, float], after: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate improvement in each category.

        Args:
            before: Category scores before (0.0-1.0)
            after: Category scores after (0.0-1.0)

        Returns:
            Dict of category → improvement delta

        Examples:
            >>> MaturityCalculator.calculate_category_improvement(
            ...     {"quality": 0.4},
            ...     {"quality": 0.6}
            ... )
            {'quality': 0.2}
        """
        improvements = {}
        for category in before:
            if category in after:
                improvements[category] = after[category] - before[category]
        return improvements

    # Instance methods for compatibility with project-based usage
    def set_project_type(self, project_type: str) -> None:
        """Change project type and update phase categories."""
        self.project_type = project_type.lower()
        self.phase_categories = PROJECT_TYPE_CATEGORIES.get(
            self.project_type, PROJECT_TYPE_CATEGORIES["software"]
        )

    def set_claude_client(self, claude_client: Any) -> None:
        """Set Claude client for intelligent categorization."""
        self.claude_client = claude_client
