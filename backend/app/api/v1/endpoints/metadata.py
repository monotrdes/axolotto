from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlmodel import Session, select
from app.database import get_session
from app.models.axolotito import Axolotito
import json

router = APIRouter()

@router.get("/axolotito/{token_id}.svg")
def get_axolotito_svg(token_id: int, session: Session = Depends(get_session)):
    axolotito = session.exec(select(Axolotito).where(Axolotito.blockchain_token_id == token_id)).first()
    if not axolotito:
        raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
        
    skin_colors = {
        "pink": "#FFD2E1",
        "gray_light_pink": "#D6C2C9",
        "gray_light": "#A3A3A3",
        "gray_dark": "#4B5563",
        "gray_dead_sea": "#262626"
    }
    fill_color = skin_colors.get(axolotito.skin_color, "#FFD2E1")
    
    if axolotito.skin_color == "astral":
        fill_color = "url(#astralGradient)"
    elif axolotito.skin_color == "gold":
        fill_color = "url(#goldGradient)"
    else:
        luck = axolotito.stat_luck
        if luck > 99.0:
            fill_color = "url(#astralGradient)"
        elif luck > 80.0:
            fill_color = "url(#goldGradient)"
        
    # Elementos dinámicos en base a los stats y skin
    luck = axolotito.stat_luck
    glow_luck_50 = f'<circle cx="200" cy="200" r="140" stroke="#FBBF24" stroke-width="4" fill="none" opacity="0.3" filter="url(#glow)" />' if (luck > 50.0 or axolotito.skin_color == "gold") else ""
    glow_luck_99 = f'<circle cx="200" cy="200" r="140" stroke="#06B6D4" stroke-width="4" fill="none" opacity="0.4" filter="url(#glow)" />' if (luck > 99.0 or axolotito.skin_color == "astral") else ""
    
    eyes_html = ""
    if axolotito.eye_type == "derp":
        eyes_html = """<circle cx="165" cy="180" r="10" fill="#ffffff" />
            <circle cx="170" cy="182" r="5" fill="#000000" />
            <circle cx="235" cy="180" r="10" fill="#ffffff" />
            <circle cx="230" cy="182" r="5" fill="#000000" />"""
    elif axolotito.eye_type == "zen":
        eyes_html = """<circle cx="165" cy="180" r="12" fill="#ffffff" filter="url(#glow)" />
            <circle cx="235" cy="180" r="12" fill="#ffffff" filter="url(#glow)" />"""
    else:
        eyes_html = """<circle cx="165" cy="180" r="10" fill="#000000" />
            <circle cx="162" cy="177" r="4" fill="#ffffff" />
            <circle cx="167" cy="182" r="2" fill="#ffffff" />
            <circle cx="235" cy="180" r="10" fill="#000000" />
            <circle cx="232" cy="177" r="4" fill="#ffffff" />
            <circle cx="237" cy="182" r="2" fill="#ffffff" />"""

    mouth_html = ""
    if axolotito.mouth_type == "rockstar":
        mouth_html = '<path d="M 185 200 Q 200 220 215 200" fill="#e11d48" stroke="#000000" stroke-width="3" />'
    elif axolotito.mouth_type == "flat":
        mouth_html = '<line x1="185" y1="200" x2="215" y2="200" stroke="#475569" stroke-width="3" stroke-linecap="round" />'
    elif axolotito.mouth_type == "divine":
        mouth_html = '<path d="M 185 198 Q 200 208 215 198" fill="none" stroke="#FCD34D" stroke-width="4" stroke-linecap="round" filter="url(#glow)" />'
    else:
        mouth_html = '<path d="M 185 198 Q 200 208 215 198" fill="none" stroke="#475569" stroke-width="3" stroke-linecap="round" />'

    forehead_html = ""
    if axolotito.forehead_type == "gem":
        forehead_html = "<polygon points='200,140 206,148 200,156 194,148' fill='#ef4444' filter='url(#glow)' />"
    elif axolotito.forehead_type == "halo":
        forehead_html = "<ellipse cx='200' cy='125' rx='30' ry='8' fill='none' stroke='#FCD34D' stroke-width='4' filter='url(#glow)' />"

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
        <defs>
            <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#0f172a" />
                <stop offset="100%" stop-color="#1e1b4b" />
            </linearGradient>
            <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#FCD34D" />
                <stop offset="50%" stop-color="#FBBF24" />
                <stop offset="100%" stop-color="#D97706" />
                <animate attributeName="x1" values="0%;100%;0%" dur="5s" repeatCount="indefinite" />
                <animate attributeName="y1" values="0%;100%;0%" dur="5s" repeatCount="indefinite" />
            </linearGradient>
            <linearGradient id="astralGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#8B5CF6" />
                <stop offset="50%" stop-color="#3B82F6" />
                <stop offset="100%" stop-color="#06B6D4" />
                <animate attributeName="x1" values="0%;100%;0%" dur="6s" repeatCount="indefinite" />
                <animate attributeName="y1" values="0%;100%;0%" dur="6s" repeatCount="indefinite" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="8" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
        </defs>

        <rect width="100%" height="100%" fill="url(#bgGradient)" />
        <circle cx="200" cy="200" r="120" fill="#1e293b" opacity="0.6" filter="url(#glow)" />
        {glow_luck_50}
        {glow_luck_99}

        <path d="M 240 220 C 310 230, 330 260, 360 250 C 320 280, 270 270, 240 240 Z" fill="{fill_color}" opacity="0.9" />
        <ellipse cx="200" cy="230" rx="60" ry="40" fill="{fill_color}" />
        <ellipse cx="200" cy="180" rx="75" ry="60" fill="{fill_color}" />

        <ellipse cx="140" cy="255" rx="15" ry="25" fill="{fill_color}" transform="rotate(-15 140 255)" />
        <ellipse cx="260" cy="255" rx="15" ry="25" fill="{fill_color}" transform="rotate(15 260 255)" />
        <ellipse cx="150" cy="210" rx="12" ry="20" fill="{fill_color}" transform="rotate(20 150 210)" />
        <ellipse cx="250" cy="210" rx="12" ry="20" fill="{fill_color}" transform="rotate(-20 250 210)" />

        <!-- Gills Left -->
        <path d="M 130 160 C 90 140, 80 170, 128 175" fill="#f43f5e" stroke="#e11d48" stroke-width="2" />
        <path d="M 125 180 C 80 170, 75 200, 125 195" fill="#f43f5e" stroke="#e11d48" stroke-width="2" />
        <path d="M 130 200 C 90 205, 80 230, 128 215" fill="#f43f5e" stroke="#e11d48" stroke-width="2" />
        
        <!-- Gills Right -->
        <path d="M 270 160 C 310 140, 320 170, 272 175" fill="#f43f5e" stroke="#e11d48" stroke-width="2" />
        <path d="M 275 180 C 320 170, 325 200, 275 195" fill="#f43f5e" stroke="#e11d48" stroke-width="2" />
        <path d="M 270 200 C 310 205, 320 230, 272 215" fill="#f43f5e" stroke="#e11d48" stroke-width="2" />

        {eyes_html}
        {mouth_html}
        {forehead_html}

        <text x="20" y="380" fill="#64748b" font-family="monospace" font-size="14">Axolotito #{token_id}</text>
        <text x="380" y="380" fill="#64748b" font-family="monospace" font-size="14" text-anchor="end">{axolotito.skin_color.upper()}</text>
    </svg>"""
    return Response(content=svg_content, media_type="image/svg+xml")

@router.get("/axolotito/{token_id}")
def get_axolotito_metadata(token_id: int, session: Session = Depends(get_session)):
    axolotito = session.exec(select(Axolotito).where(Axolotito.blockchain_token_id == token_id)).first()
    if not axolotito:
        raise HTTPException(status_code=404, detail="Axolotito no encontrado.")
        
    # Mapeo de nombres legibles para OpenSea
    # Salinidad
    sal = axolotito.stat_salinity
    if sal <= 10.0: salinity_label = "Fresco"
    elif sal <= 30.0: salinity_label = "Saladito"
    elif sal <= 60.0: salinity_label = "Salado"
    elif sal <= 90.0: salinity_label = "Muy Salado"
    else: salinity_label = "Mar Muerto"
    
    # Suerte
    luck = axolotito.stat_luck
    if axolotito.skin_color == "astral":
        luck_label = "Astral"
    elif axolotito.skin_color == "gold":
        luck_label = "El Dorado"
    else:
        if luck <= 20.0: luck_label = "Común"
        elif luck <= 50.0: luck_label = "Centellante"
        elif luck <= 80.0: luck_label = "Aura Dorada"
        elif luck <= 99.0: luck_label = "El Dorado"
        else: luck_label = "Astral"
    
    # Concentración
    focus = axolotito.stat_focus
    if focus < 20.0: focus_label = "Bizco (Derp)"
    elif focus < 50.0: focus_label = "Soñador"
    elif focus < 80.0: focus_label = "Atento"
    elif focus < 95.0: focus_label = "Intelectual"
    else: focus_label = "Zen"
    
    # Energía
    stamina = axolotito.stat_stamina
    if stamina < 80: gill_label = "Branquias Cortas"
    elif stamina < 120: gill_label = "Branquias Estándar"
    elif stamina < 160: gill_label = "Branquias Plumosas"
    elif stamina < 190: gill_label = "Corona Imperial"
    else: gill_label = "Frenesí de Fénix"
    
    # Carisma
    charisma = axolotito.stat_charisma
    if charisma < 20.0: mouth_label = "Apático"
    elif charisma < 60.0: mouth_label = "Alegre"
    elif charisma < 80.0: mouth_label = "Pícaro"
    elif charisma < 95.0: mouth_label = "Estrella de Rock"
    else: mouth_label = "Divino"
    
    # Agilidad
    agility = axolotito.stat_agility
    if agility < 30.0: tail_label = "Aleta Estándar"
    elif agility < 60.0: tail_label = "Aleta Ondulada"
    elif agility < 85.0: tail_label = "Aleta de Betta"
    else: tail_label = "Aleta de Plasma"
    
    # Sabiduría
    wisdom = axolotito.stat_wisdom
    if wisdom < 40.0: forehead_label = "Sin Patrón"
    elif wisdom < 70.0: forehead_label = "Frente Atigrada"
    elif wisdom < 90.0: forehead_label = "Gema Mística"
    else: forehead_label = "Halo Sagrado"
    
    # Fuerza
    strength = axolotito.stat_strength
    if strength < 40.0: limb_label = "Deditos de Goma"
    elif strength < 75.0: limb_label = "Garras Afiladas"
    elif strength < 95.0: limb_label = "Extremidades Escamosas"
    else: limb_label = "Armadura Coralina"

    metadata = {
        "name": axolotito.name,
        "description": f"Un ajolote criado en los estanques de Axolotto con ADN {axolotito.dna_sequence}.",
        "image": f"https://api.axolot.to/api/v1/metadata/axolotito/{token_id}.svg",
        "external_url": f"https://axolot.to/axolotito/{token_id}",
        "attributes": [
            {"trait_type": "SUERTE ✨", "value": axolotito.stat_luck,     "display_type": "number"},
            {"trait_type": "OJO \U0001f441️",   "value": axolotito.stat_focus,    "display_type": "number"},
            {"trait_type": "PILA \U0001f50b",  "value": axolotito.stat_stamina,  "display_type": "number"},
            {"trait_type": "SAL \U0001f9c2",   "value": axolotito.stat_salinity, "display_type": "number"},
            {"trait_type": "Naturaleza", "value": axolotito.nature or "desconocida"},
            {"trait_type": "Nivel",      "value": axolotito.level, "display_type": "number"},
        ]
    }
    return metadata
