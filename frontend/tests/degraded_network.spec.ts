// degraded_network.spec.ts
import { test, expect } from '@playwright/test';

/**
 * Test 1: Simulación de Latencia
 * Intercepta la petición de compra y la retrasa 2 segundos.
 */
test('latency simulation', async ({ page }) => {
  // Ruta a interceptar; ajuste según endpoint real
  await page.route('**/api/v1/shop/buy', async route => {
    // retraso de 2 segundos
    await new Promise(r => setTimeout(r, 2000));
    // continuar con la respuesta original (puede ser mockeada)
    await route.continue();
  });

  await page.goto('http://localhost:3000'); // ajuste si la app usa otro path
  // TODO: actualizar selector del botón de compra
  const buyButton = page.getByRole('button', { name: /comprar/i });
  await buyButton.click();
  // Verificar que el botón queda deshabilitado o muestra loader
  await expect(buyButton).toBeDisabled();
});

/**
 * Test 2: Verificación de Red Caída
 * Simula una respuesta 500 del backend.
 */
test('network failure handling', async ({ page }) => {
  await page.route('**/api/v1/shop/buy', async route => {
    await route.fulfill({
      status: 500,
      body: JSON.stringify({ error: 'Internal Server Error' }),
      contentType: 'application/json',
    });
  });

  await page.goto('http://localhost:3000');
  const buyButton = page.getByRole('button', { name: /comprar/i });
  await buyButton.click();
  // Verificar que aparece toast/error UI (ajustar selector)
  const toast = page.locator('[data-testid="toast"]');
  await expect(toast).toContainText('error');
});

/**
 * Test 3: Idempotencia en UI (Anti‑Doble‑Submit)
 * Asegura que múltiples clicks rápidos no disparan múltiples requests.
 */
test('anti double submit', async ({ page }) => {
  let requestCount = 0;
  await page.route('**/api/v1/shop/buy', async route => {
    requestCount++;
    await new Promise(r => setTimeout(r, 2000));
    await route.continue();
  });

  await page.goto('http://localhost:3000');
  const buyButton = page.getByRole('button', { name: /comprar/i });
  // doble click rápido
  await buyButton.dblclick();
  // Esperar que la primera petición haya deshabilitado el botón
  await expect(buyButton).toBeDisabled();
  // Verificar que solo se hizo una petición al backend
  await expect(requestCount).toBe(1);
});
