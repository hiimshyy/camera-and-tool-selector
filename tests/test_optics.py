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


class TestCalculateFov:
    """Tests for calculate_fov function."""

    def test_normal(self):
        """Normal case: typical values."""
        fov = calculate_fov(sensor_width_mm=10.0, magnification=2.0)
        assert fov == pytest.approx(5.0)

    def test_edge_large_values(self):
        """Edge case: very large sensor and magnification."""
        fov = calculate_fov(sensor_width_mm=10000.0, magnification=1000.0)
        assert fov == pytest.approx(10.0)

    def test_edge_small_values(self):
        """Edge case: very small but positive values."""
        fov = calculate_fov(sensor_width_mm=0.001, magnification=0.5)
        assert fov == pytest.approx(0.002)

    def test_edge_magnification_one(self):
        """Edge case: magnification = 1 (sensor width equals FOV)."""
        fov = calculate_fov(sensor_width_mm=10.0, magnification=1.0)
        assert fov == pytest.approx(10.0)

    def test_invalid_sensor_zero(self):
        """Invalid input: sensor_width is zero."""
        with pytest.raises(ValueError, match="sensor_width_mm must be positive"):
            calculate_fov(sensor_width_mm=0.0, magnification=2.0)

    def test_invalid_sensor_negative(self):
        """Invalid input: sensor_width is negative."""
        with pytest.raises(ValueError, match="sensor_width_mm must be positive"):
            calculate_fov(sensor_width_mm=-5.0, magnification=2.0)

    def test_invalid_magnification_zero(self):
        """Invalid input: magnification is zero."""
        with pytest.raises(ValueError, match="magnification must be positive"):
            calculate_fov(sensor_width_mm=10.0, magnification=0.0)

    def test_invalid_magnification_negative(self):
        """Invalid input: magnification is negative."""
        with pytest.raises(ValueError, match="magnification must be positive"):
            calculate_fov(sensor_width_mm=10.0, magnification=-1.0)


class TestCalculateMagnification:
    """Tests for calculate_magnification function."""

    def test_normal(self):
        """Normal case: typical sensor and FOV."""
        mag = calculate_magnification(sensor_width_mm=10.0, fov_width_mm=5.0)
        assert mag == pytest.approx(2.0)

    def test_edge_less_than_one(self):
        """Edge case: magnification < 1 (wide angle)."""
        mag = calculate_magnification(sensor_width_mm=10.0, fov_width_mm=50.0)
        assert mag == pytest.approx(0.2)

    def test_edge_greater_than_one(self):
        """Edge case: magnification > 1 (macro)."""
        mag = calculate_magnification(sensor_width_mm=10.0, fov_width_mm=2.0)
        assert mag == pytest.approx(5.0)

    def test_edge_magnification_fractional(self):
        """Edge case: magnification exactly computed from fov=sensor/3."""
        mag = calculate_magnification(sensor_width_mm=12.0, fov_width_mm=4.0)
        assert mag == pytest.approx(3.0)

    def test_invalid_sensor_zero(self):
        """Invalid input: sensor_width is zero."""
        with pytest.raises(ValueError, match="sensor_width_mm must be positive"):
            calculate_magnification(sensor_width_mm=0.0, fov_width_mm=5.0)

    def test_invalid_fov_zero(self):
        """Invalid input: fov_width is zero."""
        with pytest.raises(ValueError, match="fov_width_mm must be positive"):
            calculate_magnification(sensor_width_mm=10.0, fov_width_mm=0.0)

    def test_invalid_fov_negative(self):
        """Invalid input: fov_width is negative."""
        with pytest.raises(ValueError, match="fov_width_mm must be positive"):
            calculate_magnification(sensor_width_mm=10.0, fov_width_mm=-5.0)


class TestCalculateFocalLength:
    """Tests for calculate_focal_length function."""

    def test_normal(self):
        """Normal case: typical values."""
        f = calculate_focal_length(
            sensor_width_mm=10.0,
            fov_width_mm=5.0,
            working_distance_mm=100.0
        )
        assert f == pytest.approx(66.6666667, abs=0.0001)

    def test_edge_very_large_wd(self):
        """Edge case: working distance much larger than sensor+FOV."""
        f = calculate_focal_length(
            sensor_width_mm=5.0,
            fov_width_mm=1.0,
            working_distance_mm=10000.0
        )
        assert f == pytest.approx(8333.3333, abs=0.001)

    def test_edge_macro_setup(self):
        """Edge case: small WD, moderate magnification."""
        f = calculate_focal_length(
            sensor_width_mm=10.0,
            fov_width_mm=2.0,
            working_distance_mm=15.0
        )
        assert f == pytest.approx(12.5)

    def test_invalid_sensor_zero(self):
        """Invalid input: sensor_width is zero."""
        with pytest.raises(ValueError, match="sensor_width_mm must be positive"):
            calculate_focal_length(
                sensor_width_mm=0.0,
                fov_width_mm=5.0,
                working_distance_mm=100.0
            )

    def test_invalid_fov_zero(self):
        """Invalid input: fov_width is zero."""
        with pytest.raises(ValueError, match="fov_width_mm must be positive"):
            calculate_focal_length(
                sensor_width_mm=10.0,
                fov_width_mm=0.0,
                working_distance_mm=100.0
            )

    def test_invalid_wd_zero(self):
        """Invalid input: working_distance is zero."""
        with pytest.raises(ValueError, match="working_distance_mm must be positive"):
            calculate_focal_length(
                sensor_width_mm=10.0,
                fov_width_mm=5.0,
                working_distance_mm=0.0
            )


