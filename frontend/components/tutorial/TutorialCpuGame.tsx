"use client";

/**
 * TutorialCpuGame
 *
 * Wraps CpuSimScreen with a tutorial overlay layer.
 * The real game runs underneath; the overlay handles:
 *   - Phase-intro dialogues from the Webito
 *   - Manual interaction moments (Phase 2 distraction fix, Phase 3 Cheat Astral)
 *   - Game result dialogues
 *
 * CpuSimScreen calls its own backend endpoints (game/play), so the tutorial
 * uses a real game API call. For the tutorial "room" we use 'rookie'.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import CpuSimScreen from '@/components/screens/CpuSimScreen';
import WebitoDialogue from './WebitoDialogue';
import { getTutorialDialogue, type Nature } from './dialogues';

// ── Types ──────────────────────────────────────────────────────────────────────

export interface TutorialCpuGameProps {
  incubationId: number;
  userId: string;
  token: string | null;
  // Bonus stats accumulated during egg care (0-100)
  bonusFocus: number;
  bonusLuck: number;
  bonusAgility: number;
  bonusStamina: number;
  bonusSalinity: number;
  // Inferred personality from egg DNA
  inferredNature: Nature;
  // Which tutorial game this is (1, 2, or 3)
  tutorialPhase: 1 | 2 | 3;
  // The player's axolotito to use for the tutorial game
  selectedAxo: Record<string, unknown>;
  // The board to play with — needs at least { id, card_ids }
  selectedBoardId: number;
  playerBoards: Record<string, unknown>[];
  allCards: Record<string, unknown>[];
  onPhaseComplete: (phase: number) => void;
  onTutorialComplete: (karma: "lucky" | "salty") => void;
}

// ── Component ──────────────────────────────────────────────────────────────────

export function TutorialCpuGame({
  userId,
  token,
  bonusFocus,
  bonusLuck,
  inferredNature,
  tutorialPhase,
  selectedAxo,
  selectedBoardId,
  playerBoards,
  allCards,
  onPhaseComplete,
  onTutorialComplete,
}: TutorialCpuGameProps) {
  // ── Dialogue state ───────────────────────────────────────────────────────────
  const [dialogueText, setDialogueText]       = useState<string>("");
  const [showDialogue, setShowDialogue]       = useState(false);
  const [gameKey, setGameKey]                 = useState(0);

  // Phase 2 — distraction interaction
  const [awaitingDistraction, setAwaitingDistraction] = useState(false);
  const distractionTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Track whether the phase result outro has been shown
  const resultHandledRef = useRef(false);
  // Whether we've shown a result dialogue (to avoid double-showing)
  const [resultDialogueShown, setResultDialogueShown] = useState(false);

  // ── Show intro dialogue on mount ─────────────────────────────────────────────
  useEffect(() => {
    const intro = getTutorialDialogue(tutorialPhase, inferredNature, "phase_start");
    setDialogueText(intro);
    setShowDialogue(true);

    // Phase 2: schedule distraction check after ~5 cards (~2.5s after game visually starts)
    if (tutorialPhase === 2 && bonusFocus < 50) {
      distractionTimerRef.current = setTimeout(() => {
        setAwaitingDistraction(true);
        const distractText = getTutorialDialogue(2, inferredNature, "distracted");
        setDialogueText(distractText);
        setShowDialogue(true);
      }, 5000); // 5s — enough for intro dialogue + ~5 cards at 420ms each
    }

    if (tutorialPhase === 2 && bonusFocus >= 50) {
      // High focus — show boast after a short delay
      setTimeout(() => {
        const boastText = getTutorialDialogue(2, inferredNature, "focus_boost");
        setDialogueText(boastText);
        setShowDialogue(true);
      }, 4500);
    }

    return () => {
      if (distractionTimerRef.current) clearTimeout(distractionTimerRef.current);
    };
  // Run only when phase/nature change — not on every render
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tutorialPhase, inferredNature]);

  // ── CpuSimScreen callbacks ───────────────────────────────────────────────────

  // onDone fires once the backend result is fetched (before animation ends).
  // We use it to clear blocking states and show the outcome intro dialogue.
  // CpuSimScreen does not expose win/loss directly; we show a generic result
  // dialogue here and let the player read the CpuSimScreen result screen.
  const handleDone = useCallback(() => {
    setAwaitingDistraction(false);
    // Show a result dialogue after the game finishes, once per phase
    if (!resultDialogueShown) {
      setResultDialogueShown(true);
      // Brief delay so the game's own result overlay has a moment to appear
      setTimeout(() => {
        // We default to "phase_win" dialogue; CpuSimScreen shows the real result.
        // The Webito cheers regardless — the player sees the true outcome on screen.
        const outroText = getTutorialDialogue(tutorialPhase, inferredNature, "phase_win");
        setDialogueText(outroText);
        setShowDialogue(true);
      }, 2200);
    }
  }, [resultDialogueShown, tutorialPhase, inferredNature]);

  // When any post-game action button is pressed, advance the tutorial phase.
  const finishPhase = useCallback(() => {
    if (resultHandledRef.current) return;
    resultHandledRef.current = true;
    onPhaseComplete(tutorialPhase);
  }, [tutorialPhase, onPhaseComplete]);

  const handlePlayAgain = useCallback(() => {
    finishPhase();
    setGameKey(k => k + 1);
    resultHandledRef.current = false;
    setResultDialogueShown(false);
  }, [finishPhase]);

  const handleChangeBoard = useCallback(() => {
    finishPhase();
  }, [finishPhase]);

  const handleChangeAll = useCallback(() => {
    finishPhase();
  }, [finishPhase]);

  // ── Dismiss dialogue ─────────────────────────────────────────────────────────
  const dismissDialogue = useCallback(() => {
    setShowDialogue(false);
    // If distraction is awaiting and player dismissed, unblock the game
    if (awaitingDistraction) {
      setAwaitingDistraction(false);
    }
  }, [awaitingDistraction]);

  // ── Whether game controls are blocked ────────────────────────────────────────
  // Block interaction when showing a blocking dialogue
  const isBlocking = awaitingDistraction;

  return (
    <div className="relative">
      {/* ── CpuSimScreen — game runs underneath ───────────────────────────── */}
      <div
        style={{
          opacity: isBlocking ? 0.45 : 1,
          pointerEvents: isBlocking ? "none" : "auto",
          transition: "opacity 0.3s ease",
        }}
      >
        <CpuSimScreen
          key={gameKey}
          userId={userId}
          token={token}
          selectedAxo={selectedAxo}
          selectedBoardId={selectedBoardId}
          playerBoards={playerBoards}
          allCards={allCards}
          selectedRoom="rookie"
          onPlayAgainInPlace={handlePlayAgain}
          onChangeBoard={handleChangeBoard}
          onChangeAll={handleChangeAll}
          onDone={handleDone}
        />
      </div>

      {/* ── Tutorial overlay — dialogue bubble at bottom of game area ─────── */}
      {showDialogue && (
        <div
          className="absolute bottom-0 left-0 right-0 z-50 px-3 pb-3"
          onClick={(e) => e.stopPropagation()}
        >
          <WebitoDialogue
            text={dialogueText}
            speaker="webito"
            onDismiss={dismissDialogue}
          />
        </div>
      )}

      {/* ── Phase 2: highlighted "tap this card" instruction ──────────────── */}
      {awaitingDistraction && (
        <div
          className="absolute top-2 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-full text-[11px] font-black uppercase tracking-widest animate-pulse"
          style={{
            background: "rgba(6,6,20,0.9)",
            border: "2px solid #f97316",
            color: "#f97316",
            boxShadow: "0 0 16px rgba(249,115,22,0.5)",
          }}
        >
          Toca la carta resaltada para continuar
        </div>
      )}

    </div>
  );
}

export default TutorialCpuGame;
