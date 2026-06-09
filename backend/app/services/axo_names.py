"""
axo_names.py — Generador de nombres determinístico para Axolotitos Axolotto

Nombre final = "[Primero] [Epíteto]"
  Primero  → elegido con seed derivado del DNA + incubation_id
  Epíteto  → elegido del banco del **stat más alto** del axolotito, con género

Seed = int(dna[:8], 16) XOR (incubation_id × 2654435761)
  → Mismo axo renacido siempre da el mismo nombre.
  → Dos axos con DNA idéntico pero distinta incubación dan nombres distintos.
  → Sin números. Sin input del usuario. Sin contenido inapropiado.

Combos posibles: 196 nombres × 30 epítetos = 5 880 por categoría de stat
                                             → ~41 160 combinaciones totales
"""

from typing import Literal

# ───────────────────────────────────────────────────────────────────────────────
# NOMBRES BASE — (nombre, género: 'm'|'f')
# ───────────────────────────────────────────────────────────────────────────────

NOMBRES: list[tuple[str, str]] = [
    # ── Nahuatl / Deidades aztecas ──────────────────────────────────────────
    ("Xóchitl",         "f"), ("Citlali",          "f"), ("Quetzal",          "m"),
    ("Tlaloc",          "m"), ("Tonatiuh",         "m"), ("Coatl",            "m"),
    ("Cuauhtli",        "m"), ("Ixchel",           "f"), ("Chalchi",          "f"),
    ("Huitzilin",       "m"), ("Xipe",             "m"), ("Ehécatl",          "m"),
    ("Nanahuatzin",     "m"), ("Meztli",           "f"), ("Xilonen",          "f"),
    ("Toci",            "f"), ("Cipactli",         "m"), ("Centeotl",         "m"),
    ("Xolotl",          "m"), ("Ocelotl",          "m"), ("Coyotl",           "m"),
    ("Macuilxóchitl",   "m"), ("Tlazolteotl",      "f"), ("Coatlicue",        "f"),
    ("Iztaccihuatl",    "f"), ("Ahuizotl",         "m"), ("Tezcatlipoca",     "m"),
    ("Huitzilopochtli", "m"), ("Quetzalcoatl",     "m"), ("Mixcoatl",         "m"),
    ("Tlaltecuhtli",    "m"), ("Itzpapalotl",      "f"), ("Xochiquetzal",     "f"),

    # ── Guerreros y gobernantes históricos ──────────────────────────────────
    ("Axayácatl",       "m"), ("Moctezuma",        "m"), ("Tizoc",            "m"),
    ("Cuitláhuac",      "m"), ("Cuauhtémoc",       "m"), ("Chimalli",         "m"),
    ("Atlahua",         "m"), ("Naolin",           "m"), ("Amoxtli",          "f"),
    ("Eloxóchitl",      "f"), ("Mayahuel",         "f"), ("Ometeotl",         "m"),
    ("Yolotli",         "f"), ("Tlahuizcalpan",    "m"), ("Tepeu",            "m"),

    # ── Naturaleza mexicana ─────────────────────────────────────────────────
    ("Cenote",          "m"), ("Milpa",            "f"), ("Nopal",            "m"),
    ("Ahuejote",        "m"), ("Tule",             "m"), ("Ahuehuete",        "m"),
    ("Pochote",         "m"), ("Tabachín",         "m"), ("Colorín",          "m"),
    ("Bugambilia",      "f"), ("Jacaranda",        "f"), ("Cempasúchil",      "m"),
    ("Tepozán",         "m"), ("Achoque",          "m"), ("Axolote",          "m"),
    ("Ajolín",          "m"), ("Chinampas",        "f"), ("Xochimilco",       "m"),
    ("Tenochtitlan",    "f"), ("Anáhuac",          "m"), ("Mazorca",          "f"),
    ("Quiote",          "m"), ("Teocintle",        "m"), ("Pirúl",            "m"),
    ("Barranca",        "f"), ("Pedregal",          "m"), ("Manantial",        "m"),
    ("Cañada",          "f"), ("Arroyo",           "m"), ("Sabino",           "m"),
    ("Pochote",         "m"), ("Tepalcate",        "m"), ("Tepetate",         "m"),

    # ── Lotería mexicana (las 54 cartas) ────────────────────────────────────
    ("Catrina",         "f"), ("Sirena",           "f"), ("Valiente",         "m"),
    ("Borracho",        "m"), ("Soldado",          "m"), ("Cotorra",          "f"),
    ("Garza",           "f"), ("Camarón",          "m"), ("Alacrán",          "m"),
    ("Araña",           "f"), ("Corona",           "f"), ("Palma",            "f"),
    ("Bandera",         "f"), ("Escalera",         "f"), ("Rosa",             "f"),
    ("Chalupa",         "f"), ("Cantarito",        "m"), ("Barril",           "m"),
    ("Arpa",            "f"), ("Maceta",           "f"), ("Botella",          "f"),
    ("Sandía",          "f"), ("Melón",            "m"), ("Pera",             "f"),
    ("Corazón",         "m"), ("Estrellita",       "f"), ("Nopalito",         "m"),
    ("Tambor",          "m"), ("Diablito",         "m"), ("Bota",             "f"),
    ("Venado",          "m"), ("Paraguas",         "m"), ("Músico",           "m"),
    ("Dama",            "f"), ("Camaron",          "m"), ("Apache",           "m"),

    # ── Gastronomía y cultura popular ───────────────────────────────────────
    ("Tequila",         "m"), ("Mezcal",           "m"), ("Pulque",           "m"),
    ("Tepache",         "m"), ("Mole",             "m"), ("Pozole",           "m"),
    ("Tamalito",        "m"), ("Chapulín",         "m"), ("Chilaquil",        "m"),
    ("Cuitlacoche",     "m"), ("Atole",            "m"), ("Horchata",         "f"),
    ("Godínez",         "m"), ("Cuate",            "m"), ("Firulais",         "m"),
    ("Compadre",        "m"), ("Chela",            "f"), ("Chimichanga",      "f"),
    ("Gordita",         "f"), ("Quesillo",         "m"), ("Tlayuda",          "f"),
    ("Michelada",       "f"), ("Pelusa",           "f"), ("Peludo",           "m"),
    ("Güero",           "m"), ("Chilaquila",       "f"), ("Tlacoyito",        "m"),
    ("Esquite",         "m"), ("Tejuino",          "m"), ("Champurrado",      "m"),

    # ── Fenómenos naturales / meteorología ──────────────────────────────────
    ("Tormenta",        "f"), ("Niebla",           "f"), ("Bruma",            "f"),
    ("Aurora",          "f"), ("Amanecer",         "m"), ("Atardecer",        "m"),
    ("Medianoche",      "f"), ("Crepúsculo",       "m"), ("Solsticio",        "m"),
    ("Trueno",          "m"), ("Tempestad",        "f"), ("Huracán",          "m"),
    ("Ciclón",          "m"), ("Aguacero",         "m"), ("Granizo",          "m"),
    ("Ventisca",        "f"), ("Vendaval",         "m"), ("Ventarrón",        "m"),
    ("Ceniza",          "f"), ("Lava",             "f"), ("Lluvia",           "f"),
    ("Neblina",         "f"), ("Relente",          "m"), ("Roció",            "m"),
    ("Ventolina",       "f"), ("Borrasca",         "f"), ("Marejada",         "f"),

    # ── Minerales y materiales ──────────────────────────────────────────────
    ("Obsidiana",       "f"), ("Jade",             "m"), ("Turquesa",         "f"),
    ("Ámbar",           "m"), ("Cobalto",          "m"), ("Bermellón",        "m"),
    ("Carmesí",         "m"), ("Cinabrio",         "m"), ("Pirita",           "f"),
    ("Basalto",         "m"), ("Pórfido",          "m"), ("Pedernal",         "m"),
    ("Silex",           "m"), ("Cristal",          "m"), ("Ópalo",            "m"),

    # ── Astros y cosmos ─────────────────────────────────────────────────────
    ("Cometa",          "m"), ("Nebulosa",         "f"), ("Supernova",        "f"),
    ("Pulsar",          "m"), ("Pléyade",          "f"), ("Orión",            "m"),
    ("Sirio",           "m"), ("Vega",             "f"), ("Celeste",          "f"),
    ("Solaris",         "m"), ("Lyra",             "f"), ("Draco",            "m"),
    ("Altair",          "m"), ("Rigel",            "m"), ("Antares",          "m"),
    ("Cefeo",           "m"), ("Castor",           "m"), ("Pólux",            "m"),

    # ── Sitios arqueológicos ─────────────────────────────────────────────────
    ("Teotihuacán",     "m"), ("Tula",             "f"), ("Palenque",         "m"),
    ("Monte Albán",     "m"), ("Chichén",          "m"), ("Uxmal",            "m"),
    ("Bonampak",        "m"), ("Tajín",            "m"), ("Xochicalco",       "m"),
    ("Mitla",           "f"), ("Cholula",          "f"), ("Cantona",          "f"),
    ("Tulum",           "m"), ("Kohunlich",        "m"), ("Calakmul",         "m"),

    # ── Instrumentos y músicas mexicanas ────────────────────────────────────
    ("Jarana",          "f"), ("Huapango",         "m"), ("Danzón",           "m"),
    ("Marimba",         "f"), ("Teponaztli",       "m"), ("Caracol",          "m"),
    ("Tambora",         "f"), ("Requinto",         "m"), ("Vihuela",          "f"),
    ("Jarana",          "f"), ("Guitarrón",        "m"), ("Chirimía",         "f"),
]

