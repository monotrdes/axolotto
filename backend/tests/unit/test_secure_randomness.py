import random
from app.api.v1.endpoints.shop import _rng as shop_endpoint_rng
from app.services.shop_service import _rng as shop_service_rng
from app.api.v1.endpoints.incubation import _rng as incubation_endpoint_rng
from app.api.v1.endpoints.board import _rng as board_endpoint_rng
from app.services.game_logic import _rng as game_logic_rng
from app.services.multiplayer_service import _rng as multiplayer_service_rng

def test_secure_randomness_generators():
    """
    Verifica que todos los generadores de números aleatorios en los endpoints y servicios críticos
    sean instancias de random.SystemRandom (CSPRNG respaldado por el OS/dev/urandom),
    lo que previene que el cliente pueda predecir o manipular probabilidades.
    """
    assert isinstance(shop_endpoint_rng, random.SystemRandom), "shop endpoint debe usar SystemRandom"
    assert isinstance(shop_service_rng, random.SystemRandom), "shop_service debe usar SystemRandom"
    assert isinstance(incubation_endpoint_rng, random.SystemRandom), "incubation endpoint debe usar SystemRandom"
    assert isinstance(board_endpoint_rng, random.SystemRandom), "board endpoint debe usar SystemRandom"
    assert isinstance(game_logic_rng, random.SystemRandom), "game_logic debe usar SystemRandom"
    assert isinstance(multiplayer_service_rng, random.SystemRandom), "multiplayer_service debe usar SystemRandom"
