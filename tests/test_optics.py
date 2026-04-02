"""
Unit tests for core/optics.py

Tests cover normal cases, edge cases, and invalid inputs.
All tests are deterministic and self-contained.
"""

import pytest
from core.optics import (
    calculate_fov,
    calculate_magnification,
    calculate_focal_length,
    calculate_resolution,
    calculate_magnification_from_focal_length,
)


# ============================================
# calculate_fov
# ============================================

def test_calculate_fov_normal():
    """Normal case: typical values."""
    fov = calculate_fov(sensor_width_mm=10.0, magnification=2.0)
    assert fov == pytest.approx(5.0)


def test_calculate_fov_edge_large_values():
    """Edge case: very large sensor and magnification."""
    fov = calculate_fov(sensor_width_mm=10000.0, magnification=1000.0)
    assert fov == pytest.approx(10.0)


def test_calculate_fov_edge_small_values():
    """Edge case: very small but positive values."""
    fov = calculate_fov(sensor_width_mm=0.001, magnification=0.5)
    assert fov == pytest.approx(0.002)


def test_calculate_fov_invalid_sensor_zero():
    """Invalid input: sensor_width is zero."""
    with pytest.raises(ValueError, match="sensor_width_mm must be positive"):
        calculate_fov(sensor_width_mm=0.0, magnification=2.0)


def test_calculate_fov_invalid_sensor_negative():
    """Invalid input: sensor_width is negative."""
    with pytest.raises(ValueError, match="sensor_width_mm must be positive"):
        calculate_fov(sensor_width_mm=-5.0, magnification=2.0)


def test_calculate_fov_invalid_magnification_zero():
    """Invalid input: magnification is zero."""
    with pytest.raises(ValueError, match="magnification must be positive"):
        calculate_fov(sensor_width_mm=10.0, magnification=0.0)


def test_calculate_fov_invalid_magnification_negative():
    """Invalid input: magnification is negative."""
    with pytest.raises(ValueError, match="magnification must be positive"):
        calculate_fov(sensor_width_mm=10.0, magnification=-1.0)


# ============================================
# calculate_magnification
# ============================================

def test_calculate_magnification_normal():
    """Normal case: typical sensor and FOV."""
    mag = calculate_magnification(sensor_width_mm=10.0, fov_width_mm=5.0)
    assert mag == pytest.approx(2.0)


def test_calculate_magnification_edge_less_than_one():
    """Edge case: magnification < 1 (wide angle)."""
    mag = calculate_magnification(sensor_width_mm=10.0, fov_width_mm=50.0)
    assert mag == pytest.approx(0.2)


def test_calculate_magnification_edge_greater_than_one():
    """Edge case: magnification > 1 (macro)."""
    mag = calculate_magnification(sensor_width_mm=10.0, fov_width_mm=2.0)
    assert mag == pytest.approx(5.0)


def test_calculate_magnification_invalid_sensor_zero():
    """Invalid input: sensor_width is zero."""
    with pytest.raises(ValueError, match="sensor_width_mm must be positive"):
        calculate_magnification(sensor_width_mm=0.0, fov_width_mm=5.0)


def test_calculate_magnification_invalid_fov_zero():
    """Invalid input: fov_width is zero."""
    with pytest.raises(ValueError, match="fov_width_mm must be positive"):
        calculate_magnification(sensor_width_mm=10.0, fov_width_mm=0.0)


# ============================================
# calculate_focal_length
# ============================================

def test_calculate_focal_length_normal():
    """Normal case: typical values."""
    f = calculate_focal_length(
        sensor_width_mm=10.0,
        fov_width_mm=5.0,
        working_distance_mm=100.0
    )
    # Expected: (10*100)/(10+5) = 1000/15 ≈ 66.67
    assert f == pytest.approx(66.6667, abs=0.001)


def test_calculate_focal_length_edge_very_large_wd():
    """Edge case: working distance much larger than sensor+FOV."""
    f = calculate_focal_length(
        sensor_width_mm=5.0,
        fov_width_mm=1.0,
        working_distance_mm=10000.0
    )
    # Expected: (5*10000)/(5+1) = 50000/6 ≈ 8333.33
    assert f == pytest.approx(8333.33, abs=0.01)


def test_calculate_focal_length_edge_macro_setup():
    """Edge case: small WD, moderate magnification."""
    f = calculate_focal_length(
        sensor_width_mm=10.0,
        fov_width_mm=2.0,
        working_distance_mm=15.0
    )
    # Expected: (10*15)/(10+2) = 150/12 = 12.5
    assert f == pytest.approx(12.5)


def test_calculate_focal_length_invalid_sensor_zero():
    """Invalid input: sensor_width is zero."""
    with pytest.raises(ValueError, match="sensor_width_mm must be positive"):
        calculate_focal_length(
            sensor_width_mm=0.0,
            fov_width_mm=5.0,
            working_distance_mm=100.0
        )


