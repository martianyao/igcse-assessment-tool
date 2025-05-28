### **docs/methodology.md**
```markdown
# Assessment Methodology and Statistical Framework

## 📊 **Overview**

This document outlines the psychometric and statistical methodology underlying the IGCSE Chemistry Assessment Tool, including item response theory models, statistical validation metrics, and learning analytics approaches.

## 🧮 **Statistical Metrics and Validation**

### **Item Difficulty and Discrimination**

**Point-Biserial Correlation**
r_pb = (M_p - M_q) / S_t * √(p * q)
Where:
- `M_p` = Mean total score for students answering item correctly
- `M_q` = Mean total score for students answering item incorrectly  
- `S_t` = Standard deviation of total scores
- `p` = Proportion answering correctly
- `q` = 1 - p

**Statistical Significance Testing**
- **p-value threshold**: α = 0.05 for item discrimination
- **Effect size**: Cohen's d for practical significance
- **Confidence intervals**: 95% CI for reliability estimates

### **Reliability Analysis**

**Cronbach's Alpha**
α = (k / (k-1)) * (1 - Σσ²_i / σ²_t)
Where:
- `k` = Number of items
- `σ²_i` = Variance of item i
- `σ²_t` = Variance of total scores

**Target reliability**: α ≥ 0.80 for high-stakes assessment

## 🎯 **Item Response Theory (IRT) Framework**

### **1-Parameter Logistic (1PL) Rasch Model**

The probability that student `i` with ability `θ_i` correctly answers item `j` with difficulty `b_j`:
P(θ_i, b_j) = 1 / (1 + e^{-(θ_i - b_j)})

**Parameters:**
- `θ_i` = Student ability parameter (logit scale)
- `b_j` = Item difficulty parameter (logit scale)
- `P(θ_i, b_j)` = Probability of correct response [0,1]

**Model Assumptions:**
1. **Unidimensionality**: Single latent trait (chemistry ability)
2. **Local Independence**: Items independent given ability
3. **Monotonicity**: Higher ability → higher success probability

### **Ability Estimation**

**Maximum Likelihood Estimation (MLE)**
L(θ) = ∏[P(θ,bⱼ)^xᵢⱼ * (1-P(θ,bⱼ))^(1-xᵢⱼ)]

**Expected A Posteriori (EAP) with Prior**
θ̂_EAP = ∫ θ * L(θ) * g(θ) dθ / ∫ L(θ) * g(θ) dθ

Where `g(θ) ~ N(0,1)` is the prior distribution.

## 📈 **Diagnostic Assessment Framework**

### **Knowledge Component Modeling**

**Additive Factor Model (AFM)**
P(success) = σ(Σ(β_kc * Q_kc) + γ_s * N_kc)
Where:
- `Q_kc` = Q-matrix (item-KC association)
- `β_kc` = KC difficulty parameter
- `γ_s` = Student learning rate
- `N_kc` = Practice opportunities

### **Learning Curve Analysis**

**Power Law of Practice**
RT = a * trials^(-b)
- `RT` = Response time/error rate
- `a` = Initial performance level
- `b` = Learning rate parameter

## 🤖 **Advanced Learning Analytics**

### **Deep Knowledge Tracing (DKT)**

**Planned Implementation**: LSTM-based knowledge state modeling

```python
# Conceptual DKT architecture
h_t = LSTM(x_t, h_{t-1})  # Hidden state update
p_t = σ(W_p * h_t + b_p)  # Prediction layer
Input Features:

x_t = [item_id, correct_response, response_time, hint_usage]
Sequence length: Variable (student learning history)
Output: P(correct | next_item, knowledge_state)

Bayesian Knowledge Tracing (BKT)
State Transition Model
P(L_t+1 = learned | L_t = unlearned) = T  # Transit probability
P(L_t+1 = learned | L_t = learned) = 1-F  # Forget probability
Observation Model
P(correct | learned) = 1-S    # Slip probability
P(correct | unlearned) = G    # Guess probability
🎲 Adaptive Testing Algorithm
Item Selection Criteria
Maximum Information Selection
I(θ) = P'(θ)² / (P(θ) * (1-P(θ)))
Content Balancing: Weighted selection ensuring topic coverage
Score = w₁*Information + w₂*ContentBalance + w₃*ExposureControl
Stopping Rules

Standard Error: SE(θ̂) ≤ 0.30
Maximum Items: N ≤ 30 questions
Minimum Items: N ≥ 10 questions
Time Limit: t ≤ 45 minutes

📊 Performance Analytics
Competency Mapping
IGCSE Grade Prediction
Grade = f(θ̂, topic_mastery[], engagement_score, time_factors)
Risk Identification

At-risk threshold: θ̂ < -1.0 (below grade 4)
Intervention trigger: Consistent declining performance

Learning Progression Models
Topic Dependency Graph
pythondependencies = {
    "atomic_structure": [],
    "bonding": ["atomic_structure"],
    "stoichiometry": ["bonding", "atomic_structure"],
    "kinetics": ["stoichiometry"]
}
⚠️ Current Limitations
Statistical Limitations

