from __future__ import annotations

"""
Data models for maturity tracking system.

Provides dataclasses for tracking project maturity across phases and categories.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class CategoryScore:
    """Score for a specific category within a phase."""

    category: str
    current_score: float
    target_score: float
    confidence: float
    spec_count: int

    @property
    def percentage(self) -> float:
        """Calculate percentage of target achieved."""
        if self.target_score == 0:
            return 0.0
        return min(100.0, (self.current_score / self.target_score) * 100)

    @property
    def is_complete(self) -> bool:
        """Check if category has reached target."""
        return self.current_score >= self.target_score


    @staticmethod
    def from_dict(data: dict) -> "CategoryScore":
        """Deserialize from dictionary."""
        return CategoryScore(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        from dataclasses import asdict
        return asdict(self)

class PhaseMaturity:
    @staticmethod
    def from_dict(data: dict) -> "PhaseMaturity":
        """Deserialize from dictionary."""
        return PhaseMaturity(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        from dataclasses import asdict
        return asdict(self)


    phase: str
    overall_score: float  # 0-100%
    category_scores: Dict[str, CategoryScore]
    total_specs: int
    missing_categories: List[str]
    strongest_categories: List[str]
    weakest_categories: List[str]
    is_ready_to_advance: bool
    warnings: List[str] = field(default_factory=list)


@dataclass
class MaturityEvent:
    @staticmethod
    def from_dict(data: dict) -> "MaturityEvent":
        """Deserialize from dictionary."""
        return MaturityEvent(**data)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        from dataclasses import asdict
        return asdict(self)


    timestamp: datetime
    phase: str
    score_before: float
    score_after: float
    delta: float
    event_type: str  # 'question_answered', 'spec_added', 'phase_advanced', etc.
    details: Dict[str, Any] = field(default_factory=dict)
