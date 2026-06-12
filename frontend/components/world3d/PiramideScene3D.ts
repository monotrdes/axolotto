import * as THREE from "three";
import type { SceneAnimation, World3DScene, StallFocus } from "./ThreeWorldEngine";
import { AxolotitoBillboard } from "./AxolotitoBillboard";
import {
  PAL,
  box,
  cyl,
  ellipseShape,
  paper,
  roundedRectShape,
  textPlane,
  terraceStack,
  plant,
  rand,
  paperMat,
} from "./paperPrimitives";
import { skinToTint } from "./skinColors";
import type { AxolotitoData } from "@/types/axolotito";

export function buildPiramideScene3D(
  opts: {} = {}
): World3DScene & {
  setPodio(data: AxolotitoData[]): void;
  setAxolotitos(data: AxolotitoData[]): void;
} {
  const world = new THREE.Group();
  const animations: SceneAnimation[] = [];
  const hotspots: THREE.Object3D[] = [];
  const billboards: AxolotitoBillboard[] = [];

  // Subgrupos organizativos
  const backgroundGroup = new THREE.Group();
  const pyramidGroup = new THREE.Group();
  const podioGroup = new THREE.Group();
  const gashaponGroup = new THREE.Group();
  const salaGroup = new THREE.Group();
  const visitorsGroup = new THREE.Group();

  world.add(backgroundGroup);
  world.add(pyramidGroup);
  world.add(podioGroup);
  world.add(gashaponGroup);
  world.add(salaGroup);
  world.add(visitorsGroup);

  // Estados locales
  let lastPodioData: AxolotitoData[] = [];
  let lastAxolotitosData: AxolotitoData[] = [];

  const clearGroup = (group: THREE.Group) => {
    const hSet = new Set(hotspots);
    group.traverse((child) => {
      hSet.delete(child);
      if ((child as THREE.Mesh).geometry) (child as THREE.Mesh).geometry.dispose();
      const mats = Array.isArray((child as THREE.Mesh).material)
        ? ((child as THREE.Mesh).material as THREE.Material[])
        : (child as THREE.Mesh).material
        ? [(child as THREE.Mesh).material as THREE.Material]
        : [];
      for (const m of mats) {
        if ((m as any).map) (m as any).map.dispose();
        m.dispose();
      }
    });
    while (group.children.length > 0) {
      group.remove(group.children[0]);
    }
    hotspots.length = 0;
    hotspots.push(...hSet);
  };

  // ── 1. Base de agua y rocas (Entorno del Cenote) ──
  let baseY = 0;
  const baseLayers = [
    { w: 19.5, c: 0x06111f, h: 0.15, b: 0.015 },
    { w: 18.8, c: 0x0a233c, h: 0.15, b: 0.015 },
    { w: 18.2, c: 0x0e3656, h: 0.15, b: 0.015 },
    { w: 17.8, c: 0x124a70, h: 0.12, b: 0.015 },
  ];
  for (const L of baseLayers) {
    const m = paper(roundedRectShape(L.w, L.w * 1.34, 2.4), L.h, L.c, L.b);
    m.position.y = baseY;
    backgroundGroup.add(m);
    baseY += L.h;
  }
  const TOP = baseY; // Nivel del agua

  // Resplandor del agua
  const topWaterMesh = backgroundGroup.children[3] as THREE.Mesh & { material: THREE.MeshStandardMaterial };
  topWaterMesh.material.emissive = new THREE.Color(0x085c80);

  // Animación del agua
  animations.push((t) => {
    backgroundGroup.children[1].position.x = Math.sin(t * 0.3) * 0.05;
    backgroundGroup.children[1].position.z = Math.cos(t * 0.2) * 0.04;
    backgroundGroup.children[2].position.x = Math.sin(t * 0.4 + 1.0) * 0.08;
    backgroundGroup.children[2].position.z = Math.cos(t * 0.35 + 0.5) * 0.06;
    backgroundGroup.children[3].position.x = Math.sin(t * 0.5 + 2.0) * 0.1;
    backgroundGroup.children[3].position.z = Math.cos(t * 0.45 + 1.2) * 0.07;

    const waterGlow = 0.8 + Math.sin(t * 0.75) * 0.12;
    topWaterMesh.material.emissive.setHex(0x085c80).multiplyScalar(waterGlow);
  });

  // Paredes rocosas de la cueva al fondo y laterales
  terraceStack(backgroundGroup, TOP, 0.0, -6.6, 4.0, 6, [0x081c33, 0x0e3656, 0x124a70, 0x1c5860], 0.3, 0.15, 0.5);
  terraceStack(backgroundGroup, TOP, -5.5, -2.5, 2.2, 5, [0x081c33, 0x0e3656, 0x124a70], 0.35, 0.18, 0.6);
  terraceStack(backgroundGroup, TOP, 5.5, -2.5, 2.2, 5, [0x081c33, 0x0e3656, 0x124a70], 0.35, 0.18, 0.6);
  terraceStack(backgroundGroup, TOP, -5.8, 2.8, 1.8, 4, [0x0e3656, 0x124a70], 0.35, 0.2);
  terraceStack(backgroundGroup, TOP, 5.8, 2.8, 1.8, 4, [0x0e3656, 0x124a70], 0.35, 0.2);

  // Plantas bioluminiscentes y rayos volumétricos
  plant(backgroundGroup, TOP + 1.2, -4.6, -4.2, 0x3ee8c0, 1.4, 0.6);
  plant(backgroundGroup, TOP + 1.2, 4.6, -4.2, 0x9b6df0, 1.4, 0.6);

  // ── 2. La Pirámide de Papel (Centro) ──
  const buildPyramid = () => {
    // Escalonado de la pirámide (4 terrazas de piedra gris)
    const steps = [
      { w: 5.6, h: 0.35, d: 4.2, y: TOP + 0.175, c: 0x4d5260 },
      { w: 4.4, h: 0.35, d: 3.2, y: TOP + 0.525, c: 0x5c6273 },
      { w: 3.2, h: 0.35, d: 2.3, y: TOP + 0.875, c: 0x6b7080 },
      { w: 2.0, h: 0.35, d: 1.5, y: TOP + 1.225, c: 0x7a8090 },
    ];

    for (const step of steps) {
      const block = box(step.w, step.h, step.d, step.c);
      block.position.set(0, step.y, -1.6);
      block.userData.stallId = "podio";
      hotspots.push(block);
      pyramidGroup.add(block);
    }

    // Templo/Santuario en la cumbre
    const shrine = box(1.2, 0.55, 0.9, 0x999da8);
    shrine.position.set(0, TOP + 1.675, -1.6);
    shrine.userData.stallId = "podio";
    hotspots.push(shrine);
    pyramidGroup.add(shrine);

    const shrineRoof = box(1.4, 0.15, 1.1, 0xb8bdc8);
    shrineRoof.position.set(0, TOP + 2.025, -1.6);
    shrineRoof.userData.stallId = "podio";
    hotspots.push(shrineRoof);
    pyramidGroup.add(shrineRoof);

    // Escalinata central (Rampa inclinada simulada con un box)
    const stairs = box(0.95, 0.08, 2.7, 0x8b8f9c);
    stairs.position.set(0, TOP + 0.72, -0.1);
    stairs.rotation.x = -0.52; // inclinación de la escalera
    stairs.userData.stallId = "podio";
    hotspots.push(stairs);
    pyramidGroup.add(stairs);
  };
  buildPyramid();

  // ── 3. Explanada de Rankings (Top-3) ──
  const buildRankingsPodio = () => {
    clearGroup(podioGroup);

    const data = lastPodioData.slice(0, 3);
    const medals = ["🥇", "🥈", "🥉"];
    // Alturas de los pedestales alineadas a los tiers de la pirámide
    const podioSpots = [
      { pos: new THREE.Vector3(0.0, TOP + 1.4, -1.1), pedH: 0.22, pedCol: 0xf5c542, r: 0.22 }, // 1st
      { pos: new THREE.Vector3(-0.75, TOP + 1.05, -1.1), pedH: 0.16, pedCol: 0xc9ccd6, r: 0.20 }, // 2nd
      { pos: new THREE.Vector3(0.75, TOP + 0.7, -1.1), pedH: 0.12, pedCol: 0xc2410c, r: 0.20 }, // 3rd
    ];

    data.forEach((axo, i) => {
      const spot = podioSpots[i];
      
      // Pedestal
      const ped = cyl(spot.r, spot.r * 1.05, spot.pedH, spot.pedCol);
      ped.position.copy(spot.pos);
      ped.position.y += spot.pedH / 2;
      ped.castShadow = true;
      ped.receiveShadow = true;
      ped.userData.stallId = "podio";
      hotspots.push(ped);
      podioGroup.add(ped);

      // Billboard del axolotito
      const startY = spot.pos.y + spot.pedH;
      const b = new AxolotitoBillboard(axo, 0.85);
      b.position.set(spot.pos.x, startY, spot.pos.z);
      b.userData.stallId = "podio";
      hotspots.push(b);
      billboards.push(b);
      podioGroup.add(b);

      // Etiqueta de rango y nombre
      const namePlate = textPlane(`${medals[i]} ${axo.name} (Nv ${axo.level})`, 0.15, "#fff7ec");
      namePlate.position.set(spot.pos.x, startY + 0.95, spot.pos.z + 0.05);
      podioGroup.add(namePlate);
    });
  };

  // ── 4. Gashapones (Monumentos a los lados) ──
  const buildGashapons = () => {
    clearGroup(gashaponGroup);

    const machines = [
      { color: 0xc2410c, name: "BRONCE", pos: new THREE.Vector3(-2.2, TOP + 0.35, -0.6), rotY: 0.25 },
      { color: 0xc9ccd6, name: "PLATA", pos: new THREE.Vector3(2.2, TOP + 0.35, -0.6), rotY: -0.25 },
      { color: 0xf5c542, name: "ORO", pos: new THREE.Vector3(0.0, TOP + 0.06, 2.4), rotY: 0.0 },
    ];

    machines.forEach((m) => {
      const g = new THREE.Group();
      g.position.copy(m.pos);
      g.rotation.y = m.rotY;

      // Base / Pedestal de la máquina
      const ped = cyl(0.35, 0.38, 0.12, 0x4a4d5c);
      ped.position.y = 0.06;
      ped.castShadow = true;
      ped.receiveShadow = true;
      g.add(ped);

      // Gabinete de la máquina
      const cab = box(0.42, 0.46, 0.42, m.color);
      cab.position.y = 0.35;
      cab.castShadow = true;
      cab.receiveShadow = true;
      g.add(cab);

      // Domo de cristal
      const domeMat = new THREE.MeshStandardMaterial({
        color: 0x9bd9e4,
        transparent: true,
        opacity: 0.55,
        roughness: 0.1,
      });
      const dome = new THREE.Mesh(
        new THREE.SphereGeometry(0.18, 12, 10, 0, Math.PI * 2, 0, Math.PI / 2),
        domeMat
      );
      dome.position.y = 0.58;
      dome.castShadow = true;
      g.add(dome);

      // Cápsulas de colores dentro
      const capCols = [0xe4007c, 0x2dd4bf, 0xf59e0b, 0x4ade80, 0x9b6df0];
      for (let i = 0; i < 5; i++) {
        const cap = new THREE.Mesh(
          new THREE.SphereGeometry(0.045, 8, 6),
          paperMat(capCols[i % capCols.length])
        );
        cap.position.set(
          rand(-0.07, 0.07),
          0.62 + rand(0, 0.07),
          rand(-0.07, 0.07)
        );
        g.add(cap);
      }

      // Nombre tag
      const label = textPlane(m.name, 0.15, "#fff7ec");
      label.position.set(0, 0.9, 0);
      g.add(label);

      g.traverse((child) => {
        child.userData.stallId = "gashapon";
        if (child.userData.stallId) hotspots.push(child);
      });

      gashaponGroup.add(g);
    });
  };
  buildGashapons();

  const salaHotspot = (mesh: THREE.Object3D) => {
    mesh.userData.stallId = "salas";
    hotspots.push(mesh);
  };

  // ── 5. Salas (Portal de Entrada de la Pirámide) ──
  const buildSalas3D = () => {
    clearGroup(salaGroup);

    // Columnas de piedra
    const colLeft = box(0.24, 0.85, 0.24, 0x4d5260);
    colLeft.position.set(-0.7, TOP + 0.425, 0.8);
    salaHotspot(colLeft);
    salaGroup.add(colLeft);

    const colRight = box(0.24, 0.85, 0.24, 0x4d5260);
    colRight.position.set(0.7, TOP + 0.425, 0.8);
    salaHotspot(colRight);
    salaGroup.add(colRight);

    // Dintel del portal
    const lintel = box(1.7, 0.2, 0.32, 0x6b7080);
    lintel.position.set(0, TOP + 0.95, 0.8);
    salaHotspot(lintel);
    salaGroup.add(lintel);

    // Letrero del Cenote de Salas
    const title = textPlane("🚪 ENTRADA SALAS", 0.16, "#fff7ec");
    title.position.set(0, TOP + 1.15, 0.82);
    salaHotspot(title);
    salaGroup.add(title);

    // Pozas de agua / Portal
    const poolShape = ellipseShape(0.8, 0.4);
    const pool = new THREE.Mesh(
      new THREE.ShapeGeometry(poolShape),
      new THREE.MeshBasicMaterial({ color: 0x081c33, side: THREE.DoubleSide })
    );
    pool.rotation.x = -Math.PI / 2;
    pool.position.set(0, TOP + 0.012, 1.25);
    salaHotspot(pool);
    salaGroup.add(pool);
  };
  buildSalas3D();

  // ── 6. Sincronización y deambular de Axolotitos ──
  const syncAxolotitos = () => {
    clearGroup(visitorsGroup);

    const activeIds = new Set<string>();
    const axos = lastAxolotitosData.filter((a) => !a.isEgg).slice(0, 4);

    const FLOOR = TOP + 0.1;
    const wanderTarget = () => {
      const a = rand(0, Math.PI * 2);
      const rr = Math.sqrt(rand(0, 1));
      return new THREE.Vector3(Math.cos(a) * rr * 2.2, FLOOR, 2.2 + Math.sin(a) * rr * 1.0);
    };

    const visitors: Array<{
      b: AxolotitoBillboard;
      target: THREE.Vector3;
      speed: number;
      pause: number;
    }> = [];

    axos.forEach((axo, idx) => {
      const b = new AxolotitoBillboard(axo, 0.75);
      b.position.copy(wanderTarget());
      b.userData.stallId = "podio"; // tocar un axolotl redirige a podium/glory
      hotspots.push(b);
      billboards.push(b);
      visitorsGroup.add(b);

      visitors.push({
        b,
        target: wanderTarget(),
        speed: rand(0.4, 0.65),
        pause: rand(0, 2.5),
      });
    });

    // Loop de locomoción para transeúntes
    const animId = (t: number, dt: number) => {
      for (const v of visitors) {
        if (v.pause > 0) {
          v.pause -= dt;
          v.b.position.y = FLOOR;
          if (v.pause <= 0) v.target = wanderTarget();
          v.b.setWalk(0, 1);
          continue;
        }

        const dx = v.target.x - v.b.position.x;
        const dz = v.target.z - v.b.position.z;
        const dist = Math.hypot(dx, dz);

        if (dist < 0.08) {
          v.pause = rand(1.0, 3.0);
          v.b.setWalk(0, 1);
          continue;
        }

        const step = Math.min(dist, v.speed * dt);
        v.b.position.x += (dx / dist) * step;
        v.b.position.z += (dz / dist) * step;
        // Caminata saltarina
        v.b.position.y = FLOOR + Math.abs(Math.sin(t * 7.5 + v.speed * 20)) * 0.04;
        v.b.setWalk(dx, dz);
      }
    };

    animations.push(animId);
  };

  // Loop general de actualización de billboards de rankings
  animations.push((t, dt) => {
    for (const b of billboards) {
      b.update(t, dt);
    }
  });

  // Guirnaldas de papel picado
  const flags: THREE.Mesh[] = [];
  const flagCols = [PAL.magenta, PAL.teal, PAL.rosa, PAL.amarillo, 0xe87ad0];
  function garland(x0: number, x1: number, z: number, y0: number, sag: number, n: number, scale = 0.9): void {
    for (let i = 0; i < n; i++) {
      const tt = (i + 0.5) / n;
      const c = flagCols[i % flagCols.length];
      const f = paper(ellipseShape(0.38 * scale, 0.28 * scale), 0.015, c, 0.004);
      (f.material as THREE.MeshStandardMaterial).side = THREE.DoubleSide;
      f.castShadow = false;
      f.rotation.x = 0;
      f.position.set(x0 + (x1 - x0) * tt, y0 - Math.sin(Math.PI * tt) * sag, z);
      f.userData.phase = rand(0, 6);
      flags.push(f);
      backgroundGroup.add(f);
    }
  }
  garland(-4.0, 0.0, -5.2, TOP + 3.8, 0.6, 5);
  garland(0.0, 4.0, -5.2, TOP + 3.8, 0.6, 5);
  garland(-3.2, 3.2, -4.2, TOP + 3.0, 0.5, 6);

  animations.push((t) => {
    for (const f of flags) {
      f.rotation.z = Math.sin(t * 1.2 + (f.userData.phase as number)) * 0.05;
    }
  });

  const stallFocus: Record<string, StallFocus> = {
    "podio": { x: 0, z: -1.6, zoom: 0.65 },
    "gashapon": { x: 0, z: 0.8, zoom: 0.72 },
    "salas": { x: 0, z: 1.0, zoom: 0.68 },
  };

  const scene3D: World3DScene & {
    setPodio(data: AxolotitoData[]): void;
    setAxolotitos(data: AxolotitoData[]): void;
  } = {
    group: world,
    hotspots,
    animations,
    stallFocus,
    billboards,

    setPodio(data: AxolotitoData[]) {
      lastPodioData = data;
      buildRankingsPodio();
    },

    setAxolotitos(data: AxolotitoData[]) {
      lastAxolotitosData = data;
      syncAxolotitos();
    },

    dispose() {
      world.traverse((obj) => {
        const mesh = obj as THREE.Mesh;
        if (mesh.geometry) mesh.geometry.dispose();
        const mats = Array.isArray(mesh.material) ? mesh.material : mesh.material ? [mesh.material] : [];
        for (const m of mats) {
          (m as THREE.MeshBasicMaterial).map?.dispose();
          m.dispose();
        }
      });
    },
  };

  return scene3D;
}
