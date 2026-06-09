import httpx
import sys
import json

# URL base por defecto del backend en local (puerto expuesto en host es 8001)
BASE_URL = "http://localhost:8001"

# Colección de payloads corruptos genéricos para POST/PATCH/PUT
NOISE_PAYLOADS = [
    # 1. JSON completamente malformado (enviado como raw string, no parseable)
    ("malformed_json", '{"id": 1, "value": ', "text/plain"),
    ("empty_array", "[]", "application/json"),
    
    # 2. Datos vacíos o nulos en formato JSON válido
    ("empty_object", {}, "application/json"),
    ("nulls_everywhere", {"id": None, "user_id": None, "room_type": None, "boards": None, "amount": None}, "application/json"),
    
    # 3. Tipos de datos cruzados e inválidos
    ("wrong_types", {
        "id": "este-es-un-string-donde-va-un-int",
        "user_id": 12345, # número donde va un string
        "boards": "no-es-una-lista", # string donde va una lista
        "amount": ["lista", "en", "lugar", "de", "float"],
        "loss_limit_pct": "treinta_por_ciento",
        "profit_limit_pct": "cincuenta_por_ciento",
        "axolotito_id": "noventa_y_nueve"
    }, "application/json"),
    
    # 4. Números fuera de límites y valores extremos
    ("overflow_numbers", {
        "id": 9999999999999999999999999999999999,
        "amount": -500.0,  # negativo donde debería ser positivo
        "budget_gal": -100.0,
        "loss_limit_pct": 1000.0,  # mayor al 100%
        "profit_limit_pct": -10.0,
        "axolotito_id": -9
    }, "application/json"),

    # 5. Inyección SQL básica (intento de evasión)
    ("sql_injection", {
        "user_id": "' OR '1'='1' --",
        "room_type": "'; DROP TABLE roomregistration; --",
        "nickname": "admin' --"
    }, "application/json"),

    # 6. Inyección de script (XSS)
    ("xss_payload", {
        "nickname": "<script>alert('pwned')</script>",
        "email": 'javascript:alert(1)',
        "avatar_url": '"><img src=x onerror=alert(1)>'
    }, "application/json")
]

# Cabeceras de Autorización corruptas para probar la resiliencia del middleware/auth
AUTH_NOISE_VARIANTS = [
    {}, # Sin cabecera
    {"Authorization": "NoiseToken12345"}, # Sin prefijo Bearer
    {"Authorization": "Bearer malformed.jwt.token"}, # JWT malformado
    {"Authorization": "Bearer " + "A"*5000}, # Token extremadamente largo (intento de Buffer Overflow)
]

# Definición de todos los endpoints del backend
ENDPOINTS = [
    # --- BANK ---
    ("/api/v1/bank/wallet", "GET", False),
    ("/api/v1/bank/deposit", "POST", True),
    
    # --- AUTH / USER ---
    ("/api/v1/auth/register", "POST", True),
    ("/api/v1/auth/profile", "GET", False),
    ("/api/v1/auth/profile", "PATCH", True),
    ("/api/v1/auth/inventory/did:privy:test_user", "GET", False),
    ("/api/v1/auth/vip", "GET", False),
    ("/api/v1/auth/vip/claim", "POST", True),
    ("/api/v1/auth/vip/auto-renew", "POST", True),
    
    # --- STORE / SHOP ---
    ("/api/v1/shop/items", "GET", False),
    ("/api/v1/shop/buy", "POST", True),
    ("/api/v1/shop/booster/open", "POST", True),
    ("/api/v1/shop/capsule/free", "POST", True),
    ("/api/v1/shop/capsule/roll", "POST", True),
    
    # --- INCUBATOR ---
    ("/api/v1/incubation/nest/buy", "POST", True),
    ("/api/v1/incubation/nest/assign", "POST", True),
    ("/api/v1/incubation/egg/hatch", "POST", True),
    ("/api/v1/incubation/egg/care", "POST", True),
    
    # --- METADATA ---
    ("/api/v1/metadata/axolotito/9999", "GET", False),
    ("/api/v1/metadata/board/9999", "GET", False),
    
    # --- LEGACY ---
    ("/api/v1/legacy/verify", "POST", True),
    ("/api/v1/legacy/claim", "POST", True),
    
    # --- PLAY BOARDS ---
    ("/api/v1/board/mint", "POST", True),
    ("/api/v1/board/list", "POST", True),
    ("/api/v1/board/buy", "POST", True),
    ("/api/v1/board/rent/list", "POST", True),
    ("/api/v1/board/rent/rent", "POST", True),
    ("/api/v1/board/rent/return", "POST", True),
    ("/api/v1/board/staking/stake", "POST", True),
    ("/api/v1/board/staking/unstake", "POST", True),
    ("/api/v1/board/staking/rewards", "GET", False),
    ("/api/v1/board/staking/claim", "POST", True),
    
    # --- SINGLEPLAYER GAME ---
    ("/api/v1/game/singleplayer/start", "POST", True),
    ("/api/v1/game/singleplayer/drawn", "POST", True),
    ("/api/v1/game/singleplayer/finish", "POST", True),
    
    # --- RANKINGS ---
    ("/api/v1/ranking/xp", "GET", False),
    ("/api/v1/ranking/games", "GET", False),
    
    # --- MULTIPLAYER ---
    ("/api/v1/multiplayer/register", "POST", True),
    ("/api/v1/multiplayer/recall", "POST", True),
    ("/api/v1/multiplayer/settle", "POST", True),
    ("/api/v1/multiplayer/unread-logs", "GET", False),
    ("/api/v1/multiplayer/lobby", "GET", False),
    ("/api/v1/multiplayer/jackpot", "GET", False),
    
    # --- CHECKOUT ---
    ("/api/v1/bank/checkout/crypto/intent", "POST", True),
    ("/api/v1/bank/checkout/crypto/webhook", "POST", True)
]

