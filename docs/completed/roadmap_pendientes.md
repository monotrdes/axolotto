# Pendientes Consolidados del Ecosistema Axolotto

Este archivo consolida las tareas y flujos pendientes identificados a partir de los documentos de diseño y planificación del proyecto.

---

## ⛓️ Fase 6: Confirmación de Blockchain en todo el Flujo (Mercado Secundario)

*   **[ ] Expandir el script de simulación (`simulate_universe.py`)**
    *   **Detalle**: Actualmente, el simulador del universo (`backend/app/scripts/simulate_universe.py`) cubre la eclosión de huevos, la compra de boosters, el reclamado de staking y la simulación de partidas. Falta añadir la cobertura para el mercado secundario P2P:
        *   Simular que un jugador publica una Tabla de Lotería y un Axolotito para venta definitiva y renta.
        *   Simular que otro jugador compra el tablero y renta el Axolotito.
        *   Verificar que se ejecuten las transferencias on-chain de los tokens ERC-721 en Anvil local y que se actualicen las wallets y estados en la base de datos de manera coordinada.
