"""
Constraints module.

System-level validation and feasibility checks.
Validates camera-lens compatibility.
"""

from typing import Union
from models.camera import Camera
from models.lens import Lens


def is_valid_thin_lens_configuration(
    focal_length_mm: float,
    working_distance_mm: float
) -> bool:
    """
    Check if working distance satisfies thin lens physical constraint.

    Thin lens equation requires: working_distance > focal_length
    for real image formation with finite magnification.

    Args:
        focal_length_mm: Lens focal length in mm
        working_distance_mm: Working distance in mm

    Returns:
        True if WD > f, False otherwise
    """
    return working_distance_mm > focal_length_mm


def is_working_distance_supported(
    lens: Lens,
    working_distance_mm: float
) -> bool:
    """
    Check if working distance falls within lens's specified range.

    Args:
        lens: Lens object with min/max working distance
        working_distance_mm: Desired working distance

    Returns:
        True if WD is in [min, max], False otherwise
    """
    return lens.min_working_distance_mm <= working_distance_mm <= lens.max_working_distance_mm


def is_sensor_coverage_valid(
    lens: Lens,
    camera: Camera
) -> bool:
    """
    Check if lens can cover the camera's sensor.

    Compares lens's maximum sensor size (diagonal) against camera's
    sensor diagonal. Lens must have coverage equal or larger than camera.

    Args:
        lens: Lens with max_sensor_size_mm (diagonal)
        camera: Camera with sensor dimensions

    Returns:
        True if lens.max_sensor_size_mm >= camera diagonal, False otherwise
    """
    camera_diagonal_mm = (camera.sensor_width_mm**2 + camera.sensor_height_mm**2)**0.5
    return lens.max_sensor_size_mm >= camera_diagonal_mm


def is_mount_compatible(
    lens: Lens,
    camera: Camera
) -> bool:
    """
    Check if lens and camera mount types are compatible.

    Args:
        lens: Lens with mount_type
        camera: Camera with mount_type

    Returns:
        True if mount types match exactly, False otherwise
    """
    return lens.mount_type == camera.mount_type
