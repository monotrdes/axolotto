from datetime import datetime, timezone, timedelta
import hashlib

def get_current_weather() -> dict:
    """
    Genera el clima dinámico de Xochimilco basado en la hora local (UTC-6 constante).
    El clima cambia cada 6 horas según los 4 períodos del día:
    - Madrugada (00:00 - 05:59): Niebla Fría o Helada Ártica
    - Mañana (06:00 - 11:59): Despejado o Rocío Vitalizador
    - Tarde (12:00 - 17:59): Templado u Ola de Calor
    - Noche (18:00 - 23:59): Fresco Nocturno o Lluvia de Estrellas
    """
    # 1. Obtener hora local de Xochimilco (UTC-6 constante sin horario de verano)
    utc_minus_6 = timezone(timedelta(hours=-6))
    now_xoxo = datetime.now(timezone.utc).astimezone(utc_minus_6)
    
    hour = now_xoxo.hour
    
    # 2. Determinar período
    if 0 <= hour < 6:
        period_id = 0
        period_name = "Madrugada"
        emoji_time = "🌌"
    elif 6 <= hour < 12:
        period_id = 1
        period_name = "Mañana"
        emoji_time = "🌅"
    elif 12 <= hour < 18:
        period_id = 2
        period_name = "Tarde"
        emoji_time = "☀️"
    else:
        period_id = 3
        period_name = "Noche"
        emoji_time = "🌙"
        
    # 3. Generar semilla determinista diaria y de período
    date_str = now_xoxo.strftime("%Y-%m-%d")
    seed_str = f"xochimilco_{date_str}_{period_id}"
    hash_val = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    
    # Determinar si es un evento especial (25% de probabilidad)
    es_especial = (hash_val % 100) < 25
    
    # 4. Asignar climas
    if period_id == 0:  # Madrugada
        if es_especial:
            weather = {
                "id": "deep_freeze",
                "name": "❄️ Helada Ártica",
                "desc": "¡Clima helado extremo! Pérdida de calor crítica (5%/h). Probabilidad de congelarse a 0% de calor aumenta al 40%/h.",
                "loss_rate": 5.0,
                "heat_multiplier": 0.8,
                "stats_multiplier": 1.0,
                "freeze_chance": 0.40
            }
        else:
            weather = {
                "id": "cold_fog",
                "name": "🌫️ Niebla Fría",
                "desc": "Niebla húmeda sobre los canales. El nido se enfría más rápido (3%/h). Probabilidad de congelamiento a 0% de calor: 15%/h.",
                "loss_rate": 3.0,
                "heat_multiplier": 1.0,
                "stats_multiplier": 1.0,
                "freeze_chance": 0.15
            }
    elif period_id == 1:  # Mañana
        if es_especial:
            weather = {
                "id": "energizing_dew",
                "name": "🌱 Rocío Vitalizador",
                "desc": "Las chinampas florecen. El calor baja normal (2%/h), pero las acciones de cuidado dan +50% de ADN/estadísticas.",
                "loss_rate": 2.0,
                "heat_multiplier": 1.0,
                "stats_multiplier": 1.5,
                "freeze_chance": 0.10
            }
        else:
            weather = {
                "id": "clear",
                "name": "☀️ Despejado",
                "desc": "Mañana soleada y tranquila sobre los canales. Pérdida de calor estándar (2%/h). Probabilidad de congelamiento a 0% de calor: 10%/h.",
                "loss_rate": 2.0,
                "heat_multiplier": 1.0,
                "stats_multiplier": 1.0,
                "freeze_chance": 0.10
            }
    elif period_id == 2:  # Tarde
        if es_especial:
            weather = {
                "id": "heatwave",
                "name": "🔥 Ola de Calor",
                "desc": "Calor intenso en Xochimilco. Pérdida de calor mínima (0.5%/h). Clicks y cariños dan +50% de calor.",
                "loss_rate": 0.5,
                "heat_multiplier": 1.5,
                "stats_multiplier": 1.0,
                "freeze_chance": 0.05
            }
        else:
            weather = {
                "id": "warm",
                "name": "⛅ Templado",
                "desc": "Tarde templada con viento suave. El calor baja lentamente (1.5%/h). Probabilidad de congelamiento a 0% de calor: 8%/h.",
                "loss_rate": 1.5,
                "heat_multiplier": 1.0,
                "stats_multiplier": 1.0,
                "freeze_chance": 0.08
            }
    else:  # Noche
        if es_especial:
            weather = {
                "id": "meteor_shower",
                "name": "✨ Lluvia de Estrellas",
                "desc": "Clima cósmico sobre los canales. ¡Las acciones de cariñito otorgan el doble (2x) de ADN/estadísticas!",
                "loss_rate": 2.0,
                "heat_multiplier": 1.0,
                "stats_multiplier": 2.0,
                "freeze_chance": 0.10
            }
        else:
            weather = {
                "id": "cool",
                "name": "🍃 Fresco Nocturno",
                "desc": "Brisa fresca de la noche sobre el lago. Pérdida de calor normal (2%/h). Probabilidad de congelamiento a 0% de calor: 10%/h.",
                "loss_rate": 2.0,
                "heat_multiplier": 1.0,
                "stats_multiplier": 1.0,
                "freeze_chance": 0.10
            }
            
    weather["period"] = period_name
    weather["emoji_time"] = emoji_time
    weather["time_label"] = f"{emoji_time} {period_name}"
    
    return weather
