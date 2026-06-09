// ═══════════════════════════════════════════════════════
// CONSTANTS — Santuario
// ═══════════════════════════════════════════════════════
export const traitNames: Record<string, string> = {
  skin_color: 'Piel', gill_type: 'Branquias', eye_type: 'Ojos',
  mouth_type: 'Expresión', tail_type: 'Cola', forehead_type: 'Frente', limb_type: 'Extremidades',
};
export const statNames: Record<string, string> = {
  luck: 'SUERTE ✨', focus: 'OJO 👁️', stamina: 'PILA 🔋', salinity: 'SAL 🧂',
};
export const statColors: Record<string, string> = {
  luck: 'bg-amber-400', focus: 'bg-teal-400', stamina: 'bg-blue-400', salinity: 'bg-red-500',
};

export const rarityColor: Record<string, string> = {
  common:    'text-slate-400 border-slate-600/40 bg-slate-800/60',
  uncommon:  'text-emerald-400 border-emerald-600/40 bg-emerald-950/40',
  rare:      'text-sky-400 border-sky-600/40 bg-sky-950/40',
  epic:      'text-purple-400 border-purple-600/40 bg-purple-950/40',
  legendary: 'text-amber-400 border-amber-500/60 bg-amber-950/40',
};

export function rarityClass(r?: string) {
  return rarityColor[r?.toLowerCase() ?? ''] ?? rarityColor.common;
}
