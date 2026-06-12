"use client";

/**
 * TutorialFlow — Script orchestrator.
 *
 * Renders TUTORIAL_SCRIPT[actIndex] and advances on onComplete().
 * Each act is self-contained; adding, removing, or reordering acts
 * only requires editing TUTORIAL_SCRIPT in TutorialScript.ts.
 *
 * State is minimal: actIndex + webitoData (received from start_tutorial).
 */

import React, { useState, useCallback, useEffect, useRef } from "react";
import { usePrivy } from "@privy-io/react-auth";

import {
  TUTORIAL_SCRIPT,
  resumeActIndex,
  type WebitoData,
  type Nature,
} from "./TutorialScript";

import ActDialogueScene, { type DialogueSceneId } from "./acts/ActDialogueScene";
import ActStatReveal    from "./acts/ActStatReveal";
import ActBoardPreview  from "./acts/ActBoardPreview";
import ActGame          from "./acts/ActGame";
import ActKarmaReveal   from "./acts/ActKarmaReveal";
import ActHatching      from "./acts/ActHatching";
import ActTreasureChest from "./acts/ActTreasureChest";
import ActWorldIntro    from "./acts/ActWorldIntro";

import { API_BASE } from "@/lib/api";

export interface TutorialFlowProps {
  userId: string;
  token: string | null;
  hasPendingReward?: boolean;
  onComplete: (karma?: "lucky" | "salty", axoName?: string) => void;
}

// Keyframes injected once for hatching / karma screens
let extraStylesInjected = false;
function injectExtraStyles() {
  if (typeof document === "undefined" || extraStylesInjected) return;
  extraStylesInjected = true;
  const style = document.createElement("style");
  style.textContent = `
    @keyframes egg-hatch-burst {
      0%   { transform: scale(1);    opacity: 1; }
      40%  { transform: scale(1.35); opacity: 1; }
      70%  { transform: scale(0.85); opacity: 0.85; }
      85%  { transform: scale(1.15); opacity: 0.6; }
      100% { transform: scale(0);    opacity: 0; }
    }
    @keyframes axolotito-appear {
      0%   { transform: scale(0.4) translateY(20px); opacity: 0; }
      60%  { transform: scale(1.1) translateY(-4px);  opacity: 1; }
      100% { transform: scale(1)   translateY(0);     opacity: 1; }
    }
    @keyframes karma-appear {
      from { transform: scale(0.85) translateY(16px); opacity: 0; }
      to   { transform: scale(1)    translateY(0);    opacity: 1; }
    }
    @keyframes fade-in-up {
      from { transform: translateX(-50%) translateY(40px); opacity: 0; }
      to   { transform: translateX(-50%) translateY(0);    opacity: 1; }
    }
    @keyframes chest-open {
      0%   { transform: scale(1.1); }
      30%  { transform: scale(1.4); }
      60%  { transform: scale(0.9); }
      100% { transform: scale(1); }
    }
    @keyframes particle-float {
      from { transform: translateY(0) scale(1); opacity: 1; }
      to   { transform: translateY(-60px) scale(0); opacity: 0; }
    }
    @keyframes banner-shrink-out {
      0%   { transform: translateX(-50%) scale(1);   opacity: 1; }
      100% { transform: translateX(-50%) scale(0.3); opacity: 0; }
    }
    @keyframes badge-pop-in {
      0%   { transform: scale(0);   opacity: 0; }
      60%  { transform: scale(1.25); opacity: 1; }
      100% { transform: scale(1);    opacity: 1; }
    }
    @keyframes badge-glow {
      0%, 100% { box-shadow: 0 0 6px rgba(234,179,8,0.3), 0 0 12px rgba(234,179,8,0.15); }
      50%      { box-shadow: 0 0 12px rgba(234,179,8,0.5), 0 0 24px rgba(234,179,8,0.25); }
    }
    @keyframes badge-float {
      0%, 100% { transform: translateY(0); }
      50%      { transform: translateY(-3px); }
    }
  `;
  document.head.appendChild(style);
}

