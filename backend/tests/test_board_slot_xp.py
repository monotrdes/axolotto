import pytest
from app.models.board import PlayerBoard
from app.services.board_service import (
    _total_board_xp,
    _apply_preserved_xp_to_board,
    _level_from_total_xp,
)


def _make_board(level: int, xp: int) -> PlayerBoard:
    b = PlayerBoard(user_id="test", name="T", card_ids=[], card_first_editions=[])
    b.level = level
    b.xp = xp
    return b


def test_total_xp_level1():
    assert _total_board_xp(_make_board(1, 50)) == 50


def test_total_xp_level2():
    # Nivel 2: se gastaron 100 XP para subir de 1→2
    assert _total_board_xp(_make_board(2, 30)) == 130


def test_total_xp_level5():
    # 100+200+300+400 = 1000 XP gastados, más 150 actuales = 1150
    assert _total_board_xp(_make_board(5, 150)) == 1150


def test_apply_zero_xp():
    b = _make_board(1, 0)
    _apply_preserved_xp_to_board(b, 0)
    assert b.level == 1
    assert b.xp == 0


def test_apply_xp_crosses_levels():
    b = _make_board(1, 0)
    _apply_preserved_xp_to_board(b, 920)
    # 920: 1→2 (820 left), 2→3 (620 left), 3→4 (320 left), 320 < 400 → stop
    assert b.level == 4
    assert b.xp == 320


def test_80_percent_roundtrip():
    b = _make_board(5, 150)  # total = 1150
    preserved = int(_total_board_xp(b) * 0.8)  # 920
    nb = _make_board(1, 0)
    _apply_preserved_xp_to_board(nb, preserved)
    assert nb.level == 4
    assert nb.level < b.level  # perdió un nivel (~20%)


def test_level_from_total_xp():
    assert _level_from_total_xp(0) == 1
    assert _level_from_total_xp(99) == 1
    assert _level_from_total_xp(100) == 2
    assert _level_from_total_xp(299) == 2  # 100+200=300 necesario para nivel 3
    assert _level_from_total_xp(300) == 3


def test_roundtrip_consistency():
    """_level_from_total_xp debe devolver el mismo nivel que _apply_preserved_xp_to_board."""
    for level in range(1, 8):
        for xp_in_level in [0, 50]:
            b = _make_board(level, xp_in_level)
            total = _total_board_xp(b)
            expected_level = _level_from_total_xp(total)
            nb = _make_board(1, 0)
            _apply_preserved_xp_to_board(nb, total)
            assert nb.level == expected_level
