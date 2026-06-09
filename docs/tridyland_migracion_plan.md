# Plan de Migración: Tridyland de TiendaNube → Servidor Propio

> **Proyecto:** tridyland.com — tienda de coleccionables 3D impresos (fidgets, kawaii, pop culture)
> **Plataforma actual:** Mi Tienda Nube
> **Objetivo:** Migrar a servidor propio, eliminar cuota mensual y comisiones, control total del código

---

## Por Qué Migrar

| TiendaNube cobra | Tu servidor |
|-----------------|-------------|
| $500–2,000 MXN/mes (plan) | ~$150–300 MXN/mes hosting |
| 0–2% comisión por venta | 0% comisión |
| Código cerrado, no tuyo | Código 100% tuyo |
| Template limitado | Diseño libre |
| Apps de pago para funciones extra | Construyes exactamente lo que necesitas |

**Break-even estimado:** Con 1,000 MXN/mes de ahorro, recuperas tiempo de desarrollo en ~2-3 meses.

---

## Inventario Completo de lo que Existe en Tridyland

### Catálogo
- [ ] ~17 categorías principales
- [ ] Subcategorías y colecciones temáticas
- [ ] Variantes por atributo: Color, Personaje, Tipo de lente, Versión
- [ ] Indicadores de stock: "Sin stock", "Oferta", "Envío gratis"
- [ ] Precios en MXN con decimales
- [ ] Imágenes WebP múltiples por producto
- [ ] Paginación de listados

### Checkout y Pagos
- [ ] Carrito con cantidad editable
- [ ] Tarjetas: Visa, Mastercard, Amex, Maestro, débito
- [ ] OXXO (pago en efectivo)
- [ ] Meses sin intereses: hasta 24 meses
- [ ] Flujo de confirmación de orden

### Envíos
- [ ] Calculadora de envío por código postal
- [ ] Integración Correos de México
- [ ] Envío gratis (por monto mínimo)
- [ ] Estimación de días

### Cuenta de Cliente
- [ ] Registro / login
- [ ] Historial de órdenes
- [ ] Direcciones guardadas

### Programa de Lealtad: Tridy Quest
- [ ] Sistema de XP/puntos
- [ ] Recompensas canjeables
- [ ] (Detalles exactos: ver panel admin de TiendaNube)

### SEO y Marketing
- [ ] Schema.org (Product, AggregateOffer, BreadcrumbList) en JSON-LD
- [ ] Open Graph / redes sociales
- [ ] Newsletter signup
- [ ] Integración redes: Instagram, Facebook, YouTube, TikTok

### UX / Frontend
- [ ] Hero carousel con banners promocionales
- [ ] Filtros por atributo en listado
- [ ] Sorting: precio, alfabético, más vendidos, destacados, más nuevo
- [ ] Breadcrumbs
- [ ] FAQ section
- [ ] Diseño responsive (mobile-first)
- [ ] Badges: Oferta, Sin stock, Envío gratis

---

## Stack Recomendado

```
Frontend:   Next.js 15 (App Router) + Tailwind CSS
Backend:    Medusa.js 2.x  ← headless commerce open source
Database:   PostgreSQL (Railway o Supabase)
Pagos:      MercadoPago SDK
Envíos:     Skydropx API (agrega Correos MX, Estafeta, FedEx, DHL)
Imágenes:   Cloudinary (CDN + WebP automático)
Email:      Resend (3,000 mails/mes gratis)
Hosting FE: Vercel (gratis hasta escala alta)
Hosting BE: Railway (~$5 USD/mes con DB)
Search:     Meilisearch (self-hosted, gratis) o Algolia
```

### Por qué Medusa.js y no custom desde cero
- Maneja sin código extra: catálogo, variantes, carrito, checkout, órdenes, clientes, cupones, regiones/monedas, inventario, admin panel
- Plugin oficial `medusa-payment-mercadopago` existe
- Puedes extender con módulos propios (ej. Tridy Quest)
- Admin panel ya funcional para gestionar productos y órdenes
- API REST + Events para webhooks internos
- Ahorra ~6 semanas de desarrollo vs. custom

---

## Fases de Migración

---

### FASE 0 — Preparación y Exportación de Datos

**Objetivo:** Tener todos los datos de TiendaNube en mano antes de construir nada.

