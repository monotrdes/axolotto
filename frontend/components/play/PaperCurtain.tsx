"use client";
import { forwardRef, useImperativeHandle, useRef, useState } from "react";

/**
 * Cortina de papel picado: tiras de colores caen para cubrir la pantalla
 * durante el cambio de macrozona y se levantan al revelar la nueva.
 * Estilos en globals.css (.paper-curtain). (plan task-84 §3.2)
 */

export interface PaperCurtainHandle {
  cover(): Promise<void>;
  reveal(): Promise<void>;
}

const STRIPS = 7;
const STRIP_STAGGER_MS = 40;
const STRIP_FALL_MS = 300;

function totalMs(): number {
  return STRIP_FALL_MS + STRIP_STAGGER_MS * (STRIPS - 1) + 30;
}

const PaperCurtain = forwardRef<PaperCurtainHandle>(function PaperCurtain(_props, ref) {
  const [covered, setCovered] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const animate = (toCovered: boolean) =>
    new Promise<void>((resolve) => {
      if (timer.current) clearTimeout(timer.current);
      setCovered(toCovered);
      timer.current = setTimeout(resolve, totalMs());
    });

  useImperativeHandle(ref, () => ({
    cover: () => animate(true),
    reveal: () => animate(false),
  }));

  return (
    <div className={`paper-curtain ${covered ? "covered" : ""}`} aria-hidden>
      {Array.from({ length: STRIPS }).map((_, i) => (
        <div
          key={i}
          className="paper-curtain-strip"
          style={{ transitionDelay: `${(covered ? i : STRIPS - 1 - i) * STRIP_STAGGER_MS}ms` }}
        />
      ))}
    </div>
  );
});

export default PaperCurtain;
