// AUDIO ASSETS PENDING — this hook provides the interface for future audio implementation.
//
// This hook is designed as a drop-in ready architectural placeholder. Once real audio
// assets are available, add your AudioContext creation in the initializer, load samples
// via fetch/decodeAudioData, and replace each console.log call with the actual playback logic.
//
// Architecture outline for the real implementation:
//   1. Create AudioContext on first user interaction (browser autoplay policy)
//   2. Load audio buffers: ambient tension loop, drumroll, card call SFX, victory/defeat jingles
//   3. Route through a master GainNode for volume control
//   4. Use separate GainNode per bus (ambient, SFX, UI) for crossfade transitions
//   5. setTempo() adjusts AudioContext.playbackRate or schedules BPM-adaptive loops
//   6. Clean up on unmount: stopAll(), close AudioContext

"use client";

import { useCallback, useRef, useState } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface UseAudioTensionOptions {
  /** Enable/disable all audio (default true). When false, all methods are no-ops. */
  enabled?: boolean;
}

export interface UseAudioTensionReturn {
  /**
   * Set the music tempo / urgency speed multiplier.
   * @param speed - 1.0 normal, 1.3 medium urgency, 1.6 high urgency
   *
   * Future implementation:
   * - Adjust AudioContext.playbackRate for ambient loops
   * - Crossfade between different BPM layers
   * - Ramp gain for specific frequency bands
   */
  setTempo: (speed: number) => void;

  /**
   * Play a drumroll / crescendo effect building up to a card reveal.
   *
   * Future implementation:
   * - Trigger a short percussion loop (0.5-3s depending on urgency)
   * - Crossfade with ambient audio using a dedicated SFX gain node
   * - Support multiple simultaneous drumrolls (layered for critical moments)
   */
  playDrumroll: () => void;

  /**
   * Play the card call sound effect for a specific card number.
   * @param cardNumber - The loteria card number (1-54) being called
   *
   * Future implementation:
   * - Look up pre-recorded vocal samples per card number
   * - Fall back to a synthesized tone + reverb if sample not found
   * - Vary pitch slightly per call for organic feel
   */
  playCardCall: (cardNumber: number) => void;

  /**
   * Play the victory fanfare / celebration jingle.
   *
   * Future implementation:
   * - Trigger victory jingle buffer
   * - Optionally layer with crowd cheer SFX
   * - Fade out ambient tension
   */
  playVictory: () => void;

  /**
   * Play the defeat / consolation sound.
   *
   * Future implementation:
   * - Play a descending tone or minor-key sting
   * - Optionally play a "better luck next time" voice line
   */
  playDefeat: () => void;

  /**
   * Stop all audio immediately and reset to silence.
   *
   * Future implementation:
   * - Ramp master gain to 0 over 50ms (avoid pop clicks)
   * - Stop all active AudioBufferSourceNode instances
   * - Reset all bus gains to their default
   */
  stopAll: () => void;

  /**
   * Whether the audio system is initialized and ready to play sounds.
   * Will be true after AudioContext is created and all buffers are decoded.
   * Until then, all playback methods are no-ops.
   */
  isReady: boolean;
}

// ── Hook ──────────────────────────────────────────────────────────────────────

export function useAudioTension(
  options?: UseAudioTensionOptions
): UseAudioTensionReturn {
  const { enabled = true } = options ?? {};
  const [isReady] = useState(false);

  // AudioContext ref — will hold the context once initialized
  const audioCtxRef = useRef<AudioContext | null>(null);

  // Master gain — will route all audio through this node for volume control
  const masterGainRef = useRef<GainNode | null>(null);

  // Future references for per-bus gain nodes:
  // const ambientGainRef = useRef<GainNode | null>(null);
  // const sfxGainRef = useRef<GainNode | null>(null);
  // const musicGainRef = useRef<GainNode | null>(null);

  // Future buffer storage:
  // const buffersRef = useRef<Map<string, AudioBuffer>>(new Map());

  const setTempo = useCallback(
    (speed: number) => {
      if (!enabled) return;
      console.log(`[useAudioTension] setTempo(${speed})`);
      // Future: adjust AudioContext playbackRate or schedule BPM changes
    },
    [enabled]
  );

  const playDrumroll = useCallback(() => {
    if (!enabled) return;
    console.log(`[useAudioTension] playDrumroll()`);
    // Future: play percussion loop with gain envelope
    // const source = audioCtx.createBufferSource();
    // source.buffer = buffersRef.current.get('drumroll');
    // source.connect(sfxGainRef.current!);
    // source.start();
  }, [enabled]);

  const playCardCall = useCallback(
    (cardNumber: number) => {
      if (!enabled) return;
      console.log(`[useAudioTension] playCardCall(${cardNumber})`);
      // Future: play card-specific audio or synthesized tone
      // Pick buffer by cardNumber, or synthesize a tone with OscillatorNode
    },
    [enabled]
  );

  const playVictory = useCallback(() => {
    if (!enabled) return;
    console.log(`[useAudioTension] playVictory()`);
    // Future: play victory fanfare buffer
  }, [enabled]);

  const playDefeat = useCallback(() => {
    if (!enabled) return;
    console.log(`[useAudioTension] playDefeat()`);
    // Future: play defeat sound buffer
  }, [enabled]);

  const stopAll = useCallback(() => {
    console.log(`[useAudioTension] stopAll()`);
    // Future: ramp master gain to 0 over ~50ms, stop all source nodes
    // masterGainRef.current?.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.05);
  }, []);

  return {
    setTempo,
    playDrumroll,
    playCardCall,
    playVictory,
    playDefeat,
    stopAll,
    isReady,
  };
}