#### Checklist
- [ ] Exportar productos desde TiendaNube admin (CSV): nombre, descripción, precio, stock, variantes, imágenes URL, categorías
- [ ] Exportar órdenes históricas (para referencia)
- [ ] Exportar clientes (emails, si TN lo permite con GDPR/privacidad)
- [ ] Descargar todas las imágenes de producto (por lote o vía script del CSV)
- [ ] Documentar todos los atributos de variantes exactos (los nombres exactos importan)
- [ ] Anotar reglas de envío gratis (¿a partir de qué monto?)
- [ ] Capturar slugs de URL actuales (para hacer redirects 301)
- [ ] Screenshots del diseño actual sección por sección (referencia para replicar)
- [ ] Copiar HTML/CSS del template modificado de TiendaNube
- [ ] Documentar configuración de Tridy Quest: puntos por acción, niveles, premios

---

### FASE 1 — Infraestructura Base

**Objetivo:** Proyecto corriendo localmente con DB y admin funcional.

#### Setup Medusa Backend
- [ ] `npx create-medusa-app@latest tridyland-backend`
- [ ] Configurar PostgreSQL (Railway sandbox gratis)
- [ ] Correr migraciones: `medusa db:migrate`
- [ ] Levantar admin panel: verificar acceso en `localhost:9000/app`
- [ ] Configurar región MX: moneda MXN, zona horaria, idioma español
- [ ] Configurar impuestos México (IVA 16% si aplica)

#### Setup Next.js Storefront
- [ ] `npx create-next-app@latest tridyland-store --typescript --tailwind --app`
- [ ] Conectar al SDK de Medusa: `@medusajs/js-sdk`
- [ ] Variables de entorno: `NEXT_PUBLIC_MEDUSA_BACKEND_URL`
- [ ] Estructura de rutas:
  ```
  /                        → Home
  /productos               → Listado general
  /categoria/[slug]        → Por categoría
  /producto/[slug]         → Detalle de producto
  /carrito                 → Carrito
  /checkout                → Pago
  /cuenta                  → Dashboard cliente
  /cuenta/ordenes          → Historial
  /cuenta/tridy-quest      → Programa de lealtad
  ```

---

### FASE 2 — Catálogo de Productos

**Objetivo:** Todos los productos de TiendaNube visibles en la nueva tienda.

#### Import de Productos
- [ ] Crear script de seed que lee CSV exportado de TiendaNube
- [ ] Para cada producto: crear en Medusa via API con nombre, descripción, handle (slug), imágenes
- [ ] Por cada variante (color + personaje + versión): crear `ProductVariant` con precio y stock
- [ ] Subir imágenes a Cloudinary via script (bulk upload desde URLs del CSV)
- [ ] Asociar URL Cloudinary a cada producto en Medusa
- [ ] Crear categorías en Medusa y asignar productos
- [ ] Verificar en admin panel que todo se ve correcto

#### Frontend Catálogo
- [ ] Página de listado `/productos` con grid responsive
- [ ] Card de producto: imagen, nombre, precio, badge "Sin stock" / "Oferta" / "Envío gratis"
- [ ] Filtros por atributo en sidebar (color, personaje, versión) — conectar a Medusa query params
- [ ] Sorting: precio ASC/DESC, nombre, más vendidos, más nuevo
- [ ] Paginación (Medusa devuelve offset/limit)
- [ ] Página de detalle `/producto/[slug]`:
  - [ ] Galería de imágenes (swiper/carousel)
  - [ ] Selector de variante (color, etc.)
  - [ ] Precio actualizado por variante
  - [ ] Botón "Agregar al carrito" (deshabilitado si sin stock)
  - [ ] Badge stock
  - [ ] Descripción
  - [ ] Calculadora de envío por CP (componente separado)
  - [ ] Productos relacionados de la misma categoría
- [ ] Breadcrumbs en detalle y categoría
- [ ] Página de categoría `/categoria/[slug]` con header y descripción

#### SEO por Producto
- [ ] `generateMetadata` en Next.js para cada producto: title, description, OG image
- [ ] JSON-LD `Product` schema con precio, disponibilidad, imágenes
- [ ] Sitemap dinámico: `app/sitemap.ts` que lee todos los productos de Medusa

---

### FASE 3 — Carrito y Checkout

**Objetivo:** Flujo completo de compra funcional.

#### Carrito
- [ ] Context/estado global del carrito (usar Medusa cart API)
- [ ] Crear carrito al primer `add to cart` (Medusa crea un `cart` con ID)
- [ ] Guardar `cart_id` en localStorage/cookie
- [ ] Sidebar de carrito: lista de items, cantidades editables, subtotal
- [ ] Botón de eliminar item
- [ ] Aplicar cupón de descuento (Medusa lo soporta nativamente)

#### Checkout — Paso 1: Dirección
- [ ] Formulario: nombre, apellido, email, teléfono, calle, número, colonia, CP, ciudad, estado
- [ ] Validación de campos
- [ ] Autocompletar si cliente tiene sesión activa

