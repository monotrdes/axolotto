/**
 * Flag build-time del mundo papel picado (plan task-84). Es una constante de
 * compilación: sin NEXT_PUBLIC_PAPER_WORLD=1 el juego queda EXACTAMENTE igual.
 * Los componentes HTML la usan para aplicar el re-skin `.papel-*` de globals.css.
 */
export const PAPER_WORLD = process.env.NEXT_PUBLIC_PAPER_WORLD === "1";
