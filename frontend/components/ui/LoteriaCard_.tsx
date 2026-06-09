"use client";

/* ─── LoteriaCard — componente universal de carta de lotería ──────────────────
   Extraído de BoardEditor.tsx. Úsalo en cualquier parte de la app.
   Props:
     card        — objeto de carta con item_metadata.numero_loteria, name, dynamic_rarity, is_shiny
     size        — preset ('xxs'=18 · 'xs'=28 · 'sm'=44 · 'md'=60 · 'lg'=80) o número px directo
     interactive — agrega hover lift/scale cuando la carta no está picked/placed
     picked      — estado "seleccionada" (verde glow + elevar)
     placed      — estado "ya usada" (grayscale + lock icon)
     onClick     — callback al clickear
     showQty     — muestra badge de cantidad si availableQty > 1
─────────────────────────────────────────────────────────────────────────────── */

import { Lock } from 'lucide-react';
import Image from 'next/image';

export const LOTERIA_EMOJI: Record<number, string> = {
   1:'🐓',  2:'😈',  3:'👰',  4:'🎩',  5:'☂️',  6:'🧜',  7:'🪜',  8:'🍾',  9:'🛢️', 10:'🌳',
  11:'🍈', 12:'🤺', 13:'🧢', 14:'💀', 15:'🍐', 16:'🚩', 17:'🪕', 18:'🎻', 19:'🦩', 20:'🐦',
  21:'✋', 22:'🥾', 23:'🌙', 24:'🦜', 25:'🍺', 26:'🧒', 27:'❤️', 28:'🍉', 29:'🥁', 30:'🦐',
  31:'🏹', 32:'🎺', 33:'🕷️', 34:'🪖', 35:'⭐', 36:'🍳', 37:'🌎', 38:'🪶', 39:'🌵', 40:'🦂',
  41:'🌹', 42:'☠️', 43:'🔔', 44:'🏺', 45:'🦌', 46:'☀️', 47:'👑', 48:'🛶', 49:'🌲', 50:'🐟',
  51:'🌴', 52:'🪴', 53:'🎵', 54:'🐸',
};

export const CARD_IMAGE: Record<number, string> = {
   1: '/cartas_loteria/01 - El Axolotl.webp',
   2: '/cartas_loteria/02 - El Diablito.webp',
   3: '/cartas_loteria/03 - La Jefa.webp',
   4: '/cartas_loteria/04 - El Godin.webp',
   5: '/cartas_loteria/05 - La Piñata.webp',
   6: '/cartas_loteria/06 - La Tlanchana.webp',
   7: '/cartas_loteria/07 - El Trompo.webp',
   8: '/cartas_loteria/08 - La Botella.webp',
   9: '/cartas_loteria/09 - El Molcajete.webp',
  10: '/cartas_loteria/10 - El Chilaquil.webp',
  11: '/cartas_loteria/11 - El Aguacate.webp',
  12: '/cartas_loteria/12 - El Luchador.webp',
  13: '/cartas_loteria/13 - El Sombrero.webp',
  14: '/cartas_loteria/14 - La Catrina.webp',
  15: '/cartas_loteria/15 - El Maíz.webp',
  16: '/cartas_loteria/16 - La Bandera.webp',
  17: '/cartas_loteria/17 - El Acordeón.webp',
  18: '/cartas_loteria/18 - La Chancla.webp',
  19: '/cartas_loteria/19 - El Firulais.webp',
  20: '/cartas_loteria/20 - El Michi.webp',
  21: '/cartas_loteria/21 - El Chacmool.webp',
  22: '/cartas_loteria/22 - Los Tenis.webp',
  23: '/cartas_loteria/23 - La Luna.webp',
  24: '/cartas_loteria/24 - El Colibrí.webp',
  25: '/cartas_loteria/25 - La Caguama.webp',
  26: '/cartas_loteria/26 - El Café.webp',
  27: '/cartas_loteria/27 - El Corazón.webp',
  28: '/cartas_loteria/28 - La Salsa.webp',
  29: '/cartas_loteria/29 - El Chamoy.webp',
  30: '/cartas_loteria/30 - El Aguachile.webp',
  31: '/cartas_loteria/31 - El Papel Picado.webp',
  32: '/cartas_loteria/32 - El Músico.webp',
  33: '/cartas_loteria/33 - La Araña.webp',
  34: '/cartas_loteria/34 - El Alebrije.webp',
  35: '/cartas_loteria/35 - La Estrella.webp',
  36: '/cartas_loteria/36 - El Pan.webp',
  37: '/cartas_loteria/37 - El Tlacuache.webp',
  38: '/cartas_loteria/38 - El Taco.webp',
  39: '/cartas_loteria/39 - El Nopal.webp',
  40: '/cartas_loteria/40 - El Alacrán.webp',
  41: '/cartas_loteria/41 - La Rosa.webp',
  42: '/cartas_loteria/42 - La Calavera.webp',
  43: '/cartas_loteria/43 - La Campana.webp',
  44: '/cartas_loteria/44 - El Cantarito.webp',
  45: '/cartas_loteria/45 - El Cacomixtle.webp',
  46: '/cartas_loteria/46 - El Sol.webp',
  47: '/cartas_loteria/47 - El Penacho.webp',
  48: '/cartas_loteria/48 - La Chalupa.webp',
  49: '/cartas_loteria/49 - El Vocho.webp',
  50: '/cartas_loteria/50 - El Pejelagarto.webp',
  51: '/cartas_loteria/51 - La Cobija.webp',
  52: '/cartas_loteria/52 - La maceta.webp',
  53: '/cartas_loteria/53 - El Elote.webp',
  54: '/cartas_loteria/54 - La Botarga.webp',
};

