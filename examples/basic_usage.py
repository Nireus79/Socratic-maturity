"""
Basic usage examples for socrates-maturity library.

This file demonstrates how to use the MaturityCalculator and data models
in your own projects.
"""

from socrates_maturity import (
    MaturityCalculator,
    CategoryScore,
    PhaseMaturity,
)


def example_1_basic_calculation():
    """Example 1: Calculate overall maturity from phase scores."""
    print("=" * 70)
    print("Example 1: Calculate Overall Maturity")
    print("=" * 70)

    # Single phase (discovery only)
    overall_1 = MaturityCalculator.calculate_overall_maturity(
        {"discovery": 1.0}
    )
    print(f"Discovery only: {overall_1 * 100:.0f}%")

    # Two phases (no penalty for starting new phase)
    overall_2 = MaturityCalculator.calculate_overall_maturity(
        {"discovery": 1.0, "analysis": 0.0}
    )
    print(f"Discovery 100%, Analysis 0%: {overall_2 * 100:.0f}% (not 50%!)")

    # Two phases with progress
    overall_3 = MaturityCalculator.calculate_overall_maturity(
        {"discovery": 1.0, "analysis": 0.3}
    )
    print(f"Discovery 100%, Analysis 30%: {overall_3 * 100:.0f}%")

    # Three phases mixed
    overall_4 = MaturityCalculator.calculate_overall_maturity(
        {
            "discovery": 1.0,
            "analysis": 0.5,
            "design": 0.0,
            "implementation": 0.0,
        }
    )
    print(f"Discovery 100%, Analysis 50%, Design 0%: {overall_4 * 100:.0f}%")
    print()


def example_2_phase_estimation():
    """Example 2: Estimate current phase from maturity."""
    print("=" * 70)
    print("Example 2: Estimate Current Phase")
    print("=" * 70)

    test_values = [0.1, 0.3, 0.55, 0.85, 1.0]

    for maturity in test_values:
        phase = MaturityCalculator.estimate_current_phase(maturity)
        completion = MaturityCalculator.get_phase_completion_percentage(maturity)
        print(f"Maturity: {maturity * 100:>3.0f}% -> Phase: {phase:>14} ({completion:>2}% complete)")
    print()


def example_3_weak_categories():
    """Example 3: Identify weak categories for improvement."""
    print("=" * 70)
    print("Example 3: Identify Weak Categories")
    print("=" * 70)

    # Current state of a project
    category_scores = {
        "code_quality": 0.4,  # WEAK
        "testing_coverage": 0.3,  # WEAK
        "documentation": 0.8,  # Strong
        "architecture": 0.5,  # Medium
        "performance": 0.2,  # WEAK
    }

    weak_categories = MaturityCalculator.identify_weak_categories(category_scores)
    print(f"Category scores: {category_scores}")
    print(f"Weak categories (< 0.6): {weak_categories}")
    print()
    print("[WARNING]  These weak areas should be targeted for improvement!")
    print("   SkillGenerator will create skills to address them.")
    print()


def example_4_tracking_improvement():
    """Example 4: Track category improvement over time."""
    print("=" * 70)
    print("Example 4: Track Category Improvement")
    print("=" * 70)

    # Before improvement
    before = {
        "code_quality": 0.4,
        "testing_coverage": 0.3,
        "documentation": 0.8,
    }

    # After applying skills/improvements
    after = {
        "code_quality": 0.6,
        "testing_coverage": 0.5,
        "documentation": 0.85,
    }

    improvements = MaturityCalculator.calculate_category_improvement(before, after)

    print("Category Improvement Tracking:")
    print("-" * 40)
    for category, delta in improvements.items():
        change_pct = delta * 100
        symbol = "[UP]" if delta > 0 else "[DOWN]"
        print(f"{symbol} {category:>20}: +{change_pct:>5.1f}% ({before[category]:.1f} -> {after[category]:.1f})")
    print()


