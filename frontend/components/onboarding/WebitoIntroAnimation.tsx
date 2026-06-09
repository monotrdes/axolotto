"use client";
import { useState, useEffect } from "react";
import WebitoDialogue from "@/components/tutorial/WebitoDialogue";

interface Props {
  onComplete: () => void;
}

const INTRO_SEQUENCE = [
  {
    text: "¡AY! ¡Me caí! Perdón perdón... llevo semanas dentro de este cascarón y finalmente escuché que tú llegaste.",
    delay: 1200,
  },
  {
    text: "Soy un Webito. Un axolotito que todavía no nace. Y te elegí a ti para que seas mi jugador.",
    delay: 0,
  },
  {
    text: "Aquí afuera hay un juego llamado Lotería. ¡Y yo NECESITO jugar! ¿Me ayudas? ¿Me llevas a una mesa?",
    delay: 0,
  },
];

type AnimPhase = "falling" | "landing" | "floating" | "talking" | "done";

export default function WebitoIntroAnimation({ onComplete }: Props) {
  const [phase, setPhase] = useState<AnimPhase>("falling");
  const [dialogueIndex, setDialogueIndex] = useState(-1);
  const [showDust, setShowDust] = useState(false);

  // Secuencia de animación
  useEffect(() => {
    const t1 = setTimeout(() => {
      setPhase("landing");
      setShowDust(true);
    }, 900);
    const t2 = setTimeout(() => {
      setShowDust(false);
      setPhase("floating");
    }, 1400);
    const t3 = setTimeout(() => {
      setPhase("talking");
      setDialogueIndex(0);
    }, 1800);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, []);

  const handleDialogueDismiss = () => {
    const next = dialogueIndex + 1;
    if (next < INTRO_SEQUENCE.length) {
      setDialogueIndex(next);
    } else {
      setPhase("done");
      onComplete();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center"
      style={{ background: "radial-gradient(ellipse at center, #0d1b2a 0%, #020408 100%)" }}
    >
      {/* Estrellas de fondo — puntos estáticos */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {Array.from({ length: 40 }).map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full bg-white"
            style={{
              width: Math.random() * 2 + 1 + "px",
              height: Math.random() * 2 + 1 + "px",
              top: Math.random() * 100 + "%",
              left: Math.random() * 100 + "%",
              opacity: Math.random() * 0.5 + 0.1,
            }}
          />
        ))}
      </div>

      {/* El Webito */}
      <div className="relative flex flex-col items-center" style={{ marginTop: "-80px" }}>
        <div
          className={
            phase === "falling"
              ? "animate-webito-fall"
              : phase === "floating" || phase === "talking" || phase === "done"
              ? "animate-webito-float"
              : ""
          }
          style={{ fontSize: "96px", lineHeight: 1, userSelect: "none" }}
        >
          🥚
        </div>

        {/* Nube de polvo al aterrizar */}
        {showDust && (
          <div
            className="absolute bottom-0 animate-dust-burst"
            style={{
              width: "80px",
              height: "20px",
              background: "radial-gradient(ellipse, rgba(255,255,255,0.3) 0%, transparent 70%)",
              borderRadius: "50%",
            }}
          />
        )}
      </div>

      {/* Texto de fase antes del diálogo */}
      {phase === "falling" && (
        <p className="mt-8 text-gray-500 text-sm animate-pulse">
          algo viene del cielo...
        </p>
      )}

      {/* Diálogos */}
      {phase === "talking" && dialogueIndex >= 0 && dialogueIndex < INTRO_SEQUENCE.length && (
        <div className="absolute bottom-20 left-4 right-4 max-w-lg mx-auto z-50">
          <WebitoDialogue
            text={INTRO_SEQUENCE[dialogueIndex].text}
            speaker="webito"
            onDismiss={handleDialogueDismiss}
            autoHideMs={INTRO_SEQUENCE[dialogueIndex].delay || undefined}
          />
        </div>
      )}
    </div>
  );
}
