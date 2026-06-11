"use client";

import React, { useState, useEffect } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface HotBoardOverlayProps {
  children: React.ReactNode;
  isHot: boolean;
  /** Glow color tier */
  hotLevel: "emerald" | "indigo" | "gold";
  /** 0-100 threat percentage */
  threatPercent: number;
  /** Axolotito display name */
  axoName: string;
  /** Board just won */
  isWinner?: boolean;
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function HotBoardOverlay({
  children,
  isHot,
  hotLevel,
  threatPercent,
  axoName,
  isWinner = false,
}: HotBoardOverlayProps) {
  const [animationPhase, setAnimationPhase] = useState<
    "idle" | "enter" | "float"
  >("idle");

  // Smooth entry: first apply CSS transition for 400ms, then switch to animation
  useEffect(() => {
    if (isHot) {
      setAnimationPhase("enter");
      const t = setTimeout(() => setAnimationPhase("float"), 400);
      return () => clearTimeout(t);
    } else {
      setAnimationPhase("idle");
    }
  }, [isHot]);

  // Not hot: render children directly (no wrapper — keeps backward compat)
  if (!isHot || animationPhase === "idle") {
    return <>{children}</>;
  }

  const effectiveLevel = isWinner ? "gold" : hotLevel;

  const glowClass =
    effectiveLevel === "emerald"
      ? "animate-glow-emerald"
      : effectiveLevel === "indigo"
        ? "animate-glow-indigo"
        : "animate-glow-gold";

  const glowColor =
    effectiveLevel === "emerald"
      ? "rgba(45,212,191,0.22)"
      : effectiveLevel === "indigo"
        ? "rgba(228,0,124,0.25)"
        : "rgba(245,158,11,0.35)";

  // ── Shared inner content (aura + droplets + sparkles + children) ──────────

  const inner = (
    <>
      {/* Aura background glow */}
      <div
        className="absolute inset-0 rounded-2xl pointer-events-none z-0"
        style={{
          background: `radial-gradient(circle, ${glowColor} 0%, transparent 70%)`,
        }}
      />

      {/* ── Winner sparkles (intense confetti) ───────────────────────────── */}
      {isWinner && (
        <>
          <div
            className="absolute -top-2 -left-2 w-2 h-2 rounded-full bg-yellow-300 animate-sparkle-float"
            style={{ animationDelay: "0s", animationDuration: "1.5s" }}
          />
          <div
            className="absolute -top-1 right-0 w-1.5 h-1.5 rounded-full bg-yellow-400 animate-sparkle-float"
            style={{ animationDelay: "0.3s", animationDuration: "1.8s" }}
          />
          <div
            className="absolute bottom-0 -right-2 w-2 h-2 rounded-full bg-amber-300 animate-sparkle-float"
            style={{ animationDelay: "0.6s", animationDuration: "2s" }}
          />
        </>
      )}

      {/* ── Gold-level sparkles ──────────────────────────────────────────── */}
      {!isWinner && effectiveLevel === "gold" && (
        <>
          <div
            className="absolute -top-1 left-1/3 w-1 h-1 rounded-full bg-yellow-300 animate-sparkle-float"
            style={{ animationDelay: "0.1s" }}
          />
          <div
            className="absolute -top-1 right-1/4 w-1.5 h-1.5 rounded-full bg-amber-400 animate-sparkle-float"
            style={{ animationDelay: "0.5s" }}
          />
          <div
            className="absolute -bottom-1 left-1/2 w-1 h-1 rounded-full bg-yellow-200 animate-sparkle-float"
            style={{ animationDelay: "0.9s" }}
          />
        </>
      )}

      {/* ── Water droplets (2-3 falling upward from levitating board) ────── */}
      <div
        className="absolute -bottom-1 left-1/4 w-1 h-1 rounded-full bg-cyan-400/60 animate-droplet-rise"
        style={{ animationDelay: "0.2s" }}
      />
      <div
        className="absolute -bottom-1 left-2/3 w-1.5 h-1.5 rounded-full bg-sky-400/50 animate-droplet-rise"
        style={{ animationDelay: "0.7s" }}
      />
      <div
        className="absolute -bottom-1 left-1/2 w-1 h-1 rounded-full bg-cyan-300/40 animate-droplet-rise"
        style={{ animationDelay: "1.2s" }}
      />

      {children}
    </>
  );

  // ── ENTER phase: smooth CSS transition (0.4s ease-out) ────────────────────
  if (animationPhase === "enter") {
    return (
      <div
        className="relative inline-block transition-[transform] duration-[400ms] ease-out"
        style={{
          transform: "translateY(-12px) scale(1.5)",
        }}
        aria-label={`${axoName} - tablero caliente (${threatPercent}%)`}
      >
        {inner}
      </div>
    );
  }

  // ── FLOAT phase: continuous levitate animation + glow pulse ───────────────
  return (
    <div
      className={`relative inline-block animate-levitate ${glowClass}`}
      aria-label={`${axoName} - tablero caliente (${threatPercent}%)`}
    >
      {inner}
    </div>
  );
}