export const RARITY_RING: Record<string, string> = {
  'Legendaria': 'shadow-[0_0_0_1.5px_rgba(251,191,36,0.95),0_0_14px_rgba(251,191,36,0.55)]',
  'Épica':      'shadow-[0_0_0_1.5px_rgba(217,70,239,0.85),0_0_12px_rgba(217,70,239,0.4)]',
  'Rara':       'shadow-[0_0_0_1.5px_rgba(34,211,238,0.8),0_0_10px_rgba(34,211,238,0.35)]',
  'Poco Común': 'shadow-[0_0_0_1.5px_rgba(16,185,129,0.7),0_0_10px_rgba(16,185,129,0.3)]',
  'Común':      'shadow-[0_0_0_1.5px_rgba(148,163,184,0.45),0_4px_8px_rgba(0,0,0,0.4)]',
};

const SIZE_PRESETS: Record<string, number> = {
  xxs: 18,
  xs:  28,
  sm:  44,
  md:  60,
  lg:  80,
  xl:  90,
};

export type CardSizePreset = 'xxs' | 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type CardSize = CardSizePreset | number;

function resolveSize(size: CardSize): number {
  if (typeof size === 'number') return size;
  return SIZE_PRESETS[size] ?? 60;
}

export interface LoteriaCardProps {
  card: any;
  size?: CardSize;
  interactive?: boolean;
  picked?: boolean;
  placed?: boolean;
  onClick?: () => void;
  showQty?: boolean;
  /** Muestra badge ⭐ si la copia es de primera edición */
  isFirstEdition?: boolean;
}