# Eliminar posibles duplicados preservando orden
_seen: set[str] = set()
_NOMBRES_DEDUP: list[tuple[str, str]] = []
for _n, _g in NOMBRES:
    if _n not in _seen:
        _seen.add(_n)
        _NOMBRES_DEDUP.append((_n, _g))
NOMBRES = _NOMBRES_DEDUP


# ───────────────────────────────────────────────────────────────────────────────
# EPÍTETOS POR STAT — lista de pares (masculino, femenino)
# ───────────────────────────────────────────────────────────────────────────────

StatKey = Literal["luck", "focus", "stamina", "salinity"]

# Active stat keys (salinity excluded from dominant-stat selection as it is a penalty)
ACTIVE_STATS = ["luck", "focus", "stamina", "salinity"]

_EPITETOS_RAW: dict[str, list[tuple[str, str]]] = {

    "luck": [        # Suerte → astros, fortuna, luz
        ("Dorado",          "Dorada"),          ("Estelar",         "Estelar"),
        ("Bendito",         "Bendita"),         ("Dichoso",         "Dichosa"),
        ("Afortunado",      "Afortunada"),      ("Celestial",       "Celestial"),
        ("Áureo",           "Áurea"),           ("Venturoso",       "Venturosa"),
        ("Fulgente",        "Fulgente"),        ("Sagrado",         "Sagrada"),
        ("Predestinado",    "Predestinada"),    ("Elegido",         "Elegida"),
        ("Inmortal",        "Inmortal"),        ("Legendario",      "Legendaria"),
        ("Mítico",          "Mítica"),          ("Supremo",         "Suprema"),
        ("Excelso",         "Excelsa"),         ("Glorioso",        "Gloriosa"),
        ("Reluciente",      "Reluciente"),      ("Próspero",        "Próspera"),
        ("Prodigioso",      "Prodigiosa"),      ("Divino",          "Divina"),
        ("Maravilloso",     "Maravillosa"),     ("Iluminado",       "Iluminada"),
        ("Único",           "Única"),           ("Excepcional",     "Excepcional"),
        ("Portentoso",      "Portentosa"),      ("Venerable",       "Venerable"),
        ("Insigne",         "Insigne"),         ("Magnifico",       "Magnífica"),
    ],

    "focus": [       # Enfoque → precisión, hierro, mente
        ("Preciso",         "Precisa"),         ("Certero",         "Certera"),
        ("Sereno",          "Serena"),          ("Impasible",       "Impasible"),
        ("Imperturbable",   "Imperturbable"),   ("Infalible",       "Infalible"),
        ("Meticuloso",      "Meticulosa"),      ("Calculador",      "Calculadora"),
        ("Estratégico",     "Estratégica"),     ("Exacto",          "Exacta"),
        ("Riguroso",        "Rigurosa"),        ("Disciplinado",    "Disciplinada"),
        ("Implacable",      "Implacable"),      ("Incansable",      "Incansable"),
        ("Perseverante",    "Perseverante"),    ("Tenaz",           "Tenaz"),
        ("Constante",       "Constante"),       ("Firme",           "Firme"),
        ("Sólido",          "Sólida"),          ("Inquebrantable",  "Inquebrantable"),
        ("Determinado",     "Determinada"),     ("Resuelto",        "Resuelta"),
        ("Contundente",     "Contundente"),     ("Inflexible",      "Inflexible"),
        ("Consecuente",     "Consecuente"),     ("Férreo",          "Férrea"),
        ("Acérado",         "Acerada"),         ("Diamantino",      "Diamantina"),
        ("Impenetrable",    "Impenetrable"),    ("Inamovible",      "Inamovible"),
    ],

    "stamina": [     # Resistencia → vida, duración, naturaleza
        ("Resistente",      "Resistente"),      ("Vital",           "Vital"),
        ("Lozano",          "Lozana"),          ("Longevo",         "Longeva"),
        ("Fornido",         "Fornida"),         ("Correoso",        "Correosa"),
        ("Inagotable",      "Inagotable"),      ("Duradero",        "Duradera"),
        ("Perenne",         "Perenne"),         ("Robusto",         "Robusta"),
        ("Vigoroso",        "Vigorosa"),        ("Vivaz",           "Vivaz"),
        ("Lúcido",          "Lúcida"),          ("Fecundo",         "Fecunda"),
        ("Pujante",         "Pujante"),         ("Floreciente",     "Floreciente"),
        ("Exuberante",      "Exuberante"),      ("Frondoso",        "Frondosa"),
        ("Perpetuo",        "Perpetua"),        ("Sempiterno",      "Sempiterna"),
        ("Incombustible",   "Incombustible"),   ("Invulnerable",    "Invulnerable"),
        ("Inmortal",        "Inmortal"),        ("Eterno",          "Eterna"),
        ("Inconmovible",    "Inconmovible"),    ("Inextinguible",   "Inextinguible"),
        ("Interminable",    "Interminable"),    ("Incesante",       "Incesante"),
        ("Perdurable",      "Perdurable"),      ("Imperecedero",    "Imperecedera"),
    ],
}