def run_fuzzing():
    print(f"🔮 [Noise Generator] Iniciando pruebas de robustez contra {BASE_URL}...")
    
    client = httpx.Client(timeout=5.0)
    
    total_tests = 0
    failures = 0
    warnings = []
    
    # Reportes detallados por endpoint
    report = {}

    for path, method, expects_body in ENDPOINTS:
        url = f"{BASE_URL}{path}"
        report[path] = {"tested": 0, "crashes": 0, "details": []}
        
        # 1. Probar cabeceras de autorización corruptas
        for auth_headers in AUTH_NOISE_VARIANTS:
            total_tests += 1
            report[path]["tested"] += 1
            try:
                if method == "GET":
                    resp = client.get(url, headers=auth_headers)
                else:
                    # POST vacío con auth corrupto
                    resp = client.post(url, headers=auth_headers, json={})
                    
                status = resp.status_code
                if status == 500:
                    failures += 1
                    report[path]["crashes"] += 1
                    report[path]["details"].append(f"Auth corrupto ({auth_headers}) devolvió 500 Internal Error!")
                elif status >= 400:
                    # Es el comportamiento esperado ante token corrupto
                    pass
                else:
                    # Retornó 2xx o 3xx con auth corrupto. Podría ser un warning de autorización faltante.
                    # Excluimos metadatos públicos, rankings, lobby y jackpot que son abiertos
                    public_paths = ["/metadata", "/ranking", "/lobby", "/jackpot"]
                    if not any(p in path for p in public_paths):
                        warnings.append(f"⚠️ {method} {path} no bloqueó cabecera corrupta/vacía ({auth_headers}). Código: {status}")
            except Exception as e:
                # Excepciones de red
                failures += 1
                report[path]["crashes"] += 1
                report[path]["details"].append(f"Error de red/conector con auth corrupto: {e}")

        # 2. Si el endpoint espera cuerpo (POST/PATCH), inyectar los payloads corruptos
        if expects_body:
            for payload_name, payload, content_type in NOISE_PAYLOADS:
                total_tests += 1
                report[path]["tested"] += 1
                
                # Probar cabecera de autenticación válida ficticia para saltar el middleware en endpoints protegidos
                headers = {"Authorization": "Bearer fake_test_token"}
                
                try:
                    if content_type == "application/json":
                        resp = client.request(method, url, json=payload, headers=headers)
                    else:
                        # Raw text (para malformed JSON)
                        resp = client.request(
                            method, 
                            url, 
                            content=payload, 
                            headers={**headers, "Content-Type": content_type}
                        )
                        
                    status = resp.status_code
                    if status == 500:
                        failures += 1
                        report[path]["crashes"] += 1
                        report[path]["details"].append(f"Payload '{payload_name}' causó crash 500!")
                    elif status >= 400:
                        # Correcto: El servidor rechazó el payload corrupto de forma limpia
                        pass
                    else:
                        # Aceptó un payload corrupto sin rechazarlo
                        warnings.append(f"⚠️ {method} {path} aceptó payload corrupto '{payload_name}' (Status: {status})")
                except Exception as e:
                    failures += 1
                    report[path]["crashes"] += 1
                    report[path]["details"].append(f"Error de conector con payload '{payload_name}': {e}")
                    
    # --- RESUMEN DE RESULTADOS ---
    print("\n========================================================")
    print("         REPORTE DE ESTABILIDAD Y FUZZING               ")
    print("========================================================")
    print(f"Total de Pruebas Ejecutadas: {total_tests}")
    print(f"Crashes del Servidor (500 Internal Error): {failures}")
    print(f"Advertencias (Validación Laxa o Acceso Inseguro): {len(warnings)}")
    print("========================================================\n")
    
    if warnings:
        print("🔍 ADVERTENCIAS:")
        for w in warnings[:15]:
            print(f"  {w}")
        if len(warnings) > 15:
            print(f"  ... y {len(warnings) - 15} advertencias más.")
            
    print("\n🔍 DETALLE DE CRASHES POR ENDPOINT:")
    has_crashes = False
    for path, data in report.items():
        if data["crashes"] > 0:
            has_crashes = True
            print(f"\n💥 Endpoint: {path} ({data['crashes']} crashes de {data['tested']} pruebas)")
            for d in data["details"]:
                print(f"   - {d}")
                
    if not has_crashes:
        print("  ✅ Ningún endpoint sufrió caídas de tipo 500 (Internal Server Error).")
        print("  ¡El servidor de Axolotto es robusto e irrompible ante payloads corruptos!")

    # Guardar reporte en archivo de texto
    with open("simulation_report.txt", "w") as f:
        f.write("=== REPORTE DE RESILIENCIA Y RUIDO ===\n")
        f.write(f"Total Tests: {total_tests}\n")
        f.write(f"Crashes (500): {failures}\n")
        f.write(f"Warnings: {len(warnings)}\n\n")
        if warnings:
            f.write("=== WARNINGS ===\n")
            for w in warnings:
                f.write(f"{w}\n")
            f.write("\n")
        f.write("=== CRASHES ===\n")
        for path, data in report.items():
            if data["crashes"] > 0:
                f.write(f"{path} ({data['crashes']} crashes):\n")
                for d in data["details"]:
                    f.write(f"  - {d}\n")
                    
    print("\n📝 Reporte detallado escrito en 'simulation_report.txt'.")
    if failures > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    run_fuzzing()
