"""
Example: Agent Skill Generation Workflow

Demonstrates how maturity tracking integrates with agent systems to generate
targeted skills based on weak categories and current phase.
"""

from socratic_maturity import (
    MaturityCalculator,
    SkillRecommendationWorkflow,
    WorkflowType,
)


def agent_skill_generation_workflow():
    """
    Shows how an agent system uses maturity to generate targeted skills.
    """
    print("=" * 70)
    print("AGENT SKILL GENERATION WORKFLOW")
    print("=" * 70)
    print()

    # Step 1: Analyze current project maturity
    print("Step 1: Analyze Current Project State")
    print("-" * 70)

    phase_scores = {
        "discovery": 1.0,      # Complete
        "analysis": 0.5,       # In progress
        "design": 0.0,         # Not started
        "implementation": 0.0,
    }

    overall_maturity = MaturityCalculator.calculate_overall_maturity(phase_scores)
    current_phase = MaturityCalculator.estimate_current_phase(overall_maturity)

    print(f"Phase scores: {phase_scores}")
    print(f"Overall maturity: {overall_maturity * 100:.1f}%")
    print(f"Current phase: {current_phase}")
    print()

    # Step 2: Identify weak categories in current phase
    print("Step 2: Identify Weak Categories to Target")
    print("-" * 70)

    # Suppose these are the analysis phase category scores
    category_scores = {
        "functional_requirements": 0.3,    # WEAK
        "non_functional_requirements": 0.4,  # WEAK
        "data_model_design": 0.2,          # VERY WEAK
        "api_design": 0.6,                 # OK
        "documentation": 0.5,              # MEDIUM
    }

    weak_categories = MaturityCalculator.identify_weak_categories(
        category_scores,
        threshold=0.6
    )

    print(f"Category scores in {current_phase} phase:")
    for cat, score in sorted(category_scores.items(), key=lambda x: x[1]):
        status = "[WEAK]" if cat in weak_categories else "[OK]"
        print(f"  {status} {cat:>30}: {score:.1f}")
    print()
    print(f"Weak categories requiring focus: {weak_categories}")
    print()

    # Step 3: Use workflow to generate skill recommendations
    print("Step 3: Generate Skill Recommendations")
    print("-" * 70)

    workflow = SkillRecommendationWorkflow(
        current_phase=current_phase,
        weak_categories=weak_categories,
        overall_maturity=overall_maturity,
    )

    recommendations = workflow.generate_recommendations()

    print(f"Skill recommendations for {current_phase} phase:")
    print()
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec['skill_name']}")
        print(f"     Description: {rec['description']}")
        print(f"     Targets: {', '.join(rec['targets_categories'])}")
        print(f"     Priority: {rec['priority']}")
        print()

    # Step 4: Create agent tasks based on recommendations
    print("Step 4: Create Agent Tasks")
    print("-" * 70)

    print("Agent system would create these tasks:")
    print()

    for i, rec in enumerate(recommendations[:3], 1):
        print(f"  Task {i}: {rec['skill_name'].upper()}")
        print(f"    Assigned to: Specialist-{rec['priority'].upper()}")
        print(f"    Goal: Improve {rec['targets_categories'][0]}")
        print(f"    Deliverable: Detailed {rec['targets_categories'][0]} specification")
        print()

    # Step 5: Simulate improvements and track maturity change
    print("Step 5: Track Maturity Improvement")
    print("-" * 70)

    # After agents work on skills
    improved_scores = {
        "functional_requirements": 0.6,     # Improved by 0.3
        "non_functional_requirements": 0.65,  # Improved by 0.25
        "data_model_design": 0.4,           # Improved by 0.2
        "api_design": 0.7,                  # Improved by 0.1
        "documentation": 0.65,              # Improved by 0.15
    }

    print("After agents apply skills:")
    print()
    for cat in sorted(category_scores.keys()):
        old = category_scores[cat]
        new = improved_scores[cat]
        delta = new - old
        print(f"  {cat:>30}: {old:.1f} -> {new:.1f} (delta: +{delta:.1f})")
    print()

    # New overall maturity with improved analysis phase
    new_phase_scores = {
        "discovery": 1.0,
        "analysis": 0.62,       # Average of improved scores
        "design": 0.0,
        "implementation": 0.0,
    }

    new_overall = MaturityCalculator.calculate_overall_maturity(new_phase_scores)
    improvement = (new_overall - overall_maturity) * 100

    print(f"Overall maturity: {overall_maturity * 100:.1f}% -> {new_overall * 100:.1f}%")
    print(f"Improvement: +{improvement:.1f}%")
    print()

    # Step 6: Decision on phase advancement
    print("Step 6: Phase Advancement Decision")
    print("-" * 70)

    is_ready = all(score >= 0.8 for score in improved_scores.values())

    print(f"Analysis phase completion threshold: 80% (0.8)")
    print(f"Current lowest category: {min(improved_scores.values()):.1f}")
    print(f"Ready to advance to Design phase: {is_ready}")
    print()

    if not is_ready:
        remaining_weak = [
            cat for cat, score in improved_scores.items()
            if score < 0.8
        ]
        print(f"Categories still below threshold: {remaining_weak}")
        print("Next cycle will target these for improvement.")
    print()


def multi_phase_coordination():
    """
    Shows how maturity tracking coordinates work across multiple phases.
    """
    print("=" * 70)
    print("MULTI-PHASE AGENT COORDINATION")
    print("=" * 70)
    print()

    phases_state = {
        "discovery": {
            "status": "COMPLETE",
            "score": 1.0,
            "completion_date": "2025-04-10",
        },
        "analysis": {
            "status": "IN_PROGRESS",
            "score": 0.65,
            "weak_categories": ["data_model_design", "api_design"],
        },
        "design": {
            "status": "PENDING",
            "score": 0.0,
            "estimated_start": "2025-05-20",
        },
        "implementation": {
            "status": "PENDING",
            "score": 0.0,
            "estimated_start": "2025-07-01",
        },
    }

    print("Project Phase Status:")
    print()
    for phase, state in phases_state.items():
        print(f"  {phase.upper():>15}: {state['status']:<15} Score: {state['score']:.1f}")
    print()

    print("Agent Allocation Strategy:")
    print()
    print("  [ACTIVE]   Discovery  -> 0 agents (phase complete)")
    print("  [PRIMARY]  Analysis   -> 3 agents (weak categories)")
    print("  [STANDBY]  Design     -> 1 agent (preparing)")
    print("  [RESERVE]  Implementation -> 0 agents (waiting)")
    print()

    print("Coordination Points:")
    print()
    print("  1. Analysis agents report improvements to weak categories")
    print("  2. When analysis >= 0.8, automatically prepare design phase")
    print("  3. Design agent starts skill generation for design phase")
    print("  4. Handoff coordination: Analysis -> Design (May 20)")
    print("  5. Maturity tracking guides task prioritization")
    print()


if __name__ == "__main__":
    agent_skill_generation_workflow()
    print()
    print()
    multi_phase_coordination()
    print()
    print("=" * 70)
    print("Agent coordination workflow complete!")
    print("=" * 70)