def example_5_using_data_models():
    """Example 5: Create and use data models."""
    print("=" * 70)
    print("Example 5: Using Data Models")
    print("=" * 70)

    # Create category scores
    code_quality = CategoryScore(
        category="code_quality",
        current_score=0.6,
        target_score=0.8,
        confidence=0.9,
        spec_count=15,
    )

    testing = CategoryScore(
        category="testing_coverage",
        current_score=0.4,
        target_score=0.8,
        confidence=0.7,
        spec_count=10,
    )

    documentation = CategoryScore(
        category="documentation",
        current_score=0.9,
        target_score=0.9,
        confidence=0.95,
        spec_count=5,
    )

    # Create phase maturity
    phase = PhaseMaturity(
        phase="analysis",
        overall_score=0.63,
        category_scores={
            "code_quality": code_quality,
            "testing_coverage": testing,
            "documentation": documentation,
        },
        total_specs=30,
        missing_categories=["testing_coverage"],
        strongest_categories=["documentation"],
        weakest_categories=["testing_coverage"],
        is_ready_to_advance=False,
        warnings=["Testing coverage needs improvement before advancing"],
    )

    # Use the data
    print(f"Phase: {phase.phase}")
    print(f"Overall Score: {phase.overall_score * 100:.0f}%")
    print(f"Total Specs: {phase.total_specs}")
    print(f"Ready to Advance: {phase.is_ready_to_advance}")
    print(f"Warnings: {phase.warnings}")
    print()
    print("Category Details:")
    for name, category in phase.category_scores.items():
        status = "[OK]" if category.is_complete else "[FAIL]"
        print(f"  {status} {name:>20}: {category.percentage:>6.1f}% ({category.current_score:.1f}/{category.target_score:.1f})")
    print()


def example_6_maturity_workflow():
    """Example 6: Complete maturity tracking workflow."""
    print("=" * 70)
    print("Example 6: Complete Maturity Workflow")
    print("=" * 70)

    # Step 1: Calculate current maturity
    print("Step 1: Calculate Current Maturity")
    print("-" * 40)
    phase_scores = {
        "discovery": 1.0,
        "analysis": 0.4,
        "design": 0.0,
        "implementation": 0.0,
    }
    overall = MaturityCalculator.calculate_overall_maturity(phase_scores)
    print(f"Phase scores: {phase_scores}")
    print(f"Overall maturity: {overall * 100:.0f}%")
    print()

    # Step 2: Estimate phase and identify weak areas
    print("Step 2: Estimate Phase and Identify Weak Areas")
    print("-" * 40)
    current_phase = MaturityCalculator.estimate_current_phase(overall)
    phase_completion = MaturityCalculator.get_phase_completion_percentage(overall)
    print(f"Current phase: {current_phase}")
    print(f"Phase completion: {phase_completion}%")

    analysis_categories = {
        "functional_requirements": 0.4,  # WEAK
        "non_functional_requirements": 0.5,  # WEAK
        "data_requirements": 0.8,  # OK
    }
    weak = MaturityCalculator.identify_weak_categories(analysis_categories)
    print(f"Analysis phase category scores: {analysis_categories}")
    print(f"Weak categories to target: {weak}")
    print()

    # Step 3: Skills would be generated for weak areas
    print("Step 3: Generate Skills (next phase)")
    print("-" * 40)
    print("SkillGenerator would:")
    print(f"  [+] Load analysis phase skill templates")
    print(f"  [+] Filter for skills matching weak categories")
    print(f"  [+] Generate: 'functional_requirements_deep_dive'")
    print(f"  [+] Generate: 'non_functional_requirements_focus'")
    print()

    # Step 4: Agents apply skills and improve
    print("Step 4: Agents Apply Skills and Improve")
    print("-" * 40)
    print("After applying skills and improvements:")

    improved_categories = {
        "functional_requirements": 0.6,  # Improved
        "non_functional_requirements": 0.7,  # Improved
        "data_requirements": 0.8,  # Unchanged
    }

    improvements = MaturityCalculator.calculate_category_improvement(
        analysis_categories, improved_categories
    )
    print(f"Improvements made: {improvements}")
    print()

    # Step 5: Update maturity
    print("Step 5: Update Overall Maturity")
    print("-" * 40)
    new_phase_scores = {
        "discovery": 1.0,
        "analysis": 0.7,  # Improved
        "design": 0.0,
        "implementation": 0.0,
    }
    new_overall = MaturityCalculator.calculate_overall_maturity(new_phase_scores)
    delta = (new_overall - overall) * 100
    print(f"New phase scores: {new_phase_scores}")
    print(f"New overall maturity: {new_overall * 100:.0f}%")
    print(f"Improvement: +{delta:.1f}%")
    print()
    print("[OK] Cycle complete! Maturity increased through targeted improvement.")
    print()


if __name__ == "__main__":
    example_1_basic_calculation()
    example_2_phase_estimation()
    example_3_weak_categories()
    example_4_tracking_improvement()
    example_5_using_data_models()
    example_6_maturity_workflow()

    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
