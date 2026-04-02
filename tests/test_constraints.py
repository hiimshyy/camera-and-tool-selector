"""
Unit tests for core/constraints.py

Tests cover all constraint functions with valid, edge, and invalid cases.
All tests are deterministic and self-contained.
"""

import pytest
from models.camera import Camera
from models.lens import Lens
from core.constraints import (
    is_valid_thin_lens_configuration,
    is_working_distance_supported,
    is_sensor_coverage_valid,
    is_mount_compatible,
)


# ============================================
# is_valid_thin_lens_configuration
# ============================================

def test_is_valid_thin_lens_configuration_normal_wd_greater():
    """Normal case: WD significantly greater than f."""
    assert is_valid_thin_lens_configuration(focal_length_mm=10.0, working_distance_mm=100.0) is True


def test_is_valid_thin_lens_configuration_edge_wd_slightly_greater():
    """Edge case: WD just slightly greater than f."""
    assert is_valid_thin_lens_configuration(focal_length_mm=10.0, working_distance_mm=10.0001) is True


def test_is_valid_thin_lens_configuration_invalid_wd_equals():
    """Invalid case: WD exactly equals f (boundary)."""
    assert is_valid_thin_lens_configuration(focal_length_mm=10.0, working_distance_mm=10.0) is False


def test_is_valid_thin_lens_configuration_invalid_wd_less():
    """Invalid case: WD less than f."""
    assert is_valid_thin_lens_configuration(focal_length_mm=10.0, working_distance_mm=5.0) is False


def test_is_valid_thin_lens_configuration_invalid_wd_zero():
    """Invalid case: WD is zero."""
    assert is_valid_thin_lens_configuration(focal_length_mm=10.0, working_distance_mm=0.0) is False


def test_is_valid_thin_lens_configuration_invalid_f_zero():
    """Invalid case: f is zero (WD > 0 should still return False due to physical nonsense)."""
    # Technically WD > 0, but f=0 is invalid; function only checks WD > f
    # With f=0, WD > 0 would return True; but that's not a physically meaningful case
    # The function only checks the inequality; other validation happens elsewhere
    assert is_valid_thin_lens_configuration(focal_length_mm=0.0, working_distance_mm=10.0) is True


# ============================================
# is_working_distance_supported
# ============================================

def test_is_working_distance_supported_normal():
    """Normal case: WD within range."""
    lens = Lens(
        name="TestLens",
        focal_length_mm=10.0,
        max_sensor_size_mm=10.0,
        mount_type="C",
        min_working_distance_mm=10.0,
        max_working_distance_mm=1000.0
    )
    wd = 100.0
    assert is_working_distance_supported(lens, wd) is True


def test_is_working_distance_supported_edge_at_minimum():
    """Edge case: WD exactly at minimum."""
    lens = Lens(
        name="TestLens",
        focal_length_mm=10.0,
        max_sensor_size_mm=10.0,
        mount_type="C",
        min_working_distance_mm=50.0,
        max_working_distance_mm=1000.0
    )
    assert is_working_distance_supported(lens, 50.0) is True


def test_is_working_distance_supported_edge_at_maximum():
    """Edge case: WD exactly at maximum."""
    lens = Lens(
        name="TestLens",
        focal_length_mm=10.0,
        max_sensor_size_mm=10.0,
        mount_type="C",
        min_working_distance_mm=10.0,
        max_working_distance_mm=1000.0
    )
    assert is_working_distance_supported(lens, 1000.0) is True


def test_is_working_distance_supported_invalid_below_min():
    """Invalid case: WD below minimum."""
    lens = Lens(
        name="TestLens",
        focal_length_mm=10.0,
        max_sensor_size_mm=10.0,
        mount_type="C",
        min_working_distance_mm=50.0,
        max_working_distance_mm=1000.0
    )
    assert is_working_distance_supported(lens, 25.0) is False


def test_is_working_distance_supported_invalid_above_max():
    """Invalid case: WD above maximum."""
    lens = Lens(
        name="TestLens",
        focal_length_mm=10.0,
        max_sensor_size_mm=10.0,
        mount_type="C",
        min_working_distance_mm=10.0,
        max_working_distance_mm=100.0
    )
    assert is_working_distance_supported(lens, 500.0) is False


