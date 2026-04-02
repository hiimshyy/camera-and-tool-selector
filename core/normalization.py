"""
Unit normalization module.

Centralized conversion utilities for unit transformations.
Internal standard: millimeters (mm) for all length measurements.
Converts external inputs (µm, inch, optical format) to internal representation.
"""

# Lookup table: optical format → approximate sensor WIDTH in mm
# These values assume a 4:3 aspect ratio sensor (common in machine vision).
# Optical format is a legacy nominal designation, not a true inch measurement.
_OPTICAL_FORMAT_WIDTH_MM = {
    "1/4": 3.2,    # 4mm diagonal → width ≈ 3.2mm
    "1/3": 4.8,    # 6mm diagonal → width ≈ 4.8mm
    "1/2": 6.4,    # 8mm diagonal → width ≈ 6.4mm
    "1/1.8": 6.8,  # 8.5mm diagonal → width ≈ 6.8mm
    "1/2.5": 5.12, # 6.4mm diagonal → width ≈ 5.1mm
    "2/3": 8.8,    # 11mm diagonal → width ≈ 8.8mm
    "1": 12.8,     # 16mm diagonal → width ≈ 12.8mm
}


def pixel_size_to_mm(pixel_size_um: float) -> float:
    """
    Convert pixel size from micrometers (µm) to millimeters (mm).

    Formula: mm = µm / 1000

    Args:
        pixel_size_um: Pixel size in micrometers

    Returns:
        Pixel size in millimeters

    Raises:
        ValueError: If input is negative
    """
    if pixel_size_um < 0:
        raise ValueError("pixel_size_um must be non-negative")
    return pixel_size_um / 1000.0


def resolution_to_mm_per_pixel(resolution_um_per_pixel: float) -> float:
    """
    Convert resolution from micrometers per pixel to millimeters per pixel.

    Formula: mm/pixel = (µm/pixel) / 1000

    Args:
        resolution_um_per_pixel: Resolution in µm/pixel

    Returns:
        Resolution in mm/pixel

    Raises:
        ValueError: If input is negative
    """
    if resolution_um_per_pixel < 0:
        raise ValueError("resolution_um_per_pixel must be non-negative")
    return resolution_um_per_pixel / 1000.0


def optical_format_to_sensor_width_mm(optical_format: str) -> float:
    """
    Convert lens optical format (e.g., "1/2", "1/3") to approximate
    sensor width in millimeters.

    Note: Optical format is a legacy nominal designation, NOT a true
    inch measurement. Conversion uses a standard lookup table based on
    typical 4:3 aspect ratio sensors.

    Args:
        optical_format: Optical format string (e.g., "1/2", "1/3")

    Returns:
        Approximate sensor width in mm

    Raises:
        ValueError: If optical format is not in the lookup table
    """
    if optical_format in _OPTICAL_FORMAT_WIDTH_MM:
        return _OPTICAL_FORMAT_WIDTH_MM[optical_format]
    raise ValueError(
        f"Unknown optical format: {optical_format}. "
        f"Supported formats: {list(_OPTICAL_FORMAT_WIDTH_MM.keys())}"
    )
