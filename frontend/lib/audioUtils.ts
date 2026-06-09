"use client";

// Module-level lazy AudioContext singleton (browsers cap concurrent contexts)
let _ctx: AudioContext | null = null;

function getCtx(): AudioContext | null {
  if (typeof window === "undefined") return null;
  if (!_ctx) {
    try {
      _ctx = new AudioContext();
    } catch {
      return null;
    }
  }
  return _ctx;
}

function playNote(
  ctx: AudioContext,
  freq: number,
  startTime: number,
  duration: number,
  gainPeak = 0.25,
  type: OscillatorType = "sine"
) {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();

  osc.type = type;
  osc.frequency.setValueAtTime(freq, startTime);

  gain.gain.setValueAtTime(0, startTime);
  gain.gain.linearRampToValueAtTime(gainPeak, startTime + 0.01);
  gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

  osc.connect(gain);
  gain.connect(ctx.destination);

  osc.start(startTime);
  osc.stop(startTime + duration + 0.05);
}

/**
 * Ascending arpeggio do-mi-sol (~300ms).
 * Safe to call even if AudioContext is suspended — silently no-ops.
 */
export function playGainSound(): void {
  const ctx = getCtx();
  if (!ctx || ctx.state !== "running") return;

  const now = ctx.currentTime;
  // do-mi-sol in C4 (261.63, 329.63, 392.00)
  playNote(ctx, 261.63, now,        0.12, 0.2);
  playNote(ctx, 329.63, now + 0.10, 0.12, 0.22);
  playNote(ctx, 392.00, now + 0.20, 0.16, 0.25);
}

/**
 * Descending sol-mi-do (~300ms).
 */
export function playLossSound(): void {
  const ctx = getCtx();
  if (!ctx || ctx.state !== "running") return;

  const now = ctx.currentTime;
  playNote(ctx, 392.00, now,        0.12, 0.2,  "sawtooth");
  playNote(ctx, 329.63, now + 0.10, 0.12, 0.18, "sawtooth");
  playNote(ctx, 261.63, now + 0.20, 0.18, 0.15, "sawtooth");
}

/**
 * Single ding at 440 Hz (~150ms).
 */
export function playPurchaseSound(): void {
  const ctx = getCtx();
  if (!ctx || ctx.state !== "running") return;

  const now = ctx.currentTime;
  playNote(ctx, 440, now, 0.15, 0.3, "sine");
}

/**
 * 4-note chord (~500ms) — uses C major 7 (C4, E4, G4, B4).
 */
export function playLegendarySound(): void {
  const ctx = getCtx();
  if (!ctx || ctx.state !== "running") return;

  const now = ctx.currentTime;
  playNote(ctx, 261.63, now,        0.5, 0.35, "sine");
  playNote(ctx, 329.63, now + 0.05, 0.5, 0.35, "sine");
  playNote(ctx, 392.00, now + 0.10, 0.5, 0.35, "sine");
  playNote(ctx, 493.88, now + 0.15, 0.5, 0.35, "sine");
}
