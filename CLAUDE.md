# Camera & Lens Selector - CLAUDE.md

## 1. Project Goal

Build a professional Camera and Lens Selection Tool for industrial machine vision applications.

The system must:

* Recommend suitable cameras and lenses based on user requirements
* Ensure physical and optical feasibility
* Provide explainable, deterministic results

---

## 2. Core Principles

### Engineering First

* All outputs must be based on real optics formulas
* No heuristic-only solutions

### Separation of Concerns

Strict separation between:

* Math (core)
* Validation
* Selection logic
* Data
* UI

### Deterministic Behavior

* Same input → same output
* No randomness unless explicitly defined

---

## 3. System Architecture

- **/core**
  - `optics.py` - PURE: stateless physics functions only
  - `normalization.py` - Unit conversion (µm ↔ mm)
  - `constraints.py` - System-level validation
  - `scoring.py` - Ranking logic

- **/data**
  - `camera_db.json`
  - `lens_db.json`

- **/services**
  - `validator.py` - Early requirement validation (pre-optics)
  - `camera_selector.py`
  - `lens_selector.py`
  - `system_solver.py`

- **/models**
  - `camera.py`
  - `lens.py`
  - `requirement.py`

- **/ui**
  - optional only (not part of core logic)

---

## 4. Units & Normalization (MANDATORY)

* All internal calculations MUST use millimeters (mm)
* Pixel size MUST be converted from µm → mm before any calculation
* Conversion logic MUST be centralized in core/normalization.py

Rules:

* No mixed units inside functions
* No hardcoded conversion constants outside normalization module
* optics.py MUST only accept normalized inputs

---

## 5. Data Models

### Camera

* name
* sensor_width (mm)
* sensor_height (mm)
* pixel_size (µm → converted internally to mm)
* resolution_x
* resolution_y
* mount_type

### Lens

* name
* focal_length (mm)
* max_sensor_size
* distortion
* mount_type
* min_working_distance
* max_working_distance

### VisionRequirement

* fov_width (mm)
* fov_height (mm)
* working_distance (mm)
* required_resolution (µm/pixel → normalized internally)

---

## 6. Optics Model (STRICT)

optics.py contains ONLY:

* Pure functions
* Stateless calculations
* Physics-based formulas

Requirements:

* No database access
* No file I/O
* No business logic
* No filtering or ranking
* No side effects

Example:
calculate_fov(sensor_width_mm, magnification)

---

## 7. Early Validation (MANDATORY)

Before any optics calculation, the system MUST validate input.

Validation includes:

* All values > 0
* Physically possible FOV
* Realistic working distance
* Resolution feasibility

Behavior:

* If invalid → STOP pipeline
* Return clear diagnostic message
* Provide suggestion if possible

---

## 8. Selection Logic

### Camera Selection

* Filter by resolution capability
* Check pixel size vs requirement
* Validate sensor compatibility
* Reject impossible configurations

### Lens Selection

* Compute magnification
* Estimate focal length
* Match nearest lens
* Validate:

  * Working distance
  * Sensor coverage
  * Mount compatibility

---

## 9. System Validation

Reject combinations if:

* Lens cannot cover sensor
* Working distance invalid
* FOV not achievable
* Resolution not met

---

## 10. Scoring System

Must be:

* Deterministic
* Explainable
* Normalized (0 → 1)

Weights:

* resolution_match: 0.4
* fov_accuracy: 0.3
* working_distance: 0.2
* distortion_penalty: -0.1

---

## 11. Data Flow (STRICT)

1. Input
2. Early Validation (validator.py)
3. Unit Normalization (normalization.py)
4. Optics Calculation (optics.py)
5. Camera Selection
6. Lens Selection
7. System Validation (constraints.py)
8. Scoring
9. Output

---

## 12. Critical Rules (ENFORCED)

optics.py:

* MUST be stateless
* MUST NOT access database
* MUST NOT perform filtering or selection

validator.py:

* MUST NOT perform optics calculations
* MUST only validate feasibility

Data Flow:

* Each layer MUST depend only on previous layer
* No cross-layer shortcuts allowed

---

## 13. Error Handling

System must handle:

* Invalid input
* Missing data
* Impossible requirements

Return:

* Clear error message
* Explanation
* Suggested fix

---

## 14. Coding Guidelines

* Modular design
* No duplicated logic
* Readable over clever
* No magic numbers
* Constants must be defined

---

## 15. AI Behavior Rules

When generating code:

DO:

* Explain reasoning before coding
* Keep functions small
* Follow CLAUDE.md strictly

DO NOT:

* Rewrite entire files unnecessarily
* Mix UI with core logic
* Introduce new dependencies without reason

---

## 16. Debugging Rules

1. Identify root cause
2. Explain failure
3. Provide minimal fix
4. Suggest test case

---

## 17. Testing Strategy

* Unit tests for optics functions
* Edge cases:

  * Very small FOV
  * Large working distance
  * Extreme resolution

---

## 18. Performance Constraints

* Must handle 100+ cameras
* Avoid unnecessary O(n^2)
* Pre-filter before heavy computation

---

## 19. Final Rule

If a solution violates physics or real-world constraints → REJECT.

This is an engineering tool, not a demo.
