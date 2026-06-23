from __future__ import annotations

"""
Pure, stateless workflows for maturity tracking and progression.

These workflows handle maturity state transitions without infrastructure dependencies.
All workflows are deterministic and side-effect-free.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from socratic_maturity.calculator import PHASES, MaturityCalculator


class WorkflowType(Enum):
    """Types of maturity workflows."""

    PHASE_PROGRESSION = "phase_progression"
    SKILL_RECOMMENDATION = "skill_recommendation"
    MATURITY_TRANSITION = "maturity_transition"
    LEARNING_VELOCITY = "learning_velocity"


@dataclass
class WorkflowState:
    @staticmethod
    def from_dict(data: dict) -> "WorkflowState":
        """Deserialize from dictionary."""
        return WorkflowState(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        from dataclasses import asdict

        return asdict(self)

    workflow_type: WorkflowType
    phase_scores: Dict[str, float]
    category_scores: Dict[str, float]
    overall_maturity: float
    current_phase: str
    completion_percent: int
    transitions: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PhaseProgressionWorkflow:
    """Tracks user progression through phases."""

    @staticmethod
    def calculate_phase_progression(
        phase_scores: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Calculate current phase and progression details.

        Args:
            phase_scores: Dict mapping phase names to scores (0.0-1.0)

        Returns:
            Dict with current phase, progression, and readiness
        """
        overall = MaturityCalculator.calculate_overall_maturity(phase_scores)
        current_phase = MaturityCalculator.estimate_current_phase(overall)
        completion = MaturityCalculator.get_phase_completion_percentage(overall)

        # Calculate progress within current phase
        phase_index = PHASES.index(current_phase)

        # Next phase is the one after current
        next_phase = PHASES[phase_index + 1] if phase_index < len(PHASES) - 1 else None

        # Determine readiness for next phase (85%+ completion)
        ready_for_next = completion >= 85

        return {
            "current_phase": current_phase,
            "overall_maturity": overall,
            "completion_percent": completion,
            "phase_scores": phase_scores,
            "next_phase": next_phase,
            "ready_for_next": ready_for_next,
            "phases_completed": sum(1 for s in phase_scores.values() if s >= 0.99),
        }

    @staticmethod
    def suggest_phase_focus(
        phase_scores: Dict[str, float],
        current_velocity: Optional[float] = None,
    ) -> str:
        """
        Suggest which phase user should focus on.

        Args:
            phase_scores: Current phase scores
            current_velocity: Optional learning velocity (0-1, higher = faster learning)

        Returns:
            Phase name to focus on
        """
        overall = MaturityCalculator.calculate_overall_maturity(phase_scores)
        current_phase = MaturityCalculator.estimate_current_phase(overall)
        completion = MaturityCalculator.get_phase_completion_percentage(overall)

        # If not far enough in current phase, focus on it
        if completion < 70:
            return current_phase

        # If velocity is high, can advance
        if current_velocity and current_velocity > 0.7:
            phase_index = PHASES.index(current_phase)
            if phase_index < len(PHASES) - 1:
                return PHASES[phase_index + 1]

        return current_phase


class SkillRecommendationWorkflow:
    """Recommends skills based on maturity state."""

    # Skill templates by phase and weak categories
    SKILL_TEMPLATES = {
        "discovery": {
            "code_quality": ["Code Review Fundamentals", "Clean Code Principles"],
            "testing": ["Testing Mindset", "Basic Test Planning"],
            "documentation": ["Documentation Importance", "README Basics"],
            "architecture": ["Architecture Thinking", "Design Patterns Intro"],
            "performance": ["Performance Awareness", "Optimization Basics"],
        },
        "analysis": {
            "code_quality": ["Static Analysis", "Code Metrics"],
            "testing": ["Test Coverage", "Unit Testing"],
            "documentation": ["API Documentation", "Code Comments"],
            "architecture": ["System Design", "Component Design"],
            "performance": ["Profiling", "Performance Testing"],
        },
        "design": {
            "code_quality": ["Refactoring", "SOLID Principles"],
            "testing": ["Integration Testing", "Test Doubles"],
            "documentation": ["Architecture Documentation", "Design Docs"],
            "architecture": ["Microservices", "Design Patterns"],
            "performance": ["Caching", "Optimization Strategies"],
        },
        "implementation": {
            "code_quality": ["Advanced Refactoring", "Code Mastery"],
            "testing": ["End-to-End Testing", "Test Automation"],
            "documentation": ["Comprehensive Documentation", "Knowledge Transfer"],
            "architecture": ["Large Scale Design", "System Evolution"],
            "performance": ["Advanced Optimization", "Scalability"],
        },
    }

    @staticmethod
    def get_skill_recommendations(
        phase_scores: Dict[str, float],
        category_scores: Dict[str, float],
        weak_threshold: float = 0.6,
    ) -> List[str]:
        """
        Get recommended skills based on phase and weak categories.

        Args:
            phase_scores: Current phase scores
            category_scores: Current category scores
            weak_threshold: Score below which categories are weak

        Returns:
            List of recommended skill names
        """
        overall = MaturityCalculator.calculate_overall_maturity(phase_scores)
        current_phase = MaturityCalculator.estimate_current_phase(overall)

        # Find weak categories
        weak_categories = MaturityCalculator.identify_weak_categories(
            category_scores, weak_threshold
        )

        # Get skills for weak categories in current phase
        recommendations = []
        phase_skills = SkillRecommendationWorkflow.SKILL_TEMPLATES.get(current_phase, {})

        for category in weak_categories:
            skills = phase_skills.get(category, [])
            recommendations.extend(skills)

        return recommendations

    @staticmethod
    def prioritize_skills(
        recommendations: List[str],
        category_scores: Dict[str, float],
    ) -> List[str]:
        """
        Prioritize skills by impact on weak categories.

        Args:
            recommendations: List of recommended skills
            category_scores: Current category scores

        Returns:
            Sorted recommendations by priority
        """
        # Skills for weakest categories come first
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1])

        prioritized = []
        for category, _ in sorted_categories:
            for skill in recommendations:
                if category.lower() in skill.lower() and skill not in prioritized:
                    prioritized.append(skill)

        # Add remaining recommendations
        for skill in recommendations:
            if skill not in prioritized:
                prioritized.append(skill)

        return prioritized


