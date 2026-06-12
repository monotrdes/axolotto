# Plan: Refactorización de Arquitectura y Limpieza de Código Monolítico

> Generado por **antigravity** · tarea `task-1781235842-97` · 2026-06-11
> Basado en el punto 3 de la auditoría general de arquitectura (`task-1781194038-91`).

Este documento detalla el análisis de los principales "code smells" y archivos monolíticos del repositorio, definiendo una hoja de ruta técnica para separar responsabilidades en el backend (FastAPI) y frontend (Next.js/React), optimizar el rendimiento de renderizado y purgar código muerto.

---

## 1. Análisis de Archivos Críticos y Propuesta de Refactorización (Backend)

Actualmente, el backend de Axolotto sufre de concentración de lógica en archivos de servicios y controladores (endpoints), lo cual incrementa el riesgo de efectos colaterales al modificar reglas del juego y transacciones.

### A. Desarticular `multiplayer_service.py` (~1,415 líneas)
*   **Ubicación**: [multiplayer_service.py](file:///D:/Axolotto_2026/axolotto/backend/app/services/multiplayer_service.py)
*   **Problema**: Concentra la orquestación del WebSocket, el lobby de espera, la lógica de juego de Lotería, la inteligencia artificial de los bots (`simulate_multiplayer_match` de >600 líneas) y el reparto de la bolsa/jackpots en una única clase.
*   **Plan de Cambios (Estructura de Carpeta `app/services/multiplayer/`)**:
    1.  `state_machine.py`: Control de los estados del juego multijugador (`waiting`, `playing`, `card_called`, `rewards`). Implementa la transición asíncrona segura.
    2.  `bot_engine.py`: Simulación estocástica y probabilística de marcado de cartas por bots NPC, control de sus tiempos de reacción y selección del pool de tableros.
    3.  `reward_calculator.py`: Cálculo preciso de distribución de la bolsa de FRJ entre múltiples ganadores (reparto proporcional en caso de empates) y lógica de retenciones del Jackpot.
    4.  `multiplayer_service.py`: Reducido a un orquestador ligero que importa y coordina las llamadas a los submódulos.

### B. Modularizar `board_service.py` (~1,660 líneas)
*   **Ubicación**: [board_service.py](file:///D:/Axolotto_2026/axolotto/backend/app/services/board_service.py)
*   **Problema**: Este archivo gestiona la lógica matemática de tableros, el desarmado/quemado de cartas, el alquiler y venta P2P de tableros en el mercado, y los cálculos de staking pasivo diario.
*   **Plan de Cambios (Estructura de Carpeta `app/services/board/`)**:
    1.  `board_generator.py`: Generador aleatorio o manual de matrices $4\times4$ y validación de unicidad de cartas (evitar que una misma carta se equipe dos veces).
    2.  `deconstruct_service.py`: Gestión del desarme (Card Melter), quema de cartas, cobro de retenciones y reembolsos de componentes.
    3.  `staking_service.py`: Fórmulas del Coeficiente de Suerte Real (CSR), el multiplicador por nivel del tablero y la acumulación diaria pasiva de GAL.
    4.  `board_service.py`: Orquestador principal de operaciones de base de datos de tableros (listado, edición, borrado, alquiler).

### C. Regla de Oro para Controladores Declarativos
*   **Archivos Afectados**: 
    - [multiplayer.py](file:///D:/Axolotto_2026/axolotto/backend/app/api/v1/endpoints/multiplayer.py) (~1,080 líneas)
    - [cave_expansion.py](file:///D:/Axolotto_2026/axolotto/backend/app/api/v1/endpoints/cave_expansion.py) (~850 líneas)
*   **Problema**: Contienen lógica de negocio pesada. Por ejemplo, `register_axolotito` hace queries para validar el estado del Axolotito, verifica límites de energía, comprueba la validez del arriendo de las tablas y descuenta el saldo en escrow con bloqueos pesimistas directamente en la base de datos.
*   **Plan de Cambios**:
    1.  Toda mutación de base de datos o lógica transaccional debe delegarse al Service.
    2.  El endpoint solo debe:
        - Validar tipos y body vía Pydantic.
        - Autenticar mediante Privy JWT (`verified_user_id`).
        - Invocar al service (ej. `multiplayer_service.register_player(...)` pasando la sesión).
        - Capturar excepciones específicas de negocio (`HTTPException`) y retornar la respuesta formateada.

---

## 2. Análisis de Componentes Críticos y Modularización (Frontend)

El frontend requiere optimización en la granularidad de sus componentes para prevenir re-renders catastróficos que deterioran la experiencia móvil.

### A. Trocear el Gigante `Inventory.tsx` (~984 líneas)
*   **Ubicación**: [Inventory.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/Inventory.tsx) y su hook [useInventory.ts](file:///D:/Axolotto_2026/axolotto/frontend/hooks/useInventory.ts) (~550 líneas)
*   **Problema**: El componente renderiza pestañas de Axolotitos, boosters, cartas y consumibles en un único árbol. Un cambio en los filtros de rareza de las cartas causa el re-render total de la lista de Axolotitos o boosters.
*   **Plan de Cambios**:
    1.  Crear `frontend/components/inventory/InventoryTabs.tsx` para gestionar la cabecera e intercambiar componentes según la pestaña activa.
    2.  Crear subcomponentes aislados en `/inventory/`:
        - `AxolotitosTab.tsx`: Gestión y filtrado de Axolotitos.
        - `BoostersTab.tsx`: Animación de unboxing y listado de sobres.
        - `CardsTab.tsx`: Cuadrícula de cartas y fusión (Card Melter).
        - `ConsumablesTab.tsx`: Aplicación de comida/pociones.
    3.  Extraer y simplificar el estado del hook a un Zustand Store (`useInventoryState.ts`) o dividirlo en slices para reactividad selectiva.

### B. Aislamiento Físico y Render en `Santuario.tsx` / `NidoScene.tsx`
*   **Ubicación**: [Santuario.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/Santuario.tsx) (~805 líneas) y [NidoScene.tsx](file:///D:/Axolotto_2026/axolotto/frontend/components/santuario/NidoScene.tsx) (~407 líneas)
*   **Problema**: La piscina 2.5D genera animaciones dinámicas `@keyframes axo-swim-${axo.id}` en tiempo de render, inyectando un bloque `<style>` de CSS al DOM que se actualiza constantemente.
*   **Plan de Cambios**:
    1.  Extraer el cálculo de trayectorias, derivaciones de profundidad (`depth`) y movimientos estocásticos a un hook: `frontend/hooks/useAxoSwimming.ts`.
    2.  Crear un componente autocontenido `AxoSprite.tsx` para representar el Axolotito. Este componente cargará su propio CSS estático o dinámico aislado y encapsulará sus transformaciones de coordenadas, evitando mutar el layout del contenedor padre `NidoScene`.

---

## 3. Revisión de Código Muerto y Depuración Inmediata

Se realizó una inspección inicial sobre archivos con posible estado de "código muerto":

1.  **Backers 2021 (`legacy.py` / `LegacyBacker` model)**:
    - *Estado*: **Activo**. El frontend en `santuarioService.ts` aún consume `/api/v1/legacy/status` y `/api/v1/legacy/claim` para dar soporte a los Webitos Fundadores de los primeros backers. Se conserva por compatibilidad.
2.  **Registro de Whitelist (`whitelist.py`)**:
    - *Estado*: **Parcialmente Muerto / Legacy**. No existen componentes en el frontend actual que invoquen directamente al endpoint `/api/v1/whitelist/register`. Sin embargo, `promo_service.py` utiliza el modelo `WhitelistEntry` y la tabla en base de datos para auto-registrar usuarios que canjean códigos promocionales especiales.
    - *Plan de acción*: Se mantendrá el modelo en base de datos, pero el endpoint `whitelist.py` puede ser marcado como deprecado y removido de `main.py` si se desea total limpieza de rutas públicas inactivas.
3.  **webito_slots.py**:
    - *Estado*: **Removido**. Se confirmó que este controlador antiguo fue completamente eliminado y migrado al nuevo sistema flexible de expansión del Cenote (`cave_expansion.py`).

---

## 4. Estrategia de Ejecución y Testing

Para garantizar una refactorización segura y libre de regresiones:
1.  **Firma y Contratos de Métodos**: No alterar la firma de retorno de las llamadas de los endpoints para no romper el contrato con el Frontend.
2.  **Pruebas Unitarias de Regresión**: Correr `pytest` en el backend antes y después del split en cada submódulo para asegurar la coherencia de la máquina de estados y las staking claims.
3.  **Validación del Flujo de Inventario**: Verificar a nivel E2E que la separación de pestañas en React mantiene el binding de Zustand y la actualización correcta del saldo en el header.
