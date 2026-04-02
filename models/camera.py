"""
Camera data model.

Represents a camera with normalized internal values.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Camera:
    """Camera specification with normalized units."""
    name: str
    sensor_width_mm: float
    sensor_height_mm: float
    pixel_size_mm: float       # INTERNAL: always stored normalized to mm
    resolution_x: int
    resolution_y: int
    mount_type: str            # e.g., "C", "CS"