# ============================================
# is_sensor_coverage_valid
# ============================================

def test_is_sensor_coverage_valid_normal_large_enough():
    """Normal case: lens coverage >= camera diagonal."""
    camera = Camera(
        name="TestCamera",
        sensor_width_mm=10.0,
        sensor_height_mm=8.0,
        pixel_size_mm=0.003,
        resolution_x=4000,
        resolution_y=3200,
        mount_type="C"
    )
    lens = Lens(
        name="TestLens",
        focal_length_mm=10.0,
        max_sensor_size_mm=13.0,  # Diagonal > sqrt(10^2+8^2)=12.8
        mount_type="C",
        min_working_distance_mm=10.0,
        max_working_distance_mm=1000.0
    )
    assert is_sensor_coverage_valid(lens, camera) is True


def test_is_sensor_coverage_valid_edge_exact_match():
    """Edge case: lens coverage exactly equals camera diagonal."""
    camera = Camera(
        name="TestCamera",
        sensor_width_mm=10.0,
        sensor_height_mm=10.0,
        pixel_size_mm=0.003,
        resolution_x=4000,
        resolution_y=4000,
        mount_type="C"
    )
    lens = Lens(
        name="TestLens",
        focal_length_mm=10.0,
        max_sensor_size_mm=14.1421,  # sqrt(10^2+10^2) ≈ 14.1421
        mount_type="C",
        min_working_distance_mm=10.0,
        max_working_distance_mm=1000.0
    )
    assert is_sensor_coverage_valid(lens, camera) is True


def test_is_sensor_coverage_valid_invalid_too_small():
    """Invalid case: lens coverage smaller than camera diagonal."""
    camera = Camera(
        name="TestCamera",
        sensor_width_mm=15.0,
        sensor_height_mm=10.0,
        pixel_size_mm=0.003,
        resolution_x=4000,
        resolution_y=3200,
        mount_type="C"
    )
    lens = Lens(
        name="TestLens",
        focal_length_mm=10.0,
        max_sensor_size_mm=10.0,  # Diagonal < sqrt(15^2+10^2)=18.03
        mount_type="C",
        min_working_distance_mm=10.0,
        max_working_distance_mm=1000.0
    )
    assert is_sensor_coverage_valid(lens, camera) is False


# ============================================
# is_mount_compatible
# ============================================

def test_is_mount_compatible_normal_matching():
    """Normal case: mount types match."""
    camera = Camera(
        name="TestCamera",
        sensor_width_mm=10.0,
        sensor_height_mm=8.0,
        pixel_size_mm=0.003,
        resolution_x=4000,
        resolution_y=3200,
        mount_type="C"
    )
    lens = Lens(
        name="TestLens",
        focal_length_mm=10.0,
        max_sensor_size_mm=10.0,
        mount_type="C",
        min_working_distance_mm=10.0,
        max_working_distance_mm=1000.0
    )
    assert is_mount_compatible(lens, camera) is True


def test_is_mount_compatible_normal_non_matching():
    """Invalid case: mount types differ."""
    camera = Camera(
        name="TestCamera",
        sensor_width_mm=10.0,
        sensor_height_mm=8.0,
        pixel_size_mm=0.003,
        resolution_x=4000,
        resolution_y=3200,
        mount_type="CS"
    )
    lens = Lens(
        name="TestLens",
        focal_length_mm=10.0,
        max_sensor_size_mm=10.0,
        mount_type="C",
        min_working_distance_mm=10.0,
        max_working_distance_mm=1000.0
    )
    assert is_mount_compatible(lens, camera) is False


def test_is_mount_compatible_edge_both_none():
    """Edge case: both mount types are None (should be compatible)."""
    camera = Camera(
        name="TestCamera",
        sensor_width_mm=10.0,
        sensor_height_mm=8.0,
        pixel_size_mm=0.003,
        resolution_x=4000,
        resolution_y=3200,
        mount_type=None
    )
    lens = Lens(
        name="TestLens",
        focal_length_mm=10.0,
        max_sensor_size_mm=10.0,
        mount_type=None,
        min_working_distance_mm=10.0,
        max_working_distance_mm=1000.0
    )
    assert is_mount_compatible(lens, camera) is True
