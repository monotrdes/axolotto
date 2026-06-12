# Contrato de sprites — Axolotito (puppet 3D-diorama)

Cómo entregar el arte real para sustituir el dibujo procedural del puppet
(`frontend/components/world3d/puppet/`). Modelo **cut-out**: 1 PNG por
parte × vista; el código anima rotando las piezas en sus pivotes (caminar,
nadar, mecer branquias). **No** se entregan frames de cuerpo completo.

## Espacio de referencia

- Celda lógica: **256×280 px** (entregar @2x: 512×560 px, PNG transparente).
- El puppet de pie mide ~245 px de alto en la celda lógica; cabeza ≈ 48%.
- El perfil ("side") mira a la **izquierda** (cara en −x, cola en +x);
  el código lo espeja, no entregar versión derecha.
- Estilo: papel picado — filo de papel `#fff7ec`, tinta `#2b2b3a`,
  pieles tinte-ables (ver abajo).

## Partes y pivotes

Cada PNG lleva un sidecar JSON con su pivote en px del PNG (`{"pivot":{"x":..,"y":..}}`).
El pivote es el punto de la pieza que cae en el ancla del rig y alrededor
del cual rota.

| Parte | Vistas | Tamaño aprox (lógico) | Pivote |
|---|---|---|---|
| body | front, side | 104×112 / 108×104 | centro del cuerpo |
| belly (overlay) | front, side | 64×80 | centro del cuerpo |
| head | front, back, side | 132×120 / 120×112 | centro de la cabeza |
| arm | front, side | 26×40 | hombro (borde superior-centro) |
| leg | front, side | 34×56 | cadera (borde superior-centro) |
| tail | side, back | 100×46 (betta ~110×70) | base de la cola (extiende a +x) |
| gillFrond | todas | 60×24 | raíz de la fronda (extiende a +x); se instancia ×3 por lado |
| eyes (overlay) | front, side | sobre cabeza | centro de la cabeza |
| mouth (overlay) | front, side | sobre cabeza | centro de la cabeza |
| forehead (overlay) | front, side | 64×40 | parte alta de la cabeza |

## Variantes por ADN

Una variante = **solo el PNG de esa parte** (no un cuerpo nuevo):

- `gillFrond`: short, normal, feathery, crown, phoenix
- `eyes`: derp, dreamer, cute, intellectual, zen (+ versión cerrada de cada uno)
- `mouth`: flat, smile, fang, rockstar, divine
- `tail`: standard, wavy, betta, plasma
- `forehead`: stripes, gem, halo (none = sin PNG)
- `leg`/`arm`: soft, claws, scales, coral

## Colores de piel

Opción A (preferida): piezas de piel en **gris neutro** (#c0c0c0 medio) y el
código las tiñe con los 5 skin colors (pink, gray_light, gray_dark, gold,
astral). Opción B: 5 sets ya pintados por color. Las branquias usan el
acento cálido (`gillAccent`), también tinte-able.

## Animación dibujada (opcional, por parte)

Si una parte necesita animación que la rotación no logra (p.ej. branquias
ondeando), entregar **tira horizontal de N frames** del mismo tamaño de
celda; declarar `"frames": N` en el sidecar. El código la reproduce en
lugar de rotar la pieza estática.

## Nomenclatura

```
axolotito/<parte>_<vista>_<tipoADN>.png        p.ej. gillFrond_side_crown.png
axolotito/<parte>_<vista>_<tipoADN>.json       (sidecar pivote)
```

## Tabla de ciclos (referencia, los genera el código)

| Ciclo | Vista | Frames | Qué se anima |
|---|---|---|---|
| idle | front/back | 2 + blink | branquias A/B, bracitos, parpadeo |
| walk | side | 6 | piernas alternadas ±0.55 rad, brazos contralaterales, bob, lean 8° |
| walk | front/back | 2 | paso sutil |
| swim | side | 4 | cuerpo horizontal, cola propulsando, patitas plegadas |
| sleep | side | 2 | acostado, ojos cerrados, respiración |
