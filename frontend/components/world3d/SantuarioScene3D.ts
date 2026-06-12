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
import type { AmigoData } from "@/services/mapBackendAxolotito";
import type { CaveStatusData, DecoracionesData, DecorItemDetail } from "../world/zones/santuario/santuarioTypes";

// Posicionamiento de slots de nidos en 3D (4 en fila trasera, 4 en fila delantera)
const NEST_SLOTS_X = [-2.5, -0.8, 0.8, 2.5];
function nestSlotPos3D(i: number): THREE.Vector3 {
  const isBackRow = i < 4;
  return new THREE.Vector3(
    NEST_SLOTS_X[i % 4],
    isBackRow ? 2.6 : 1.9,
    isBackRow ? -4.2 : -2.8
  );
}

// Anclas para decoración de la sala en 3D
const SALA_DECOR_ANCHORS: Record<string, ReadonlyArray<readonly [number, number, number]>> = {
  AMBIENTE: [[-3.0, 1.4, 0.0]],
  LUZ: [[0.0, 4.2, -0.5]],
  MESA: [[-1.2, 1.6, 0.5]],
  MANTEL: [[0.0, 1.6, 0.7]],
  SILLAS: [[1.2, 1.6, 0.5]],
  FONDO: [
    [-3.2, 1.4, -1.2],
    [3.2, 1.4, -1.2],
  ],
  ESPECIAL: [
    [-2.2, 1.4, 0.8],
    [2.2, 1.4, 0.8],
  ],
};

function parseHexColor(color: string | null | undefined, fallback: number): number {
  if (!color) return fallback;
  const n = parseInt(color.replace("#", ""), 16);
  return Number.isNaN(n) ? fallback : n;
}

interface PuppetEntry3D {
  billboard: AxolotitoBillboard;
  mode: "sala" | "toBed" | "inBed" | "toSala";
  bedPos: THREE.Vector3;
  salaTarget: THREE.Vector3;
  pauseTimer: number;
  speed: number;
  swimPhase: number;
  particleTimer: number;
}

interface TrajineraEntry3D {
  group: THREE.Group;
  baseX: number;
  baseY: number;
  baseZ: number;
  angle: number;
  phase: number;
  amigoId: string;
}

interface Particle3D {
  mesh: THREE.Object3D;
  vy: number;
  life: number;
  maxLife: number;
  wobbleSpeed: number;
  wobbleAmp: number;
  seed: number;
}