Guessing Parameter: 1PL model doesn't account for guessing

Mitigation: Monitor low-ability high-performance patterns
Future: Implement 3PL model with guessing parameter


Sequential Dependencies: Current model assumes independence

Issue: Learning effects between items
Future: Hidden Markov Models for state transitions


Multidimensionality: Chemistry involves multiple skills

Current: Unidimensional ability modeling
Future: MIRT (Multidimensional IRT) implementation



Data Requirements

Minimum sample: N ≥ 500 students for stable item parameters
Calibration sample: Representative of target population
Missing data: MAR assumption may not hold

🔬 Validation Studies
Construct Validity
Factor Analysis: Confirmatory factor analysis of item responses
χ²/df < 2.0, CFI > 0.95, RMSEA < 0.06
Convergent Validity: Correlation with external chemistry assessments

Target: r > 0.70 with teacher assessments
Target: r > 0.80 with standardized tests

Predictive Validity
IGCSE Grade Prediction Accuracy

Classification accuracy: ≥ 85% within one grade
Early prediction: 8 weeks before examination

📚 References and Theoretical Foundation
Core Learning Analytics Literature

Baker, R. S., & Inventado, P. S. (2014). "Learning analytics and educational data mining: towards communication and collaboration." Proceedings of the 2nd International Conference on Learning Analytics and Knowledge.

Foundation for EDM approaches in this tool


Pelánek, R. (2017). "Bayesian knowledge tracing, logistic models, and beyond: an overview of learner modeling techniques." User Modeling and User-Adapted Interaction, 27(3-5), 313-350.

Theoretical basis for knowledge state modeling


Piech, C., Bassen, J., Huang, J., Ganguli, S., Sahami, M., Guibas, L. J., & Sohl-Dickstein, J. (2015). "Deep knowledge tracing." Advances in Neural Information Processing Systems.

Advanced modeling approach for future implementation



Psychometric Foundations

Rasch, G. (1960). Probabilistic models for some intelligence and attainment tests. Copenhagen: Danish Institute for Educational Research.
van der Linden, W. J., & Hambleton, R. K. (Eds.). (2013). Handbook of modern item response theory. Springer Science & Business Media.

Educational Assessment Research

Nichols, P. D., Chipman, S. F., & Brennan, R. L. (Eds.). (2012). Cognitively diagnostic assessment. Routledge.
Rupp, A. A., Templin, J., & Henson, R. A. (2010). Diagnostic measurement: Theory, methods, and applications. Guilford Press.

🔄 Implementation Roadmap
Phase 1: Current Implementation

✅ Classical Test Theory metrics
✅ Basic IRT (1PL Rasch model)
✅ Descriptive analytics

Phase 2: Enhanced Modeling

🔄 3PL IRT with guessing parameter
🔄 Multidimensional IRT
🔄 Adaptive testing algorithms

Phase 3: Advanced Analytics

📅 Deep Knowledge Tracing implementation
📅 Real-time learning analytics
📅 Personalized intervention systems


Last Updated: May 2025
Version: 1.0
Authors: IGCSE Assessment Tool Development Team

## 🔧 **2. Configuration Files**

### **pyproject.toml** (Root directory)
```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "igcse-assessment-tool"
description = "AI-Powered Comprehensive Performance Analysis for IGCSE Chemistry Education"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "IGCSE Assessment Tool Team", email = "igcse-assessment-tool@example.com"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Education",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Education",
    "Topic :: Scientific/Engineering",
]
dynamic = ["version"]

dependencies = [
    "Flask>=2.3.0",
    "Flask-SQLAlchemy>=3.0.0",
    "Flask-CORS>=4.0.0",
    "numpy>=1.21.0",
    "scipy>=1.7.0",
    "matplotlib>=3.5.0",
    "seaborn>=0.11.0",
    "reportlab>=3.6.0",
    "requests>=2.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-flask>=1.2.0",
    "pytest-xdist>=3.0.0",
    "black>=22.0.0",
    "isort>=5.10.0",
    "ruff>=0.0.290",
    "mypy>=1.0.0",
    "bandit>=1.7.0",
    "pre-commit>=2.20.0",
]
performance = [
    "locust>=2.0.0",
]
docs = [
    "sphinx>=5.0.0",
    "sphinx-rtd-theme>=1.0.0",
    "myst-parser>=0.18.0",
]

[project.urls]
Homepage = "https://github.com/your-username/igcse-assessment-tool"
Documentation = "https://your-username.github.io/igcse-assessment-tool"
Repository = "https://github.com/your-username/igcse-assessment-tool.git"
"Bug Tracker" = "https://github.com/your-username/igcse-assessment-tool/issues"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools_scm]
write_to = "src/_version.py"

[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["src"]

[tool.ruff]
target-version = "py39"
line-length = 88
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]

[tool.mypy]
python_version = "3.9"
check_untyped_defs = true
disallow_any_generics = true
disallow_incomplete_defs = true
disallow_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "matplotlib.*",
    "seaborn.*",
    "reportlab.*",
    "flask_sqlalchemy.*",
]
ignore_missing_imports = true

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]