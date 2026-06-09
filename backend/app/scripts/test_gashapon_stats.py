import random
import math
import sys

# --- DEFINITIONS ---
class Rarity:
    COMMON = "COMMON"
    RARE = "RARE"
    EPIC = "EPIC"
    LEGENDARY = "LEGENDARY"

# 1. Gashapon Rates
# Common: 70% COMMON, 25% RARE, 5% EPIC
# Premium: 40% RARE, 45% EPIC, 15% LEGENDARY
def simulate_gashapon_roll(roll_type: str) -> str:
    rand = random.random()
    if roll_type == "common":
        if rand < 0.70:
            return Rarity.COMMON
        elif rand < 0.95:
            return Rarity.RARE
        else:
            return Rarity.EPIC
    else:
        if rand < 0.40:
            return Rarity.RARE
        elif rand < 0.85:
            return Rarity.EPIC
        else:
            return Rarity.LEGENDARY

# 2. Capsule Tiers Pools
TIER_POOLS = {
    "bronce": [(0.45, "gal"), (0.75, "carta"), (0.85, "accesorio"), (0.95, "sobre"), (1.0, "axolotito")],
    "plata": [(0.20, "gal"), (0.65, "carta"), (0.80, "accesorio"), (0.90, "sobre"), (1.0, "axolotito")],
    "oro":   [(0.05, "gal"), (0.45, "carta"), (0.65, "accesorio"), (0.75, "sobre"), (1.0, "axolotito")],
}
PITY_LIMITS = {"bronce": 10, "plata": 5, "oro": 3}

# Simulación de la tirada base de una cápsula (sin pity)
def simulate_capsule_base_roll(tier: str) -> str:
    rand = random.random()
    for threshold, outcome in TIER_POOLS[tier]:
        if rand < threshold:
            return outcome
    return "axolotito"

# Simulación de tiradas consecutivas de cápsula con pity
class CapsulePitySimulator:
    def __init__(self, tier: str):
        self.tier = tier
        self.limit = PITY_LIMITS[tier]
        self.pity_count = 0

    def roll(self) -> str:
        # Si alcanza el límite de pity, se le garantiza un axolotito
        if self.pity_count >= self.limit:
            outcome = "axolotito"
        else:
            outcome = simulate_capsule_base_roll(self.tier)
            
        if outcome == "axolotito":
            self.pity_count = 0  # reset pity
        else:
            self.pity_count += 1
            
        return outcome

def chi_squared_test(observed: dict, expected: dict) -> float:
    chi_sq = 0.0
    for key in expected:
        o = observed.get(key, 0)
        e = expected[key]
        chi_sq += ((o - e) ** 2) / e
    return chi_sq

