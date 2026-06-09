"""
simulate_high_volume_traffic.py — Simulación de alto volumen con Locust (§3.1)

Ejecutar:
    cd backend/
    locust -f tests/simulation/simulate_high_volume_traffic.py \
           --host http://localhost:8000 \
           --users 500 --spawn-rate 50 \
           --headless --run-time 2m \
           --html tests/simulation/report.html

Umbral de aceptación: p95 < 500 ms bajo 500 usuarios concurrentes.

Variables de entorno opcionales:
    AXOLOTTO_BOOSTER_ITEM_ID   — item_id del booster activo en la BD (default: 1)
    AXOLOTTO_GASHAPON_COST     — ignorado por Locust, solo documentativo
    LOCUST_EXPECTED_FAIL_CODES — códigos HTTP tratados como "éxito esperado" (default: 400,402,404,409)
"""

import os
import uuid
from locust import HttpUser, TaskSet, between, task, events
from locust.exception import StopUser

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

BOOSTER_ITEM_ID: int = int(os.getenv("AXOLOTTO_BOOSTER_ITEM_ID", "1"))

# Códigos que el sistema devuelve por lógica de negocio (saldo insuficiente,
# ítem agotado, etc.) y que NO deben contarse como errores de infraestructura.
_EXPECTED_FAIL_CODES: set[int] = {
    int(c) for c in os.getenv("LOCUST_EXPECTED_FAIL_CODES", "400,402,404,409,422").split(",")
}


def _user_qp(user_id: str) -> dict:
    """Query params para autenticación en modo dev (sin PRIVY_APP_ID)."""
    return {"user_id": user_id}


# ---------------------------------------------------------------------------
# Tareas de solo lectura — alta frecuencia, sin estado
# ---------------------------------------------------------------------------

class ReadTasks(TaskSet):
    """Lecturas públicas: catálogo de tienda, jackpot, actividad reciente."""

    @task(5)
    def get_shop_items(self):
        with self.client.get("/api/v1/shop/items", catch_response=True) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"GET /shop/items → {r.status_code}")

    @task(3)
    def get_jackpot_status(self):
        with self.client.get("/api/v1/multiplayer/jackpot", catch_response=True) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"GET /multiplayer/jackpot → {r.status_code}")

    @task(2)
    def get_shop_activity(self):
        with self.client.get("/api/v1/shop/activity", catch_response=True) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"GET /shop/activity → {r.status_code}")

    @task(1)
    def get_capsule_daily_status(self):
        uid = getattr(self.user, "user_id", f"anon-{uuid.uuid4().hex[:8]}")
        with self.client.get(
            "/api/v1/shop/capsule/daily-status",
            params=_user_qp(uid),
            catch_response=True,
        ) as r:
            if r.status_code in (200, 401):
                r.success()
            else:
                r.failure(f"GET /shop/capsule/daily-status → {r.status_code}")


# ---------------------------------------------------------------------------
# Tareas de escritura — flujo de usuario autenticado
# ---------------------------------------------------------------------------

class WriteTasks(TaskSet):
    """Operaciones de escritura: compras, apertura de boosters, gashapón, lobby."""

    @task(4)
    def sync_user(self):
        uid = self.user.user_id
        with self.client.post(
            "/api/v1/auth/sync",
            params=_user_qp(uid),
            json={"privy_did": uid, "email": f"{uid}@locust.test"},
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"POST /auth/sync → {r.status_code}")

    @task(3)
    def buy_booster(self):
        uid = self.user.user_id
        with self.client.post(
            "/api/v1/shop/buy",
            params=_user_qp(uid),
            json={
                "user_id": uid,
                "item_id": BOOSTER_ITEM_ID,
                "payment_currency": "axogema",
            },
            catch_response=True,
        ) as r:
            if r.status_code == 200 or r.status_code in _EXPECTED_FAIL_CODES:
                r.success()
            else:
                r.failure(f"POST /shop/buy → {r.status_code}: {r.text[:120]}")

    @task(2)
    def open_booster(self):
        uid = self.user.user_id
        with self.client.post(
            "/api/v1/shop/booster/open",
            params=_user_qp(uid),
            json={"item_id": BOOSTER_ITEM_ID},
            catch_response=True,
        ) as r:
            if r.status_code == 200 or r.status_code in _EXPECTED_FAIL_CODES:
                r.success()
            else:
                r.failure(f"POST /shop/booster/open → {r.status_code}: {r.text[:120]}")

    @task(3)
    def spin_gashapon(self):
        uid = self.user.user_id
        with self.client.post(
            "/api/v1/shop/gashapon/roll",
            params=_user_qp(uid),
            json={"user_id": uid, "roll_type": "common"},
            catch_response=True,
        ) as r:
            if r.status_code == 200 or r.status_code in _EXPECTED_FAIL_CODES:
                r.success()
            else:
                r.failure(f"POST /shop/gashapon/roll → {r.status_code}: {r.text[:120]}")

    @task(1)
    def claim_daily_capsule(self):
        uid = self.user.user_id
        with self.client.post(
            "/api/v1/shop/capsule/daily-claim",
            params=_user_qp(uid),
            json={"user_id": uid},
            catch_response=True,
        ) as r:
            if r.status_code == 200 or r.status_code in _EXPECTED_FAIL_CODES:
                r.success()
            else:
                r.failure(f"POST /shop/capsule/daily-claim → {r.status_code}: {r.text[:120]}")

    @task(1)
    def get_unread_multiplayer_logs(self):
        uid = self.user.user_id
        with self.client.get(
            "/api/v1/multiplayer/unread-logs",
            params=_user_qp(uid),
            catch_response=True,
        ) as r:
            if r.status_code in (200, 404):
                r.success()
            else:
                r.failure(f"GET /multiplayer/unread-logs → {r.status_code}")

    @task(1)
    def get_lobby_status(self):
        with self.client.get("/api/v1/multiplayer/lobby", catch_response=True) as r:
            if r.status_code in (200, 404):
                r.success()
            else:
                r.failure(f"GET /multiplayer/lobby → {r.status_code}")


