"""
Camera selector service.

Filters and selects cameras based on resolution and sensor requirements.
"""

from typing import List
from models.requirement import VisionRequirement
from models.camera import Camera


def select_cameras(
    requirement: VisionRequirement,
    cameras: List[Camera]
) -> List[Camera]:
    """
    Filter cameras that satisfy required resolution and have sensor aspect ratio
    compatible with the required FOV.

    Selection logic:
    1. Camera resolution must meet or exceed required pixels in both dimensions.
    2. Sensor aspect ratio should be within 20% of required FOV aspect ratio.

    Note:
    - This is deterministic filtering only; no ranking or scoring.
    - No optics calculations are performed.
    - Does not access database; input cameras are provided as list.

    Args:
        requirement: User's vision requirements
        cameras: List of available cameras to filter

    Returns:
        Subset of cameras that pass both filters (preserving original order)
    """
    # Convert required resolution from µm/pixel to mm/pixel
    required_resolution_mm_per_pixel = requirement.required_resolution_um_per_pixel / 1000.0

    # Compute minimum required pixels for each dimension
    required_pixels_x = requirement.fov_width_mm / required_resolution_mm_per_pixel
    required_pixels_y = requirement.fov_height_mm / required_resolution_mm_per_pixel

    # Required FOV aspect ratio (width/height)
    required_aspect_ratio = requirement.fov_width_mm / requirement.fov_height_mm

    # Tolerance for aspect ratio compatibility (20%)
    ASPECT_RATIO_TOLERANCE = 0.20

    selected: List[Camera] = []

    for camera in cameras:
        # Filter 1: Resolution capability
        # Camera must have at least the required number of pixels in both dimensions
        if camera.resolution_x < required_pixels_x or camera.resolution_y < required_pixels_y:
            continue

        # Filter 2: Sensor size compatibility (aspect ratio)
        camera_aspect_ratio = camera.sensor_width_mm / camera.sensor_height_mm
        lower_bound = required_aspect_ratio * (1 - ASPECT_RATIO_TOLERANCE)
        upper_bound = required_aspect_ratio * (1 + ASPECT_RATIO_TOLERANCE)
        if not (lower_bound <= camera_aspect_ratio <= upper_bound):
            continue

        # Camera passes both filters
        selected.append(camera)

    return selected
