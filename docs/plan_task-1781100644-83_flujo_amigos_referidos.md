# Plan de Implementacion: Flujo de Amigos y Referidos

**Task:** task-1781100644-83
**Estado:** planning
**Fecha:** 2026-06-11
**Autor:** Claude

---

## Alcance

Construir el sistema completo de amigos (social graph) y referidos (viral loop) como capa social unificada del juego. Se implementa en 2 fases secuenciales.

El diseno maestro completo esta en `docs/plan_social_layer.md`. Este plan extrae y prioriza lo que construimos ahora.

---

## Fase 1: Core Social Graph (Prioridad Inmediata)

**Objetivo:** Amigos funcionales -- agregar, aceptar, listar amigos, ver cuevas, dar likes.

### Backend

| # | Archivo | Accion | Detalle |
|---|---------|--------|---------|
| 1.1 | `backend/app/models/social.py` | CREAR | `FriendRelation`, `SocialActionLog`, `FriendStatus` enum, `SocialActionType` enum |
| 1.2 | `backend/app/models/__init__.py` | MODIFICAR | Exportar modelos sociales |
| 1.3 | Migracion Alembic | CREAR | Tablas `friend_relations`, `social_action_logs` |
| 1.4 | `backend/app/services/social_service.py` | CREAR | `send_friend_request()`, `accept_friend_request()`, `reject_friend_request()`, `remove_friend()`, `get_friends_list()`, `get_online_status()`, `process_like()` |
| 1.5 | `backend/app/api/v1/endpoints/social.py` | CREAR | Router con endpoints CRUD de amigos |
| 1.6 | `backend/app/main.py` | MODIFICAR | Incluir router social |
| 1.7 | Endpoint busqueda | CREAR | `GET /social/friends/search?q=nickname` |
| 1.8 | Endpoint recientes | CREAR | `GET /social/friends/recent-players` |
| 1.9 | Endpoint likes | CREAR | `POST /social/like/{target_user_id}` |
| 1.10 | Endpoint visitas | CREAR | `POST /social/visit/{target_user_id}` |
| 1.11 | Modificar salas | MODIFICAR | Validar visibilidad `friends` contra grafo social en `POST /multiplayer/create-room` |

### Frontend

| # | Archivo | Accion | Detalle |
|---|---------|--------|---------|
| 1.12 | `frontend/hooks/useSocial.ts` | CREAR | Hook `useFriends()`, `useFriendRequests()`, `useSocialActions()` |
| 1.13 | `frontend/components/social/AmigosPage.tsx` | CREAR | Pantalla completa de amigos con 4 tabs: Amigos, Solicitudes, Buscar, Referidos |
| 1.14 | `frontend/components/social/FriendRequestPanel.tsx` | CREAR | Panel de solicitudes recibidas con Aceptar/Rechazar |
| 1.15 | `frontend/components/social/FriendCaveView.tsx` | CREAR | Vista de cueva de amigo (reemplaza ZonaCentral) |
| 1.16 | `frontend/components/santuario/ZonaInferior.tsx` | MODIFICAR | Conectar a datos reales: 4 amigos mas activos |
| 1.17 | `frontend/components/screens/AmigosScreen.tsx` | CREAR | Pantalla tipo pantalla completa (wrapper de AmigosPage) |

### Integracion

| # | Archivo | Accion | Detalle |
|---|---------|--------|---------|
| 1.18 | `frontend/components/PlayMode.tsx` | MODIFICAR | Agregar tab/pantalla de Amigos en el dock de navegacion |

### Criterios de Aceptacion Fase 1

- [ ] Buscar jugador por nickname y enviar solicitud
- [ ] Destinatario recibe solicitud y puede aceptar/rechazar
- [ ] Amigos aparecen en ZonaInferior (4 mas activos)
- [ ] Tocar ojo (visitar) muestra cueva del amigo
- [ ] Like funciona (1 toque, +1 FRJ ambos)
- [ ] Sala "friends" solo deja entrar a amigos confirmados
- [ ] Rate-limit: 10 solicitudes/hora, max 20 pendientes

---

## Fase 2: Sistema de Referidos

**Objetivo:** Codigo unico por usuario, recompensas progresivas, sharing nativo.

### Backend

