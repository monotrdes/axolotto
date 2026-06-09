/**
 * TutorialScript.ts — Master script for the Axolotto tutorial.
 *
 * Add, remove, or reorder acts by editing TUTORIAL_SCRIPT.
 * Each act is a self-contained component; the orchestrator (TutorialFlow)
 * just renders TUTORIAL_SCRIPT[actIndex] and advances on onComplete().
 *
 * Backend phase → resume act mapping:
 *   phase 0 (fresh)  → act index 0  (start from beginning)
 *   phase 1          → act index 4  (Game SAL)
 *   phase 2          → act index 5  (Game OJO)
 *   phase 3          → act index 6  (Game SUERTE+PILA)
 *   phase 4          → act index 7  (Karma reveal)
 */

export type Nature = "lucky" | "salty" | "hyperactive" | "methodical" | "shy";
export type ActType =
  | "dialogue-scene"
  | "stat-reveal"
  | "board-preview"
  | "game"
  | "karma-reveal"
  | "hatching"
  | "treasure-chest"
  | "world-intro";

export type StatFocus = "SAL" | "OJO" | "SUERTE_PILA";

export interface ActGameData {
  statFocus: StatFocus;
  backendPhase: 1 | 2 | 3;
}

export interface WebitoData {
  tutorialId: number;
  nature: Nature;
  bonusLuck: number;
  bonusFocus: number;
  bonusStamina: number;
  bonusSalinityAdj: number;
  baseStatLuck: number;
  baseStatFocus: number;
  baseStatStamina: number;
  baseStatSalinity: number;
  token: string | null;
  userId: string;
  karma: "lucky" | "salty" | null;
}

export interface TutorialContext {
  hasPendingReward: boolean;
}

export interface TutorialAct {
  id: string;
  type: ActType;
  data?: ActGameData;
  /** If condition returns false, the act is skipped. Receives full context. */
  condition?: (ctx: TutorialContext) => boolean;
}

export const TUTORIAL_SCRIPT: TutorialAct[] = [
  { id: "acto-1-presentacion",  type: "dialogue-scene" },
  { id: "acto-2-adn",           type: "stat-reveal" },
  { id: "acto-3-tabla",         type: "board-preview" },
  { id: "acto-4-pacto",         type: "dialogue-scene" },
  { id: "acto-5-sal",           type: "game", data: { statFocus: "SAL",        backendPhase: 1 } },
  { id: "acto-6-ojo",           type: "game", data: { statFocus: "OJO",        backendPhase: 2 } },
  { id: "acto-7-suerte-pila",   type: "game", data: { statFocus: "SUERTE_PILA", backendPhase: 3 } },
  { id: "acto-8-karma",         type: "karma-reveal" },
  { id: "acto-9-nace",          type: "hatching" },
  { id: "acto-10-cofre",        type: "treasure-chest", condition: (ctx) => ctx.hasPendingReward === true },
  { id: "acto-11-mundo",        type: "world-intro" },
];

/** Maps a backend phase number to the act index where tutorial should resume. */
export function resumeActIndex(phase: number): number {
  if (phase <= 0) return 0;
  if (phase === 1) return 4;  // Game SAL
  if (phase === 2) return 5;  // Game OJO
  if (phase === 3) return 6;  // Game SUERTE+PILA
  if (phase === 4) return 7;  // Karma reveal
  return 0;
}

