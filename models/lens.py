"""
Lens data model.

Represents a lens with normalized internal values.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Lens:
    """Lens specification with normalized units."""
    name: str
    focal_length_mm: float
    max_sensor_size_mm: float  # Diagonal measurement in mm (coverage limit)
    mount_type: str
    min_working_distance_mm: float
    max_working_distance_mm: float
    distortion: Optional[str | float] = None  # Qualitative label or percentage
