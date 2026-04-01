"""
Vision requirement model.

Represents user's imaging requirements.
External units may differ; normalization happens before calculations.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VisionRequirement:
    """User's imaging requirements in external units."""
    fov_width_mm: float
    fov_height_mm: float
    working_distance_mm: float
    required_resolution_um_per_pixel: float  # e.g., 5.0 means 5 µm/pixel
