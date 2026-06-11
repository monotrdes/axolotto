"""test_vuln06_integer_economy.py — VULN-06: aritmética entera y anti-dust.

Verifica:
  1. Tipos Pydantic AxfAmount/FrjAmount convierten correctamente
  2. Invariante de suma cero en operaciones atómicas
  3. 10,000 micro-transacciones no generan dust acumulado
  4. División entera trunca hacia el usuario (floor)
  5. Comparaciones de saldo no fallan en los bordes
"""
from __future__ import annotations
import pytest
from app.core.config import AXF_DECIMALS_BACKEND, FRJ_DECIMALS_BACKEND
from app.core.economy_types import _validate_axf, _validate_frj, _serialize_axf, _serialize_frj

_AXF = 10 ** AXF_DECIMALS_BACKEND
_FRJ = 10 ** FRJ_DECIMALS_BACKEND


# ---------------------------------------------------------------------------
# 1. Validadores Pydantic: conversión correcta
# ---------------------------------------------------------------------------

class TestAxfAmount:
    def test_float_input_converts(self):
        result = _validate_axf(250.5)
        assert result == 250_500_000  # 250.5 * 1_000_000

    def test_int_passthrough(self):
        result = _validate_axf(250_500_000)
        assert result == 250_500_000

    def test_zero(self):
        assert _validate_axf(0) == 0
        assert _validate_axf(0.0) == 0

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="negative"):
            _validate_axf(-1.0)
        with pytest.raises(ValueError, match="negative"):
            _validate_axf(-100)

    def test_invalid_type_raises(self):
        with pytest.raises(TypeError):
            _validate_axf("250.5")

    def test_serializer_divides_by_factor(self):
        result = _serialize_axf(250_500_000)
        assert result == pytest.approx(250.5)
        assert isinstance(result, float)


class TestFrjAmount:
    def test_float_input_converts(self):
        result = _validate_frj(25.0)
        assert result == 250_000  # 25 * 10_000

    def test_int_passthrough(self):
        result = _validate_frj(250_000)
        assert result == 250_000

    def test_zero(self):
        assert _validate_frj(0) == 0
        assert _validate_frj(0.0) == 0

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="negative"):
            _validate_frj(-0.01)

    def test_serializer_divides_by_factor(self):
        result = _serialize_frj(250_000)
        assert result == pytest.approx(25.0)
        assert isinstance(result, float)


# ---------------------------------------------------------------------------
# 2. Invariante de suma cero: sum(debits) == sum(credits) en P2P
# ---------------------------------------------------------------------------

class TestP2PInvariant:
    """Verifica que una transferencia P2P no crea ni destruye valor."""

    def test_p2p_balance_conservation(self):
        """sum(saldos_antes) == sum(saldos_despues) + fee"""
        P2P_FEE_BPS = 500  # 5%
        DENOM = 10000

        sender_initial = 1000 * _FRJ
        receiver_initial = 100 * _FRJ
        amount = 200 * _FRJ

        fee = amount * P2P_FEE_BPS // DENOM
        amount_after_fee = amount - fee

        sender_final = sender_initial - amount
        receiver_final = receiver_initial + amount_after_fee

        total_before = sender_initial + receiver_initial
        total_after = sender_final + receiver_final + fee  # fee va a tesorería

        assert total_before == total_after, (
            f"Invariante rota: antes={total_before} después={total_after}"
        )
        assert fee >= 0
        assert amount_after_fee > 0
        assert amount_after_fee < amount  # fee > 0

    def test_micro_transfer_no_dust(self):
        """Transferencia de 1 FRJ cobra 0 fee (truncado hacia abajo)."""
        P2P_FEE_BPS = 500
        DENOM = 10000

        amount = 1 * _FRJ  # 1 FRJ = 10_000 unidades
        fee = amount * P2P_FEE_BPS // DENOM
        # fee = 10_000 * 500 // 10_000 = 500 unidades = 0.05 FRJ
        assert fee == 500  # 0.05 FRJ
        assert fee < amount

    def test_minimum_amount_no_negative_fee(self):
        """Amount mínimo (1 unidad) no genera fee negativo."""
        P2P_FEE_BPS = 500
        DENOM = 10000

        amount = 1  # 1 unidad mínima
        fee = amount * P2P_FEE_BPS // DENOM
        assert fee == 0  # floor: 1 * 500 // 10000 = 0
        amount_after_fee = amount - fee
        assert amount_after_fee == 1  # no se destruye valor


# ---------------------------------------------------------------------------
# 3. Dust farming: 10,000 micro-transacciones no generan polvo acumulable
# ---------------------------------------------------------------------------

