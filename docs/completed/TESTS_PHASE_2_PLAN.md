# Plan de Implementación: Automatización de Pruebas de Interfaz (E2E Frontend - Fase 2)

Este plan detalla los pasos para configurar e implementar la Fase 2 del plan de pruebas, introduciendo pruebas automatizadas E2E mediante **Playwright** en Next.js para simular red degradada y verificar resiliencia en la UI.

## Proposed Changes

### 1. Setup de Playwright en el Frontend

#### [NEW] [playwright.config.ts](file:///home/monotr/axolotto/frontend/playwright.config.ts)
- Configurar el archivo básico para Playwright para definir dónde residen las pruebas, habilitar el servidor local Next.js en segundo plano si es necesario, y configurar navegadores (preferiblemente Chromium headless para velocidad).

#### [MODIFY] [package.json](file:///home/monotr/axolotto/frontend/package.json)
- Agregar un script `"test:e2e": "playwright test"` para facilitar la ejecución.

### 2. Casos de Prueba Críticos (E2E)

#### [NEW] [degraded_network.spec.ts](file:///home/monotr/axolotto/frontend/tests/degraded_network.spec.ts)
- **Test 1: Simulación de Latencia**
  - Cargar el panel de compra.
  - Interceptar peticiones a `/api/v1/shop/buy` o `/api/v1/shop/booster/open` e inyectar un retraso artificial de 2 segundos.
  - Clic en el botón.
  - Verificar que el botón cambia a estado `disabled` o muestra un spinner/loader mientras la petición está en vuelo.
- **Test 2: Verificación de Red Caída**
  - Interceptar peticiones críticas a la API para responder con un estado `500 Internal Server Error`.
  - Clic en el botón de compra o abrir.
  - Verificar que se muestra un mensaje de error o toast notificando el problema sin colapsar/congelar la página.
- **Test 3: Idempotencia en UI (Anti-Doble-Submit)**
  - Interceptar endpoint, retrasar la respuesta por 2s.
  - Simular clicks rápidos dobles/múltiples en el botón de acción.
  - Validar que el botón se deshabilita de inmediato en el primer click y no se disparan llamadas API redundantes al servidor.

---

## Verification Plan

### Automated Tests
- Instalar dependencias en `frontend/` y ejecutar la suite:
  ```bash
  npm install --save-dev @playwright/test
  npx playwright install chromium
  npm run test:e2e
  ```

### Manual Verification
- Validar que no se introducen regresiones de compilación de TypeScript:
  `npx tsc --noEmit` en `frontend/`.