# ---------------------------------------------------------------------------
# Clases de usuario Locust
# ---------------------------------------------------------------------------

class AxolottoReadUser(HttpUser):
    """Simula visitantes / usuarios no autenticados — solo lecturas."""
    weight = 2
    wait_time = between(0.5, 3)
    tasks = [ReadTasks]

    def on_start(self):
        self.user_id = f"anon-{uuid.uuid4().hex[:10]}"


class AxolottoUser(HttpUser):
    """Simula usuarios registrados realizando el flujo completo del juego."""
    weight = 3
    wait_time = between(0.1, 2)
    tasks = {ReadTasks: 2, WriteTasks: 3}

    def on_start(self):
        self.user_id = f"locust-{uuid.uuid4().hex[:10]}"
        # Sincronizar usuario para que exista en BD
        resp = self.client.post(
            "/api/v1/auth/sync",
            params=_user_qp(self.user_id),
            json={"privy_did": self.user_id, "email": f"{self.user_id}@locust.test"},
        )
        if resp.status_code not in (200, 201):
            raise StopUser()


class AxolottoHeavyUser(HttpUser):
    """Simula whale / usuario VIP con rafagas de compras."""
    weight = 1
    wait_time = between(0.05, 0.5)
    tasks = {WriteTasks: 5, ReadTasks: 1}

    def on_start(self):
        self.user_id = f"whale-{uuid.uuid4().hex[:8]}"
        self.client.post(
            "/api/v1/auth/sync",
            params=_user_qp(self.user_id),
            json={"privy_did": self.user_id, "email": f"{self.user_id}@locust.test"},
        )


# ---------------------------------------------------------------------------
# Hook: resumen de aceptación al terminar la ejecución
# ---------------------------------------------------------------------------

@events.quitting.add_listener
def _check_sla(environment, **kwargs):
    """Imprime un resumen de SLA al finalizar y falla si p95 > 500 ms."""
    stats = environment.runner.stats.total if environment.runner else None
    if not stats:
        return

    p95_ms = stats.get_response_time_percentile(0.95)
    error_rate = stats.fail_ratio

    print("\n" + "=" * 60)
    print("📊  RESUMEN DE SIMULACIÓN AXOLOTTO")
    print("=" * 60)
    print(f"  Solicitudes totales : {stats.num_requests}")
    print(f"  Fallos totales      : {stats.num_failures}")
    print(f"  Tasa de error       : {error_rate:.2%}")
    print(f"  p50 latencia        : {stats.get_response_time_percentile(0.50):.0f} ms")
    print(f"  p95 latencia        : {p95_ms:.0f} ms")
    print(f"  p99 latencia        : {stats.get_response_time_percentile(0.99):.0f} ms")

    if p95_ms > 500:
        print(f"\n❌  SLA VIOLADO: p95={p95_ms:.0f}ms supera el umbral de 500ms")
        environment.process_exit_code = 1
    elif error_rate > 0.05:
        print(f"\n❌  SLA VIOLADO: tasa de error {error_rate:.2%} supera el 5%")
        environment.process_exit_code = 1
    else:
        print("\n✅  SLA CUMPLIDO")
    print("=" * 60)