#### Checkout — Paso 2: Envío
- [ ] Al ingresar CP, llamar backend → Skydropx API → devolver opciones de paquetería con precio y días
- [ ] Mostrar: Correos MX, Estafeta, FedEx, etc. con precio y tiempo estimado
- [ ] Seleccionar opción de envío → actualizar total en Medusa cart
- [ ] Si aplica envío gratis: mostrarlo automáticamente

#### Checkout — Paso 3: Pago (MercadoPago)
- [ ] Instalar plugin `medusa-payment-mercadopago` en Medusa
- [ ] Configurar credenciales MercadoPago en `.env`: `MP_ACCESS_TOKEN`, `MP_PUBLIC_KEY`
- [ ] Payment Brick de MercadoPago (`@mercadopago/sdk-react`): muestra tarjetas, OXXO, cuotas automáticamente
- [ ] Al completar pago: webhook de MercadoPago → Medusa confirma orden
- [ ] Página de éxito `/checkout/success?order_id=...`
- [ ] Página de error `/checkout/error`

#### Meses Sin Intereses
- [ ] Configurar en MercadoPago dashboard: activar cuotas para la cuenta
- [ ] En el Payment Brick, las cuotas aparecen automáticamente si la tarjeta las soporta
- [ ] Mostrar en producto: "Hasta 24 meses de $XX" (calcular client-side)

---

### FASE 4 — Envíos (Skydropx)

**Objetivo:** Cotización en tiempo real y generación de guías.

#### Cotización en Checkout
- [ ] Crear cuenta en Skydropx (tienen sandbox/test mode)
- [ ] Endpoint en Medusa: `POST /store/shipping/quote`
  ```
  Input: { cp_destino, peso_total, dimensiones }
  Output: [{ paqueteria, precio, dias_estimados, carrier_id }]
  ```
- [ ] Integrar con carrito: calcular peso total sumando todos los items (agregar campo `weight` a productos)
- [ ] Mostrar opciones en checkout paso 2

#### Generación de Guía al Confirmar Orden
- [ ] Hook en Medusa: `order.placed` → llamar Skydropx API para crear envío
- [ ] Guardar número de guía en metadatos de la orden
- [ ] Mostrar número de guía en email de confirmación y en "Mis Órdenes"

#### Admin: Gestión de Envíos
- [ ] En Medusa admin, ver guía asignada por orden
- [ ] Marcar como enviado → trigger email automático al cliente con número de guía
- [ ] Link de rastreo por paquetería

#### Configuración de Envío Gratis
- [ ] Crear regla en Medusa: envío gratis cuando subtotal >= $X MXN
- [ ] Mostrar banner "¡Agrega $X más y obtén envío gratis!" en carrito

---

### FASE 5 — Cuentas de Cliente

**Objetivo:** Registro, login, historial de órdenes.

- [ ] Página `/cuenta/login` con formulario email + contraseña
- [ ] Página `/cuenta/registro`
- [ ] Recuperación de contraseña vía email (Resend)
- [ ] Dashboard `/cuenta`: nombre, email, botón editar
- [ ] `/cuenta/ordenes`: lista de órdenes con estado, fecha, total, link a detalle
- [ ] `/cuenta/ordenes/[id]`: detalle con items, tracking, estado
- [ ] `/cuenta/direcciones`: gestionar direcciones guardadas
- [ ] Checkout autocompletado si hay sesión activa

---

### FASE 6 — Tridy Quest (Programa de Lealtad)

**Objetivo:** Replicar y mejorar el sistema de XP/recompensas.

#### Módulo Custom en Medusa
- [ ] Tabla `loyalty_accounts`: user_id, xp_total, nivel_actual, creado_en
- [ ] Tabla `loyalty_events`: user_id, tipo, xp, descripción, orden_id, creado_en
- [ ] Tabla `loyalty_rewards`: nombre, xp_costo, tipo (descuento/producto), valor, activo

#### Reglas de XP
- [ ] Primera compra: +100 XP
- [ ] Cada $100 MXN gastados: +10 XP
- [ ] Referir amigo que compra: +200 XP
- [ ] Cumpleaños: +50 XP
- [ ] Reseña de producto: +25 XP
- [ ] Seguir en Instagram (verificación manual o via webhook): +30 XP

#### Niveles Sugeridos
| Nivel | XP Requerido | Beneficio |
|-------|-------------|-----------|
| Explorador | 0 | Base |
| Coleccionista | 500 | 5% descuento |
| Maestro Axolotl | 1,500 | 10% descuento + envío prioritario |
| Leyenda Tridy | 5,000 | 15% + acceso preventa + regalo mensual |

