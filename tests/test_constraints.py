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
# Fixtures
# ============================================

@pytest.fixture
def sample_camera():
    """Reusable Camera fixture with typical dimensions."""
    return Camera(
        name="TestCamera",
        sensor_width_mm=10.0,
        sensor_height_mm=8.0,
        pixel_size_mm=0.003,
        resolution_x=4000,
        resolution_y=3200,
        mount_type="C"
    )


@pytest.fixture
def sample_lens():
    """Reusable Lens fixture with typical parameters."""
    return Lens(
        name="TestLens",
        focal_length_mm=10.0,
        max_sensor_size_mm=13.0,
        mount_type="C",
        min_working_distance_mm=10.0,
        max_working_distance_mm=1000.0
    )


@pytest.fixture
def square_camera():
    """Camera with 4:3 aspect ratio (10x7.5) but using square for diagonal test."""
    return Camera(
        name="SquareCamera",
        sensor_width_mm=10.0,
        sensor_height_mm=10.0,
        pixel_size_mm=0.003,
        resolution_x=4000,
        resolution_y=4000,
        mount_type="C"
    )


# ============================================
# is_valid_thin_lens_configuration
# ============================================

class TestIsValidThinLensConfiguration:
    """Tests for is_valid_thin_lens_configuration constraint."""

    @pytest.mark.parametrize(
        "f, wd, expected",
        [
            (10.0, 100.0, True),      # WD >> f
            (10.0, 10.1, True),       # WD barely > f (high mag)
            (10.0, 10.0001, True),    # WD just above boundary
            (10.0, 10.0, False),      # WD == f (boundary)
            (10.0, 9.9, False),       # WD < f
            (10.0, 0.0, False),       # WD zero
            (10.0, -5.0, False),      # WD negative
            (0.0, 10.0, True),        # f=0 (precondition violation, but mathematically 10>0 = True)
        ]
    )
    def test_various_cases(self, f, wd, expected):
        """Parametrized test for various f and WD combinations."""
        result = is_valid_thin_lens_configuration(focal_length_mm=f, working_distance_mm=wd)
        assert result is expected

    def test_edge_extreme_high_magnification(self):
        """Edge case: WD just 1µm above f (extreme precision)."""
        # 10.0 vs 10.000001 → still True
        assert is_valid_thin_lens_configuration(10.0, 10.000001) is True

    def test_edge_wd_just_below_f(self):
        """Edge case: WD just 1µm below f."""
        assert is_valid_thin_lens_configuration(10.0, 9.999999) is False

    # Note: test with f=0 or negative is physically meaningless and violates
    # the precondition that focal_length must be positive. Those cases are
    # responsibility of optics layer validation, not this constraint.
    # The constraint's contract assumes valid positive inputs; we test boundary
    # behavior of the WD > f inequality only.


# ============================================
# is_working_distance_supported
# ============================================

class TestWorkingDistanceSupported:
    """Tests for is_working_distance_supported constraint."""

    def test_normal(self, sample_lens):
        """Normal case: WD within range."""
        assert is_working_distance_supported(sample_lens, 100.0) is True

    def test_edge_at_minimum(self, sample_lens):
        """Edge case: WD exactly at minimum."""
        assert is_working_distance_supported(sample_lens, sample_lens.min_working_distance_mm) is True

    def test_edge_at_maximum(self, sample_lens):
        """Edge case: WD exactly at maximum."""
        assert is_working_distance_supported(sample_lens, sample_lens.max_working_distance_mm) is True

    def test_edge_exact_point(self):
        """Edge case: min == max, WD exactly that value."""
        lens = Lens(
            name="FixedWD",
            focal_length_mm=10.0,
            max_sensor_size_mm=10.0,
            mount_type="C",
            min_working_distance_mm=50.0,
            max_working_distance_mm=50.0
        )
        assert is_working_distance_supported(lens, 50.0) is True

    def test_invalid_below_min(self, sample_lens):
        """Invalid case: WD below minimum."""
        assert is_working_distance_supported(sample_lens, 5.0) is False

    def test_invalid_above_max(self, sample_lens):
        """Invalid case: WD above maximum."""
        assert is_working_distance_supported(sample_lens, 2000.0) is False

    @pytest.mark.parametrize(
        "min_wd, max_wd, wd, expected",
        [
            (10.0, 100.0, 0.0, False),    # WD zero
            (10.0, 100.0, -10.0, False),  # WD negative
            (0.0, 100.0, 50.0, True),     # min=0 (edge) – WD still within range
        ]
    )
    def test_edge_with_zero_bounds(self, min_wd, max_wd, wd, expected):
        """Edge cases involving zero or negative bounds (though unusual)."""
        lens = Lens(
            name="EdgeLens",
            focal_length_mm=10.0,
            max_sensor_size_mm=10.0,
            mount_type="C",
            min_working_distance_mm=min_wd,
            max_working_distance_mm=max_wd
        )
        assert is_working_distance_supported(lens, wd) is expected


