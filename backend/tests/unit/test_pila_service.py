from app.services.pila_service import recovery_multiplier


def test_pila_min_is_full_time():
    assert recovery_multiplier(50) == 1.0


def test_pila_max_is_half():
    # 1 - (200-50)/300 = 1 - 0.5 = 0.5
    assert abs(recovery_multiplier(200) - 0.5) < 0.001


def test_pila_base_100():
    # 1 - (100-50)/300 = 1 - 0.167 = 0.833
    m = recovery_multiplier(100)
    assert 0.82 < m < 0.85


def test_pila_clamped_floor():
    # Formula could go below 0.35 with very high PILA
    assert recovery_multiplier(10000) == 0.35


def test_pila_clamp_ceiling():
    # Can't exceed 1.0
    assert recovery_multiplier(0) == 1.0
