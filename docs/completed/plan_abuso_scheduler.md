# Plan de Implementación: Mitigación del Abuso del Scheduler de Multiplayer

Este plan detalla los cambios requeridos en el backend para mitigar la explotación del lobby multijugador por parte de cuentas múltiples asociadas a la misma dirección de billetera Web3 (wallet_address), limitando la cantidad de tableros/registros en salas en espera y verificando la aleatoriedad segura del sorteo.

---

## 1. Cambios en Backend (Python / SQLModel)

### 1.1. Restricción a Nivel de Wallet en `multiplayer.py` (`POST /register`)
- Al registrar un Axolotito en `register_axolotito`:
  - Obtener el objeto `User` correspondiente al `verified_user_id`.
  - Si el usuario tiene una dirección de billetera configurada (`user.wallet_address` no nula y no vacía), verificar que no existan registros activos en estado `"waiting"` de ese mismo tipo de sala (`room_type`) que pertenezcan a algún usuario con el mismo `wallet_address`.
  - Si ya existe un registro asociado a ese `wallet_address`, lanzar un error `HTTPException(400)` para impedir el registro de cuentas duplicadas/sybil que compartan la misma billetera.

### 1.2. Límite de 5 Tablas por Sala por Usuario/Billetera
- Adicionalmente, al inscribirse:
  - Verificar que el número total de tablas que tiene el usuario (y cualquier otra cuenta vinculada a la misma `wallet_address`) en la sala de espera elegida no supere las 5 tablas en total.
  - Si supera el límite de 5 tablas, denegar el registro con `HTTPException(400)`.

### 1.3. Modificación de `get_or_create_waiting_room` en `multiplayer_service.py`
- Actualizar la firma de `get_or_create_waiting_room`:
  ```python
  def get_or_create_waiting_room(
      session: Session, 
      room_type: str, 
      boards_count: int, 
      user_id: Optional[str] = None
  ) -> GameRoom:
  ```
- Lógica de asignación de salas en espera:
  - Si se proporciona `user_id`, consultar su `wallet_address` desde el modelo `User`.
  - Al iterar sobre las salas `"waiting"` disponibles:
    - Omitir cualquier sala donde el `user_id` o el `wallet_address` (si no es nulo) ya tengan un registro activo en esa sala.
    - Esto evita que, mediante auto-re-registro (al terminar una partida anterior), múltiples Axolotitos que comparten el mismo usuario o billetera terminen en la misma sala de espera.
    - Si todas las salas existentes tienen conflicto o están llenas, crear una nueva sala de espera y retornarla.

### 1.4. Actualización de llamadas a `get_or_create_waiting_room`
- Modificar los siguientes puntos de llamada para pasar el parámetro `user_id`:
  1. En `multiplayer.py` (`register_axolotito`):
     ```python
     room = get_or_create_waiting_room(session, req.room_type, len(req.boards), user_id=verified_user_id)
     ```
  2. En `multiplayer_service.py` (`simulate_multiplayer_match` en el paso de auto-reinscripción):
     ```python
     new_room = get_or_create_waiting_room(session, room.room_type, len(b_ids), user_id=axo_obj.user_id)
     ```
  3. En `simulate_universe.py` (script de simulación):
     ```python
     room = get_or_create_waiting_room(session, "rookie", len(board_list), user_id=user_id)
     ```

### 1.5. Auditoría y Confirmación de la Aleatoriedad Criptográfica
- Verificar que el scheduler utiliza `random.SystemRandom().shuffle(deck)` para mezclar la baraja de cartas del sorteo.
- Documentar que `random.SystemRandom` utiliza el CSPRNG del sistema operativo (`/dev/urandom` en Linux), haciendo que el orden de las cartas sea completamente impredecible y no manipulable externamente a través de semillas del reloj o re-ejecución local.

---

## 2. Plan de Verificación y Pruebas

### 2.1. Pruebas Automatizadas
- Crear un nuevo suite de pruebas unitarias en `backend/tests/unit/test_multiplayer_limits.py` que valide:
  1. **Límite por user_id**: Registrar un Axolotito de un usuario e intentar registrar otro del mismo usuario en la misma sala/tipo de sala, arrojando error 400.
  2. **Límite por wallet_address**: Registrar un Axolotito con el usuario A (billetera `0x123...`). Intentar registrar un Axolotito con el usuario B (misma billetera `0x123...`) y verificar que es rechazado con error 400.
  3. **Límite de 5 tablas**: Comprobar que no se puedan superar las 5 tablas por billetera en la misma sala, incluso si se intenta simular un bypass manual de los otros filtros.
  4. **Auto-re-registro no duplicado**: Comprobar que si el usuario A y el usuario B (con la misma billetera) terminan una partida, la auto-reinscripción los coloca en salas separadas en lugar de la misma.
  5. **Seguridad de la aleatoriedad**: Verificar que la mezcla del mazo produce secuencias diferentes de forma consistente y que está utilizando `SystemRandom`.

### 2.2. Pruebas Manuales
- Correr `pytest` sobre el nuevo suite de pruebas unitarias para confirmar que las restricciones se aplican correctamente en la base de datos de pruebas.
- Ejecutar el script `simulate_universe.py` para asegurar que las modificaciones no rompen la orquestación general ni el flujo de juego automático.
