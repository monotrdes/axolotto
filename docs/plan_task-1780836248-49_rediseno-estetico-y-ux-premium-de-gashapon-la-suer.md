# Plan: Rediseno Estetico y UX Premium de Gashapon (La Suertuda)

> Generado por **Antigravity (AGY)** · tarea `task-1780836248-49` · 2026-06-07T12:45:00Z

## Descripción
Actualmente, la máquina de Gashapon ("La Suertuda") ofrece una experiencia visual plana: tras pulsar el botón, se muestra inmediatamente el resultado en un modal estático. Queremos transformar este flujo en un evento de alto impacto visual y dopamina, típico de los mejores videojuegos móviles de tipo Gacha.

Implementaremos un flujo de revelación en 3 etapas:
1. **Fase de Suspenso (Vibración y Caída):** La cápsula sale de la máquina virtual, vibra intensamente en el centro de la pantalla mientras destella con energía de misterio.
2. **Fase de Apertura (Explosión):** La cápsula se abre en dos mitades (arriba y abajo) mediante una transición CSS premium con un estallido de luz/partículas del color correspondiente a su rareza.
3. **Fase de Revelación:** El premio se eleva y flota en el centro con efectos holográficos o brillo ambiental, mostrando con orgullo el icono gigante, tipo de recompensa, cantidad, descripción y estadísticas de bonificación en tarjetas flotantes premium, con un botón explícito de "Tocar para Continuar".

---

## Análisis de Impacto
- **Frontend (`frontend/components/Gashapon.tsx`):** Rediseño total de los estados visuales `rolling` y `ResultOverlay` / `ResultCard`. Se introduce un mini-motor de partículas ligeras CSS y animaciones en dos tiempos.
- **Backend:** Cero cambios. Seguimos consumiendo los mismos endpoints `/shop/capsule/roll`, `/shop/capsule/daily-claim` y `/shop/capsule/triple-suerte`.

---

## Archivos a crear/modificar
- `frontend/components/Gashapon.tsx` (Rediseño de interfaz, CSS local de partículas y animación en dos mitades).

---

## Checklist de criterios de aceptación
- [ ] **Simulador de Cápsula Física:** Agregar animación de una cápsula 3D/2.5D cayendo, rebotando y vibrando.
- [ ] **Efectos de Rareza:**
  - *Común:* Destello Teal/Verde suave, partículas circulares básicas.
  - *Raro:* Destello Azul/Cyan eléctrico, partículas romboidales con rastro.
  - *Épico:* Destello Púrpura/Violeta misterioso, partículas tipo estrella de 4 puntas y aura cósmica.
  - *Legendario/Mítico:* Super flash dorado o astral, lluvia de destellos brillantes y texto con gradiente dorado animado.
- [ ] **Efecto Apertura por la Mitad:** La cápsula se separa físicamente en dos partes: hemisferio superior sube, hemisferio inferior baja, revelando el premio que emerge desde el interior.
- [ ] **UX de Recompensa Flotante:** El premio se muestra flotando, con micro-animaciones (levitación y rotación suave), texto grande de cantidad (+X FRJ, Carta X, etc.) y diseño limpio.
- [ ] **Mobile-First UX:** Layout adaptado a una sola mano (fácil acceso al botón de continuar o saltar, gestos fluidos).

---

## Notas de Diseño (UX y Game Design)

### 1. El Flujo Visual en Pantalla

```
[ HOLD BUTTON TO ROLL ]
          │
          ▼
[ CÁPSULA CAE AL CENTRO ] ───► Vibración acelerada (0.8s) + Luz blanca interna
          │
          ▼
[ CLICK / AUTO EXPLODE ] ───► Dos mitades se separan + Explosión de Partículas HSL
          │
          ▼
[ PREMIO EMERGE Y FLOTA ] ───► Tarjeta holográfica flotando + Nombre + Tipo de Item
          │
          ▼
[ CLICK PARA CONTINUAR ]
```

### 2. Rarezas y Paleta de Colores HSL
- **Common (Común):** `hsl(170, 75%, 45%)` (Teal activo)
- **Rare (Raro):** `hsl(195, 85%, 50%)` (Cyan brillante)
- **Epic (Épico):** `hsl(280, 80%, 60%)` (Púrpura neón)
- **Legendary (Legendario):** `hsl(45, 100%, 55%)` (Dorado radiante)
- **Astral (Mítico):** `hsl(295, 95%, 65%)` (Púrpura galáctico / rosa espacial)

### 3. Partículas CSS Ultra-Ligeras
Para no saturar el rendimiento móvil, utilizaremos animaciones CSS con propiedades `transform` y `opacity` aceleradas por hardware (`will-change: transform`). Un set de 15 a 20 partículas flotando radialmente desde el centro de la cápsula es suficiente para crear una sensación premium sin retraso.

---

## Guía de Verificación
1. **Lanzar Cápsula de Bronce/Plata/Oro:** Validar la caída, la vibración inicial, y la explosión.
2. **Comprobar Animación por Rareza:** Forzar un resultado común, raro y legendario (o ver la simulación en local) y asegurar que los destellos coinciden.
3. **Triple Suerte:** Confirmar que las 3 cápsulas se abren secuencialmente una por una con "Siguiente" manteniendo la emoción para cada drop.