| # | Archivo | Accion | Detalle |
|---|---------|--------|---------|
| 2.1 | `backend/app/models/social.py` | MODIFICAR | Agregar `ReferralCode`, `ReferralTracking`, `ReferralStatus` enum |
| 2.2 | Migracion Alembic | CREAR | Tablas `referral_codes`, `referral_tracking` |
| 2.3 | `backend/app/services/referral_service.py` | CREAR | `generate_referral_code()`, `claim_referral()`, `process_referral_reward()`, `check_anti_fraud()` |
| 2.4 | `backend/app/api/v1/endpoints/referrals.py` | CREAR | Router: `GET /code`, `POST /claim/{code}`, `GET /dashboard`, `GET /rewards/history` |
| 2.5 | `backend/app/main.py` | MODIFICAR | Incluir router referrals |
| 2.6 | Reward processor | CREAR | Funcion async que entrega rewards por hitos (registro, tutorial, D7, primera compra) |
| 2.7 | Job nocturno | CREAR | Detectar churn (30d sin actividad), recalcular metricas |

### Frontend

| # | Archivo | Accion | Detalle |
|---|---------|--------|---------|
| 2.8 | `frontend/hooks/useReferrals.ts` | CREAR | `useReferralCode()`, `useReferralDashboard()` |
| 2.9 | `frontend/components/social/ReferralDashboard.tsx` | CREAR | Dashboard de referidos: codigo, stats, rewards |
| 2.10 | `frontend/components/social/ShareCodeSheet.tsx` | CREAR | Bottom sheet nativo OS con opciones: WhatsApp, IG, Twitter, Copiar link, QR |
| 2.11 | `frontend/components/social/ReferralPage.tsx` | CREAR | Landing ligera `axolot.to/join/{code}` con info del referidor |

### Integracion

| # | Archivo | Accion | Detalle |
|---|---------|--------|---------|
| 2.12 | Modificar registro | MODIFICAR | Al crear cuenta (callback de Privy), verificar si hay codigo de referido pendiente y asociarlo |
| 2.13 | Auto-friend | MODIFICAR | `referral_service.claim_referral()` crea `FriendRelation` entre referidor y referido |
| 2.14 | Boton compartir post-partida | MODIFICAR | En pantalla de victoria, boton "Invitar amigo" que abre ShareCodeSheet |
| 2.15 | Boton compartir post-eclosion | MODIFICAR | Al obtener axolotito legendario/raro, sugerir compartir |

### Criterios de Aceptacion Fase 2

- [ ] Cada usuario tiene codigo unico generado (lazy, primera consulta)
- [ ] Share sheet nativo con link pre-escrito para WhatsApp
- [ ] Link `axolot.to/join/CODE` muestra info del referidor
- [ ] Al registrarse con codigo, ambos reciben rewards
- [ ] Dashboard muestra referidos y rewards acumulados
- [ ] Referidor se vuelve amigo automatico del referido
- [ ] Anti-fraud detecta misma IP/wallet (no permite auto-referido)
- [ ] Limite 10 referidos activos/mes, 100 de por vida

---

## Estructura de Recompensas (Referidos)

| Hito | Recompensa Referidor | Recompensa Referido |
|------|---------------------|---------------------|
| Registro | +50 FRJ | +50 FRJ |
| Tutorial completado | +20 AXF | +20 AXF |
| Primera partida | +30 FRJ | -- |
| D7 retencion | +100 FRJ + item "Corcholata del Compadre" | Item "Corcholata del Ahijado" |
| Primera compra | +5% bonus en siguiente purchase | +5% bonus en esta compra |
| Sube a VIP Coral | +3 dias VIP extra | +3 dias VIP extra |

---

## Modelos de Datos Resumidos

### FriendRelation
- user_a, user_b (FK -> users.privy_did)
- status: pending | active | blocked | removed
- friends_since, interaction_count, last_interaction_at
- UniqueConstraint(user_a, user_b)

### ReferralCode
- user_id (FK, unique)
- code (unique, max 30 chars, formato: `AXOLOTO-{NICKNAME}` o `AX-{CODIGO}`)
- total_uses, active_referrals, rewards_earned_frj, rewards_earned_axf

### ReferralTracking
- referrer_id, referred_id (FK -> users)
- code_used (FK -> referral_codes.code)
- status: registered | tutorial_done | d7_retained | converted | churned
- rewards_given_to_referrer (JSON), rewards_given_to_referred (JSON)

### SocialActionLog
- actor_id, target_id, action_type
- metadata_json (item_id, quantity, etc.)
- Usado para analytics y anti-abuse

---

## Referencias

- `docs/plan_social_layer.md` -- Diseno maestro completo
- `docs/plan_chat_integration.md` -- Chat (Fase 3+)
- `docs/plan_santuario_mobile_layout.md` -- Layout santuario
- `docs/GDD.md` -- Game Design Document
