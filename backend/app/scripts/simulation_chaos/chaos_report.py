"""
chaos_report.py — Critical security audit report generator.

Classifies all SecurityIncidents by severity and produces a structured
Markdown report with attack summaries, mitigation rates, and recommendations.
"""
import os
from datetime import datetime
from collections import Counter
from typing import Optional
from chaos_types import IncidentSeverity, SecurityIncident, ChaosConfig


def _sort_key(sev: IncidentSeverity) -> int:
    """Sort order: CRITICAL first, then WARNING, then INFO."""
    order = {IncidentSeverity.CRITICAL: 0, IncidentSeverity.WARNING: 1, IncidentSeverity.INFO: 2}
    return order.get(sev, 99)


def generate_chaos_report(
    incidents: list[SecurityIncident],
    counters: dict,
    stats: dict,
    config: ChaosConfig,
    runtime_seconds: float = 0.0,
) -> str:
    """Generate a complete Markdown security audit report."""

    # ── Classify incidents ───────────────────────────────────────────────────
    criticals = [i for i in incidents if i.severity == IncidentSeverity.CRITICAL]
    warnings  = [i for i in incidents if i.severity == IncidentSeverity.WARNING]
    infos     = [i for i in incidents if i.severity == IncidentSeverity.INFO]

    criticals.sort(key=lambda i: i.timestamp)
    warnings.sort(key=lambda i: i.timestamp)

    mitigation_pct = _calc_mitigation(counters)

    report = f"""
{'='*70}
🛡️  REPORTE DE AUDITORÍA DE SEGURIDAD — CHAOS & SECURITY SIMULATOR V2
{'='*70}
⏰  Generado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
⏱️  Duración total: {runtime_seconds:.1f}s
{'='*70}
📋  CONFIGURACIÓN DE LA PRUEBA
{'─'*70}
  👥 Total bots:        {config.total_bots}
     🐋 Whales:          {config.whale_count} (20%)
     📦 Collectors:      {config.collector_count} (30%)
     🆓 Free2Play:       {config.free2play_count} (50%)
  ⏱️  Duración:           {config.duration_seconds}s
  🔄 Replay Attack:      {'✅' if config.enable_replay_attack else '❌'}
  👤 ID Spoofing:        {'✅' if config.enable_id_spoofing else '❌'}
  ⚡ Race Condition:     {'✅' if config.enable_race_condition else '❌'}
  🎯 Double Booking:     {'✅' if config.enable_double_booking else '❌'}
  💉 Boundary Injection: {'✅' if config.enable_boundary_injection else '❌'}
  ⏱️  Cooldown Bypass:    {'✅' if config.enable_cooldown_bypass else '❌'}
{'='*70}
📊  RESUMEN EJECUTIVO
{'─'*70}
  🔴 CRITICAL:  {len(criticals)}  — Acción inmediata requerida
  🟡 WARNING:   {len(warnings)}   — Revisar y optimizar
  🟢 INFO:      {len(infos)}      — Comportamiento correcto
  📈 Total incidentes: {len(incidents)}
{'─'*70}
  🎯 Tasa de mitigación de ataques: {mitigation_pct:.1f}%
  🔗 Acciones de bots:              {stats.get('bot_actions', 0)}
  ⚡ Throughput:                     {stats.get('bot_actions', 0) / max(1, runtime_seconds):.1f} acciones/s
  💥 Errores 500 en bots:           {stats.get('bot_500s', 0)}
  🎮 Partidas jugadas:              {stats.get('games_played', 0)}
  🎓 Axolotitos en staking:         {stats.get('axolotitos_staked', 0)}
  🔓 Axolotitos retirados (unstake): {stats.get('axolotitos_unstaked', 0)}
"""

    # ── CRITICAL section ─────────────────────────────────────────────────────
    report += f"\n{'='*70}\n🔴  CRITICALS ({len(criticals)}) — ACCIÓN INMEDIATA REQUERIDA\n{'─'*70}\n"
    if criticals:
        # Group by category
        crit_by_cat: dict[str, list[SecurityIncident]] = {}
        for c in criticals:
            crit_by_cat.setdefault(c.category, []).append(c)

        for cat, items in crit_by_cat.items():
            report += f"\n  📌 {cat.upper()} ({len(items)} incidencias)\n"
            for item in items[:10]:  # Show first 10 per category
                report += f"    [{item.timestamp}] {item.description}\n"
                report += f"    Status: {item.status_code} | Thread: {item.thread_id}\n"
                report += f"    Detail: {item.detail[:200]}\n\n"
            if len(items) > 10:
                report += f"    ... y {len(items) - 10} más\n\n"
    else:
        report += "  ✅ Ningún ataque logró vulnerar el sistema.\n"

    # ── WARNING section ──────────────────────────────────────────────────────
    report += f"\n{'─'*70}\n🟡  WARNINGS ({len(warnings)}) — REVISAR Y OPTIMIZAR\n{'─'*70}\n"
    if warnings:
        warn_by_cat: dict[str, list[SecurityIncident]] = {}
        for w in warnings:
            warn_by_cat.setdefault(w.category, []).append(w)

        for cat, items in warn_by_cat.items():
            report += f"\n  📌 {cat.upper()} ({len(items)} incidencias)\n"
            for item in items[:5]:
                report += f"    [{item.timestamp}] {item.description}\n"
                report += f"    Status: {item.status_code} | {item.detail[:120]}\n\n"
            if len(items) > 5:
                report += f"    ... y {len(items) - 5} más\n\n"
    else:
        report += "  ✅ Sin warnings.\n"

    # ── INFO summary (compressed) ────────────────────────────────────────────
    report += f"\n{'─'*70}\n🟢  INFO ({len(infos)}) — COMPORTAMIENTO CORRECTO\n{'─'*70}\n"
    if infos:
        info_by_cat: dict[str, int] = Counter(i.category for i in infos)
        for cat, count in sorted(info_by_cat.items()):
            report += f"  ✅ {cat}: {count} intentos bloqueados exitosamente\n"
    else:
        report += "  Sin registros INFO.\n"

    # ── Attack summary table ─────────────────────────────────────────────────
    report += f"""
{'─'*70}
📊  RESUMEN DE ATAQUES POR TIPO
{'─'*70}
  {'Tipo':<22} {'Lanzados':>8}  {'Bloqueados':>10}  {'Exitosos':>8}  {'Tasa':>6}
  {'─'*22} {'─'*8}  {'─'*10}  {'─'*8}  {'─'*6}
"""
    attack_types = [
        ("replay",        "Replay Attack"),
        ("spoof",         "ID Spoofing"),
        ("race",          "Race Condition"),
        ("booking",       "Double Booking"),
        ("injection",     "Boundary Injection"),
        ("cooldown",      "Cooldown Bypass"),
    ]
    for key, label in attack_types:
        launched = counters.get(f"{key}_launched", 0)
        blocked  = counters.get(f"{key}_blocked", 0)
        succeeded = counters.get(f"{key}_succeeded", 0)
        rate = (blocked / launched * 100) if launched > 0 else 0.0
        report += f"  {label:<22} {launched:>8}  {blocked:>10}  {succeeded:>8}  {rate:>5.1f}%\n"

    report += f"""
{'─'*70}
  TOTAL:            {sum(counters.get(f'{k}_launched', 0) for k, _ in attack_types):>8} lanzados
  BLOQUEADOS:       {sum(counters.get(f'{k}_blocked', 0) for k, _ in attack_types):>8}
  EXITOSOS:         {sum(counters.get(f'{k}_succeeded', 0) for k, _ in attack_types):>8}
  MITIGACIÓN:       {mitigation_pct:>7.1f}%
{'='*70}
🏁  SIMULACIÓN CAÓTICA COMPLETADA
{'='*70}
"""
    return report


