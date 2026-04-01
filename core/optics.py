"""
optics module

working_distance_mm is assumed to approximate object distance (o)
in thin lens model. Real systems may have mechanical offsets.
"""

from typing import Union


def calculate_fov(
    sensor_width_mm: float,
    magnification: float
) -> float:
    """
    Calculate horizontal field of view (FOV) in millimeters.

    Formula: FOV = sensor_width / magnification

    Args:
        sensor_width_mm: Sensor width in mm (must be > 0)
        magnification: Magnification ratio (must be > 0)

    Returns:
        Horizontal FOV in mm

    Raises:
        ValueError: If inputs are <= 0
    """
    if sensor_width_mm <= 0:
        raise ValueError("sensor_width_mm must be positive")
    if magnification <= 0:
        raise ValueError("magnification must be positive")

    return sensor_width_mm / magnification


def calculate_magnification(
    sensor_width_mm: float,
    fov_width_mm: float
) -> float:
    """
    Calculate magnification ratio (dimensionless).

    Formula: M = sensor_width / fov_width

    Args:
        sensor_width_mm: Sensor width in mm (must be > 0)
        fov_width_mm: Field of view width in mm (must be > 0)

    Returns:
        Magnification (ratio)

    Raises:
        ValueError: If inputs are <= 0
    """
    if sensor_width_mm <= 0:
        raise ValueError("sensor_width_mm must be positive")
    if fov_width_mm <= 0:
        raise ValueError("fov_width_mm must be positive")

    return sensor_width_mm / fov_width_mm


def calculate_focal_length(
    sensor_width_mm: float,
    fov_width_mm: float,
    working_distance_mm: float
) -> float:
    """
    Calculate focal length using thin lens equation.

    Formula: f = (sensor_width × working_distance) / (sensor_width + fov_width)

    Derivation:
    1. M = sensor_width / fov_width (magnification)
    2. Thin lens: f = (M × WD) / (M + 1)
    3. Substituting M gives the formula above

    Assumptions:
    - Thin lens model
    - Object at finite working distance (not infinity)
    - Paraxial approximation (small angles)
    - Image distance measured from lens to sensor

    Args:
        sensor_width_mm: Sensor width in mm (must be > 0)
        fov_width_mm: Desired FOV width in mm (must be > 0)
        working_distance_mm: Object distance in mm (must be > 0)

    Returns:
        Focal length in mm

    Raises:
        ValueError: If inputs are <= 0
    """
    if sensor_width_mm <= 0:
        raise ValueError("sensor_width_mm must be positive")
    if fov_width_mm <= 0:
        raise ValueError("fov_width_mm must be positive")
    if working_distance_mm <= 0:
        raise ValueError("working_distance_mm must be positive")

    return (sensor_width_mm * working_distance_mm) / (sensor_width_mm + fov_width_mm)


def calculate_resolution(
    fov_width_mm: float,
    sensor_pixels_x: int
) -> float:
    """
    Calculate spatial resolution in mm/pixel.

    Formula: resolution = FOV / pixel_count

    This represents the ground sample distance - the physical size
    represented by a single pixel in the object plane.

    Args:
        fov_width_mm: Field of view width in mm (must be > 0)
        sensor_pixels_x: Number of horizontal pixels (must be > 0)

    Returns:
        Resolution in mm/pixel (e.g., 0.005 means 5µm/pixel)

    Raises:
        ValueError: If inputs are <= 0
    """
    if fov_width_mm <= 0:
        raise ValueError("fov_width_mm must be positive")
    if sensor_pixels_x <= 0:
        raise ValueError("sensor_pixels_x must be positive")

    return fov_width_mm / sensor_pixels_x