export default function LoteriaCard({
  card,
  size = 'md',
  interactive = false,
  picked = false,
  placed = false,
  onClick,
  showQty = true,
  isFirstEdition = false,
}: LoteriaCardProps) {
  const w = resolveSize(size);
  const h = Math.round(w * 1.5);

  const numero    = Number(card.item_metadata?.numero_loteria) || 0;
  const hue       = (numero * 47) % 360;
  const emoji     = LOTERIA_EMOJI[numero] || '🃏';
  const rarity    = card.dynamic_rarity || 'Común';
  // Only render images at sm+ (44px+). At xxs/xs the emoji is more legible.
  const imageSrc  = (w >= 44 && CARD_IMAGE[numero]) ? CARD_IMAGE[numero] : null;

  const ringClass = picked
    ? 'shadow-[0_0_0_2px_#34d399,0_0_24px_rgba(52,211,153,0.7),0_12px_24px_rgba(0,0,0,0.6)]'
    : RARITY_RING[rarity] || RARITY_RING['Común'];

  return (
    <div
      onClick={placed ? undefined : onClick}
      className={`relative shrink-0 select-none ${placed ? 'cursor-not-allowed' : onClick ? 'cursor-pointer' : ''}`}
      style={{
        width: w,
        height: h,
        transform: picked
          ? 'translateY(-8px) scale(1.06)'
          : undefined,
        transition: interactive || picked
          ? 'transform .18s cubic-bezier(.2,.7,.3,1)'
          : undefined,
        opacity: placed ? 0.32 : 1,
        filter: placed ? 'grayscale(0.9) brightness(0.7)' : undefined,
      }}
      /* hover lift — only when interactive and not picked/placed */
      onMouseEnter={interactive && !picked && !placed ? (e) => {
        (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-4px) scale(1.04)';
      } : undefined}
      onMouseLeave={interactive && !picked && !placed ? (e) => {
        (e.currentTarget as HTMLDivElement).style.transform = '';
      } : undefined}
    >
      <div
        className={`absolute inset-0 overflow-hidden ${ringClass}`}
        style={imageSrc ? { background: '#0a0a14' } : {
          background: `radial-gradient(110% 75% at 50% 0%, hsl(${hue},75%,55%) 0%, hsl(${hue},70%,30%) 55%, hsl(${hue},80%,12%) 100%)`,
        }}
      >
        {/* Imagen real de la carta */}
        {imageSrc ? (
          <Image
            src={imageSrc}
            alt={card.name || `Carta ${numero}`}
            className="absolute inset-0 w-full h-full object-cover"
            draggable={false}
            fill
            sizes={`${w}px`}
          />
        ) : (
          <>
            {/* Trama diagonal (fallback sin imagen) */}
            <div
              className="absolute inset-0 mix-blend-overlay pointer-events-none"
              style={{ background: 'repeating-linear-gradient(45deg, transparent 0 6px, rgba(255,255,255,0.04) 6px 7px)' }}
            />
            {/* Brillo superior */}
            <div
              className="absolute top-0 left-0 right-0 h-[40%] pointer-events-none"
              style={{ background: 'linear-gradient(180deg, rgba(255,255,255,0.25), transparent)' }}
            />
            {/* Emoji principal */}
            <div
              className="absolute leading-none"
              style={{
                top: '38%',
                left: '50%',
                transform: 'translate(-50%,-50%)',
                fontSize: w * 0.55,
                filter: 'drop-shadow(0 2px 3px rgba(0,0,0,0.7))',
              }}
            >
              {emoji}
            </div>
          </>
        )}
        {/* Número — siempre visible sobre la imagen */}
        <div
          className="absolute font-black italic text-white bg-black/60 backdrop-blur-sm rounded-[4px] flex items-center justify-center leading-none z-10"
          style={{
            top: w * 0.06,
            left: w * 0.08,
            padding: `0 ${Math.max(2, w * 0.06)}px`,
            minWidth: Math.max(14, w * 0.28),
            height: Math.max(12, w * 0.22),
            fontSize: Math.max(7, w * 0.18),
            letterSpacing: '-0.5px',
          }}
        >
          {numero || '?'}
        </div>
        {/* Nombre — siempre visible sobre la imagen */}
        <div
          className="absolute bottom-0 left-0 right-0 font-black italic text-white text-center uppercase whitespace-nowrap overflow-hidden text-ellipsis z-10"
          style={{
            padding: `${w * 0.08}px ${w * 0.05}px ${w * 0.06}px`,
            background: 'linear-gradient(180deg,transparent,rgba(0,0,0,0.85))',
            fontSize: Math.max(7, w * 0.13),
            letterSpacing: '0.3px',
            lineHeight: 1.1,
            textShadow: '0 1px 2px rgba(0,0,0,0.9)',
          }}
        >
          {(card.name || '').replace(/^(EL |LA |Las |Los |El |La )/i, '')}
        </div>
        {/* Holo overlay para shiny / Legendaria */}
        {(card.is_shiny || rarity === 'Legendaria') && !placed && (
          <div className="holo-overlay z-20" />
        )}
      </div>

      {/* Badge primera edición ⭐ */}
      {isFirstEdition && !placed && (
        <div
          className="absolute z-20 flex items-center justify-center"
          style={{
            top: Math.max(2, w * 0.04),
            right: Math.max(2, w * 0.04),
            fontSize: Math.max(6, w * 0.2),
            lineHeight: 1,
            filter: 'drop-shadow(0 0 3px rgba(251,191,36,0.9))',
          }}
          title="Primera Edición"
        >
          ⭐
        </div>
      )}

      {/* Badge de cantidad */}
      {showQty && (card.availableQty ?? 0) > 1 && !placed && (
        <div className="absolute -top-1.5 -right-1.5 min-w-[18px] h-[18px] px-1 rounded-full bg-emerald-500 text-black font-black italic text-[10px] flex items-center justify-center border-2 border-[#060610] shadow-[0_0_8px_rgba(16,185,129,0.6)] z-10">
          ×{card.availableQty}
        </div>
      )}

      {/* Overlay de lock cuando está placed */}
      {placed && (
        <div
          className="absolute inset-0 bg-black/55 flex items-center justify-center z-10"
          style={{ fontSize: w * 0.4 }}
        >
          <Lock size={w * 0.32} className="text-emerald-400/70" />
        </div>
      )}
    </div>
  );
}