def _calc_mitigation(counters: dict) -> float:
    """Calculate overall attack mitigation percentage."""
    total_launched = sum(
        counters.get(f"{k}_launched", 0)
        for k in ("replay", "spoof", "race", "booking", "injection", "cooldown")
    )
    total_succeeded = sum(
        counters.get(f"{k}_succeeded", 0)
        for k in ("replay", "spoof", "race", "booking", "injection", "cooldown")
    )
    if total_launched == 0:
        return 100.0
    return (1.0 - total_succeeded / total_launched) * 100


def save_chaos_report(report: str, path: str = "/app/chaos_simulation_report.txt") -> str:
    """Write the report to disk. Returns the path written."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    return path


def generate_setup_summary(stats: dict) -> str:
    """Generate a brief Markdown summary of the setup phase (for progress log)."""
    return f"""📋 Setup completado:
  👥 Usuarios creados:      {stats.get('users_created', 0)}
  💸 AXF comprados:         {stats.get('axg_purchased_qty', 0):.0f} AXF
  🃏 Boosters comprados:    {stats.get('boosters_bought', 0)}
  🥚 Webitos adoptados:     {stats.get('eggs_bought', 0)}
  🐣 Axolotitos nacidos:    {stats.get('eggs_hatched', 0)}
  📋 Tableros creados:      {stats.get('boards_created', 0)}
  👑 VIP activaciones:      {stats.get('vip_activations', 0)}
"""
