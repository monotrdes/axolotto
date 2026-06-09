"use client";
import { useState } from "react";

interface Props {
  axoName: string;
  karma: "lucky" | "salty";
  onPayAndPlay: () => void; // → ir a la tienda/banco
  onPlayFree: () => void;   // → modo F2P espectador
}

const AXO_DIALOGUE_BY_KARMA = {
  lucky: "¡Estoy listo para las ligas mayores! Siento la suerte corriendo por mis branquias. ¡Necesito entrar a una sala real AHORA!",
  salty: "Okay, el agua estuvo salada en el tutorial... pero eso fue entrenamiento. En una partida real voy a demostrar quién soy.",
};

export default function PostTutorialBranch({ axoName, karma, onPayAndPlay, onPlayFree }: Props) {
  const [chosen, setChosen] = useState<"premium" | "free" | null>(null);

  const handlePremium = () => {
    setChosen("premium");
    setTimeout(onPayAndPlay, 600);
  };
  const handleFree = () => {
    setChosen("free");
    setTimeout(onPlayFree, 600);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center px-6"
      style={{ background: "radial-gradient(ellipse at center, #0a0f1a 0%, #020408 100%)" }}
    >
      {/* Axolotito */}
      <div className="text-8xl mb-2 animate-webito-float">🦎</div>
      <p
        className="text-sm font-black tracking-widest mb-1"
        style={{ color: karma === "lucky" ? "#FBBF24" : "#60A5FA" }}
      >
        {axoName.toUpperCase()}
      </p>

      {/* Diálogo del Axo */}
      <div className="max-w-sm w-full bg-black/60 border border-cyan-500/30 rounded-2xl p-5 mb-8 text-center">
        <p className="text-sm text-cyan-100 italic leading-relaxed">
          "{AXO_DIALOGUE_BY_KARMA[karma]}"
        </p>
      </div>

      {/* Las dos opciones */}
      <div className="max-w-sm w-full space-y-4">
        {/* Opción premium */}
        <button
          onClick={handlePremium}
          disabled={chosen !== null}
          className="w-full py-5 rounded-2xl font-black text-lg transition-all transform hover:scale-105 active:scale-95 disabled:opacity-60 text-white"
          style={{
            background: chosen === "premium"
              ? "linear-gradient(135deg, #FBBF24, #F59E0B)"
              : "linear-gradient(135deg, #E4007C, #B30062)",
            boxShadow: "0 0 30px rgba(228,0,124,0.4)",
          }}
        >
          💎 ¡Que juegue de verdad!
          <span className="block text-xs font-normal opacity-80 mt-0.5">
            Compra FRJ → acceso completo al juego
          </span>
        </button>

        {/* Opción F2P */}
        <button
          onClick={handleFree}
          disabled={chosen !== null}
          className="w-full py-4 rounded-2xl font-black text-base border border-white/10 hover:border-white/30 transition-all transform hover:scale-102 active:scale-98 disabled:opacity-60 text-white"
          style={{ background: "rgba(255,255,255,0.04)" }}
        >
          👁️ Primero quiero ver cómo se juega
          <span className="block text-xs font-normal text-gray-400 mt-0.5">
            Entra gratis · tu Axolotito especta partidas reales
          </span>
        </button>
      </div>

      <p className="text-gray-600 text-xs mt-6 text-center max-w-xs">
        Puedes cambiar de modo cuando quieras desde el menú principal.
      </p>
    </div>
  );
}