# ============================================
# is_sensor_coverage_valid
# ============================================

class TestSensorCoverageValid:
    """Tests for is_sensor_coverage_valid constraint."""

    def test_normal_large_enough(self, sample_camera):
        """Normal case: lens coverage >= camera diagonal."""
        lens = Lens(
            name="TestLens",
            focal_length_mm=10.0,
            max_sensor_size_mm=13.0,  # Diagonal > sqrt(10^2+8^2)=12.806
            mount_type="C",
            min_working_distance_mm=10.0,
            max_working_distance_mm=1000.0
        )
        assert is_sensor_coverage_valid(lens, sample_camera) is True

    def test_edge_exact_match(self, square_camera):
        """Edge case: lens coverage exactly equals camera diagonal."""
        camera = square_camera  # 10x10 → diagonal = sqrt(200) ≈ 14.1421356237
        lens = Lens(
            name="TestLens",
            focal_length_mm=10.0,
            max_sensor_size_mm=14.142135623730951,  # Exact diagonal
            mount_type="C",
            min_working_distance_mm=10.0,
            max_working_distance_mm=1000.0
        )
        # Use approx to handle floating point
        assert is_sensor_coverage_valid(lens, camera) is True

    def test_edge_epsilon_less(self, square_camera):
        """Edge case: lens coverage just slightly less than diagonal (within tolerance)."""
        camera = square_camera
        lens = Lens(
            name="TestLens",
            focal_length_mm=10.0,
            max_sensor_size_mm=14.142,  # 0.000135 less
            mount_type="C",
            min_working_distance_mm=10.0,
            max_working_distance_mm=1000.0
        )
        assert is_sensor_coverage_valid(lens, camera) is False

    def test_invalid_too_small(self, sample_camera):
        """Invalid case: lens coverage smaller than camera diagonal."""
        lens = Lens(
            name="TestLens",
            focal_length_mm=10.0,
            max_sensor_size_mm=10.0,  # Diagonal < sqrt(10^2+8^2)=12.806
            mount_type="C",
            min_working_distance_mm=10.0,
            max_working_distance_mm=1000.0
        )
        assert is_sensor_coverage_valid(lens, sample_camera) is False

    def test_invalid_camera_diagonal_zero(self):
        """Invalid case: camera has zero sensor width and height."""
        camera = Camera(
            name="ZeroCamera",
            sensor_width_mm=0.0,
            sensor_height_mm=0.0,
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
        # Camera diagonal = 0, lens coverage >= 0 → True (but physically nonsense)
        # Precondition: camera dimensions should be > 0; constraint doesn't enforce that.
        assert is_sensor_coverage_valid(lens, camera) is True


# ============================================
# is_mount_compatible
# ============================================

class TestMountCompatible:
    """Tests for is_mount_compatible constraint."""

    def test_normal_matching(self, sample_camera, sample_lens):
        """Normal case: mount types match."""
        # Both are "C"
        sample_camera.mount_type = "C"
        sample_lens.mount_type = "C"
        assert is_mount_compatible(sample_lens, sample_camera) is True

    def test_normal_non_matching(self):
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

    def test_edge_both_none(self):
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

    def test_edge_lens_none_camera_defined(self):
        """Edge case: lens mount is None, camera is defined (not compatible)."""
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
            mount_type=None,
            min_working_distance_mm=10.0,
            max_working_distance_mm=1000.0
        )
        assert is_mount_compatible(lens, camera) is False

    def test_edge_camera_none_lens_defined(self):
        """Edge case: camera mount is None, lens is defined (not compatible)."""
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
            mount_type="C",
            min_working_distance_mm=10.0,
            max_working_distance_mm=1000.0
        )
        assert is_mount_compatible(lens, camera) is False