class TestCalculateResolution:
    """Tests for calculate_resolution function."""

    def test_normal(self):
        """Normal case: typical FOV and pixel count."""
        res = calculate_resolution(fov_width_mm=10.0, sensor_pixels_x=2000)
        assert res == pytest.approx(0.005)  # 5 µm/pixel

    def test_edge_large_fov(self):
        """Edge case: large FOV with many pixels."""
        res = calculate_resolution(fov_width_mm=1000.0, sensor_pixels_x=10000)
        assert res == pytest.approx(0.1)

    def test_edge_small_fov_few_pixels(self):
        """Edge case: small FOV with few pixels."""
        res = calculate_resolution(fov_width_mm=1.0, sensor_pixels_x=100)
        assert res == pytest.approx(0.01)

    def test_invalid_fov_zero(self):
        """Invalid input: FOV is zero."""
        with pytest.raises(ValueError, match="fov_width_mm must be positive"):
            calculate_resolution(fov_width_mm=0.0, sensor_pixels_x=1000)

    def test_invalid_fov_negative(self):
        """Invalid input: FOV is negative."""
        with pytest.raises(ValueError, match="fov_width_mm must be positive"):
            calculate_resolution(fov_width_mm=-5.0, sensor_pixels_x=1000)

    def test_invalid_pixels_zero(self):
        """Invalid input: pixel count is zero."""
        with pytest.raises(ValueError, match="sensor_pixels_x must be positive"):
            calculate_resolution(fov_width_mm=10.0, sensor_pixels_x=0)

    def test_invalid_pixels_negative(self):
        """Invalid input: pixel count is negative."""
        with pytest.raises(ValueError, match="sensor_pixels_x must be positive"):
            calculate_resolution(fov_width_mm=10.0, sensor_pixels_x=-100)


class TestCalculateMagnificationFromFocalLength:
    """Tests for calculate_magnification_from_focal_length function."""

    @pytest.mark.parametrize(
        "focal_length, working_distance, expected",
        [
            (10.0, 100.0, 0.111111),  # Normal: WD >> f
            (50.0, 10000.0, 0.005025),  # Very low mag
            (10.0, 10.1, 100.0),  # WD just above f (high mag)
            (25.0, 25.01, 2500.0),  # Extreme high mag
        ]
    )
    def test_normal_cases(self, focal_length, working_distance, expected):
        """Parametrized normal and edge cases."""
        mag = calculate_magnification_from_focal_length(focal_length, working_distance)
        assert mag == pytest.approx(expected, abs=1e-6)

    def test_edge_wd_just_above_f_large(self):
        """Edge case: WD just above f with larger values."""
        mag = calculate_magnification_from_focal_length(focal_length_mm=100.0, working_distance_mm=100.001)
        # Expected: 100 / 0.001 = 100000
        assert mag == pytest.approx(100000.0)

    def test_invalid_f_zero(self):
        """Invalid input: focal_length is zero."""
        with pytest.raises(ValueError, match="focal_length_mm must be positive"):
            calculate_magnification_from_focal_length(focal_length_mm=0.0, working_distance_mm=100.0)

    def test_invalid_f_negative(self):
        """Invalid input: focal_length is negative."""
        with pytest.raises(ValueError, match="focal_length_mm must be positive"):
            calculate_magnification_from_focal_length(focal_length_mm=-10.0, working_distance_mm=100.0)

    def test_invalid_wd_equals_f(self):
        """Invalid input: WD equals focal length."""
        with pytest.raises(ValueError, match="working_distance_mm.*must be greater than focal_length_mm"):
            calculate_magnification_from_focal_length(focal_length_mm=10.0, working_distance_mm=10.0)

    def test_invalid_wd_less_than_f(self):
        """Invalid input: WD less than focal length."""
        with pytest.raises(ValueError, match="working_distance_mm.*must be greater than focal_length_mm"):
            calculate_magnification_from_focal_length(focal_length_mm=10.0, working_distance_mm=5.0)

    def test_invalid_wd_negative(self):
        """Invalid input: WD is negative."""
        with pytest.raises(ValueError, match="working_distance_mm must be positive"):
            calculate_magnification_from_focal_length(focal_length_mm=10.0, working_distance_mm=-10.0)