export function buildSantuarioScene3D(
  opts: { visitantes?: any[] } = {}
): World3DScene & {
  setAxolotitos(data: AxolotitoData[]): void;
  setCaveStatus(status: CaveStatusData): void;
  setDecoraciones(data: DecoracionesData): void;
  setAmigos(amigos: AmigoData[]): void;
  toggleActionBubbles(amigoId: string): void;
} {
  const world = new THREE.Group();
  const animations: SceneAnimation[] = [];
  const hotspots: THREE.Object3D[] = [];
  const billboards: AxolotitoBillboard[] = [];

  // Subgrupos para organización y actualización dinámica
  const backgroundGroup = new THREE.Group();
  const nestGroup = new THREE.Group();
  const salaGroup = new THREE.Group();
  const amigosGroup = new THREE.Group();
  const particleGroup = new THREE.Group();
  const puppetsGroup = new THREE.Group();

  world.add(backgroundGroup);
  world.add(nestGroup);
  world.add(salaGroup);
  world.add(amigosGroup);
  world.add(particleGroup);
  world.add(puppetsGroup);

  // Estados locales para sincronización
  let lastAxolotitos: AxolotitoData[] = [];
  let caveStatus: CaveStatusData = { level: 1, spots: 1, hasTable: false, tableSeats: 0 };
  let decoraciones: DecoracionesData | null = null;
  let amigosList: AmigoData[] = [];

  const puppets = new Map<string, PuppetEntry3D>();
  const activeTrajineras: TrajineraEntry3D[] = [];
  const particles: Particle3D[] = [];

  let activeFriendId: string | null = null;
  let actionBubbleGroup: THREE.Group | null = null;
  let actionBubblesTimer: NodeJS.Timeout | null = null;

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
    { w: 18.8, c: 0x0b233a, h: 0.15, b: 0.015 },
    { w: 18.2, c: 0x103d5c, h: 0.15, b: 0.015 },
    { w: 17.8, c: 0x145275, h: 0.12, b: 0.015 },
  ];
  for (const L of baseLayers) {
    const m = paper(roundedRectShape(L.w, L.w * 1.34, 2.4), L.h, L.c, L.b);
    m.position.y = baseY;
    backgroundGroup.add(m);
    baseY += L.h;
  }
  const TOP = baseY; // Nivel de la superficie del agua

  // Resplandor del agua
  const topWaterMesh = backgroundGroup.children[3] as THREE.Mesh & { material: THREE.MeshStandardMaterial };
  topWaterMesh.material.emissive = new THREE.Color(0x0a6b8c);

  // Corrientes de agua sutiles
  const streaks: THREE.Mesh[] = [];
  for (let i = 0; i < 18; i++) {
    const st = paper(ellipseShape(rand(0.6, 1.5), rand(0.06, 0.1)), 0.02, 0x5bc0be, 0.008);
    st.castShadow = false;
    const stMat = st.material as THREE.MeshStandardMaterial;
    stMat.transparent = true;
    stMat.opacity = 0.45;
    st.position.set(rand(-7, 7), TOP + 0.005, rand(-6, 7.5));
    st.rotation.z = rand(-0.3, 0.3);
    st.userData.phase = rand(0, 6);
    streaks.push(st);
    backgroundGroup.add(st);
  }

  // Animación del agua
  animations.push((t, dt) => {
    backgroundGroup.children[1].position.x = Math.sin(t * 0.35) * 0.06;
    backgroundGroup.children[1].position.z = Math.cos(t * 0.25) * 0.05;
    backgroundGroup.children[2].position.x = Math.sin(t * 0.45 + 1.0) * 0.09;
    backgroundGroup.children[2].position.z = Math.cos(t * 0.4 + 0.5) * 0.07;
    backgroundGroup.children[3].position.x = Math.sin(t * 0.55 + 2.0) * 0.12;
    backgroundGroup.children[3].position.z = Math.cos(t * 0.5 + 1.2) * 0.08;

    const waterGlow = 0.8 + Math.sin(t * 0.85) * 0.15;
    topWaterMesh.material.emissive.setHex(0x0a6b8c).multiplyScalar(waterGlow);

    for (const s of streaks) {
      const phase = s.userData.phase as number;
      s.position.x += dt * 0.22;
      s.position.z += Math.sin(t * 1.4 + phase) * 0.002;
      if (s.position.x > 8.5) {
        s.position.x = -8.5;
        s.position.z = rand(-6, 7.5);
      }
      (s.material as THREE.MeshStandardMaterial).opacity = 0.2 + Math.sin(t * 0.75 + phase) * 0.15;
    }
  });

  // Rocas y paredes de la cueva (Laterales y fondo)
  // Fondo alto para la crianza
  terraceStack(backgroundGroup, TOP, 0.0, -6.5, 3.8, 6, [0x0c2540, 0x103d5c, 0x145275, 0x1f5f66, 0x2e7d7a], 0.28, 0.12, 0.55);
  // Lados que cierran el cenote
  terraceStack(backgroundGroup, TOP, -5.2, -2.5, 2.0, 5, [0x0c2540, 0x103d5c, 0x145275], 0.35, 0.18, 0.6);
  terraceStack(backgroundGroup, TOP, 5.2, -2.5, 2.0, 5, [0x0c2540, 0x103d5c, 0x145275], 0.35, 0.18, 0.6);
  terraceStack(backgroundGroup, TOP, -5.5, 2.5, 1.8, 4, [0x103d5c, 0x145275], 0.35, 0.2);
  terraceStack(backgroundGroup, TOP, 5.5, 2.5, 1.8, 4, [0x103d5c, 0x145275], 0.35, 0.2);

  // Plantas bioluminiscentes colgantes
  plant(backgroundGroup, TOP + 1.2, -4.5, -4.5, 0x3ee8c0, 1.4, 0.6);
  plant(backgroundGroup, TOP + 1.2, 4.5, -4.5, 0x9b6df0, 1.4, 0.6);
  plant(backgroundGroup, TOP + 0.6, -4.8, 0.5, 0xe87ad0, 1.2, 0.45);
  plant(backgroundGroup, TOP + 0.6, 4.8, 0.5, 0x3ee8c0, 1.2, 0.45);

  // ── 2. Sala central (La Plataforma de Madera) ──
  const buildSalaPlatform = () => {
    clearGroup(salaGroup);

    const platShape = roundedRectShape(7.2, 3.4, 0.6);
    const plat = paper(platShape, 0.32, 0x8b5e34, 0.04);
    plat.position.set(0, TOP + 0.9, -0.6);
    salaGroup.add(plat);

    // Mesa de juego
    const decor = decoraciones;
    const itemAt = (slotId: string): DecorItemDetail | null => {
      const itemId = decor?.decorations?.[slotId];
      if (itemId === null || itemId === undefined) return null;
      return decor?.items?.[String(itemId)] ?? null;
    };

    const mesaItem = itemAt("MESA_0");
    const mantelItem = itemAt("MANTEL_0");
    const sillasItem = itemAt("SILLAS_0");

    const mesaColor = parseHexColor(mesaItem?.color, 0xa9743f);
    const boardShape = ellipseShape(1.2, 0.7);
    const tableBoard = paper(boardShape, 0.12, mesaColor, 0.02);
    tableBoard.position.set(0, TOP + 1.22 + 0.15, -0.6);
    tableBoard.userData.stallId = "mesa-amigos";
    hotspots.push(tableBoard);
    salaGroup.add(tableBoard);

    if (mantelItem) {
      const mantelColor = parseHexColor(mantelItem.color, 0xe4007c);
      const mantelShape = ellipseShape(0.9, 0.5);
      const mantel = paper(mantelShape, 0.03, mantelColor, 0.015);
      mantel.position.set(0, TOP + 1.22 + 0.21, -0.6);
      mantel.userData.stallId = "mesa-amigos";
      hotspots.push(mantel);
      salaGroup.add(mantel);
    }

    if (caveStatus.hasTable && caveStatus.tableSeats > 0) {
      const sillaColor = parseHexColor(sillasItem?.color, 0x8b5e34);
      const numSillas = Math.min(caveStatus.tableSeats, 8);
      for (let i = 0; i < numSillas; i++) {
        const ang = (i / numSillas) * Math.PI * 2;
        const silla = cyl(0.18, 0.2, 0.32, sillaColor);
        silla.position.set(Math.cos(ang) * 1.5, TOP + 1.22 + 0.16, -0.6 + Math.sin(ang) * 0.95);
        silla.castShadow = true;
        silla.receiveShadow = true;
        silla.userData.stallId = "mesa-amigos";
        hotspots.push(silla);
        salaGroup.add(silla);
      }
    }

    // Chips de slots de decoración
    if (!decor) return;
    const idxBySubcat = new Map<string, number>();
    for (const slot of decor.slots) {
      const anchors = SALA_DECOR_ANCHORS[slot.subcategory];
      const idx = idxBySubcat.get(slot.subcategory) ?? 0;
      idxBySubcat.set(slot.subcategory, idx + 1);
      const anchor = anchors?.[idx];
      if (!anchor) continue;

      const equipped = itemAt(slot.slot_id);
      const pos = new THREE.Vector3(anchor[0], TOP + anchor[1], anchor[2]);
      
      const chipGroup = new THREE.Group();
      chipGroup.position.copy(pos);

      if (equipped) {
        // Pedestal de piedra para decoración
        const ped = cyl(0.24, 0.26, 0.18, 0x4a5d6e);
        ped.position.y = 0.09;
        ped.castShadow = true;
        ped.receiveShadow = true;
        chipGroup.add(ped);

        const icon = textPlane(equipped.emoji || "🏺", 0.46, "#fff");
        icon.position.set(0, 0.35, 0);
        chipGroup.add(icon);
      } else {
        // Círculo plano transparente con "+" discreto
        const ringGeo = new THREE.RingGeometry(0.16, 0.18, 16);
        const ringMat = new THREE.MeshBasicMaterial({ color: 0xfff7ec, transparent: true, opacity: 0.4 });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = -Math.PI / 2;
        ring.position.y = 0.01;
        chipGroup.add(ring);

        const plus = textPlane("➕", 0.32, "#fff");
        plus.position.set(0, 0.22, 0);
        chipGroup.add(plus);
      }

      chipGroup.traverse((child) => {
        child.userData.stallId = "decor:" + slot.slot_id;
        if (child.userData.stallId) hotspots.push(child);
      });

      salaGroup.add(chipGroup);
    }
  };

  // ── 3. Nidos e incubadora (Crianza, Terraza Superior) ──
  const buildNests3D = () => {
    clearGroup(nestGroup);

    const eggs = lastAxolotitos.filter((a) => a.isEgg);
    const axos = lastAxolotitos.filter((a) => !a.isEgg);
    const spots = Math.max(1, Math.min(caveStatus.spots, 8));

    for (let slot = 0; slot < 8; slot++) {
      const pos = nestSlotPos3D(slot);
      const isBackRow = slot < 4;
      const slotY = pos.y + TOP;

      if (slot >= spots) {
        // Slot bloqueado: roca con candado
        const rock = cyl(0.38, 0.38, 0.35, 0x2e3c45);
        rock.position.set(pos.x, slotY + 0.175, pos.z);
        rock.castShadow = true;
        rock.receiveShadow = true;
        rock.userData.stallId = "nido-bloqueado";
        hotspots.push(rock);
        nestGroup.add(rock);

        const lock = textPlane("🔒", 0.3, "#fff");
        lock.position.set(pos.x, slotY + 0.42, pos.z + 0.08);
        lock.userData.stallId = "nido-bloqueado";
        hotspots.push(lock);
        nestGroup.add(lock);
      } else {
        const egg = eggs.find((e) => e.caveIndex === slot);
        const owner = axos.find((a) => a.caveIndex === slot);

        const nestBase = new THREE.Mesh(
          new THREE.TorusGeometry(0.28, 0.08, 8, 14),
          paperMat(0x8a6d4e)
        );
        nestBase.rotation.x = -Math.PI / 2;
        nestBase.position.set(pos.x, slotY + 0.04, pos.z);
        nestBase.castShadow = true;
        nestBase.receiveShadow = true;
        
        let slotId = "nido-vacio";
        if (egg) slotId = "nido-huevo:" + egg.id;
        else if (owner) slotId = "nido-axo:" + owner.id;

        nestBase.userData.stallId = slotId;
        hotspots.push(nestBase);
        nestGroup.add(nestBase);

        if (egg) {
          // Huevo 3D
          const eggColor = skinToTint(egg.skinColor);
          const eggGeo = new THREE.SphereGeometry(0.18, 12, 10);
          const eggMat = paperMat(eggColor);
          eggMat.emissive = new THREE.Color(eggColor).multiplyScalar(0.15);
          
          const eggMesh = new THREE.Mesh(eggGeo, eggMat);
          eggMesh.scale.y = 1.35;
          eggMesh.position.set(pos.x, slotY + 0.18, pos.z);
          eggMesh.castShadow = true;
          eggMesh.userData.stallId = slotId;
          hotspots.push(eggMesh);
          nestGroup.add(eggMesh);
        } else if (owner) {
          // Camita/Cuna para axolotito nacido
          const mattress = box(0.65, 0.12, 0.55, 0xfff7ec);
          mattress.position.set(pos.x, slotY + 0.06, pos.z);
          mattress.castShadow = true;
          mattress.userData.stallId = slotId;
          hotspots.push(mattress);
          nestGroup.add(mattress);

          const pillow = box(0.16, 0.07, 0.44, 0xffcccc);
          pillow.position.set(pos.x - 0.22, slotY + 0.14, pos.z);
          pillow.userData.stallId = slotId;
          hotspots.push(pillow);
          nestGroup.add(pillow);

          const blanket = box(0.42, 0.04, 0.51, 0x99ccff);
          blanket.position.set(pos.x + 0.1, slotY + 0.1, pos.z);
          blanket.userData.stallId = slotId;
          hotspots.push(blanket);
          nestGroup.add(blanket);

          // Nombre sobre la camita
          const namePlate = textPlane(owner.name, 0.15, "#fff7ec");
          namePlate.position.set(pos.x, slotY + 0.35, pos.z + 0.05);
          nestGroup.add(namePlate);
        }
      }
    }
  };

  // ── 4. Embarcadero y Trajineritas (Frente) ──
  const buildEmbarcadero3D = () => {
    clearGroup(amigosGroup);
    activeTrajineras.length = 0;

    // Muelle de madera
    for (let i = 0; i < 5; i++) {
      const plank = box(0.42, 0.08, 1.8, i % 2 ? 0x9c6b3f : 0xc59a64);
      plank.position.set(-1.0 + i * 0.46, TOP + 0.08, 3.6);
      dockHotspot(plank);
      amigosGroup.add(plank);
    }
    // Pilotes del muelle
    for (const [px, pz] of [[-1.1, 2.8], [1.1, 2.8], [-1.1, 4.4], [1.1, 4.4]] as const) {
      const pile = cyl(0.08, 0.09, 0.65, 0x7a4e2c, 8);
      pile.position.set(px, TOP + 0.24, pz);
      dockHotspot(pile);
      amigosGroup.add(pile);
    }

    // Canasta de mimbre para abrir amigos
    const basket = cyl(0.24, 0.2, 0.28, 0xa9743f);
    basket.position.set(0.9, TOP + 0.26, 3.2);
    basket.castShadow = true;
    dockHotspot(basket);
    amigosGroup.add(basket);

    const basketHandle = new THREE.Mesh(
      new THREE.TorusGeometry(0.18, 0.035, 6, 12, Math.PI),
      paperMat(0x8b5e34)
    );
    basketHandle.position.set(0.9, TOP + 0.4, 3.2);
    dockHotspot(basketHandle);
    amigosGroup.add(basketHandle);

    const basketTag = textPlane("🧺 Amigos", 0.2, "#fff7ec");
    basketTag.position.set(0.9, TOP + 0.54, 3.2);
    basketTag.userData.stallId = "canasta-amigos";
    hotspots.push(basketTag);
    amigosGroup.add(basketTag);

    // Trajineritas de amigos
    const visibles = amigosList.slice(0, 4);
    visibles.forEach((amigo, i) => {
      const baseX = -2.3 + i * 1.5;
      const baseZ = 4.7 + (i % 2) * 0.45;
      const angle = i % 2 === 0 ? 0.12 : -0.12;

      const boat = new THREE.Group();
      boat.position.set(baseX, TOP, baseZ);
      boat.rotation.y = angle;

      // Casco
      const hull = box(1.15, 0.18, 0.46, 0x8b5e34);
      hull.position.y = 0.09;
      hull.castShadow = true;
      boat.add(hull);

      // Toldo de color
      const roofColor = amigo.isOnline ? 0xe04a7a : 0x7fa86e;
      const roof = box(0.95, 0.06, 0.42, roofColor);
      roof.position.y = 0.54;
      roof.castShadow = true;
      boat.add(roof);

      // Postes toldo
      for (const [sx, sz] of [[-0.42, -0.16], [0.42, -0.16], [-0.42, 0.16], [0.42, 0.16]] as const) {
        const stick = cyl(0.02, 0.02, 0.46, 0xfff7ec);
        stick.position.set(sx, 0.3, sz);
        boat.add(stick);
      }

      // Punto online/offline
      const dot = cyl(0.035, 0.035, 0.06, amigo.isOnline ? 0x6cc06a : 0x6b7080);
      dot.rotation.x = Math.PI / 2;
      dot.position.set(0.52, 0.12, 0);
      boat.add(dot);

      // Nombre tag
      const tag = textPlane(amigo.nickname, 0.16, "#fff7ec");
      tag.position.set(0, 0.68, 0);
      boat.add(tag);

      // Registrar hotspot local de trajinera
      boat.traverse((child) => {
        child.userData.stallId = "trajinera:" + amigo.id;
        if (child.userData.stallId) hotspots.push(child);
      });

      amigosGroup.add(boat);
      activeTrajineras.push({
        group: boat,
        baseX,
        baseY: TOP,
        baseZ,
        angle,
        phase: i * 1.3,
        amigoId: amigo.id,
      });
    });
  };

  const dockHotspot = (mesh: THREE.Object3D) => {
    mesh.userData.stallId = "canasta-amigos";
    hotspots.push(mesh);
  };

  // ── 5. Partículas (Polvito, Zzz y Burbujas) ──
  const spawnParticle3D = (textOrEmoji: string, pos: THREE.Vector3, vy: number, maxLife: number, color = "#fff7ec") => {
    const mesh = textPlane(textOrEmoji, 0.22, color);
    mesh.position.copy(pos);
    particleGroup.add(mesh);

    particles.push({
      mesh,
      vy,
      life: 0,
      maxLife,
      wobbleSpeed: 4 + Math.random() * 4,
      wobbleAmp: 0.08 + Math.random() * 0.08,
      seed: Math.random() * 10,
    });
  };

  animations.push((t, dt) => {
    // Actualización de partículas
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.life += dt;
      if (p.life >= p.maxLife) {
        particleGroup.remove(p.mesh);
        p.mesh.traverse((child) => {
          if ((child as THREE.Mesh).geometry) (child as THREE.Mesh).geometry.dispose();
        });
        particles.splice(i, 1);
      } else {
        p.mesh.position.y += p.vy * dt;
        p.mesh.position.x += Math.sin(t * p.wobbleSpeed + p.seed) * p.wobbleAmp * dt;
        
        const mat = (p.mesh as THREE.Mesh).material as THREE.MeshBasicMaterial;
        mat.transparent = true;
        mat.opacity = 1.0 - (p.life / p.maxLife);
      }
    }
  });

  // ── 6. Sincronización y locomoción de Axolotitos Billboards ──
  const syncAxolotitoBillboards = () => {
    const activeIds = new Set<string>();
    const axos = lastAxolotitos.filter((a) => !a.isEgg);

    for (const axo of axos) {
      activeIds.add(axo.id);
      let entry = puppets.get(axo.id);
      
      const isSleeping = axo.energy === 0 || axo.state === "sleeping";
      const nestPos = nestSlotPos3D(Math.min(Math.max(axo.caveIndex, 0), 7));
      const bedPos = new THREE.Vector3(nestPos.x, nestPos.y + TOP + 0.16, nestPos.z);
      
      if (!entry) {
        // Crear nuevo títere
        const b = new AxolotitoBillboard(axo, 0.9);
        const salaTarget = new THREE.Vector3(rand(-2.2, 2.2), TOP + 1.22 + 0.16, rand(-1.2, 1.2));
        
        if (isSleeping) {
          b.position.copy(bedPos);
        } else {
          b.position.copy(salaTarget);
        }
        
        puppetsGroup.add(b);
        billboards.push(b);

        entry = {
          billboard: b,
          mode: isSleeping ? "inBed" : "sala",
          bedPos,
          salaTarget,
          pauseTimer: rand(1.0, 3.0),
          speed: rand(0.5, 0.8),
          swimPhase: Math.random() * Math.PI,
          particleTimer: Math.random() * 2.0,
        };
        puppets.set(axo.id, entry);
      } else {
        // Actualizar estados
        entry.bedPos.copy(bedPos);
        
        if (isSleeping && (entry.mode === "sala" || entry.mode === "toSala")) {
          entry.mode = "toBed";
        } else if (!isSleeping && (entry.mode === "inBed" || entry.mode === "toBed")) {
          entry.mode = "toSala";
          entry.salaTarget.set(rand(-2.2, 2.2), TOP + 1.22 + 0.16, rand(-1.2, 1.2));
        }
      }
    }

    // Remover axolotitos obsoletos
    for (const [id, entry] of puppets.entries()) {
      if (!activeIds.has(id)) {
        puppetsGroup.remove(entry.billboard);
        const bIdx = billboards.indexOf(entry.billboard);
        if (bIdx > -1) billboards.splice(bIdx, 1);
        puppets.delete(id);
      }
    }
  };

  // Loop de locomoción y Zzz de axolotitos
  animations.push((t, dt) => {
    const platformY = TOP + 1.22 + 0.16;

    for (const entry of puppets.values()) {
      const { billboard } = entry;
      entry.particleTimer -= dt;

      // Zzz y burbujas periódicas
      if (entry.particleTimer <= 0) {
        if (entry.mode === "inBed") {
          spawnParticle3D("💤", new THREE.Vector3(billboard.position.x + 0.14, billboard.position.y + 0.42, billboard.position.z), 0.35, 1.8, "#a8d3e8");
          entry.particleTimer = 1.6 + Math.random() * 0.8;
        } else if (entry.mode === "toBed" || entry.mode === "toSala") {
          spawnParticle3D("🫧", billboard.position, 0.45, 1.0, "#a8e4e0");
          entry.particleTimer = 0.35 + Math.random() * 0.4;
        } else if (entry.mode === "sala" && entry.billboard.position.distanceTo(entry.salaTarget) > 0.2) {
          spawnParticle3D("✨", new THREE.Vector3(billboard.position.x, billboard.position.y - 0.08, billboard.position.z), 0.18, 0.55, "#e8d3a8");
          entry.particleTimer = 0.5 + Math.random() * 0.5;
        } else {
          entry.particleTimer = 1.0 + Math.random();
        }
      }

      switch (entry.mode) {
        case "sala": {
          const dist = billboard.position.distanceTo(entry.salaTarget);
          if (dist < 0.15) {
            entry.pauseTimer -= dt;
            billboard.setState("idle");
            billboard.setWalk(0, 1); // De frente si reposa
            if (entry.pauseTimer <= 0) {
              entry.salaTarget.set(rand(-2.2, 2.2), platformY, rand(-1.0, 1.0));
              entry.pauseTimer = rand(1.5, 4.0);
              entry.speed = rand(0.45, 0.8);
            }
          } else {
            const dir = new THREE.Vector3().subVectors(entry.salaTarget, billboard.position).normalize();
            billboard.position.addScaledVector(dir, entry.speed * dt);
            billboard.position.y = platformY; // el ciclo de caminado vive en el billboard
            billboard.setState("walk");
            billboard.setWalk(dir.x, dir.z);
          }
          break;
        }
        case "toBed": {
          const dist = billboard.position.distanceTo(entry.bedPos);
          if (dist < 0.15) {
            billboard.position.copy(entry.bedPos);
            entry.mode = "inBed";
          } else {
            const dir = new THREE.Vector3().subVectors(entry.bedPos, billboard.position).normalize();
            billboard.position.addScaledVector(dir, 1.6 * dt);
            billboard.setState("swim"); // ondulación interna del billboard
            billboard.setWalk(dir.x, dir.z);
          }
          break;
        }
        case "toSala": {
          const dist = billboard.position.distanceTo(entry.salaTarget);
          if (dist < 0.15) {
            billboard.position.copy(entry.salaTarget);
            entry.mode = "sala";
            entry.pauseTimer = rand(0.5, 2.0);
          } else {
            const dir = new THREE.Vector3().subVectors(entry.salaTarget, billboard.position).normalize();
            billboard.position.addScaledVector(dir, 1.6 * dt);
            billboard.setState("swim");
            billboard.setWalk(dir.x, dir.z);
          }
          break;
        }
        case "inBed": {
          billboard.position.copy(entry.bedPos); // respiración interna (sleep)
          billboard.setState("sleep");
          break;
        }
      }
    }
  });

  // Animación del balanceo de las trajineras
  animations.push((t) => {
    for (const tr of activeTrajineras) {
      tr.group.position.y = tr.baseY + Math.sin(t * 1.1 + tr.phase) * 0.04;
      tr.group.rotation.z = Math.sin(t * 0.9 + tr.phase) * 0.022;
      tr.group.rotation.y = tr.angle + Math.cos(t * 0.8 + tr.phase) * 0.015;
    }
  });

  // Enfoques de cámara por zona
  const stallFocus: Record<string, StallFocus> = {
    "mesa-amigos": { x: 0, z: -0.5, zoom: 0.62 },
    "canasta-amigos": { x: 0, z: 3.5, zoom: 0.65 },
    "nidos": { x: 0, z: -4.0, zoom: 0.62 },
  };

  const scene3D: World3DScene & {
    setAxolotitos(data: AxolotitoData[]): void;
    setCaveStatus(status: CaveStatusData): void;
    setDecoraciones(data: DecoracionesData): void;
    setAmigos(amigos: AmigoData[]): void;
    toggleActionBubbles(amigoId: string): void;
  } = {
    group: world,
    hotspots,
    animations,
    stallFocus,
    billboards,
    
    setAxolotitos(data: AxolotitoData[]) {
      lastAxolotitos = data;
      buildNests3D();
      syncAxolotitoBillboards();
    },

    setCaveStatus(status: CaveStatusData) {
      caveStatus = status;
      buildNests3D();
      buildSalaPlatform();
    },

    setDecoraciones(data: DecoracionesData) {
      decoraciones = data;
      buildSalaPlatform();
    },

    setAmigos(amigos: AmigoData[]) {
      amigosList = amigos;
      buildEmbarcadero3D();
    },

    toggleActionBubbles(amigoId: string) {
      if (actionBubbleGroup) {
        world.remove(actionBubbleGroup);
        actionBubbleGroup.traverse((child) => {
          if ((child as THREE.Mesh).geometry) (child as THREE.Mesh).geometry.dispose();
        });
        const hSet = new Set(hotspots);
        actionBubbleGroup.traverse((child) => hSet.delete(child));
        hotspots.length = 0;
        hotspots.push(...hSet);
        actionBubbleGroup = null;
      }

      if (activeFriendId === amigoId) {
        activeFriendId = null;
        return;
      }

      activeFriendId = amigoId;
      const traj = activeTrajineras.find((t) => t.amigoId === amigoId);
      if (!traj) return;

      const group = new THREE.Group();
      group.position.copy(traj.group.position);
      group.position.y += 0.85;

      const actions = [
        { emoji: "❤️", kind: "amigo-like", x: -0.38, y: 0.1 },
        { emoji: "👁", kind: "amigo-visita", x: 0.0, y: 0.24 },
        { emoji: "🎲", kind: "amigo-invita", x: 0.38, y: 0.1 }
      ];

      actions.forEach((act) => {
        const bubble = new THREE.Group();
        bubble.position.set(act.x, act.y, 0.02);

        // Disco de fondo
        const disk = new THREE.Mesh(
          new THREE.CircleGeometry(0.14, 16),
          new THREE.MeshBasicMaterial({ color: 0xfff7ec, side: THREE.DoubleSide })
        );
        bubble.add(disk);

        // Emoji
        const txt = textPlane(act.emoji, 0.18, "#e04a7a");
        txt.position.z = 0.01;
        bubble.add(txt);

        bubble.traverse((child) => {
          child.userData.stallId = act.kind + ":" + amigoId;
          if (child.userData.stallId) hotspots.push(child);
        });

        group.add(bubble);
      });

      world.add(group);
      actionBubbleGroup = group;

      if (actionBubblesTimer) clearTimeout(actionBubblesTimer);
      actionBubblesTimer = setTimeout(() => {
        if (activeFriendId === amigoId) {
          this.toggleActionBubbles(amigoId);
        }
      }, 5000);
    },

    dispose() {
      if (actionBubblesTimer) clearTimeout(actionBubblesTimer);
      
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