def test_calculate_focal_length_invalid_fov_zero():
    """Invalid input: fov_width is zero."""
    with pytest.raises(ValueError, match="fov_width_mm must be positive"):
        calculate_focal_length(
            sensor_width_mm=10.0,
            fov_width_mm=0.0,
            working_distance_mm=100.0
        )


def test_calculate_focal_length_invalid_wd_zero():
    """Invalid input: working_distance is zero."""
    with pytest.raises(ValueError, match="working_distance_mm must be positive"):
        calculate_focal_length(
            sensor_width_mm=10.0,
            fov_width_mm=5.0,
            working_distance_mm=0.0
        )


# ============================================
# calculate_resolution
# ============================================

def test_calculate_resolution_normal():
    """Normal case: typical FOV and pixel count."""
    res = calculate_resolution(fov_width_mm=10.0, sensor_pixels_x=2000)
    assert res == pytest.approx(0.005)  # 5 µm/pixel = 0.005 mm/pixel


def test_calculate_resolution_edge_large_fov():
    """Edge case: large FOV with many pixels."""
    res = calculate_resolution(fov_width_mm=1000.0, sensor_pixels_x=10000)
    assert res == pytest.approx(0.1)


def test_calculate_resolution_edge_small_fov_few_pixels():
    """Edge case: small FOV with few pixels."""
    res = calculate_resolution(fov_width_mm=1.0, sensor_pixels_x=100)
    assert res == pytest.approx(0.01)


def test_calculate_resolution_invalid_fov_zero():
    """Invalid input: FOV is zero."""
    with pytest.raises(ValueError, match="fov_width_mm must be positive"):
        calculate_resolution(fov_width_mm=0.0, sensor_pixels_x=1000)


def test_calculate_resolution_invalid_fov_negative():
    """Invalid input: FOV is negative."""
    with pytest.raises(ValueError, match="fov_width_mm must be positive"):
        calculate_resolution(fov_width_mm=-5.0, sensor_pixels_x=1000)


def test_calculate_resolution_invalid_pixels_zero():
    """Invalid input: pixel count is zero."""
    with pytest.raises(ValueError, match="sensor_pixels_x must be positive"):
        calculate_resolution(fov_width_mm=10.0, sensor_pixels_x=0)


def test_calculate_resolution_invalid_pixels_negative():
    """Invalid input: pixel count is negative."""
    with pytest.raises(ValueError, match="sensor_pixels_x must be positive"):
        calculate_resolution(fov_width_mm=10.0, sensor_pixels_x=-100)


# ============================================
# calculate_magnification_from_focal_length
# ============================================

def test_calculate_magnification_from_focal_length_normal():
    """Normal case: WD significantly larger than f."""
    mag = calculate_magnification_from_focal_length(focal_length_mm=10.0, working_distance_mm=100.0)
    # Expected: 10 / (100 - 10) = 10/90 ≈ 0.1111
    assert mag == pytest.approx(0.111111, abs=0.00001)


def test_calculate_magnification_from_focal_length_edge_wd_just_above_f():
    """Edge case: WD just slightly greater than f (high magnification)."""
    mag = calculate_magnification_from_focal_length(focal_length_mm=10.0, working_distance_mm=10.1)
    # Expected: 10 / (10.1 - 10) = 10 / 0.1 = 100
    assert mag == pytest.approx(100.0)


def test_calculate_magnification_from_focal_length_edge_wd_much_larger():
    """Edge case: WD >> f (very low magnification)."""
    mag = calculate_magnification_from_focal_length(focal_length_mm=50.0, working_distance_mm=10000.0)
    # Expected: 50 / (10000 - 50) ≈ 0.005025
    assert mag == pytest.approx(0.005025, abs=0.000001)


def test_calculate_magnification_from_focal_length_invalid_f_zero():
    """Invalid input: focal_length is zero."""
    with pytest.raises(ValueError, match="focal_length_mm must be positive"):
        calculate_magnification_from_focal_length(focal_length_mm=0.0, working_distance_mm=100.0)


def test_calculate_magnification_from_focal_length_invalid_f_negative():
    """Invalid input: focal_length is negative."""
    with pytest.raises(ValueError, match="focal_length_mm must be positive"):
        calculate_magnification_from_focal_length(focal_length_mm=-10.0, working_distance_mm=100.0)


def test_calculate_magnification_from_focal_length_invalid_wd_equals_f():
    """Invalid input: WD equals focal length."""
    with pytest.raises(ValueError, match="working_distance_mm .* must be greater than focal_length_mm"):
        calculate_magnification_from_focal_length(focal_length_mm=10.0, working_distance_mm=10.0)


def test_calculate_magnification_from_focal_length_invalid_wd_less_than_f():
    """Invalid input: WD less than focal length."""
    with pytest.raises(ValueError, match="working_distance_mm .* must be greater than focal_length_mm"):
        calculate_magnification_from_focal_length(focal_length_mm=10.0, working_distance_mm=5.0)
