# 🦎 REVISIÓN DE DOCUMENTOS Y ESTADO DEL SISTEMA

Este reporte analiza el estado de implementación de cada documento que se encontraba en el directorio `docs/` en comparación con el codebase actual de **Axolotto**, clasifica los documentos como **Completados** (ya archivados) o **Activos/Pendientes**, y detalla las tareas y fases que restan para finalizar el proyecto.

---

## 📂 Clasificación de Documentos de Planificación

### 1. Documentos Completados y Archivados
Los siguientes 12 documentos han sido trasladados y archivados en `docs/completed/` debido a que sus diseños, análisis de seguridad y planes de tareas han sido plenamente implementados o resueltos en el codebase:

| Documento | Estado de Implementación en Código | Acción Realizada |
| :--- | :--- | :--- |
| [AUDITORIA_LEGAL_FINANCIERA.md](file:///D:/Axolotto_2026/axolotto/docs/completed/AUDITORIA_LEGAL_FINANCIERA.md) | **Implementado.** Analizó el spread de recompra del 70% y el riesgo regulatorio. Sirvió de base para pivotar al modelo de moneda blanda F2P. | Archivado |
| [PLAN_PIVOTE_ECO_LEGAL.md](file:///D:/Axolotto_2026/axolotto/docs/completed/PLAN_PIVOTE_ECO_LEGAL.md) | **Implementado.** Estableció el loop F2P (moneda blanda `FRJ` para jugar lotería y comprar consumibles; `AXF` premium para mercado P2P y retiros/DevEx). | Archivado |
| [MATRIZ_TRANSACCIONES_Y_REPARTOS.md](file:///D:/Axolotto_2026/axolotto/docs/completed/MATRIZ_TRANSACCIONES_Y_REPARTOS.md) | **Implementado.** Aplica las distribuciones del 80% a reserva y 20% a tesorería en compras de AXF, y desactiva el uso directo de AXF en lobbies. | Archivado |
| [DISENIO_JUEGO_DE_DESTREZA.md](file:///D:/Axolotto_2026/axolotto/docs/completed/DISENIO_JUEGO_DE_DESTREZA.md) | **Supersedido.** Evaluó opciones de destreza ( lobbies simétricos / speed dabbing). Decidido en favor del Pivot Eco-Legal. | Archivado |
| [SECURITY_AUDIT_2026_06_04.md](file:///D:/Axolotto_2026/axolotto/docs/completed/SECURITY_AUDIT_2026_06_04.md) | **Resuelto.** Segunda auditoría. Los hallazgos críticos/altos (`NEW-1` a `NEW-7`) como condiciones de carrera en claims, double-hatch y fragmentos F2P ilimitados fueron corregidos con locks pesimistas (`with_for_update()`) y caps diarios. | Archivado |
| [cpu_betting_analysis.md](file:///D:/Axolotto_2026/axolotto/docs/completed/cpu_betting_analysis.md) | **Implementado.** Alineó las tarifas de Rookie (100 FRJ) / Champion (500 FRJ) y habilitó el selector de stakes (x1, x2, x5, x10) en `BoardSelectScreen.tsx`. | Archivado |
| [plan_modular_code_guard_refactor.md](file:///D:/Axolotto_2026/axolotto/docs/completed/plan_modular_code_guard_refactor.md) | **Implementado.** Redujo el acoplamiento y tamaño de los componentes monolíticos (`Santuario.tsx`, `Inventory.tsx`, `Store.tsx`, `VipModal.tsx`) creando directorios modulares y hooks dedicados. | Archivado |
| [agent-terminal-orchestra.md](file:///D:/Axolotto_2026/axolotto/docs/completed/agent-terminal-orchestra.md) & [_v1-original.md](file:///D:/Axolotto_2026/axolotto/docs/completed/agent-terminal-orchestra_v1-original.md) | **Implementado.** Define el workflow local-first con Git. El orquestador de terminales y el Taskboard local en puerto `8181` están activos. | Archivado |
| [task_board_workflow_plan.md](file:///D:/Axolotto_2026/axolotto/docs/completed/task_board_workflow_plan.md) | **Implementado.** Arquitectura Kanban de 6 columnas operando con base de datos SQLite y AIRouter multi-provider. | Archivado |
| [plan_task-1780622810-2...md](file:///D:/Axolotto_2026/axolotto/docs/completed/plan_task-1780622810-2_ampliar-sistema-de-etiquetas-categoras-con-nuevos-.md) | **Implementado.** Expande las categorías y badges de tareas en el modal de ideas y prompts del AI Router. | Archivado |
| [plan_task-1780620307-0...md](file:///D:/Axolotto_2026/axolotto/docs/completed/plan_task-1780620307-0_geg-tarea-sin-especificar-requiere-clarificacin.md) | **Cancelado.** Planificación para una tarea de prueba vacía ("geg"), considerada completada como descarte/historial. | Archivado |

### 2. Documentos Activos / Pendientes
Estos documentos permanecen en `docs/` debido a que contienen hojas de ruta globales o diseños cuyas partes funcionales/visuales aún no se han implementado:

*   [000_PLAN_GLOBAL_PENDIENTES.md](file:///D:/Axolotto_2026/axolotto/docs/000_PLAN_GLOBAL_PENDIENTES.md): **Hoja de ruta viva**. Consolida todo lo pendiente del proyecto.
*   [MASTER_PLAN_CRIADERO.md](file:///D:/Axolotto_2026/axolotto/docs/MASTER_PLAN_CRIADERO.md): **Pendiente desarrollo UI**. Aunque el backend de excavación y niveles del Cenote está en código, el renderizado visual 2.5D interactivo sigue en fase de diseño/desarrollo (Fase 5).
*   [tridyland_migracion_plan.md](file:///D:/Axolotto_2026/axolotto/docs/tridyland_migracion_plan.md): **Pendiente de ejecución**. Plan de migración de TiendaNube a Medusa.js/Next.js que no ha sido inicializado en este repositorio.

---

## 🛠️ ¿Qué tanto falta por hacer? (Pendientes Críticos)

De acuerdo con el plan global y la verificación de código, esto es lo que falta estructurado en orden de prioridad:

### 🔴 Prioridad Alta (Seguridad Pre-Mainnet y Finanzas)
1.  **Fase 0 (Seguridad Final)**:
    *   Rotar `TREASURY_PRIVATE_KEY` en producción (actualmente usa la dev key de Anvil).
    *   Añadir constraints `CHECK (gemas_alga >= 0)` y `CHECK (axogema >= 0)` en la tabla `Wallet` de la base de datos.
    *   Validar la firma y expiración JWT de Privy de forma estricta usando una firma real en producción.
    *   Contratar auditoría externa antes de manejar fondos reales.
2.  **Fase 1 (Blockchain Testnet)**:
    *   Desplegar los smart contracts en la red **Polygon Amoy** (`Chain ID 80002`).
    *   Actualizar las direcciones de contratos en `.env` (backend) y `.env.local` (frontend), y cambiar el interruptor `BLOCKCHAIN_MODE=polygon_amoy`.
3.  **Fase 2 (Pasarelas de Pago)**:
    *   **Mercado Pago (Fíat)**: Desarrollar el servicio en `mercadopago_service.py`, el webhook de cobro y redirigir en la tienda.
    *   **Ramp/MoonPay (Cripto)**: Integrar SDK de Ramp y añadir endpoint `/moonpay-sign` con firma HMAC-SHA256 para producción.
4.  **Fase 3 (Sistema de Retiros / DevEx)**:
    *   Crear modelo `WithdrawalRequest` y auditar retenciones fiscales (retención del 7% por Régimen de Premios en México).
    *   Integrar con la API de *Facturapi* para expedir CFDI de retenciones en PDF/XML.
    *   Implementar la **regla de retención anti-fraude de 14 días** sobre Axofichas (`AXF`) ganadas en el mercado P2P antes de que sean elegibles para retiro.

### 🟠 Prioridad Media (Gameplay, UI e Infraestructura)
1.  **Fase 5 (Interfaz Visual y Cenote 2.5D)**:
    *   Implementar el canvas estructurado en CSS de múltiples capas para **El Nido Cenote 2.5D** con comportamiento y animaciones fluidas de los Axolotitos eclosionados.
    *   Renderizar las 5 tablas enemigas de fondo con escala reducida y efecto blur en el simulador multijugador Champion (1v5).
    *   Añadir advertencia visual `"⚠️ CPU cerca..."` al llegar al 70% de tabla de un bot.
2.  **Fase 6 (CI/CD y Cobertura)**:
    *   Escribir el pipeline en `.github/workflows/ci.yml` para correr pytest y forge test en cada commit.
    *   Exigir cobertura superior al **70%** en servicios críticos (`shop_service`, `bank_service`, `multiplayer_service`).
    *   Implementar pruebas automáticas E2E con **Playwright** para tolerancia a fallos de red en el frontend.

### 🟡 Prioridad Baja (Mecánicas de Retención y Gamificación)
1.  **Fase 7 (Gamificación F2P en Tiempo Real)**:
    *   Canal WebSocket (`ws://api/rooms/{room_id}/spectate`) para retransmitir partidas a espectadores.
    *   Loop de eclosión gratis acumulando 100 Fragmentos Astrales para obtener un huevo inicial.
    *   Reto de misiones diarias (Daily Bounties) con recompensas cosméticas.
