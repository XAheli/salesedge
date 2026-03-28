from __future__ import annotations

import pytest

from app.utils.confidence import bootstrap_ci, wilson_score


class TestBootstrapCI:
    def test_empty_data(self):
        lower, upper = bootstrap_ci([])
        assert lower == 0.0
        assert upper == 0.0

    def test_single_value(self):
        lower, upper = bootstrap_ci([5.0], seed=42)
        assert lower == 5.0
        assert upper == 5.0

    def test_identical_values(self):
        lower, upper = bootstrap_ci([3.0, 3.0, 3.0, 3.0], seed=42)
        assert lower == 3.0
        assert upper == 3.0

    def test_known_distribution(self):
        data = list(range(1, 101))
        lower, upper = bootstrap_ci(data, seed=42)
        assert 45.0 < lower < 55.0
        assert 45.0 < upper < 55.0
        assert lower <= upper

    def test_ci_width_shrinks_with_more_data(self):
        small_data = [1.0, 2.0, 3.0, 4.0, 5.0]
        large_data = list(range(1, 1001))
        lo_s, hi_s = bootstrap_ci(small_data, seed=42)
        lo_l, hi_l = bootstrap_ci(large_data, seed=42)
        assert (hi_l - lo_l) < (hi_s - lo_s)

    def test_confidence_level_affects_width(self):
        data = list(range(1, 51))
        lo_90, hi_90 = bootstrap_ci(data, confidence_level=0.90, seed=42)
        lo_99, hi_99 = bootstrap_ci(data, confidence_level=0.99, seed=42)
        assert (hi_99 - lo_99) > (hi_90 - lo_90)

    def test_reproducibility_with_seed(self):
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        result1 = bootstrap_ci(data, seed=123)
        result2 = bootstrap_ci(data, seed=123)
        assert result1 == result2


class TestWilsonScore:
    def test_zero_total(self):
        lower, upper = wilson_score(0, 0)
        assert lower == 0.0
        assert upper == 0.0

    def test_all_successes(self):
        lower, upper = wilson_score(10, 10)
        assert lower > 0.5
        assert upper <= 1.0

    def test_no_successes(self):
        lower, upper = wilson_score(0, 10)
        assert lower >= 0.0
        assert upper < 0.5

    def test_half_successes(self):
        lower, upper = wilson_score(50, 100)
        assert lower < 0.5
        assert upper > 0.5

    def test_bounds_are_valid(self):
        lower, upper = wilson_score(3, 10)
        assert 0.0 <= lower <= upper <= 1.0

    def test_small_sample(self):
        lower, upper = wilson_score(1, 2)
        assert 0.0 <= lower
        assert upper <= 1.0
        assert lower < upper

    def test_large_sample_converges(self):
        lower, upper = wilson_score(500, 1000)
        assert 0.45 < lower < 0.50
        assert 0.50 < upper < 0.55

    def test_custom_z_wider_interval(self):
        lo_95, hi_95 = wilson_score(30, 100, z=1.96)
        lo_99, hi_99 = wilson_score(30, 100, z=2.576)
        assert (hi_99 - lo_99) > (hi_95 - lo_95)
