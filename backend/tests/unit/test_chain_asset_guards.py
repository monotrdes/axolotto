"""Chain-authoritative asset mutations must fail before touching the DB."""

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.incubation import _perform_hatch
from app.core.config import settings
from app.services.board.board_generator import create_manual_board_operation
from app.services.reciclon_service import recycle_cards


@pytest.fixture(autouse=True)
def safe_mode(monkeypatch):
    monkeypatch.setattr(settings, "PRODUCT_MODE", "non_gambling")


@pytest.mark.parametrize(
    ("flag", "call", "feature"),
    [
        (
            "ENABLE_BOARD_ASSET_MUTATIONS",
            lambda: create_manual_board_operation("user", "board", [], [], None),
            "board_asset_mutations",
        ),
        (
            "ENABLE_HATCHING",
            lambda: _perform_hatch(None, None, None),
            "hatching",
        ),
        (
            "ENABLE_RECICLON",
            lambda: recycle_cards(None, "user", []),
            "reciclon",
        ),
    ],
)
def test_disabled_asset_mutation_fails_before_data_access(
    monkeypatch,
    flag,
    call,
    feature,
):
    monkeypatch.setattr(settings, flag, False)

    with pytest.raises(HTTPException) as exc:
        call()

    assert exc.value.status_code == 503
    assert exc.value.detail["feature"] == feature
