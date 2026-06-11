"""phase_10_social.py — Simulación de Capa Social: Amigos y Referidos.

Simula toda la actividad social entre jugadores:
  1. Enviar friend requests entre pares aleatorios
  2. Auto-aceptar solicitudes mutuas
  3. Aceptar solicitudes pendientes
  4. Rechazar algunas solicitudes
  5. Like entre amigos (respetando límite diario)
  6. Visitar cuevas de amigos
  7. Bloquear usuarios
  8. Eliminar amistades
  9. Generar y canjear códigos de referido
  10. Procesar milestones de referidos
  11. Buscar jugadores por nickname
  12. Verificar sugerencias (amigos de amigos)
  13. Rate-limit: intentar exceder solicitudes/hora
  14. Anti-fraud: intentar auto-referido y multi-referido
"""

from sqlmodel import Session, select
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.models.social import (
    FriendRelation, FriendStatus, SocialActionLog, SocialActionType,
    ReferralCode, ReferralTracking, ReferralStatus,
)
from app.models.user import User
from app.models.economy import Wallet
from app.services.social_service import SocialService
from app.services.referral_service import ReferralService
from app.services.bank_service import BankService

from sim_types import _rng


def phase_social_simulation(engine, config, **state) -> dict:
    """Simula toda la actividad social del ecosistema."""
    session: Session = state["session"]
    progress = state["progress"]
    players: list = state["players"]
    stats: dict = state["stats"]
    errors: list = state["errors"]

    progress("  👥 Simulando Capa Social — Amigos y Referidos...")

    user_ids = [p["user_id"] for p in players]
    if len(user_ids) < 2:
        progress("  ⚠️  Se necesitan al menos 2 jugadores para simular actividad social.")
        return {}

    # Asegurar que todos los jugadores tengan wallet (necesario para likes y rewards)
    for uid in user_ids:
        BankService.get_or_create_wallet(session, uid)

    # ── Estadísticas acumuladas ────────────────────────────────────────────
    friend_requests_sent = 0
    friend_requests_accepted = 0
    friend_requests_rejected = 0
    likes_given = 0
    cave_visits = 0
    blocks_created = 0
    friends_removed = 0
    codes_generated = 0
    codes_claimed = 0
    milestones_processed = 0
    rate_limit_hits = 0
    anti_fraud_blocks = 0
    suggestions_checked = 0

    # ═══════════════════════════════════════════════════════════════════════════
    # FASE A: Friend Requests entre pares
    # ═══════════════════════════════════════════════════════════════════════════

    progress("  📨 Enviando solicitudes de amistad entre jugadores...")

    # Cada jugador envía solicitudes a 25-60% de los otros jugadores
    for sender_id in user_ids:
        potential_targets = [uid for uid in user_ids if uid != sender_id]
        # Excluir usuarios con los que ya tiene relación
        available = []
        for tid in potential_targets:
            existing = SocialService._find_relation(session, sender_id, tid)
            if not existing:
                available.append(tid)

        num_requests = _rng.randint(
            max(1, len(available) // 4),
            max(2, len(available) // 2)
        )
        targets = _rng.sample(available, min(num_requests, len(available)))

        for target_id in targets:
            try:
                SocialService.send_friend_request(session, sender_id, target_id)
                friend_requests_sent += 1
            except HTTPException as e:
                if e.status_code == 429:
                    rate_limit_hits += 1
                # Otros errores (ya amigos, bloqueados) son normales
                pass

    # ═══════════════════════════════════════════════════════════════════════════
    # FASE B: Aceptar / Rechazar solicitudes pendientes
    # ═══════════════════════════════════════════════════════════════════════════

    progress("  ✅ Aceptando y rechazando solicitudes pendientes...")

    for user_id in user_ids:
        pending = SocialService.get_pending_requests(session, user_id)
        for req in pending:
            # 70% acepta, 30% rechaza
            if _rng.random() < 0.70:
                try:
                    SocialService.accept_friend_request(session, user_id, req["id"])
                    friend_requests_accepted += 1
                except HTTPException:
                    pass
            else:
                try:
                    SocialService.reject_friend_request(session, user_id, req["id"])
                    friend_requests_rejected += 1
                except HTTPException:
                    pass

    # ═══════════════════════════════════════════════════════════════════════════
    # FASE C: Interacción social entre amigos (likes + visitas)
    # ═══════════════════════════════════════════════════════════════════════════

    progress("  ❤️  Likes y visitas a cuevas entre amigos...")

    for user_id in user_ids:
        friends = SocialService.get_friends_list(session, user_id)
        for friend in friends[:5]:  # Interactuar con hasta 5 amigos
            friend_id = friend["friend_id"]

            # 80% probabilidad de like (si no excedió límite diario)
            if _rng.random() < 0.80:
                try:
                    SocialService.process_like(session, user_id, friend_id)
                    likes_given += 1
                except HTTPException:
                    pass  # Ya dio like hoy, normal

            # 60% probabilidad de visitar cueva
            if _rng.random() < 0.60:
                try:
                    SocialService.visit_cave(session, user_id, friend_id)
                    cave_visits += 1
                except HTTPException:
                    pass

    # ═══════════════════════════════════════════════════════════════════════════
    # FASE D: Bloqueos y eliminación de amistad
    # ═══════════════════════════════════════════════════════════════════════════

    progress("  🚫 Simulando bloqueos y eliminación de amistades...")

    for user_id in user_ids:
        friends = SocialService.get_friends_list(session, user_id)
        if not friends:
            continue

        # 5-15% de amigos son eliminados
        num_remove = max(1, int(len(friends) * _rng.uniform(0.05, 0.15)))
        to_remove = _rng.sample(friends, min(num_remove, len(friends)))
        for friend in to_remove:
            try:
                SocialService.remove_friend(session, user_id, friend["relation_id"])
                friends_removed += 1
            except HTTPException:
                pass

        # Bloquear a 1-2 jugadores aleatorios que NO sean amigos
        non_friends = [
            uid for uid in user_ids
            if uid != user_id
            and not SocialService.are_friends(session, user_id, uid)
            and SocialService._find_relation(session, user_id, uid) is None
        ]
        num_blocks = min(_rng.randint(1, 2), len(non_friends))
        if num_blocks > 0:
            to_block = _rng.sample(non_friends, num_blocks)
            for target_id in to_block:
                try:
                    SocialService.block_user(session, user_id, target_id)
                    blocks_created += 1
                except HTTPException:
                    pass

    # ═══════════════════════════════════════════════════════════════════════════
    # FASE E: Búsqueda y sugerencias
    # ═══════════════════════════════════════════════════════════════════════════

    progress("  🔍 Probando búsqueda y sugerencias de jugadores...")

    for user_id in _rng.sample(user_ids, min(3, len(user_ids))):
        # Buscar por fragmento de nickname
        user = session.exec(select(User).where(User.privy_did == user_id)).first()
        if user and user.nickname:
            query = user.nickname[:3]  # Primeras 3 letras
            try:
                results = SocialService.search_players(session, query, user_id)
                stats["search_results_sample"] = len(results)
            except HTTPException:
                pass

        # Obtener sugerencias
        try:
            suggestions = SocialService.get_suggestions(session, user_id, limit=5)
            suggestions_checked += len(suggestions)
        except HTTPException:
            pass

    # ═══════════════════════════════════════════════════════════════════════════
    # FASE F: Sistema de Referidos
    # ═══════════════════════════════════════════════════════════════════════════

    progress("  🔗 Generando códigos de referido y canjeando...")

    # Todos los jugadores generan su código
    referral_codes = {}
    for user_id in user_ids:
        try:
            code = ReferralService.get_or_create_referral_code(session, user_id)
            referral_codes[user_id] = code.code
            codes_generated += 1
        except Exception:
            pass

    # El 40% de jugadores canjea un código de otro jugador
    # (simulando que fueron referidos por alguien)
    if len(user_ids) >= 2 and len(referral_codes) >= 2:
        # Elegir quiénes serán "referidos" y quiénes "referidores"
        num_referred = max(1, int(len(user_ids) * 0.4))
        referred_pool = _rng.sample(user_ids, num_referred)

        for referred_id in referred_pool:
            # Buscar un referidor que no sea él mismo
            possible_referrers = [
                uid for uid in user_ids
                if uid != referred_id and uid in referral_codes
            ]
            if not possible_referrers:
                continue

            referrer_id = _rng.choice(possible_referrers)
            code = referral_codes[referrer_id]

            try:
                result = ReferralService.claim_referral(session, code, referred_id)
                if result["status"] == "ok":
                    codes_claimed += 1

                    # Procesar algunos milestones para este referido
                    milestones = ["tutorial_done", "first_game"]
                    for milestone in milestones:
                        try:
                            ms_result = ReferralService.process_milestone(
                                session, referred_id, milestone
                            )
                            if ms_result["status"] == "ok":
                                milestones_processed += 1
                        except Exception:
                            pass
                elif result["status"] == "self_referral":
                    anti_fraud_blocks += 1
                elif result["status"] == "referrer_limit":
                    anti_fraud_blocks += 1
            except Exception:
                pass

    # ═══════════════════════════════════════════════════════════════════════════
    # FASE G: Pruebas de edge cases y anti-abuso
    # ═══════════════════════════════════════════════════════════════════════════

    progress("  🛡️  Probando edge cases y protecciones anti-abuso...")

    if len(user_ids) >= 2:
        test_user = user_ids[0]
        other_user = user_ids[1]

        # 1. Intento de auto-like (debe fallar)
        try:
            SocialService.process_like(session, test_user, test_user)
        except HTTPException as e:
            if e.status_code == 400:
                anti_fraud_blocks += 1

        # 2. Intento de auto-referido (debe fallar)
        try:
            code = ReferralService.get_or_create_referral_code(session, test_user)
            result = ReferralService.claim_referral(session, code.code, test_user)
            if result["status"] == "self_referral":
                anti_fraud_blocks += 1
        except Exception:
            pass

        # 3. Segundo like mismo día (debe fallar si ya se dio like)
        if SocialService.are_friends(session, test_user, other_user):
            try:
                SocialService.process_like(session, test_user, other_user)
                # Intentar de nuevo inmediatamente
                try:
                    SocialService.process_like(session, test_user, other_user)
                except HTTPException as e:
                    if e.status_code == 400:
                        rate_limit_hits += 1
            except HTTPException:
                pass

        # 4. Visita a no-amigo (debe fallar)
        non_friend_candidates = [
            uid for uid in user_ids
            if uid != test_user
            and not SocialService.are_friends(session, test_user, uid)
        ]
        if non_friend_candidates:
            stranger = _rng.choice(non_friend_candidates)
            try:
                SocialService.visit_cave(session, test_user, stranger)
            except HTTPException as e:
                if e.status_code == 403:
                    anti_fraud_blocks += 1

    # ═══════════════════════════════════════════════════════════════════════════
    # FASE H: Verificación de integridad post-simulación
    # ═══════════════════════════════════════════════════════════════════════════

    progress("  📊 Verificando integridad de datos sociales...")

    # Contar total de amistades activas
    total_active_friendships = len(session.exec(
        select(FriendRelation).where(FriendRelation.status == FriendStatus.ACTIVE)
    ).all())

    # Contar total de códigos generados
    total_codes = len(session.exec(select(ReferralCode)).all())

    # Contar total de referidos
    total_referrals = len(session.exec(
        select(ReferralTracking).where(
            ReferralTracking.status != ReferralStatus.CHURNED
        )
    ).all())

    # Contar interacciones sociales registradas
    total_likes = len(session.exec(
        select(SocialActionLog).where(
            SocialActionLog.action_type == SocialActionType.LIKE_GIVEN
        )
    ).all())

    total_cave_visits_logged = len(session.exec(
        select(SocialActionLog).where(
            SocialActionLog.action_type == SocialActionType.CAVE_VISITED
        )
    ).all())

    # ── Reporte ────────────────────────────────────────────────────────────
    progress(f"  📊 Amistades activas: {total_active_friendships}")
    progress(f"  📊 Solicitudes enviadas: {friend_requests_sent} | "
             f"Aceptadas: {friend_requests_accepted} | "
             f"Rechazadas: {friend_requests_rejected}")
    progress(f"  📊 Likes: {likes_given} (total BD: {total_likes}) | "
             f"Visitas: {cave_visits} (total BD: {total_cave_visits_logged})")
    progress(f"  📊 Bloqueos: {blocks_created} | "
             f"Amistades eliminadas: {friends_removed}")
    progress(f"  📊 Códigos generados: {codes_generated} (total BD: {total_codes}) | "
             f"Canjeados: {codes_claimed}")
    progress(f"  📊 Milestones procesados: {milestones_processed} | "
             f"Referidos totales: {total_referrals}")
    progress(f"  📊 Sugerencias encontradas: {suggestions_checked}")
    progress(f"  🛡️  Anti-abuso: {anti_fraud_blocks} bloqueos | "
             f"Rate-limit: {rate_limit_hits} hits")
    progress(f"  ✅ Simulación social completada.")

    # ── Actualizar estadísticas in-place (mismo patrón que otros phases) ──
    stats["social_friend_requests_sent"] = friend_requests_sent
    stats["social_friend_requests_accepted"] = friend_requests_accepted
    stats["social_friend_requests_rejected"] = friend_requests_rejected
    stats["social_likes_given"] = likes_given
    stats["social_cave_visits"] = cave_visits
    stats["social_blocks_created"] = blocks_created
    stats["social_friends_removed"] = friends_removed
    stats["social_codes_generated"] = codes_generated
    stats["social_codes_claimed"] = codes_claimed
    stats["social_milestones_processed"] = milestones_processed
    stats["social_rate_limit_hits"] = rate_limit_hits
    stats["social_anti_fraud_blocks"] = anti_fraud_blocks
    stats["social_suggestions_checked"] = suggestions_checked
    stats["social_total_active_friendships"] = total_active_friendships
    stats["social_total_codes"] = total_codes
    stats["social_total_referrals"] = total_referrals
    stats["social_total_likes_logged"] = total_likes
    stats["social_total_visits_logged"] = total_cave_visits_logged
    return {}
