"""
Validator service.

Early validation of user requirements before optics calculations.
Checks for physically impossible or out-of-bounds inputs.
Does NOT access camera/lens database.
"""

from dataclasses import dataclass
from typing import List, Optional
from models.requirement import VisionRequirement


# ============================================
# Threshold Constants (with explanations)
# ============================================

# Physical bounds - what's mathematically possible
MIN_POSITIVE_VALUE = 1e-9  # Near-zero values indicate unit errors or invalid input

# Realistic ranges for machine vision applications
MAX_FOV_MM = 10000         # ~10m - beyond this is typically industrial/lidar territory
MIN_FOV_MM = 0.01          # 10µm - sub-micrometer FOV is impractical
MAX_WORKING_DISTANCE_MM = 100000  # ~100m - extremely large distances
MIN_WORKING_DISTANCE_MM = 1        # Contact/proximity imaging
MAX_RESOLUTION_UM = 100     # >100 µm/pixel is very coarse (cellphone: ~1µm, industrial: 5-20µm)
MIN_RESOLUTION_UM = 0.01    # Sub-nanometer resolution exceeds current technology

# Geometry sanity - aspect ratio and FOV/WD ratio
MIN_ASPECT_RATIO = 0.1
MAX_ASPECT_RATIO = 10
MAX_FOV_TO_WD_RATIO = 5.0  # FOV shouldn't be 1000x larger than WD in normal setups


@dataclass(frozen=True)
class ValidationError:
    """Single validation failure with diagnostic information."""
    field: str
    message: str
    suggestion: Optional[str] = None


@dataclass(frozen=True)
class ValidationResult:
    """Result of requirement validation."""
    is_valid: bool
    errors: List[ValidationError]


def _check_positive(
    value: float,
    field_name: str,
    min_value: float = MIN_POSITIVE_VALUE
) -> Optional[ValidationError]:
    """
    Helper: Check if value is positive (or above min_value).

    Args:
        value: Value to check
        field_name: Name of the field for error reporting
        min_value: Minimum acceptable value (default: MIN_POSITIVE_VALUE)

    Returns:
        ValidationError if invalid, None otherwise
    """
    if value <= min_value:
        return ValidationError(
            field=field_name,
            message=f"{field_name} must be greater than {min_value}",
            suggestion=f"Provide a positive value (got {value})"
        )
    return None


def validate_requirements(
    requirement: VisionRequirement
) -> ValidationResult:
    """
    Validate VisionRequirement for physical feasibility.
    Checks positivity and basic sanity bounds.
    Does NOT perform optics calculations or check against database.

    Args:
        requirement: User requirement to validate

    Returns:
        ValidationResult with is_valid flag and list of errors (if any)
    """
    errors: List[ValidationError] = []

    # Positive value checks (using helper)
    fov_w_error = _check_positive(requirement.fov_width_mm, "fov_width_mm")
    if fov_w_error:
        errors.append(fov_w_error)

    fov_h_error = _check_positive(requirement.fov_height_mm, "fov_height_mm")
    if fov_h_error:
        errors.append(fov_h_error)

    wd_error = _check_positive(requirement.working_distance_mm, "working_distance_mm")
    if wd_error:
        errors.append(wd_error)

    res_error = _check_positive(
        requirement.required_resolution_um_per_pixel,
        "required_resolution_um_per_pixel"
    )
    if res_error:
        errors.append(res_error)

    # If basic positivity checks failed, skip further validation
    # because we may have undefined values
    if errors:
        return ValidationResult(is_valid=False, errors=errors)

    # Range sanity checks with contextual suggestions
    if requirement.fov_width_mm > MAX_FOV_MM:
        errors.append(ValidationError(
            field="fov_width_mm",
            message=f"FOV width seems unreasonably large (>{MAX_FOV_MM/1000:.1f}m)",
            suggestion="Check if units are correct (should be mm)"
        ))

    if requirement.fov_width_mm < MIN_FOV_MM:
        errors.append(ValidationError(
            field="fov_width_mm",
            message=f"FOV width seems extremely small (<{MIN_FOV_MM}mm)",
            suggestion="Check if units are correct (should be mm)"
        ))

    if requirement.working_distance_mm < MIN_WORKING_DISTANCE_MM:
        errors.append(ValidationError(
            field="working_distance_mm",
            message=f"Working distance seems too small (<{MIN_WORKING_DISTANCE_MM}mm)",
            suggestion="Check if units are correct (should be mm)"
        ))

    if requirement.working_distance_mm > MAX_WORKING_DISTANCE_MM:
        errors.append(ValidationError(
            field="working_distance_mm",
            message=f"Working distance seems unreasonably large (>{MAX_WORKING_DISTANCE_MM/1000:.1f}m)",
            suggestion="Check if units are correct (should be mm)"
        ))

    if requirement.required_resolution_um_per_pixel > MAX_RESOLUTION_UM:
        errors.append(ValidationError(
            field="required_resolution_um_per_pixel",
            message=f"Resolution requirement too coarse (>{MAX_RESOLUTION_UM} µm/pixel)",
            suggestion="Typical industrial machine vision uses 1-20 µm/pixel depending on application"
        ))

    if requirement.required_resolution_um_per_pixel < MIN_RESOLUTION_UM:
        errors.append(ValidationError(
            field="required_resolution_um_per_pixel",
            message=f"Resolution requirement too fine (<{MIN_RESOLUTION_UM} µm/pixel)",
            suggestion="This exceeds current sensor technology limits"
        ))

    # Aspect ratio sanity
    aspect_ratio = requirement.fov_width_mm / requirement.fov_height_mm
    if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:
        errors.append(ValidationError(
            field="fov_width_mm,fov_height_mm",
            message=f"Aspect ratio ({aspect_ratio:.2f}) is unusual for machine vision",
            suggestion="Verify FOV width and height values (typical 4:3, 16:9, or 1:1)"
        ))

    # FOV vs working distance ratio check
    # For typical macro/vision setups, FOV shouldn't vastly exceed WD
    fov_wd_ratio = requirement.fov_width_mm / requirement.working_distance_mm
    if fov_wd_ratio > MAX_FOV_TO_WD_RATIO:
        errors.append(ValidationError(
            field="fov_width_mm,working_distance_mm",
            message=f"FOV width ({requirement.fov_width_mm}mm) is disproportionally large "
                   f"relative to working distance ({requirement.working_distance_mm}mm)",
            suggestion="Check if both values are in correct units or if magnification is achievable"
        ))

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors
    )
