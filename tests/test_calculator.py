"""Unit tests for MaturityCalculator."""

from socrates_maturity import MaturityCalculator


class TestOverallMaturityCalculation:
    """Tests for calculate_overall_maturity."""

    def test_empty_phase_scores(self):
        """Empty phase scores should return 0.0."""
        assert MaturityCalculator.calculate_overall_maturity({}) == 0.0

    def test_single_phase_complete(self):
        """Single completed phase should return its score."""
        assert MaturityCalculator.calculate_overall_maturity({"discovery": 1.0}) == 1.0

    def test_single_phase_partial(self):
        """Single partial phase should return its score."""
        assert MaturityCalculator.calculate_overall_maturity({"discovery": 0.5}) == 0.5

    def test_two_phases_no_penalty_for_new_phase(self):
        """Starting a new phase should not decrease overall maturity.

        This is the KEY feature: Discovery 100%, Analysis 0% = 100% overall (not 50%)
        """
        # Starting analysis phase doesn't decrease overall maturity
        assert (
            MaturityCalculator.calculate_overall_maturity({"discovery": 1.0, "analysis": 0.0})
            == 1.0
        )

    def test_two_phases_both_progress(self):
        """Two phases with progress should average them."""
        # Discovery 100%, Analysis 30% = 65%
        result = MaturityCalculator.calculate_overall_maturity({"discovery": 1.0, "analysis": 0.3})
        assert abs(result - 0.65) < 0.001

    def test_three_phases_mixed_progress(self):
        """Three phases should average only non-zero scores."""
        # Discovery 100%, Analysis 50%, Design 0% = 75% (not 50%)
        result = MaturityCalculator.calculate_overall_maturity(
            {"discovery": 1.0, "analysis": 0.5, "design": 0.0}
        )
        assert abs(result - 0.75) < 0.001

    def test_all_phases_zero(self):
        """All zero phases should return 0.0."""
        result = MaturityCalculator.calculate_overall_maturity(
            {
                "discovery": 0.0,
                "analysis": 0.0,
                "design": 0.0,
                "implementation": 0.0,
            }
        )
        assert result == 0.0

    def test_four_phases_all_progress(self):
        """All four phases should average correctly."""
        result = MaturityCalculator.calculate_overall_maturity(
            {
                "discovery": 1.0,
                "analysis": 0.75,
                "design": 0.5,
                "implementation": 0.25,
            }
        )
        assert abs(result - 0.625) < 0.001


class TestPhaseEstimation:
    """Tests for estimate_current_phase."""

    def test_discovery_phase(self):
        """0.0-0.25 should be discovery."""
        assert MaturityCalculator.estimate_current_phase(0.0) == "discovery"
        assert MaturityCalculator.estimate_current_phase(0.1) == "discovery"
        assert MaturityCalculator.estimate_current_phase(0.25) == "analysis"  # Boundary

    def test_analysis_phase(self):
        """0.25-0.5 should be analysis."""
        assert MaturityCalculator.estimate_current_phase(0.25) == "analysis"
        assert MaturityCalculator.estimate_current_phase(0.35) == "analysis"
        assert MaturityCalculator.estimate_current_phase(0.5) == "design"  # Boundary

    def test_design_phase(self):
        """0.5-0.75 should be design."""
        assert MaturityCalculator.estimate_current_phase(0.5) == "design"
        assert MaturityCalculator.estimate_current_phase(0.65) == "design"
        assert MaturityCalculator.estimate_current_phase(0.75) == "implementation"  # Boundary

    def test_implementation_phase(self):
        """0.75+ should be implementation."""
        assert MaturityCalculator.estimate_current_phase(0.75) == "implementation"
        assert MaturityCalculator.estimate_current_phase(0.9) == "implementation"
        assert MaturityCalculator.estimate_current_phase(1.0) == "implementation"

    def test_percentage_scale(self):
        """Should handle 0-100 scale as well as 0-1.0."""
        assert MaturityCalculator.estimate_current_phase(50) == "design"
        assert MaturityCalculator.estimate_current_phase(75) == "implementation"


class TestPhaseCompletion:
    """Tests for get_phase_completion_percentage."""

    def test_early_discovery(self):
        """Early discovery should show low completion."""
        completion = MaturityCalculator.get_phase_completion_percentage(0.05)
        assert 10 <= completion <= 30  # Should be in discovery

    def test_mid_discovery(self):
        """Mid discovery should show 50% completion."""
        completion = MaturityCalculator.get_phase_completion_percentage(0.125)
        assert 40 <= completion <= 60

    def test_late_discovery(self):
        """Late discovery should show high completion."""
        completion = MaturityCalculator.get_phase_completion_percentage(0.24)
        assert 80 <= completion <= 100

    def test_early_analysis(self):
        """Early analysis should show low completion."""
        completion = MaturityCalculator.get_phase_completion_percentage(0.26)
        assert 0 <= completion <= 20


class TestWeakCategoryIdentification:
    """Tests for identify_weak_categories."""

    def test_no_weak_categories(self):
        """High scores should return no weak categories."""
        weak = MaturityCalculator.identify_weak_categories(
            {
                "code_quality": 0.9,
                "testing": 0.8,
                "documentation": 0.7,
            }
        )
        assert weak == []

    def test_some_weak_categories(self):
        """Categories below threshold should be identified."""
        weak = MaturityCalculator.identify_weak_categories(
            {
                "code_quality": 0.4,
                "testing": 0.8,
                "documentation": 0.3,
            }
        )
        assert set(weak) == {"code_quality", "documentation"}

    def test_all_weak_categories(self):
        """All low scores should all be weak."""
        weak = MaturityCalculator.identify_weak_categories(
            {
                "code_quality": 0.2,
                "testing": 0.1,
                "documentation": 0.3,
            }
        )
        assert set(weak) == {"code_quality", "testing", "documentation"}

    def test_custom_weak_threshold(self):
        """Custom threshold should be respected."""
        weak = MaturityCalculator.identify_weak_categories(
            {"code_quality": 0.7, "testing": 0.5},
            weak_threshold=0.8,
        )
        assert set(weak) == {"code_quality", "testing"}


class TestCategoryImprovement:
    """Tests for calculate_category_improvement."""

    def test_single_improvement(self):
        """Single category improvement should be calculated."""
        improvement = MaturityCalculator.calculate_category_improvement(
            {"quality": 0.4},
            {"quality": 0.6},
        )
        assert abs(improvement["quality"] - 0.2) < 0.001

    def test_multiple_improvements(self):
        """Multiple improvements should be calculated."""
        improvement = MaturityCalculator.calculate_category_improvement(
            {"quality": 0.4, "testing": 0.3, "docs": 0.8},
            {"quality": 0.6, "testing": 0.5, "docs": 0.9},
        )
        assert abs(improvement["quality"] - 0.2) < 0.001
        assert abs(improvement["testing"] - 0.2) < 0.001
        assert abs(improvement["docs"] - 0.1) < 0.001

    def test_negative_change(self):
        """Negative changes should be captured."""
        improvement = MaturityCalculator.calculate_category_improvement(
            {"quality": 0.7},
            {"quality": 0.5},
        )
        assert abs(improvement["quality"] - (-0.2)) < 0.001

    def test_missing_categories(self):
        """Missing categories in after should be ignored."""
        improvement = MaturityCalculator.calculate_category_improvement(
            {"quality": 0.4, "testing": 0.3},
            {"quality": 0.6},
        )
        assert "quality" in improvement
        assert abs(improvement["quality"] - 0.2) < 0.001
        assert "testing" not in improvement
