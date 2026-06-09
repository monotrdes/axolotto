import random
from app.services.sal_service import apply_sal_bias, sal_slip_chance, room_entropy


def test_sal_zero_does_not_change_deck():
    rng = random.Random(42)
    deck = list(range(54))
    board = list(range(16))
    result = apply_sal_bias(deck.copy(), board, sal=0.0, rng=rng)
    assert result == deck


def test_sal_bias_pushes_board_cards_to_second_half():
    rng = random.Random(1)
    deck = list(range(54))
    board = list(range(16))
    result = apply_sal_bias(deck.copy(), board, sal=100.0, rng=rng)
    half = len(deck) // 2
    first_half_board = [c for c in result[:half] if c in board]
    assert len(first_half_board) < 16


def test_sal_bias_preserves_all_cards():
    rng = random.Random(7)
    deck = list(range(54))
    board = [3, 9, 21, 40]
    result = apply_sal_bias(deck.copy(), board, sal=60.0, rng=rng)
    assert sorted(result) == sorted(deck)


def test_sal_slip_chance_zero():
    assert sal_slip_chance(0.0) == 0.0


def test_sal_slip_chance_max():
    # sal=100 -> 100/300 = 0.333...
    assert abs(sal_slip_chance(100.0) - 0.3333) < 0.001


def test_sal_slip_chance_clamped():
    # Very high SAL still capped at 1/3
    assert sal_slip_chance(999.0) <= 0.3334


def test_room_entropy_empty():
    assert room_entropy([]) == 0.0


def test_room_entropy_all_clean():
    assert room_entropy([0.0, 0.0, 5.0]) < 0.1


def test_room_entropy_all_salty():
    # Average 100 -> entropy = 1.0
    assert room_entropy([100.0, 100.0, 100.0]) == 1.0


def test_room_entropy_mixed():
    e = room_entropy([50.0, 50.0])
    assert abs(e - 0.5) < 0.01