def run_statistics():
    N_TRIALS = 100000
    print(f"📊 [Stats Engine] Iniciando simulación estadística ({N_TRIALS:,} tiradas por caso)...")
    
    # ----------------------------------------------------
    # I. GASHAPÓN (COMÚN Y PREMIUM)
    # ----------------------------------------------------
    gashapon_common_obs = {Rarity.COMMON: 0, Rarity.RARE: 0, Rarity.EPIC: 0}
    gashapon_premium_obs = {Rarity.RARE: 0, Rarity.EPIC: 0, Rarity.LEGENDARY: 0}
    
    for _ in range(N_TRIALS):
        gashapon_common_obs[simulate_gashapon_roll("common")] += 1
        gashapon_premium_obs[simulate_gashapon_roll("premium")] += 1
        
    gash_common_exp = {Rarity.COMMON: N_TRIALS * 0.70, Rarity.RARE: N_TRIALS * 0.25, Rarity.EPIC: N_TRIALS * 0.05}
    gash_premium_exp = {Rarity.RARE: N_TRIALS * 0.40, Rarity.EPIC: N_TRIALS * 0.45, Rarity.LEGENDARY: N_TRIALS * 0.15}
    
    chi_gash_common = chi_squared_test(gashapon_common_obs, gash_common_exp)
    chi_gash_premium = chi_squared_test(gashapon_premium_obs, gash_premium_exp)
    
    # ----------------------------------------------------
    # II. CÁPSULAS (BRONCE/COBRE, PLATA, ORO) - TIRADAS BASE (SIN PITY)
    # Para validar el generador aleatorio puro con Chi-Cuadrado (5 categorías, df = 4, valor crítico = 9.488)
    # ----------------------------------------------------
    capsule_base_obs = {
        "bronce": {"gal": 0, "carta": 0, "accesorio": 0, "sobre": 0, "axolotito": 0},
        "plata": {"gal": 0, "carta": 0, "accesorio": 0, "sobre": 0, "axolotito": 0},
        "oro":   {"gal": 0, "carta": 0, "accesorio": 0, "sobre": 0, "axolotito": 0}
    }
    
    for tier in ("bronce", "plata", "oro"):
        for _ in range(N_TRIALS):
            outcome = simulate_capsule_base_roll(tier)
            capsule_base_obs[tier][outcome] += 1
            
    capsule_exp = {
        "bronce": {"gal": N_TRIALS * 0.45, "carta": N_TRIALS * 0.30, "accesorio": N_TRIALS * 0.10, "sobre": N_TRIALS * 0.10, "axolotito": N_TRIALS * 0.05},
        "plata": {"gal": N_TRIALS * 0.20, "carta": N_TRIALS * 0.45, "accesorio": N_TRIALS * 0.15, "sobre": N_TRIALS * 0.10, "axolotito": N_TRIALS * 0.10},
        "oro":   {"gal": N_TRIALS * 0.05, "carta": N_TRIALS * 0.40, "accesorio": N_TRIALS * 0.20, "sobre": N_TRIALS * 0.10, "axolotito": N_TRIALS * 0.25}
    }
    
    chi_capsules = {}
    for tier in ("bronce", "plata", "oro"):
        chi_capsules[tier] = chi_squared_test(capsule_base_obs[tier], capsule_exp[tier])

    # ----------------------------------------------------
    # III. CÁPSULAS CON PITY ACTIVO
    # Muestra el comportamiento real esperado por el jugador en tiradas sucesivas
    # ----------------------------------------------------
    capsule_pity_obs = {
        "bronce": {"gal": 0, "carta": 0, "accesorio": 0, "sobre": 0, "axolotito": 0},
        "plata": {"gal": 0, "carta": 0, "accesorio": 0, "sobre": 0, "axolotito": 0},
        "oro":   {"gal": 0, "carta": 0, "accesorio": 0, "sobre": 0, "axolotito": 0}
    }
    
    for tier in ("bronce", "plata", "oro"):
        sim = CapsulePitySimulator(tier)
        for _ in range(N_TRIALS):
            outcome = sim.roll()
            capsule_pity_obs[tier][outcome] += 1

    # ----------------------------------------------------
    # IV. VERIFICACIÓN Y COMPROBACIÓN DE LÍMITES CRÍTICOS
    # ----------------------------------------------------
    gash_critical = 5.991    # df = 2, alpha = 0.05
    capsule_critical = 9.488 # df = 4, alpha = 0.05
    
    gash_passed = (chi_gash_common < gash_critical) and (chi_gash_premium < gash_critical)
    capsules_passed = all(chi_capsules[t] < capsule_critical for t in ("bronce", "plata", "oro"))
    
    # ----------------------------------------------------
    # IMPRESIÓN DEL REPORTE
    # ----------------------------------------------------
    print("\n==========================================================================")
    print("                REPORTE ESTADÍSTICO DE TASAS DE DROP (SISTEMAS)            ")
    print("==========================================================================")
    print(f"Número de tiradas simuladas por caso: {N_TRIALS:,}")
    print("--------------------------------------------------------------------------")
    print("1. GASHAPÓN:")
    print("  * Común (Objetivo: 70% Común, 25% Rara, 5% Épica):")
    print(f"    - COMÚN:      {gashapon_common_obs[Rarity.COMMON]/N_TRIALS*100:.3f}% (Esperado: 70.0%)")
    print(f"    - RARA:       {gashapon_common_obs[Rarity.RARE]/N_TRIALS*100:.3f}% (Esperado: 25.0%)")
    print(f"    - ÉPICA:      {gashapon_common_obs[Rarity.EPIC]/N_TRIALS*100:.3f}% (Esperado: 5.0%)")
    print(f"    - Chi-Sq:     {chi_gash_common:.4f} (Límite: {gash_critical})")
    
    print("  * Premium (Objetivo: 40% Rara, 45% Épica, 15% Legendaria):")
    print(f"    - RARA:       {gashapon_premium_obs[Rarity.RARE]/N_TRIALS*100:.3f}% (Esperado: 40.0%)")
    print(f"    - ÉPICA:      {gashapon_premium_obs[Rarity.EPIC]/N_TRIALS*100:.3f}% (Esperado: 45.0%)")
    print(f"    - LEGENDARIA: {gashapon_premium_obs[Rarity.LEGENDARY]/N_TRIALS*100:.3f}% (Esperado: 15.0%)")
    print(f"    - Chi-Sq:     {chi_gash_premium:.4f} (Límite: {gash_critical})")
    print(f"  * Resultado de Gashapón: {'✅ ACEPTADO (Aleatoriedad Correcta)' if gash_passed else '❌ FALLADO'}")
    
    print("--------------------------------------------------------------------------")
    print("2. CÁPSULAS SORPRESA (Bronce/Cobre, Plata, Oro) - DISTRIBUCIÓN BASE:")
    for tier in ("bronce", "plata", "oro"):
        label = "BRONCE" if tier == "bronce" else tier.upper()
        print(f"  * Cápsula de {label}:")
        for out in ("gal", "carta", "accesorio", "sobre", "axolotito"):
            exp_pct = (capsule_exp[tier][out] / N_TRIALS) * 100
            print(f"    - {out:<10}: {capsule_base_obs[tier][out]/N_TRIALS*100:.3f}% (Esperado: {exp_pct:.1f}%)")
        print(f"    - Chi-Sq:     {chi_capsules[tier]:.4f} (Límite: {capsule_critical})")
    print(f"  * Resultado de Cápsulas Base: {'✅ ACEPTADO (Aleatoriedad Correcta)' if capsules_passed else '❌ FALLADO'}")
    
    print("--------------------------------------------------------------------------")
    print("3. CÁPSULAS SORPRESA - EFECTO REAL DE LA RACHA DE SEGURIDAD (PITY):")
    print("   (Muestra cómo el Pity eleva la probabilidad de Axolotito sacrificando GAL/accesorios)")
    for tier in ("bronce", "plata", "oro"):
        label = "BRONCE" if tier == "bronce" else tier.upper()
        pity_lim = PITY_LIMITS[tier]
        print(f"  * Cápsula de {label} (Garantía Pity a las {pity_lim} tiradas sin Axolotito):")
        for out in ("gal", "carta", "accesorio", "sobre", "axolotito"):
            base_pct = (capsule_exp[tier][out] / N_TRIALS) * 100
            pity_pct = (capsule_pity_obs[tier][out] / N_TRIALS) * 100
            print(f"    - {out:<10}: Con Pity: {pity_pct:.3f}% | Sin Pity: {base_pct:.1f}% (Diferencia: {pity_pct - base_pct:+.3f}%)")
            
    print("==========================================================================\n")
    
    # Escribir reporte en archivo
    with open("gashapon_stats_report.txt", "w") as f:
        f.write("=== REPORTE ESTADÍSTICO DE GASHAPÓN Y CÁPSULAS ===\n")
        f.write(f"Tiradas Simuladas por Caso: {N_TRIALS}\n\n")
        
        f.write("--- GASHAPÓN ---\n")
        f.write(f"Common Chi-Sq: {chi_gash_common:.4f} (Límite: {gash_critical}) - {'PASSED' if chi_gash_common < gash_critical else 'FAILED'}\n")
        f.write(f"Premium Chi-Sq: {chi_gash_premium:.4f} (Límite: {gash_critical}) - {'PASSED' if chi_gash_premium < gash_critical else 'FAILED'}\n\n")
        
        f.write("--- CÁPSULAS BASE ---\n")
        for t in ("bronce", "plata", "oro"):
            f.write(f"Tier {t.upper()} Chi-Sq: {chi_capsules[t]:.4f} (Límite: {capsule_critical}) - {'PASSED' if chi_capsules[t] < capsule_critical else 'FAILED'}\n")
            
        f.write("\n--- CÁPSULAS CON PITY (COMPORTAMIENTO EMPÍRICO REAL) ---\n")
        for t in ("bronce", "plata", "oro"):
            f.write(f"Tier {t.upper()} (Pity {PITY_LIMITS[t]}):\n")
            for out in ("gal", "carta", "accesorio", "sobre", "axolotito"):
                f.write(f"  - {out}: {capsule_pity_obs[t][out]/N_TRIALS*100:.3f}%\n")
                
    if gash_passed and capsules_passed:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    run_statistics()
