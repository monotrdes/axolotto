// Harness de iteración visual del PUPPET (untracked, como _harness3d.ts).
// Bundle: npx esbuild _harness_puppet.ts --bundle --outfile=../docs/prototipos/_puppet_bundle.js
// Captura: node _shot.mjs _puppet_harness.html _puppet_shot.png 1200 900
import * as THREE from "three";
import { AxolotitoBillboard } from "./components/world3d/AxolotitoBillboard";

const host = document.getElementById("host")!;
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(1200, 900);
renderer.setClearColor(0x2e6f73);
host.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.add(new THREE.AmbientLight(0xffffff, 1.4));
const sun = new THREE.DirectionalLight(0xfff2dd, 1.2);
sun.position.set(3, 6, 5);
scene.add(sun);

const cam = new THREE.OrthographicCamera(-6, 6, 4.5, -4.5, 0.1, 50);
cam.position.set(0, 0.8, 10);
cam.lookAt(0, 0.8, 0);

// piso de referencia
const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(14, 10),
  new THREE.MeshBasicMaterial({ color: 0x1d4e52 }),
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -3.2;
scene.add(floor);

const puppets: AxolotitoBillboard[] = [];
const add = (b: AxolotitoBillboard, x: number, y: number) => {
  b.position.set(x, y, 0);
  scene.add(b);
  puppets.push(b);
  return b;
};

// ── Modo DNA (?dna): grid de variantes, una dimensión por fila ──
const DNA_MODE = location.search.includes("dna");
if (DNA_MODE) {
  const rows: Array<[string, string[], "front" | "side"]> = [
    ["gillType", ["short", "normal", "feathery", "crown", "phoenix"], "front"],
    ["eyeType", ["derp", "dreamer", "cute", "intellectual", "zen"], "front"],
    ["mouthType", ["flat", "smile", "fang", "rockstar", "divine"], "front"],
    ["tailType", ["standard", "wavy", "betta", "plasma"], "side"],
    ["foreheadType", ["none", "stripes", "gem", "halo"], "front"],
    ["limbType", ["soft", "claws", "scales", "coral"], "front"],
  ];
  const skins = ["pink", "gold", "astral", "gray_light", "gray_dark"];
  const page = location.search.includes("p2") ? 1 : 0;
  rows.slice(page * 3, page * 3 + 3).forEach(([key, values, view], r) => {
    values.forEach((v, i) => {
      const dna: Record<string, unknown> = { skinColor: skins[i % skins.length], seed: 5 + i };
      dna[key] = v;
      const b = add(new AxolotitoBillboard(dna, 1.9), -4.8 + i * 2.35, 2.0 - r * 2.9);
      if (view === "side") {
        b.setState("walk");
        b.setWalk(-1, 0);
        b.update(0, 0.001);
      } else {
        b.update(0.6, 0.016);
      }
    });
  });
}

// ── Fila 1 (arriba): ciclo de CAMINADO lateral, 6 fases ──
if (!DNA_MODE) for (let i = 0; i < 6; i++) {
  const b = add(new AxolotitoBillboard({ skinColor: "pink", seed: 7 }, 1.3), -5 + i * 2, 2.6);
  b.setState("walk");
  b.setWalk(-1, 0); // perfil mirando a la izquierda
  b.update(0, i * 0.1 + 0.001); // 10fps → frame i
}

// ── Fila 2: NADO, 4 fases + SLEEP x2 ──
if (!DNA_MODE) for (let i = 0; i < 4; i++) {
  const b = add(new AxolotitoBillboard({ skinColor: "gold", seed: 12 }, 1.3), -5 + i * 2, 0.2);
  b.setState("swim");
  b.setWalk(-1, 0);
  b.update(0, i / 7 + 0.001);
}
if (!DNA_MODE) for (let i = 0; i < 2; i++) {
  const b = add(new AxolotitoBillboard({ skinColor: "astral", seed: 21 }, 1.3), 3 + i * 2, 0.2);
  b.setState("sleep");
  b.update(0, i / 1.2 + 0.001);
}

// ── Fila 3 (abajo): IDLE front A/B/blink + back A/B + walk front/back ──
const idles: Array<[string, number]> = [
  ["pink", 3],
  ["gray_light", 5],
  ["gray_dark", 9],
];
if (!DNA_MODE) idles.forEach(([skin, seed], i) => {
  const b = add(new AxolotitoBillboard({ skinColor: skin, seed }, 1.3), -5 + i * 1.7, -2.4);
  b.update(0.6, 0.016);
});
if (!DNA_MODE) {
  const back = add(new AxolotitoBillboard({ skinColor: "pink", seed: 3 }, 1.3), 0.2, -2.4);
  back.setWalk(0, -1); // de espaldas
  back.update(0.6, 0.016);
  const wf = add(new AxolotitoBillboard({ skinColor: "gold", seed: 5 }, 1.3), 1.9, -2.4);
  wf.setState("walk");
  wf.setWalk(0.05, 1);
  wf.update(0, 0.001);
  const wb = add(new AxolotitoBillboard({ skinColor: "astral", seed: 8 }, 1.3), 3.6, -2.4);
  wb.setState("walk");
  wb.setWalk(0.05, -1);
  wb.update(0, 0.001);
}

// loop de render: estático (poses congeladas) o animado con ?anim
const animate = location.search.includes("anim");
const clock = new THREE.Clock();
let t = 0;
const loop = () => {
  const dt = clock.getDelta();
  t += dt;
  if (animate) for (const p of puppets) p.update(t, dt);
  renderer.render(scene, cam);
  requestAnimationFrame(loop);
};
loop();
