/**
 * Puente de eventos mundo↔React. El mundo Pixi emite, React escucha (y viceversa)
 * sin acoplar el game loop a la reconciliación de React. (plan task-84 §3.1)
 */

export interface WorldEvents {
  /** El usuario tocó un hotspot del diorama (puesto, mesa, nido...). */
  hotspot: { kind: string; id?: string };
  /** Cambio de zona completado (la cámara ya está en el encuadre final). */
  zoneSettled: { macro: string; sub?: string };
  /** Reporte de calidad medida (para telemetría/ajuste de tier). */
  perf: { fps: number };
}

type Listener<K extends keyof WorldEvents> = (payload: WorldEvents[K]) => void;

export class WorldBridge {
  // Map interno sin genéricos; el tipado fuerte vive en la firma pública.
  private listeners = new Map<keyof WorldEvents, Set<(payload: never) => void>>();

  on<K extends keyof WorldEvents>(event: K, fn: Listener<K>): () => void {
    let set = this.listeners.get(event);
    if (!set) {
      set = new Set();
      this.listeners.set(event, set);
    }
    set.add(fn as (payload: never) => void);
    return () => set!.delete(fn as (payload: never) => void);
  }

  emit<K extends keyof WorldEvents>(event: K, payload: WorldEvents[K]): void {
    this.listeners.get(event)?.forEach((fn) => (fn as Listener<K>)(payload));
  }

  clear(): void {
    this.listeners.clear();
  }
}