class MaturityTransitionWorkflow:
    """Handles phase transitions with validation."""

    @staticmethod
    def can_transition_to_phase(
        phase_scores: Dict[str, float],
        target_phase: str,
    ) -> Tuple[bool, str]:
        """
        Check if user can transition to target phase.

        Args:
            phase_scores: Current phase scores
            target_phase: Target phase to transition to

        Returns:
            Tuple of (can_transition: bool, reason: str)
        """
        if target_phase not in PHASES:
            return False, f"Invalid phase: {target_phase}"

        target_index = PHASES.index(target_phase)

        # Check all previous phases are at least started (> 0)
        for i in range(target_index):
            phase = PHASES[i]
            if phase not in phase_scores or phase_scores[phase] == 0:
                prev_phase = PHASES[i - 1] if i > 0 else "starting"
                return False, f"Must complete {prev_phase} first"

        # Check current phase completion
        overall = MaturityCalculator.calculate_overall_maturity(phase_scores)
        completion = MaturityCalculator.get_phase_completion_percentage(overall)
        current_phase = MaturityCalculator.estimate_current_phase(overall)
        current_index = PHASES.index(current_phase)

        # Can only move forward by one phase at a time
        if target_index > current_index + 1:
            return False, "Can only advance one phase at a time"

        # Must be 85%+ through current phase to advance
        if target_index == current_index + 1 and completion < 85:
            return False, f"Must reach 85% completion (currently {completion}%)"

        return True, "Ready to transition"

    @staticmethod
    def execute_phase_transition(
        phase_scores: Dict[str, float],
        target_phase: str,
    ) -> Tuple[bool, Dict[str, float], str]:
        """
        Execute a phase transition if allowed.

        Args:
            phase_scores: Current phase scores
            target_phase: Target phase to transition to

        Returns:
            Tuple of (success: bool, new_scores: dict, message: str)
        """
        can_transition, reason = MaturityTransitionWorkflow.can_transition_to_phase(
            phase_scores, target_phase
        )

        if not can_transition:
            return False, phase_scores, reason

        # Create new scores with target phase initialized
        new_scores = phase_scores.copy()
        if target_phase not in new_scores:
            new_scores[target_phase] = 0.0

        return True, new_scores, f"Transitioned to {target_phase}"


class LearningVelocityWorkflow:
    """Tracks learning speed and adjusts difficulty."""

    @staticmethod
    def calculate_learning_velocity(
        phase_scores_history: List[Dict[str, float]],
    ) -> float:
        """
        Calculate learning velocity from history.

        Args:
            phase_scores_history: List of phase scores snapshots in order

        Returns:
            Velocity as float 0.0-1.0 (higher = faster learning)
        """
        if len(phase_scores_history) < 2:
            return 0.5  # Default to medium

        # Calculate overall maturity at each point
        maturities = [
            MaturityCalculator.calculate_overall_maturity(scores) for scores in phase_scores_history
        ]

        # Calculate average improvement per step
        improvements = []
        for i in range(1, len(maturities)):
            improvement = maturities[i] - maturities[i - 1]
            if improvement > 0:
                improvements.append(improvement)

        if not improvements:
            return 0.1  # No improvement detected

        avg_improvement = sum(improvements) / len(improvements)

        # Normalize: 0.1 improvement = velocity 1.0, 0.01 = 0.1
        velocity = min(1.0, avg_improvement * 10)
        return velocity

    @staticmethod
    def suggest_difficulty_adjustment(
        phase_scores_history: List[Dict[str, float]],
    ) -> str:
        """
        Suggest difficulty adjustment based on learning velocity.

        Args:
            phase_scores_history: List of phase scores snapshots

        Returns:
            Suggestion: "increase", "maintain", or "decrease"
        """
        velocity = LearningVelocityWorkflow.calculate_learning_velocity(phase_scores_history)

        if velocity > 0.7:
            return "increase"  # Fast learner, increase difficulty
        elif velocity < 0.3:
            return "decrease"  # Slow progress, decrease difficulty
        else:
            return "maintain"  # Good pace, keep steady

    @staticmethod
    def estimate_phase_completion_time(
        current_scores: Dict[str, float],
        target_phase: str,
        phase_scores_history: List[Dict[str, float]],
    ) -> Optional[int]:
        """
        Estimate days to complete target phase.

        Args:
            current_scores: Current phase scores
            target_phase: Target phase
            phase_scores_history: Historical scores (assumed 1 entry per day)

        Returns:
            Estimated days to completion, or None if unknown
        """
        if len(phase_scores_history) < 7:
            return None  # Need at least a week of history

        velocity = LearningVelocityWorkflow.calculate_learning_velocity(phase_scores_history)

        if velocity == 0:
            return None

        current_maturity = MaturityCalculator.calculate_overall_maturity(current_scores)
        target_maturity_min = PHASES.index(target_phase) * 0.25  # Min maturity for phase

        remaining = target_maturity_min - current_maturity
        if remaining <= 0:
            return 0

        # Estimate: how many days at current velocity
        days_to_complete = int(remaining / velocity)
        return days_to_complete
