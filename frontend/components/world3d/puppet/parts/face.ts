import { blob } from "../paintUtils";
import type { PartCtx } from "./partCtx";

/**
 * Cara (ojos + boca + chapas) en coords locales de cabeza (origen = centro).
 * De perfil solo se ve un ojo/media boca. eyeType y mouthType del ADN.
 * No se dibuja nada en vista "back".
 */

function eyeOpen(p: PartCtx, x: number, y: number, r: number): void {
  const { ctx, pal } = p;
  ctx.fillStyle = pal.ink;
  switch (p.dna.eye) {
    case "dreamer": {
      // párpado a media asta + pestaña
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI);
      ctx.fill();
      ctx.strokeStyle = pal.ink;
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(x - r, y);
      ctx.lineTo(x + r, y);
      ctx.stroke();
      ctx.lineWidth = 7;
      break;
    }
    case "zen": {
      eyeClosed(p, x, y, r);
      break;
    }
    case "intellectual": {
      ctx.beginPath();
      ctx.arc(x, y, r * 0.8, 0, Math.PI * 2);
      ctx.fill();
      // arito de lentes
      ctx.strokeStyle = pal.edge;
      ctx.lineWidth = 3.5;
      ctx.beginPath();
      ctx.arc(x, y, r + 4, 0, Math.PI * 2);
      ctx.stroke();
      ctx.lineWidth = 7;
      break;
    }
    default: {
      // cute / derp (derp varía tamaño/altura por ojo en paintFace)
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
      // brillito
      ctx.fillStyle = pal.edge;
      ctx.beginPath();
      ctx.arc(x + r * 0.35, y - r * 0.35, r * 0.3, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

function eyeClosed(p: PartCtx, x: number, y: number, r: number): void {
  const { ctx, pal } = p;
  ctx.strokeStyle = pal.ink;
  ctx.lineWidth = 6;
  ctx.beginPath();
  ctx.arc(x, y - 2, r + 1.5, 0.15 * Math.PI, 0.85 * Math.PI);
  ctx.stroke();
  ctx.lineWidth = 7;
}

function mouth(p: PartCtx, x: number, y: number, s: number): void {
  const { ctx, pal } = p;
  ctx.strokeStyle = pal.ink;
  ctx.lineWidth = 5.5;
  switch (p.dna.mouth) {
    case "flat": {
      ctx.beginPath();
      ctx.moveTo(x - 12 * s, y + 8);
      ctx.lineTo(x + 12 * s, y + 8);
      ctx.stroke();
      break;
    }
    case "fang": {
      ctx.beginPath();
      ctx.arc(x, y, 16 * s, 0.2 * Math.PI, 0.8 * Math.PI);
      ctx.stroke();
      // colmillito
      ctx.fillStyle = pal.edge;
      ctx.beginPath();
      ctx.moveTo(x + 8 * s, y + 13);
      ctx.lineTo(x + 12 * s, y + 13);
      ctx.lineTo(x + 10 * s, y + 20);
      ctx.closePath();
      ctx.fill();
      break;
    }
    case "rockstar": {
      // boca abierta cantando
      blob(p.ctx, x, y + 10, 9 * s, 11, pal.ink, 0, null);
      blob(p.ctx, x, y + 15, 5 * s, 4.5, p.pal.accent, 0, null);
      break;
    }
    case "divine": {
      ctx.beginPath();
      ctx.arc(x, y + 9, 5 * s, 0, Math.PI * 2);
      ctx.stroke();
      break;
    }
    default: {
      // smile
      ctx.beginPath();
      ctx.arc(x, y, 16 * s, 0.2 * Math.PI, 0.8 * Math.PI);
      ctx.stroke();
    }
  }
  ctx.lineWidth = 7;
}

export function paintFace(p: PartCtx): void {
  if (p.view === "back") return;
  const { ctx, rnd, pal, pose } = p;
  const closed = pose.eyes === "closed";
  const derp = p.dna.eye === "derp";

  if (p.view === "side") {
    if (closed) eyeClosed(p, -28, -6, 8);
    else eyeOpen(p, -28, derp ? -10 : -6, derp ? 9 : 8);
    mouth(p, -42, -2, 0.7);
    ctx.globalAlpha = 0.45;
    blob(ctx, -10, 18, 9 + rnd(1) * 3, 6, pal.accent, 0, null);
    ctx.globalAlpha = 1;
    return;
  }

  // front
  if (closed) {
    eyeClosed(p, -26, -2, 8);
    eyeClosed(p, 26, -2, 8);
  } else if (derp) {
    eyeOpen(p, -26, -6, 8.5);
    eyeOpen(p, 26, 1, 6.5);
  } else {
    eyeOpen(p, -26, -2, 7.5);
    eyeOpen(p, 26, -2, 7.5);
  }
  mouth(p, 0, 10, 1);
  // chapas
  ctx.globalAlpha = 0.45;
  blob(ctx, -40, 20, 9 + rnd(1) * 3, 6, pal.accent, 0, null);
  blob(ctx, 40, 20, 9 + rnd(2) * 3, 6, pal.accent, 0, null);
  ctx.globalAlpha = 1;
}