#### Frontend
- [ ] Página `/cuenta/tridy-quest`: barra de progreso, XP actual, nivel, historial de eventos
- [ ] Modal de celebración al subir de nivel
- [ ] Catálogo de recompensas canjeables
- [ ] Badge de nivel en el header cuando hay sesión

---

### FASE 7 — Email Transaccional

**Objetivo:** Todos los emails que TiendaNube mandaba, ahora desde tu sistema.

Usar **Resend** con templates React:

- [ ] Confirmación de orden (orden #, items, total, estimado de envío)
- [ ] Orden enviada (número de guía, link de rastreo)
- [ ] Pago rechazado
- [ ] Contraseña restablecida
- [ ] Bienvenida al registrarse
- [ ] OXXO — código de pago y vencimiento
- [ ] Subiste de nivel en Tridy Quest
- [ ] Newsletter (integrar con Mailchimp o lista propia)

---

### FASE 8 — Home y Contenido

**Objetivo:** Página principal fiel al diseño actual con mejoras.

- [ ] Hero carousel con banners (archivos JSON editables como CMS simple)
- [ ] Sección "Novedades" → productos más recientes
- [ ] Sección "Más vendidos"
- [ ] Sección por colección destacada
- [ ] Sección newsletter
- [ ] Footer: redes, contacto, FAQ, políticas
- [ ] Página FAQ
- [ ] Páginas estáticas: Sobre nosotros, Política de devoluciones, Términos

---

### FASE 9 — SEO y Performance

**Objetivo:** No perder posicionamiento al migrar.

- [ ] Redirects 301 de todas las URLs anteriores de TiendaNube al nuevo formato
- [ ] `app/sitemap.ts` dinámico
- [ ] `app/robots.ts`
- [ ] `generateMetadata` en todas las páginas (title, description, og:image)
- [ ] JSON-LD en productos y categorías
- [ ] Core Web Vitals: imágenes con `next/image`, lazy loading, fonts optimizados
- [ ] Verificar en Google Search Console que el nuevo sitio indexa igual
- [ ] Google Analytics 4 (o Plausible si prefieres sin cookies)

---

### FASE 10 — Launch y Corte

**Objetivo:** Migrar sin perder ventas ni datos.

- [ ] Deploy frontend en Vercel con dominio temporal (ej. `tridyland.vercel.app`)
- [ ] Deploy backend en Railway con dominio temporal
- [ ] QA completo: flujo de compra de punta a punta con tarjeta de prueba
- [ ] QA en mobile (iOS y Android)
- [ ] QA con pago OXXO
- [ ] Prueba de carga básica (simular 10 usuarios simultáneos)
- [ ] Backup de TiendaNube: exportar todo antes de tocar el dominio
- [ ] **Mantener TiendaNube activa 2 semanas en paralelo** (cambiar DNS, monitorear)
- [ ] Apuntar DNS de `tridyland.com` → Vercel
- [ ] Verificar SSL automático
- [ ] Monitorear errores en Vercel (logs, Sentry o similar)
- [ ] Anunciar a clientes: email + redes sociales
- [ ] Cancelar plan TiendaNube solo cuando todo esté estable

---

## Ideas de Mejora vs TiendaNube

### UX / Conversión
- **Vista rápida de producto** (modal sin salir del listado) — TN no tiene esto
- **Wishlist / Lista de deseos** — TN lo tiene en planes pagos, puedes hacerlo gratis
- **Comprado juntos** — recomendaciones por colección o atributo compartido
- **Historial de navegación** (últimos vistos) — local storage
- **Notificación de reposición de stock** — email cuando "sin stock" vuelva a estar disponible
- **Zoom en imágenes de producto** — con `react-medium-image-zoom`

### Checkout
- **Checkout en 1 paso** (todo en una sola página) — convierte mejor que el de 3 pasos de TN
- **Guardar carrito entre sesiones** si el usuario cierra y regresa
- **Guest checkout** sin necesidad de crear cuenta

### Marketing
- **Programa de referidos con link único** — "comparte este link, si tu amigo compra tú y él ganan XP"
- **Descuentos por primera compra** vía popup al entrar (con email capture)
- **Countdown timer en ofertas** — urgencia
- **Bundle deals** — "compra 3 fidgets y lleva 1 gratis" (Medusa soporta esto nativamente)
- **Preventa** — productos que se pueden comprar antes de fabricar con fecha estimada

### Admin / Operacional
- **Dashboard de métricas propio** — ventas por día, productos más vendidos, tasa de conversión
- **Gestión de inventario por lotes** — si produces por tandas de 10
- **Notas internas en órdenes** — para anotar personalizaciones
- **Impresión de guías en lote** — desde admin, imprimir todas las guías del día
- **Alertas de stock bajo** — email automático cuando queda menos de 3 unidades

### Técnico
- **PWA** (Progressive Web App) — los clientes pueden "instalar" la tienda en su cel
- **Búsqueda con Meilisearch** — búsqueda instantánea, tolerante a typos, con o sin acentos
- **Modo oscuro** — muchos compradores de coleccionables lo prefieren
- **Multi-idioma** — si hay interés en vender a otros países (Medusa lo soporta nativamente)

---

## Costos Estimados

### Hosting Mensual
| Servicio | Costo |
|---------|-------|
| Vercel (frontend) | Gratis (hasta límite generoso) |
| Railway (Medusa + Postgres) | ~$5 USD = ~$100 MXN |
| Cloudinary (imágenes) | Gratis hasta 25GB |
| Resend (emails) | Gratis 3,000/mes, luego $20 USD |
| Skydropx | Paga por guía generada, sin mensualidad |
| MercadoPago | 3.49% + $4 MXN por transacción |
| **Total hosting** | **~$100-200 MXN/mes** |

### vs TiendaNube
| Plan TN | Mensualidad | Comisión |
|---------|-------------|----------|
| Básico | ~$500 MXN | 2% por venta |
| Profesional | ~$1,200 MXN | 1% |
| Avanzado | ~$2,000 MXN | 0% |

**Ahorro mensual: $400–$1,800 MXN + comisiones recuperadas**

---

## Riesgos y Mitigaciones

| Riesgo | Mitigación |
|--------|-----------|
| Caída durante el corte | Mantener TN activa 2 semanas en paralelo |
| Perder posicionamiento SEO | Redirects 301 exactos + Google Search Console |
| MercadoPago falla en producción | Probar exhaustivamente en sandbox antes |
| Envíos descuadrados (peso/dimensiones) | Agregar campo `weight` a cada producto desde el inicio |
| Clientes no encuentran sus órdenes viejas | Importar historial o mantener email de soporte |
| Bugs post-launch | Rollback rápido: TN todavía activa, solo cambiar DNS de vuelta |

---

## Estructura de Archivos del Proyecto

```
tridyland-backend/
  src/
    modules/
      loyalty/         ← Tridy Quest (custom Medusa module)
        models/        ← loyalty_accounts, loyalty_events, loyalty_rewards
        services/      ← LoyaltyService (add XP, check level, redeem reward)
        api/           ← endpoints /store/loyalty/*
      shipping/
        api/           ← POST /store/shipping/quote (llama Skydropx)
    subscribers/
      order-placed.ts  ← trigger XP, generar guía Skydropx
      order-shipped.ts ← enviar email con tracking

tridyland-store/
  app/
    (store)/
      page.tsx
      productos/page.tsx
      producto/[slug]/page.tsx
      categoria/[slug]/page.tsx
    (checkout)/
      carrito/page.tsx
      checkout/page.tsx
      checkout/success/page.tsx
    (cuenta)/
      cuenta/page.tsx
      cuenta/ordenes/page.tsx
      cuenta/tridy-quest/page.tsx
    sitemap.ts
    robots.ts
  components/
    ProductCard.tsx
    ProductFilters.tsx
    ShippingCalculator.tsx   ← CP → cotización Skydropx
    CartSidebar.tsx
    LoyaltyBar.tsx
    PaymentBrick.tsx         ← wrapper de MercadoPago React SDK

scripts/
  import-products.ts    ← leer CSV TiendaNube → crear en Medusa via API
  upload-images.ts      ← bulk upload a Cloudinary
```

---

## Orden de Desarrollo Recomendado

1. **Fase 0** — Exportar datos (1 día)
2. **Fase 1** — Infraestructura base (2 días)
3. **Fase 2** — Catálogo + import (3-4 días)
4. **Fase 3** — Carrito + checkout (3-4 días)
5. **Fase 4** — Envíos Skydropx (2-3 días)
6. **Fase 7** — Emails transaccionales (1-2 días)
7. **Fase 8** — Home y páginas de contenido (2-3 días)
8. **Fase 9** — SEO (1-2 días)
9. **Fase 5** — Cuentas de cliente (2-3 días)
10. **Fase 6** — Tridy Quest (3-4 días)
11. **Fase 10** — Launch (1 semana de QA + corte)

**Timeline total estimado con Claude + Gemini ayudando: 6-8 semanas a tiempo parcial**