export function TutorialFlow({ userId, token, hasPendingReward, onComplete }: TutorialFlowProps) {
  const { getAccessToken, authenticated } = usePrivy();

  const [actIndex, setActIndex] = useState<number | null>(null); // null = loading
  const [webito, setWebito]     = useState<WebitoData | null>(null);
  const [loading, setLoading]   = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);
  const [refreshCount, setRefreshCount] = useState(0);
  const startedRef              = useRef(false);
  const completedRef            = useRef(false);
  const axoNameRef              = useRef<string | undefined>(undefined);
  const [bannerCollapsed, setBannerCollapsed] = useState(false);
  const bannerTimerRef          = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [rewardClaimed, setRewardClaimed] = useState(false);

  useEffect(() => {
    injectExtraStyles();
  }, []);

  // ── Banner auto-collapse: full message → small badge after 5 seconds ──────
  useEffect(() => {
    if (!hasPendingReward) return;
    bannerTimerRef.current = setTimeout(() => {
      setBannerCollapsed(true);
    }, 5000);
    return () => {
      if (bannerTimerRef.current) clearTimeout(bannerTimerRef.current);
    };
  }, [hasPendingReward]);

  // Expand banner again on hover/click, auto-collapse after 3s
  const expandBanner = useCallback(() => {
    setBannerCollapsed(false);
    if (bannerTimerRef.current) clearTimeout(bannerTimerRef.current);
    bannerTimerRef.current = setTimeout(() => {
      setBannerCollapsed(true);
    }, 3000);
  }, []);

  // ── Init: call start_tutorial to get tutorial id + stats ─────────────────────
  useEffect(() => {
    if (!authenticated || startedRef.current) return;
    startedRef.current = true;

    const init = async () => {
      try {
        const t = token ?? (authenticated ? await getAccessToken() : null);
        const headers: Record<string, string> = { "Content-Type": "application/json" };
        if (t) headers["Authorization"] = `Bearer ${t}`;

        const res = await fetch(`${API_BASE}/tutorial/start`, {
          method: "POST",
          headers,
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail ?? `Error ${res.status}`);
        }

        const data = await res.json();
        console.log("[TutorialFlow] start_tutorial response:", data);

        const nature = (data.inferred_nature ?? "salty") as Nature;
        const tutorialId = data.id ?? data.tutorial_id ?? 0;
        const phase = data.phase ?? 0;
        const freshStart = data.fresh_start === true;

        // Checkpoint: use tutorial_act_index if present, fallback to resumeActIndex(phase)
        const startAct = freshStart ? 0 : (data.tutorial_act_index ?? resumeActIndex(phase));
        console.log(`[TutorialFlow] phase=${phase} fresh_start=${freshStart} tutorial_act_index=${data.tutorial_act_index} → starting at act ${startAct} (${TUTORIAL_SCRIPT[startAct]?.id})`);

        if (startAct === 0 && !freshStart) {
          const savedCount = localStorage.getItem("axolotto_tutorial_refresh_count");
          const count = savedCount ? parseInt(savedCount, 10) : 0;
          const newCount = count + 1;
          localStorage.setItem("axolotto_tutorial_refresh_count", newCount.toString());
          setRefreshCount(newCount);
        } else if (startAct > 0) {
          localStorage.removeItem("axolotto_tutorial_refresh_count");
        }

        const webitoData: WebitoData = {
          tutorialId,
          nature,
          bonusLuck:         data.bonus_luck          ?? 50,
          bonusFocus:        data.bonus_focus         ?? 50,
          bonusStamina:      data.bonus_stamina       ?? 100,
          bonusSalinityAdj:  data.bonus_salinity_adj  ?? 25,
          baseStatLuck:      data.base_stat_luck      ?? 0,
          baseStatFocus:     data.base_stat_focus     ?? 0,
          baseStatStamina:   data.base_stat_stamina   ?? 0,
          baseStatSalinity:  data.base_stat_salinity  ?? 0,
          token: t,
          userId,
          karma: null,
        };

        setWebito(webitoData);
        setActIndex(startAct);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Error iniciando tutorial";
        setApiError(msg);
      } finally {
        setLoading(false);
      }
    };

    init();
  }, [authenticated, token, userId, getAccessToken]);

  // ── Update webito stats mid-tutorial (e.g. after SAL game persists bonus_stamina) ──
  const updateWebitoStats = useCallback((updates: Partial<WebitoData>) => {
    setWebito(prev => prev ? { ...prev, ...updates } : prev);
  }, []);

  // ── Persist tutorial act progress to backend ─────────────────────────────────
  const saveActIndex = useCallback(async (index: number) => {
    if (!webito || !webito.tutorialId) return;
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (webito.token) headers["Authorization"] = `Bearer ${webito.token}`;

      const res = await fetch(`${API_BASE}/tutorial/save-act/${webito.tutorialId}`, {
        method: "POST",
        headers,
        body: JSON.stringify({ act_index: index }),
      });
      if (!res.ok) {
        console.error(`[TutorialFlow] save-act index=${index} falló: ${res.status}`);
      } else {
        console.log(`[TutorialFlow] Guardado act_index=${index} en servidor`);
      }
    } catch (e) {
      console.error("[TutorialFlow] Error guardando act_index:", e);
    }
  }, [webito]);

  // ── Advance to next act ───────────────────────────────────────────────────────
  // axoName se propaga desde el acto de eclosión (ActHatching) hasta onComplete.
  const advance = useCallback((karmaOrNothing?: "lucky" | "salty", axoName?: string) => {
    if (karmaOrNothing) {
      setWebito(prev => prev ? { ...prev, karma: karmaOrNothing } : prev);
    }
    // El nombre llega en el acto de eclosión, pero onComplete dispara tras world-intro.
    // Lo guardamos en un ref para no perderlo entre actos.
    if (axoName) axoNameRef.current = axoName;
    setActIndex(prev => {
      if (prev === null) return 0;
      const nextIndex = prev + 1;
      saveActIndex(nextIndex);
      return nextIndex;
    });
  }, [saveActIndex]);

  // Clear refresh count when advancing past Act 0
  useEffect(() => {
    if (actIndex !== null && actIndex > 0) {
      localStorage.removeItem("axolotto_tutorial_refresh_count");
    }
  }, [actIndex]);

  // Auto-skip acts whose condition returns false
  useEffect(() => {
    if (actIndex === null || !webito || completedRef.current) return;
    const ctx = { hasPendingReward: hasPendingReward ?? false };
    let idx = actIndex;
    while (idx < TUTORIAL_SCRIPT.length) {
      const act = TUTORIAL_SCRIPT[idx];
      if (!act.condition || act.condition(ctx)) break;
      console.log(`[TutorialFlow] skip: ${act.id} (condition=false) → siguiente`);
      idx++;
    }
    if (idx >= TUTORIAL_SCRIPT.length) {
      console.log("[TutorialFlow] Tutorial COMPLETO → onComplete()");
      completedRef.current = true;
      setTimeout(() => onComplete(webito.karma ?? undefined, axoNameRef.current), 50);
      return;
    }
    if (idx !== actIndex) {
      setActIndex(idx);
      saveActIndex(idx);
    }
  }, [actIndex, webito, hasPendingReward, onComplete, saveActIndex]);

  // ── finalize trigger: when advance pushes past end ─────────────────────────────
  useEffect(() => {
    if (actIndex !== null && actIndex >= TUTORIAL_SCRIPT.length && !completedRef.current) {
      console.log("[TutorialFlow] actIndex superó longitud → onComplete()");
      completedRef.current = true;
      setTimeout(() => onComplete(undefined, axoNameRef.current), 50);
    }
  }, [actIndex, onComplete]);

  // ── Loading ───────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-20">
        <div className="text-[64px] animate-pulse">🥚</div>
        <p className="text-sm font-bold animate-pulse" style={{ color: "#00e5ff" }}>
          Despertando al Webito...
        </p>
      </div>
    );
  }

  if (apiError) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-20 text-center px-4">
        <p className="text-[48px]">😵</p>
        <p className="text-rose-400 text-sm font-bold">{apiError}</p>
        <button
          onClick={() => { startedRef.current = false; setLoading(true); setApiError(null); }}
          className="px-6 py-2 rounded-xl text-sm font-bold border border-rose-500/30 text-rose-400 hover:bg-rose-500/10 transition-colors"
        >
          Reintentar
        </button>
      </div>
    );
  }

  if (actIndex === null || !webito) return null;

  const currentAct = TUTORIAL_SCRIPT[actIndex];
  console.log(`[TutorialFlow] render: actIndex=${actIndex} act=${currentAct?.id} type=${currentAct?.type}`);
  if (!currentAct) {
    console.log("[TutorialFlow] actIndex fuera de rango → onComplete");
    onComplete(webito.karma ?? undefined);
    return null;
  }

  // ── Render current act ────────────────────────────────────────────────────────
  const energyBefore =
    currentAct.id === "acto-5-sal"         ? 0 :
    currentAct.id === "acto-6-ojo"         ? 1 :
    currentAct.id === "acto-7-suerte-pila" ? 2 : 0;

  return (
    <div className="w-full">
      {/* 🎁 Corcholata prize indicator — full banner → shrinks to badge */}
      {hasPendingReward && !rewardClaimed && (
        <>
          {/* Full banner — fades out when collapsed */}
          <div
            className="fixed bottom-6 left-1/2 z-50 rounded-full px-6 py-2.5 shadow-lg backdrop-blur-md border border-yellow-500/30 cursor-pointer"
            style={{
              transform: "translateX(-50%)",
              background: "rgba(234,179,8,0.1)",
              animation: bannerCollapsed
                ? "banner-shrink-out 0.5s ease-in forwards"
                : "fade-in-up 0.5s ease-out 0.5s both",
              pointerEvents: bannerCollapsed ? "none" : "auto",
            }}
            onClick={expandBanner}
            onMouseEnter={expandBanner}
          >
            <p className="text-yellow-400 text-xs font-bold flex items-center gap-2 whitespace-nowrap">
              <span>🎁</span> Tu premio Corcholata te espera al final del tutorial
            </p>
          </div>

          {/* Collapsed badge — pops in when banner shrinks */}
          <div
            className="fixed z-50 cursor-pointer select-none"
            style={{
              bottom: bannerCollapsed ? "24px" : "12px",
              right: bannerCollapsed ? "20px" : "50%",
              transform: bannerCollapsed ? "translateX(0)" : "translateX(50%)",
              opacity: bannerCollapsed ? 1 : 0,
              pointerEvents: bannerCollapsed ? "auto" : "none",
              transition: "all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)",
              animation: bannerCollapsed
                ? "badge-pop-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 0.35s both, badge-glow 3s ease-in-out 1s infinite, badge-float 4s ease-in-out 1s infinite"
                : "none",
            }}
            onClick={expandBanner}
            onMouseEnter={expandBanner}
            title="¡Tu premio Corcholata te espera!"
          >
            <div
              className="flex items-center gap-1.5 rounded-full px-3 py-1.5 shadow-lg backdrop-blur-md border border-yellow-500/40"
              style={{ background: "rgba(234,179,8,0.15)" }}
            >
              <span className="text-lg leading-none">🎁</span>
              <span className="text-yellow-400 text-[10px] font-black uppercase tracking-wider">
                Premio
              </span>
            </div>
          </div>
        </>
      )}

      {/* Act label (debug-style, subtle) */}
      <div className="flex justify-center mb-2">
        <span
          className="text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full"
          style={{ color: "#1e293b", background: "rgba(255,255,255,0.04)" }}
        >
          {currentAct.id}
        </span>
      </div>

      {currentAct.type === "dialogue-scene" && (
        <ActDialogueScene
          actId={currentAct.id as DialogueSceneId}
          webito={webito}
          refreshCount={actIndex === 0 ? refreshCount : 0}
          onComplete={advance}
        />
      )}

      {currentAct.type === "stat-reveal" && (
        <ActStatReveal webito={webito} onComplete={advance} />
      )}

      {currentAct.type === "board-preview" && (
        <ActBoardPreview webito={webito} onComplete={advance} />
      )}

      {currentAct.type === "game" && currentAct.data && (
        <ActGame
          key={currentAct.id}
          statFocus={currentAct.data.statFocus}
          backendPhase={currentAct.data.backendPhase}
          webito={webito}
          energyBefore={energyBefore}
          onComplete={advance}
          onStatsUpdate={updateWebitoStats}
        />
      )}

      {currentAct.type === "karma-reveal" && (
        <ActKarmaReveal
          webito={webito}
          onComplete={(karma) => advance(karma)}
        />
      )}

      {currentAct.type === "hatching" && (
        <ActHatching webito={webito} onComplete={(axoName) => advance(undefined, axoName)} />
      )}

      {currentAct.type === "treasure-chest" && (
        <ActTreasureChest
          hasPendingReward={hasPendingReward ?? false}
          token={webito.token}
          onRewardClaimed={() => setRewardClaimed(true)}
          onComplete={() => advance()}
        />
      )}

      {currentAct.type === "world-intro" && (
        <ActWorldIntro webito={webito} onComplete={advance} />
      )}
    </div>
  );
}

export default TutorialFlow;
