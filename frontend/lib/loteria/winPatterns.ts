/**
 * Espejo cliente de los patrones de victoria del backend
 * (backend/app/services/game_logic.py — mantener sincronizados).
 * Usado por la Mesa de Competencia para el escalado dinámico de tablillas
 * (plan task-84 §5): cuántas cartas le faltan a cada jugador para ganar.
 *
 * Tablero 4×4, índices 0-15. Nombres de patrón = los de room_config
 * (multiplayer.py valid_patterns).
 */

const LINES: number[][] = [
  [0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15], // filas
  [0, 4, 8, 12], [1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15], // columnas
  [0, 5, 10, 15], [3, 6, 9, 12], // diagonales
];

const CUADRITOS: number[][] = [
  [0, 1, 4, 5], [1, 2, 5, 6], [2, 3, 6, 7],
  [4, 5, 8, 9], [5, 6, 9, 10], [6, 7, 10, 11],
  [8, 9, 12, 13], [9, 10, 13, 14], [10, 11, 14, 15],
];

const POCITO: number[][] = [[5, 6, 9, 10]];
const ESQUINAS: number[][] = [[0, 3, 12, 15]];
const CRUZ_DIAGONAL: number[][] = [[0, 3, 5, 6, 9, 10, 12, 15]];

const L_SHAPES: number[][] = [
  [0, 1, 2, 3, 4, 8, 12],
  [0, 1, 2, 3, 7, 11, 15],
  [0, 4, 8, 12, 13, 14, 15],
  [3, 7, 11, 12, 13, 14, 15],
];

const Z_SHAPES: number[][] = [
  [0, 1, 2, 3, 6, 9, 12, 13, 14, 15],
  [0, 1, 2, 3, 5, 10, 12, 13, 14, 15],
];

// Cruz recta: cualquier fila completa + cualquier columna completa (unión de 7 celdas).
const CRUZ: number[][] = (() => {
  const rows = LINES.slice(0, 4);
  const cols = LINES.slice(4, 8);
  const out: number[][] = [];
  for (const r of rows) for (const c of cols) out.push([...new Set([...r, ...c])]);
  return out;
})();

const FULL_BOARD: number[][] = [Array.from({ length: 16 }, (_, i) => i)];

const PATTERN_SETS: Record<string, number[][]> = {
  line: LINES,
  cuadrito: CUADRITOS,
  pocito: POCITO,
  esquinas: ESQUINAS,
  cruz: CRUZ,
  cruz_diagonal: CRUZ_DIAGONAL,
  l_shape: L_SHAPES,
  z_shape: Z_SHAPES,
  full_board: FULL_BOARD,
};

/**
 * Mínimo de cartas que faltan para completar ALGÚN patrón activo de la sala.
 * 0 = ya ganó. Si no se reconoce ningún patrón, usa line+cuadrito (default
 * del backend).
 */
export function cartasFaltantes(
  marked: Iterable<number>,
  winPatterns: string[] = ["line", "cuadrito"],
): number {
  const markedSet = new Set(marked);
  let min = Infinity;
  let any = false;
  for (const name of winPatterns) {
    const sets = PATTERN_SETS[name];
    if (!sets) continue;
    any = true;
    for (const cells of sets) {
      let missing = 0;
      for (const cell of cells) if (!markedSet.has(cell)) missing++;
      if (missing < min) min = missing;
      if (min === 0) return 0;
    }
  }
  if (!any) return cartasFaltantes(markedSet, ["line", "cuadrito"]);
  return min === Infinity ? 16 : min;
}

/** Escalado de tablilla por tensión (plan §5). */
export interface TablillaTension {
  scale: number;
  opacity: number;
  /** 1-2 cartas faltantes: borde dorado pulsante + chispas + CasiCanto. */
  matchPoint: boolean;
}

export function tablillaTension(faltantes: number): TablillaTension {
  if (faltantes <= 2) return { scale: 1.4, opacity: 1, matchPoint: true };
  if (faltantes <= 8) return { scale: 1.0, opacity: 1, matchPoint: false };
  return { scale: 0.6, opacity: 0.5, matchPoint: false };
}
