"use client";
import { useState, useEffect, useCallback } from "react";
import { usePrivy } from "@privy-io/react-auth";
import WebitoDialogue from "@/components/tutorial/WebitoDialogue";

interface Axolotito {
  id: number;
  name: string;
  nature?: string;
  stat_luck?: number;
  stat_salinity?: number;
}

interface Props {
  axolotito: Axolotito;
  isWatchingGame: boolean;        // true mientras el usuario está en la vista espectador
  gameResult?: "win" | "lose" | null;
  onBuyGal: () => void;            // → redirige a tienda/banco
}

// Comentarios del Axo mientras especta (no necesita API, hardcoded para F2P)
const SPECTATOR_COMMENTS: Record<string, string[]> = {
  watching: [
    "Yo podría hacer eso. Fácil. Denme una mesa.",
    "¿Ves esa tabla? Yo la llenaría en la mitad de tiempo.",
    "¡¡El Gritón cantó EL AXOLOTITO!! ¡Esa carta me pertenece a mí!",
    "Si tuviera FRJ ahorita mismo, estaría ganando. Te lo juro.",
    "Las cartas de ese jugador son de las buenas. Yo merezco esas cartas.",
    "¡Anda, canta La Sirena! ¡La Sirena! ¡LA SIRENA!",
  ],
  win_witnessed: [
    "¡YO SABÍA QUE IBA A GANAR! Bueno, no, no sabía. Pero me alegra.",
    "¡Lotería! ¡Lotería! ...ojalá fuera yo.",
    "Ese jugador ganó bien chido. Yo también quiero ganar chido.",
  ],
  lose_witnessed: [
    "Le faltó un poco de suerte. A mí no me faltaría, yo tengo aura.",
    "Pobre. Hubiera necesitado menos salinidad. Yo ya sé cómo funciona.",
    "La sal. Siempre la sal. Ya sé por qué perdió.",
  ],
  idle: [
    "¿Cuándo jugamos de verdad?",
    "Tengo las branquias listas. Y los reflejos también.",
    "Sigo aquí. Por si me necesitas. Para jugar. Eso.",
  ],
};

const getRandom = (arr: string[]) => arr[Math.floor(Math.random() * arr.length)];

export default function AwakeAxoSpectator({ axolotito, isWatchingGame, gameResult, onBuyGal }: Props) {
  const { getAccessToken } = usePrivy();
  const [currentComment, setCurrentComment] = useState("");
  const [fragmentsToday, setFragmentsToday] = useState(0);
  const [galToday, setGalToday] = useState(0);
  const [capped, setCapped] = useState(false);
  const [showComment, setShowComment] = useState(false);

  // Comentario aleatorio cada vez que el estado cambia
  useEffect(() => {
    let comment = "";
    if (gameResult === "win") comment = getRandom(SPECTATOR_COMMENTS.win_witnessed);
    else if (gameResult === "lose") comment = getRandom(SPECTATOR_COMMENTS.lose_witnessed);
    else if (isWatchingGame) comment = getRandom(SPECTATOR_COMMENTS.watching);
    else comment = getRandom(SPECTATOR_COMMENTS.idle);

    if (comment) {
      setCurrentComment(comment);
      setShowComment(true);
    }
  }, [isWatchingGame, gameResult]);

  // Acreditar recompensa F2P cuando termina una partida espectada
  const claimWatchReward = useCallback(async (won: boolean) => {
    try {
      const token = await getAccessToken();
      const res = await fetch(`/api/v1/f2p/watch-reward?won=${won}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return;
      const data = await res.json();
      if (data.capped) {
        setCapped(true);
      } else {
        setFragmentsToday(prev => prev + (data.fragments_added ?? 0));
        setGalToday(prev => prev + (data.gal_earned ?? 0));
      }
    } catch (e) {
      console.error("watch-reward failed", e);
    }
  }, [getAccessToken]);

  useEffect(() => {
    if (gameResult === "win") claimWatchReward(true);
    else if (gameResult === "lose") claimWatchReward(false);
  }, [gameResult, claimWatchReward]);

  return (
    <div className="relative">
      {/* Card del Axolotito */}
      <div
        className="bg-black/40 border border-cyan-500/20 rounded-2xl p-4 text-center animate-tab-fade"
        style={{ boxShadow: "0 0 20px rgba(0,229,255,0.05)" }}
      >
        <div className="text-5xl mb-2 animate-webito-float">🦎</div>
        <p className="font-black text-sm text-cyan-300">{axolotito.name}</p>
        {axolotito.nature && (
          <p className="text-xs text-gray-500 mt-0.5 capitalize">{axolotito.nature}</p>
        )}

        {/* Micro-stats del día */}
        <div className="flex justify-center gap-4 mt-3">
          <div className="text-center">
            <p className="text-[10px] text-gray-500 uppercase tracking-widest">FRJ hoy</p>
            <p className="text-sm font-black text-emerald-400">+{galToday.toFixed(1)}</p>
          </div>
          <div className="text-center">
            <p className="text-[10px] text-gray-500 uppercase tracking-widest">Fragmentos</p>
            <p className="text-sm font-black text-purple-400">+{fragmentsToday}</p>
          </div>
        </div>

        {/* Cap alcanzado */}
        {capped && (
          <p className="text-[10px] text-yellow-500 mt-2 px-2">
            Límite diario alcanzado. Vuelve mañana o compra FRJ para jugar sin límite.
          </p>
        )}

        {/* CTA */}
        <button
          onClick={onBuyGal}
          className="mt-4 w-full py-3 rounded-xl font-black text-sm transition-all hover:scale-105 active:scale-95 text-white"
          style={{
            background: "linear-gradient(135deg, rgba(228,0,124,0.13), rgba(179,0,98,0.13))",
            border: "1px solid rgba(228,0,124,0.27)",
            color: "#FF8DA1",
          }}
        >
          💎 Comprar FRJ — que juegue de verdad
        </button>
      </div>

      {/* Comentario del Axo */}
      {showComment && currentComment && (
        <div className="absolute bottom-24 left-1/2 -translate-x-1/2 w-72 z-50">
          <WebitoDialogue
            text={currentComment}
            speaker="axo"
            onDismiss={() => setShowComment(false)}
            autoHideMs={5000}
          />
        </div>
      )}
    </div>
  );
}