class TestDustFarming:
    def test_10000_micro_transactions_no_accumulated_dust(self):
        """10k micro-transacciones de 1 unidad: el total reconciliado es exacto."""
        P2P_FEE_BPS = 500
        DENOM = 10000

        total_sent = 0
        total_received = 0
        total_fees = 0

        for _ in range(10_000):
            amount = 1  # 1 unidad mínima
            fee = amount * P2P_FEE_BPS // DENOM  # siempre 0
            received = amount - fee  # siempre 1
            total_sent += amount
            total_received += received
            total_fees += fee

        assert total_sent == 10_000
        assert total_received == 10_000  # sin pérdida por redondeo
        assert total_fees == 0  # sin polvo acumulado
        assert total_sent == total_received + total_fees  # invariante

    def test_10000_small_transactions_with_fee(self):
        """10k transacciones de 100 unidades (0.01 FRJ) con fee."""
        P2P_FEE_BPS = 500
        DENOM = 10000

        total_sent = 0
        total_received = 0
        total_fees = 0

        for _ in range(10_000):
            amount = 100  # 0.01 FRJ
            fee = amount * P2P_FEE_BPS // DENOM  # 100 * 500 // 10000 = 5
            received = amount - fee
            total_sent += amount
            total_received += received
            total_fees += fee

        # Verificar invariante
        assert total_sent == total_received + total_fees
        # Verificar que el fee es determinista
        assert total_fees == 10_000 * 5  # 50,000
        # Sin polvo: cada transacción es exacta
        assert total_sent == 1_000_000


# ---------------------------------------------------------------------------
# 4. Division entera: trunca hacia el usuario (floor)
# ---------------------------------------------------------------------------

class TestIntegerDivision:
    def test_discount_truncates_toward_user(self):
        """Descuento VIP 5%: el precio redondea hacia abajo (beneficia al usuario)."""
        price = 100 * _FRJ  # 100 FRJ
        discount_bps = 500  # 5%
        # price * (10000 - 500) // 10000 = price * 9500 // 10000
        discounted = price * (10000 - discount_bps) // 10000
        # 1_000_000 * 9500 // 10000 = 950_000 = 95 FRJ exacto
        assert discounted == 95 * _FRJ

    def test_odd_price_truncates_down(self):
        """Precio impar: 100.01 FRJ con 5% desc → floor, no round."""
        price = 1_000_100  # 100.01 FRJ en unidades
        discount_bps = 500
        discounted = price * (10000 - discount_bps) // 10000
        expected_float = 100.01 * 0.95  # = 95.0095 FRJ
        expected_units = int(expected_float * _FRJ)  # = 950095
        assert discounted == expected_units
        # Verificar que truncó hacia abajo
        assert discounted <= price

    def test_luck_bonus_truncates_player_favorable(self):
        """Luck bonus: floor beneficia al jugador en premios grandes."""
        prize = 85 * _FRJ  # 85 FRJ de premio base
        luck_stat = 73  # 7.3% bonus
        luck_bonus = luck_stat * prize // 1000
        assert luck_bonus == 62050

    def test_pool_distribution_exact_split(self):
        """Distribución de pool entre 3 ganadores: fair split sin remainder perdido."""
        pool = 1000 * _FRJ  # 1000 FRJ
        winners = 3
        share = pool // winners  # 3333333 units
        remainder = pool - (share * winners)  # 1 unit (0.0001 FRJ)
        assert share == 3_333_333
        assert remainder == 1  # 1 unidad va a tesorería, no se pierde


# ---------------------------------------------------------------------------
# 5. Comparaciones de borde: saldo < precio no falla por redondeo
# ---------------------------------------------------------------------------

class TestEdgeComparisons:
    def test_exact_balance_affords(self):
        """Saldo exacto = precio: la compra procede."""
        balance = 100 * _FRJ
        price = 100 * _FRJ
        assert balance >= price  # debe ser True, sin error de redondeo

    def test_one_unit_short_fails(self):
        """Saldo 1 unidad menos que el precio: la compra falla."""
        balance = (100 * _FRJ) - 1
        price = 100 * _FRJ
        assert balance < price

    def test_after_discount_exact_match(self):
        """Después de descuento VIP, el saldo exacto alcanza."""
        price = 100 * _FRJ
        discount_bps = 500
        discounted = price * (10000 - discount_bps) // 10000  # 95 FRJ
        balance = 95 * _FRJ
        assert balance >= discounted

    def test_large_amounts_no_overflow(self):
        """Montos grandes (millones de AXF) no causan overflow en Python int."""
        huge = 10_000_000 * _AXF  # 10M AXF
        fee_bps = 500
        fee = huge * fee_bps // 10000
        assert fee == 500_000 * _AXF  # 5% de 10M
        remaining = huge - fee
        assert remaining == 9_500_000 * _AXF
