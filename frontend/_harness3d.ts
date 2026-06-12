// Harness de iteración visual (untracked, como _shot.mjs).
// Bundle: npx esbuild _harness3d.ts --bundle --outfile=../docs/prototipos/_world3d_bundle.js
// Captura: node _shot.mjs _world3d_harness.html _world3d_shot.png 450 920
import { ThreeWorldEngine } from "./components/world3d/ThreeWorldEngine";
import { buildTianguisScene3D } from "./components/world3d/TianguisScene3D";

const host = document.getElementById("host")!;
const engine = ThreeWorldEngine.create(host);
engine.setScene(
  buildTianguisScene3D({
    visitantes: [
      { skinColor: "pink", seed: 3 },
      { skinColor: "gold", seed: 8 },
      { skinColor: "astral", seed: 15 },
    ],
  }),
);
engine.onHotspot = (id) => console.log("hotspot:", id);
