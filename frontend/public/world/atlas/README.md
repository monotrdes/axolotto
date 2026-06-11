# Atlases del mundo papel picado

Convención (plan task-84 §3.1, Fase 0):

```
public/world/atlas/<macrozona>[.<subzona>].webp   ← textura (≤2048×2048)
public/world/atlas/<macrozona>[.<subzona>].json   ← spritesheet Pixi
public/world/atlas/axolotito-parts.webp/.json     ← partes del puppet (compartido)
```

- Macrozonas: `santuario`, `tianguis`, `piramide`.
- Subzonas de la Pirámide (carga perezosa): `piramide.rankings`, `piramide.salas`, `piramide.capsulas`.
- Formato JSON: spritesheet estándar de Pixi (TexturePacker free CLI o @assetpack/core).
- Presupuesto: ≤2 atlases residentes por macrozona (la Pirámide admite 3 con lazy-load).

Fase 0 usa escenas placeholder (Graphics) — este directorio se llena en Fases 1-4.
