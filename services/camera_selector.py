"""
Camera selector service.

Filters and selects cameras based on resolution and sensor requirements.
"""

from typing import List
from models.requirement import VisionRequirement
from models.camera import Camera
from core.normalization import resolution_to_mm_per_pixel


def select_cameras(
    requirement: VisionRequirement,
    cameras: List[Camera]
) -> List[Camera]:
    """
    Filter cameras that satisfy required resolution and have sensor aspect ratio
    compatible with the required FOV.

    Selection logic:
    1. Camera pixel size must be <= required resolution (mm/pixel)
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
    # Convert required resolution from µm/pixel to mm/pixel using normalization
    required_resolution_mm_per_pixel = resolution_to_mm_per_pixel(
        requirement.required_resolution_um_per_pixel
    )

    # Required FOV aspect ratio (width/height)
    required_aspect_ratio = requirement.fov_width_mm / requirement.fov_height_mm

    # Tolerance for aspect ratio compatibility (20%)
    ASPECT_RATIO_TOLERANCE = 0.20

    selected: List[Camera] = []

    for camera in cameras:
        # Filter 1: Resolution capability via pixel size
        # Camera pixel size must be at least as fine (smaller) than required resolution.
        if camera.pixel_size_mm > required_resolution_mm_per_pixel:
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
