"""
Lens selector service.

Computes magnification and FOV, validates against requirement.
All other compatibility checks delegated to core.constraints.
"""

import math
from typing import List
from models.requirement import VisionRequirement
from models.camera import Camera
from models.lens import Lens
from core.optics import (
    calculate_magnification_from_focal_length,
    calculate_fov,
)
from core.constraints import (
    is_working_distance_supported,
    is_sensor_coverage_valid,
    is_mount_compatible,
)


def select_lenses(
    requirement: VisionRequirement,
    camera: Camera,
    lenses: List[Lens]
) -> List[Lens]:
    """
    Filter lenses compatible with the given requirement and camera.

    Selection logic:
    1. For each lens, compute actual magnification via optics module.
       If computation fails (e.g., WD <= f), skip lens.
    2. Compute actual FOV from camera sensor width and magnification.
    3. Keep lenses with FOV matching requirement within tolerance (±10%).
    4. Other compatibility checks delegated to constraints module:
       - Working distance within lens range
       - Sensor coverage sufficient for camera
       - Mount types compatible

    Design rationale:
    - FOV matching is kept in services because it's the direct outcome validation
      against the user requirement. Other checks are predicate validations and
      belong in the constraints layer.
    - Optics module provides physics formulas; services orchestrate only.
    - Deterministic filtering; no ranking or scoring.

    Args:
        requirement: User's vision requirements
        camera: Selected camera (after camera selection)
        lenses: List of available lenses to filter

    Returns:
        Subset of lenses that pass all compatibility checks (preserving order)
    """
    # Tolerance for FOV matching (relative)
    FOV_RELATIVE_TOLERANCE = 0.10

    selected: List[Lens] = []

    for lens in lenses:
        # Compute actual magnification from lens focal length and working distance
        # Uses optics module; raises ValueError if WD <= f (physically invalid)
        try:
            actual_magnification = calculate_magnification_from_focal_length(
                lens.focal_length_mm,
                requirement.working_distance_mm
            )
        except ValueError:
            continue

        # Compute actual FOV from sensor width and magnification
        # FOV is horizontal width in the object plane
        actual_fov = calculate_fov(camera.sensor_width_mm, actual_magnification)

        # FOV must match requirement within tolerance (orchestration logic stays in service)
        lower_fov = requirement.fov_width_mm * (1 - FOV_RELATIVE_TOLERANCE)
        upper_fov = requirement.fov_width_mm * (1 + FOV_RELATIVE_TOLERANCE)
        if not (lower_fov <= actual_fov <= upper_fov):
            continue

        # All other validations delegated to constraints module
        if not is_working_distance_supported(lens, requirement.working_distance_mm):
            continue

        if not is_sensor_coverage_valid(lens, camera):
            continue

        if not is_mount_compatible(lens, camera):
            continue

        # Lens passes all filters
        selected.append(lens)

    return selected
