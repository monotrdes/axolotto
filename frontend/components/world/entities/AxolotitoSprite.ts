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
  state: "idle" | "walking" | "sleeping" | "playing";
  caveIndex: number;
  isEgg: boolean;
  eggProgress?: number;
  skinColor?: string;
}
