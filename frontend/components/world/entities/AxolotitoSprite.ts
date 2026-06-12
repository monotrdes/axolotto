export interface AxolotitoStats {
  suerte: number;
  ojo: number;
  pila: number;
  sal: number;
}

export interface AxolotitoData {
  id: string;
  name: string;
  level: number;
  energy: number;
  stats: AxolotitoStats;
  state: "idle" | "walking" | "swimming" | "sleeping" | "playing";
  caveIndex: number;
  isEgg: boolean;
  eggProgress?: number;
  skinColor?: string;
  // Variantes visuales por rareza (axolotito.py líneas 11-17).
  gillType?: string;
  eyeType?: string;
  mouthType?: string;
  tailType?: string;
  foreheadType?: string;
  limbType?: string;
}