# Stats que SE EXCLUYEN al buscar el top (salinity es penalización, no virtud)
_EXCLUDED_STATS = {"salinity"}


# ───────────────────────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ───────────────────────────────────────────────────────────────────────────────

def generar_nombre_axolotito(dna: str, incubation_id: int, stats: dict) -> str:
    """
    Genera un nombre único y determinístico para un axolotito.

    Args:
        dna:            cadena hexadecimal del ADN empaquetado (ej. "a3f1b2c4...")
        incubation_id:  ID de la incubación (garantiza unicidad aunque el DNA sea igual)
        stats:          diccionario con valores float de cada stat
                        (ej. {"luck": 82.5, "focus": 34.1, "stamina": 100.0, "salinity": 5.0})

    Returns:
        str: nombre compuesto, ej. "Xóchitl Dorada" o "Tlaloc Veloz"
    """
    # Seed combinado: DNA ⊕ incubation_id (primo 2654435761 = Knuth multiplicative hash)
    try:
        dna_int = int(dna[:8], 16)
    except (ValueError, IndexError):
        dna_int = abs(hash(dna)) & 0xFFFFFFFF

    seed = dna_int ^ (incubation_id * 2654435761 & 0xFFFFFFFF)

    # ── Elegir nombre base ──────────────────────────────────────────────────
    nombre, genero = NOMBRES[seed % len(NOMBRES)]

    # ── Encontrar stat más alto (excluyendo salinity) ───────────────────────
    stat_validos = {k: v for k, v in stats.items() if k not in _EXCLUDED_STATS}
    if stat_validos:
        top_stat = max(stat_validos, key=lambda s: float(stat_validos.get(s, 0)))
    else:
        top_stat = "luck"

    # Fallback si el stat no tiene banco propio
    banco = _EPITETOS_RAW.get(top_stat) or _EPITETOS_RAW["luck"]

    # ── Elegir epíteto (bits distintos del seed para independencia) ─────────
    epiteto_par = banco[(seed >> 8) % len(banco)]
    epiteto = epiteto_par[0] if genero == "m" else epiteto_par[1]

    return f"{nombre} {epiteto}"
