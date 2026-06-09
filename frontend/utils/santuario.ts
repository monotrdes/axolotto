// ═══════════════════════════════════════════════════════
// PURE HELPERS — Santuario
// ═══════════════════════════════════════════════════════
export function formatCooldown(secs: number): string {
  if (secs <= 0) return 'Listo';
  const h = Math.floor(secs / 3600), m = Math.floor((secs % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

export function obtenerEstiloHuevo(nombre: string) {
  if (nombre?.includes('Génesis'))  return { aura: '#F59E0B', shadow: 'rgba(245,158,11,0.6)' };
  if (nombre?.includes('Fundador')) return { aura: '#9333EA', shadow: 'rgba(147,51,234,0.6)' };
  return { aura: '#E4007C', shadow: 'rgba(228,0,124,0.6)' };
}

export function formatTiempoEscudo(fecha: string): string {
  if (!fecha) return '';
  const dif = new Date(fecha).getTime() - Date.now();
  if (dif <= 0) return '';
  return `${Math.floor(dif / 3_600_000)}h ${Math.floor((dif % 3_600_000) / 60_000)}m`;
}

export function getFrostPhase(calor: number, is_frozen: boolean): 'frozen' | 'freezing' | 'cool' | 'warm' {
  if (is_frozen) return 'frozen';
  if (calor < 25) return 'freezing';
  if (calor < 50) return 'cool';
  return 'warm';
}

export function obtenerFaseHuevo(inc: any): { clase: string; fase: number } {
  const prog = 1 - (inc.horasRestantes || 0) * 3600000 / (7 * 24 * 3600000);
  if (inc.horasRestantes === 0) return { clase: 'animate-bounce', fase: 4 };
  if (prog >= 0.9) return { clase: 'animate-pulse scale-110', fase: 3 };
  if (prog >= 0.6) return { clase: 'animate-pulse', fase: 2 };
  return { clase: 'animate-egg-pulse', fase: 1 };
}
