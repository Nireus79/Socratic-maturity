# Socrates Maturity Tracking System

[![PyPI](https://img.shields.io/pypi/v/socratic-maturity.svg)](https://pypi.org/project/socratic-maturity/)
[![Downloads](https://img.shields.io/pypi/dm/socratic-maturity.svg)](https://pypi.org/project/socratic-maturity/)
[![GitHub](https://img.shields.io/github/stars/Nireus79/Socratic-maturity.svg?style=social)](https://github.com/Nireus79/Socratic-maturity)
[![License](https://img.shields.io/github/license/Nireus79/Socratic-maturity.svg)](LICENSE)


A pure, standalone library for calculating and tracking project maturity across four phases and five quality categories. This is the core foundation of the Socrates AI system's agent coordination.

## What is Maturity?

Project maturity is measured across:

**Four Phases:**
- **Discovery** (0-25%): Define problem, scope, audience
- **Analysis** (25-50%): Gather requirements, analyze data
- **Design** (50-75%): Technology choices, architecture
- **Implementation** (75-100%): Code development, testing

**Five Quality Categories:**
- Code Quality
- Testing Coverage
- Documentation
- Architecture
- Performance

## Key Features

### Smart Calculation Algorithm

The maturity calculation uses a unique algorithm that:
- **Never penalizes advancing to new phases**
- **Only averages phases being worked on**
- **Example**: Discovery 100%, Analysis 0% = **100% overall** (not 50%)

### Pure Data Transformation

- No side effects
- No external dependencies
- Fully deterministic
- Can be used standalone or composed with other libraries

### Comprehensive Category Tracking

- Per-phase category scores (0.0-1.0)
- Weak category identification (< 0.6)
- Category improvement tracking
- Historical event logging

## Installation

```bash
pip install socrates-maturity
```

## Quick Start

```python
from socrates_maturity import MaturityCalculator

# Calculate overall maturity from phase scores
phase_scores = {"discovery": 1.0, "analysis": 0.3}
overall = MaturityCalculator.calculate_overall_maturity(phase_scores)
# overall = 0.65 (65%)

# Estimate current phase
current_phase = MaturityCalculator.estimate_current_phase(overall)
# current_phase = "design"

# Find weak categories
weak = MaturityCalculator.identify_weak_categories({
    "code_quality": 0.4,
    "testing": 0.8,
    "documentation": 0.3
})
# weak = ["code_quality", "documentation"]

# Get phase completion
completion = MaturityCalculator.get_phase_completion_percentage(overall)
# completion = 60 (60% through current phase)
```

## API Reference

### MaturityCalculator

Static utility class providing maturity calculation functions.

#### `calculate_overall_maturity(phase_scores: Dict[str, float]) -> float`

Calculate overall project maturity from phase scores.

**Args:**
- `phase_scores`: Dict mapping phase names to scores (0.0-1.0)

**Returns:** Overall maturity as float (0.0-1.0)

**Examples:**
```python
# Single phase
MaturityCalculator.calculate_overall_maturity({"discovery": 1.0})
# → 1.0

# Two phases (no penalty for new phase)
MaturityCalculator.calculate_overall_maturity({"discovery": 1.0, "analysis": 0.0})
# → 1.0

# Two phases with progress
MaturityCalculator.calculate_overall_maturity({"discovery": 1.0, "analysis": 0.3})
# → 0.65
```

#### `estimate_current_phase(overall_maturity: float) -> str`

Estimate current phase based on overall maturity.

**Args:**
- `overall_maturity`: Overall maturity (0.0-1.0 or 0-100)

**Returns:** Phase name ("discovery", "analysis", "design", "implementation")

**Examples:**
```python
MaturityCalculator.estimate_current_phase(0.1)   # → "discovery"
MaturityCalculator.estimate_current_phase(0.4)   # → "analysis"
MaturityCalculator.estimate_current_phase(0.65)  # → "design"
MaturityCalculator.estimate_current_phase(0.9)   # → "implementation"
```

#### `get_phase_completion_percentage(overall_maturity: float) -> int`

Get completion percentage within current phase.

**Args:**
- `overall_maturity`: Overall maturity (0.0-1.0)

**Returns:** Completion percentage (0-100)

**Examples:**
```python
MaturityCalculator.get_phase_completion_percentage(0.1)   # → 40 (40% through discovery)
MaturityCalculator.get_phase_completion_percentage(0.4)   # → 60 (60% through analysis)
MaturityCalculator.get_phase_completion_percentage(0.9)   # → 60 (60% through implementation)
```

#### `identify_weak_categories(category_scores: Dict[str, float], weak_threshold: float = 0.6) -> List[str]`

Identify categories below weakness threshold.

**Args:**
- `category_scores`: Dict mapping category names to scores (0.0-1.0)
- `weak_threshold`: Score threshold for weakness (default 0.6)

**Returns:** List of weak category names

**Examples:**
```python
MaturityCalculator.identify_weak_categories({
    "code_quality": 0.4,
    "testing": 0.3,
    "documentation": 0.8
})
# → ["code_quality", "testing"]
```

#### `calculate_category_improvement(before: Dict[str, float], after: Dict[str, float]) -> Dict[str, float]`

Calculate improvement in each category.

**Args:**
- `before`: Category scores before (0.0-1.0)
- `after`: Category scores after (0.0-1.0)

**Returns:** Dict of category → improvement delta

**Examples:**
```python
MaturityCalculator.calculate_category_improvement(
    {"quality": 0.4},
    {"quality": 0.6}
)
# → {"quality": 0.2}
```

### Data Models

#### `CategoryScore`

Per-category maturity score within a phase.

**Fields:**
- `category: str` - Category name
- `current_score: float` - Current score (0.0-1.0)
- `target_score: float` - Target score (0.0-1.0)
- `confidence: float` - Confidence in score
- `spec_count: int` - Number of specs in category

**Properties:**
- `percentage: float` - Percentage of target achieved
- `is_complete: bool` - Has reached target?

#### `PhaseMaturity`

Complete maturity information for a phase.

**Fields:**
- `phase: str` - Phase name
- `overall_score: float` - Phase overall score (0-100%)
- `category_scores: Dict[str, CategoryScore]` - Per-category scores
- `total_specs: int` - Total specs in phase
- `missing_categories: List[str]` - Categories below target
- `strongest_categories: List[str]` - Categories at/above target
- `weakest_categories: List[str]` - Weakest categories
- `is_ready_to_advance: bool` - Can move to next phase?
- `warnings: List[str]` - Any warnings

#### `MaturityEvent`

Historical maturity change event.

**Fields:**
- `timestamp: datetime` - When event occurred
- `phase: str` - Phase involved
- `score_before: float` - Score before event
- `score_after: float` - Score after event
- `delta: float` - Change in score
- `event_type: str` - Type of event
- `details: Dict[str, Any]` - Additional details

## How It Drives Agent Coordination

This maturity system is used by the Socrates AI agent coordination layer:

1. **QualityController** analyzes code and calculates maturity
2. **SkillGenerator** detects weak categories from maturity data
3. **SkillGenerator** creates adaptive skills for weak areas
4. **Target agents** receive skills and adjust their behavior
5. **LearningAgent** tracks which skills were effective
6. **System updates** maturity as weak areas improve
7. **Cycle repeats** with higher maturity and better recommendations

Example workflow:
```python
# 1. Calculate maturity
overall = MaturityCalculator.calculate_overall_maturity(
    {"discovery": 1.0, "analysis": 0.3}
)  # → 0.65

# 2. Identify weak categories
current_phase = MaturityCalculator.estimate_current_phase(overall)  # → "design"
weak_categories = MaturityCalculator.identify_weak_categories({
    "functional_requirements": 0.4,
    "non_functional_requirements": 0.5,
    "data_requirements": 0.8
})  # → ["functional_requirements", "non_functional_requirements"]

# 3. SkillGenerator creates skills for weak areas
# (skills generation happens in socratic-agents)

# 4. Agents apply skills, improving weak areas
# → After improvements, maturity increases to 0.72
```

## Testing

Run the test suite:

```bash
pytest tests/
```

With coverage:

```bash
pytest --cov=src/socrates_maturity tests/
```

## Design Principles

### Pure Functions

All calculation functions are pure - same input always produces same output, with no side effects.

### Deterministic

Completely deterministic and stateless. Can be used in parallel or distributed systems.

### Flexible

Works with any phase or category naming scheme. Not tied to Socrates specifically.

### Extensible

Easy to add new phases, categories, or calculation rules.

## License

MIT

## Contributing

Contributions welcome! Please ensure:
- Tests pass: `pytest`
- Code formatted: `black src/`
- No linting issues: `ruff check src/`
- Type hints present: `mypy src/`

## More Information

- [Full Documentation](docs/)
- [Socrates AI Repository](https://github.com/socrates-ai/socrates)
- [Architecture Guide](docs/ARCHITECTURE.md)


---

## Part of Socrates AI Ecosystem

This package is a component of [**Socrates AI**](https://github.com/Nireus79/Socrates), a production-ready platform for building intelligent multi-agent systems with constitutional governance.

### Use This Package Standalone:
```bash
pip install socratic-maturity
```

### Or As Part of Socrates Platform:
```bash
pip install socrates-ai  # Includes 37+ modules + all 11 packages
```

### Integration Example:

See the [**Socrates ECOSYSTEM.md**](https://github.com/Nireus79/Socrates/blob/main/ECOSYSTEM.md#layer-2-specialized-libraries) for detailed integration examples showing how to use socratic-maturity with other Socratic packages.

**Related packages you might use together:**
- See [Complete Package Map](https://github.com/Nireus79/Socrates/blob/main/ECOSYSTEM.md)

### More Information:
- 📖 [Full Socrates Documentation](https://github.com/Nireus79/Socrates/tree/main/docs)
- 🏗️ [Complete Architecture Guide](https://github.com/Nireus79/Socrates/blob/main/ECOSYSTEM.md)
- 💬 [Socrates Discussions](https://github.com/Nireus79/Socrates/discussions)

---
