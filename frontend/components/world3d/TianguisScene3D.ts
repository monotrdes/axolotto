import * as THREE from "three";
import type { SceneAnimation, World3DScene, StallFocus } from "./ThreeWorldEngine";
import { AxolotitoBillboard } from "./AxolotitoBillboard";
import {
  PAL,
  blobShape,
  box,
  cyl,
  ellipseShape,
  flat,
  paper,
  picadoShape,
  plant,
  rand,
  roundedRectShape,
  sign,
  terraceStack,
  textPlane,
} from "./paperPrimitives";
import { detectQualityTier } from "./qualityTier";

function createSunRayTexture(): THREE.CanvasTexture {
  const canvas = document.createElement("canvas");
  canvas.width = 64;
  canvas.height = 256;
  const ctx = canvas.getContext("2d")!;
  ctx.clearRect(0, 0, 64, 256);
  
  for (let y = 0; y < 256; y++) {
    const progress = y / 256;
    const width = 10 + progress * 24;
    const alpha = (1 - progress) * 0.42 * Math.sin(Math.PI * (1 - progress * 0.4));
    
    const gradH = ctx.createLinearGradient(32 - width, 0, 32 + width, 0);
    gradH.addColorStop(0, "rgba(255, 255, 220, 0)");
    gradH.addColorStop(0.5, `rgba(255, 255, 245, ${alpha})`);
    gradH.addColorStop(1, "rgba(255, 255, 220, 0)");
    
    ctx.fillStyle = gradH;
    ctx.fillRect(32 - width, y, width * 2, 1);
  }
  
  const tex = new THREE.CanvasTexture(canvas);
  return tex;
}

function createSunRays(parent: THREE.Object3D, topY: number, animations: SceneAnimation[]): void {
  const tex = createSunRayTexture();
  const rayGroup = new THREE.Group();
  
  const rayCount = 4;
  const raysData: Array<{
    mesh: THREE.Mesh;
    baseOpacity: number;
    phase: number;
    speed: number;
  }> = [];
  
  const placements = [
    { x: -3.5, z: -3.0, w: 2.2, h: 10.0, opacity: 0.55 },
    { x: 1.0, z: -1.0, w: 2.8, h: 11.0, opacity: 0.65 },
    { x: 4.5, z: -4.0, w: 2.0, h: 9.0, opacity: 0.50 },
    { x: -1.5, z: 2.5, w: 2.4, h: 10.5, opacity: 0.60 }
  ];
  
  for (let i = 0; i < rayCount; i++) {
    const p = placements[i];
    const geo = new THREE.PlaneGeometry(p.w, p.h);
    const mat = new THREE.MeshBasicMaterial({
      map: tex,
      transparent: true,
      opacity: p.opacity,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      side: THREE.DoubleSide
    });
    
    const mesh = new THREE.Mesh(geo, mat);
    mesh.rotation.z = -0.3; 
    mesh.rotation.x = 0.45;
    mesh.position.set(p.x, topY + p.h * 0.32, p.z);
    
    rayGroup.add(mesh);
    
    raysData.push({
      mesh,
      baseOpacity: p.opacity,
      phase: i * 1.5,
      speed: 0.8 + i * 0.2
    });
  }
  
  parent.add(rayGroup);
  
  animations.push((t) => {
    for (const r of raysData) {
      const mat = r.mesh.material as THREE.MeshBasicMaterial;
      mat.opacity = r.baseOpacity * (0.6 + Math.sin(t * r.speed + r.phase) * 0.4);
    }
  });
}

function createLily(parent: THREE.Object3D, topY: number, x: number, z: number, phase: number, lilies: THREE.Group[]): void {
  const g = new THREE.Group();
  
  const padShape = new THREE.Shape();
  padShape.absarc(0, 0, 0.4, 0, Math.PI * 1.78, false);
  padShape.lineTo(0, 0);
  padShape.closePath();
  
  const pad = paper(padShape, 0.03, 0x3d7e5d, 0.01);
  g.add(pad);
  
  const petalCols = [0xffffff, 0xffd4e5];
  for (let i = 0; i < 4; i++) {
    const petalShape = ellipseShape(0.08, 0.18);
    const petal = paper(petalShape, 0.015, petalCols[i % 2], 0.005);
    petal.rotation.x = 0;
    petal.rotation.y = (i / 4) * Math.PI * 2;
    petal.rotation.z = 0.25;
    petal.position.y = 0.03;
    g.add(petal);
  }
  
  const center = cyl(0.05, 0.05, 0.04, PAL.amarillo);
  center.position.y = 0.03;
  g.add(center);
  
  g.position.set(x, topY + 0.01, z);
  g.userData.phase = phase;
  
  parent.add(g);
  lilies.push(g);
}

function addLantern(
  parent: THREE.Object3D,
  x: number,
  y: number,
  z: number,
  color: number,
  glowIntensity: number,
  quality: string,
  glowingMeshes: THREE.Mesh[]
): void {
  const g = new THREE.Group();
  
  const hanger = box(0.03, 0.35, 0.03, 0x4a2e12);
  hanger.position.y = 0.175;
  g.add(hanger);
  
  const body = cyl(0.15, 0.17, 0.28, color, 6);
  body.position.y = -0.14;
  body.castShadow = true;
  g.add(body);
  
  const coreMat = new THREE.MeshStandardMaterial({
    color: 0xfff7c2,
    roughness: 0.9,
    emissive: new THREE.Color(0xfff7c2).multiplyScalar(glowIntensity)
  });
  const core = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.18, 0.11), coreMat);
  core.position.y = -0.14;
  g.add(core);
  
  core.userData.baseEmissive = coreMat.emissive.clone();
  glowingMeshes.push(core);
  
  const roof = cyl(0.20, 0.04, 0.08, 0x7a4e2c, 6);
  roof.position.y = 0.02;
  roof.castShadow = true;
  g.add(roof);
  
  if (quality !== "ligera") {
    const light = new THREE.PointLight(0xffebb3, 1.8, 4.0);
    light.position.set(0, -0.14, 0);
    light.castShadow = quality === "alta";
    light.shadow.bias = -0.002;
    g.add(light);
  }
  
  g.position.set(x, y, z);
  parent.add(g);
}

/**
 * Tianguis 3D — port del prototipo aprobado (docs/prototipos/tianguis_demo_3d.html,
 * VoBo usuario 2026-06-12) al estilo del concept art: diorama de papel extruido,
 * río cyan dominante, plaza de arena, 5 puestos con tendero visible (toldos
 * altos, cámara 34°).
 *
 * Ids de hotspot compatibles con el cableado existente de page.tsx
 * (onStallClick): fountain=Banco, forja=El Reciclón (la forja se rediseñó
 * como Reciclón), booster=Venta de Sobrecitos, adopcion=Webitos Adopción,
 * p2p=Trajineras P2P.
 *
 * Cada puesto expone un ancla vacía `attendant:<id>` donde irá el axolotito
 * billboard 2D que lo atiende (siguiente fase).
 */

export interface TianguisVisitor {
  skinColor?: string;
  seed?: number;
}

export function buildTianguisScene3D(
  opts: { visitantes?: TianguisVisitor[] } = {},
): World3DScene {
  const world = new THREE.Group();
  const animations: SceneAnimation[] = [];
  const hotspots: THREE.Object3D[] = [];
  const quality = detectQualityTier();
  const glowingMeshes: THREE.Mesh[] = [];

  const markStall = (g: THREE.Object3D, stallId: string) => {
    g.userData.stallId = stallId;
    hotspots.push(g);
  };
  const attendantAnchor = (parent: THREE.Object3D, id: string, x: number, y: number, z: number) => {
    const a = new THREE.Group();
    a.name = `attendant:${id}`;
    a.position.set(x, y, z);
    parent.add(a);
  };

  // ── Base de agua en capas delgadas (estilo papel picado concept art) ──
  const base = new THREE.Group();
  let baseY = 0;
  const baseLayers = [
    { w: 19.5, c: 0x241e3c, h: 0.15, b: 0.015 },
    { w: 18.8, c: 0x123f55, h: 0.15, b: 0.015 },
    { w: 18.2, c: PAL.aguaProfunda, h: 0.15, b: 0.015 },
    { w: 17.8, c: PAL.agua, h: 0.12, b: 0.015 },
  ];
  for (const L of baseLayers) {
    const m = paper(roundedRectShape(L.w, L.w * 1.34, 2.4), L.h, L.c, L.b);
    m.position.y = baseY;
    base.add(m);
    baseY += L.h;
  }
  const TOP = baseY;
  // el agua emite un poco de luz propia (cyan vivo de la referencia)
  const topWaterMesh = base.children[3] as THREE.Mesh & { material: THREE.MeshStandardMaterial };
  topWaterMesh.material.emissive = new THREE.Color(0x0a8da3); // Cyan-azul más vivo y limpio, menos verdoso
  world.add(base);

  // Desplazamiento relativo de las capas de agua (parallax de papel) + pulso de color del agua
  const baseEmissiveColor = new THREE.Color(0x0a8da3);
  animations.push((t) => {
    base.children[1].position.x = Math.sin(t * 0.4) * 0.08;
    base.children[1].position.z = Math.cos(t * 0.3) * 0.06;
    
    base.children[2].position.x = Math.sin(t * 0.5 + 1.0) * 0.12;
    base.children[2].position.z = Math.cos(t * 0.45 + 0.5) * 0.08;
    
    base.children[3].position.x = Math.sin(t * 0.6 + 2.0) * 0.15;
    base.children[3].position.z = Math.cos(t * 0.55 + 1.2) * 0.10;

    const waterGlow = 0.85 + Math.sin(t * 0.9) * 0.15;
    topWaterMesh.material.emissive.copy(baseEmissiveColor).multiplyScalar(waterGlow);
  });

  // Corrientes del río: vetas claras onduladas con flujo continuo hacia la derecha
  const streaks: THREE.Mesh[] = [];
  for (let i = 0; i < 26; i++) {
    const st = paper(ellipseShape(rand(0.7, 1.9), rand(0.07, 0.12)), 0.02, PAL.aguaClara, 0.008);
    st.castShadow = false;
    const stMat = st.material as THREE.MeshStandardMaterial;
    stMat.transparent = true;
    stMat.opacity = 0.5;
    st.position.set(rand(-8, 8), TOP + 0.005, rand(-7, 8.6));
    st.rotation.z = rand(-0.4, 0.4);
    st.userData.phase = rand(0, 6);
    streaks.push(st);
    world.add(st);
  }
  animations.push((t, dt) => {
    for (const s of streaks) {
      const phase = s.userData.phase as number;
      // Flujo continuo hacia la derecha (X positivo)
      s.position.x += dt * 0.28;
      // Ondulación en Z
      s.position.z += Math.sin(t * 1.6 + phase) * 0.003;
      // Re-envolver al salir del diorama
      if (s.position.x > 9.5) {
        s.position.x = -9.5;
        s.position.z = rand(-7, 8.6);
      }
      (s.material as THREE.MeshStandardMaterial).opacity = 0.25 + Math.sin(t * 0.8 + phase) * 0.15;
    }
  });

  // ── Colinas del fondo y rocas laterales ───────────────────────
  // cordillera trasera: gradiente del concept (teal en la base → durazno →
  // arena → crema en las cumbres), capas más altas para más presencia
  terraceStack(world, TOP, -2.6, -7.6, 2.3, 6, [PAL.tealRoca, PAL.durazno, PAL.arenaCalida, PAL.arena, PAL.crema, PAL.blanco], 0.3, 0.14, 0.5);
  terraceStack(world, TOP, 0.6, -8.0, 2.7, 7, [PAL.tealOscuro, PAL.tealRoca, PAL.durazno, PAL.arenaCalida, PAL.arena, PAL.crema, PAL.blanco], 0.3, 0.12, 0.5);
  terraceStack(world, TOP, 3.4, -7.4, 2.1, 6, [PAL.tealRoca, PAL.durazno, PAL.arenaCalida, PAL.arena, PAL.crema, PAL.blanco], 0.3, 0.15, 0.5);
  terraceStack(world, TOP, -5.0, -6.6, 1.9, 6, [PAL.tealRoca, PAL.salvia, PAL.oliva], 0.24, 0.18, 0.6);
  terraceStack(world, TOP, 5.6, -6.2, 1.8, 5, [PAL.oliva, PAL.tealRoca, PAL.salvia], 0.24, 0.18, 0.6);
  terraceStack(world, TOP, -4.6, -3.6, 1.3, 6, [PAL.tealOscuro, PAL.tealRoca, PAL.salvia], 0.2, 0.2);
  terraceStack(world, TOP, -6.4, 0.6, 1.7, 4, [PAL.salvia, PAL.oliva, PAL.pasto], 0.22, 0.2);
  terraceStack(world, TOP, -4.3, 7.4, 1.9, 5, [PAL.tealRoca, PAL.oliva, PAL.salvia], 0.22, 0.2);
  terraceStack(world, TOP, 5.4, 7.2, 1.7, 4, [PAL.oliva, PAL.pasto, PAL.arena], 0.22, 0.2);
  terraceStack(world, TOP, 6.6, 1.8, 1.5, 3, [PAL.salvia, PAL.pasto], 0.22, 0.2);

  // ── Plaza central + camino al embarcadero ─────────────────────
  // espuma de borde: capas delgadas de papel aquaClara bajo cada orilla
  const foamAt = (x: number, z: number, r: number, seed: number) => {
    const f = paper(blobShape(r, 0.16, 10, seed), 0.03, PAL.aguaClara, 0.008);
    f.position.set(x, TOP + 0.002, z);
    world.add(f);
  };
  foamAt(0.3, -2.5, 3.45, 2);
  foamAt(1.35, 4.0, 1.0, 12);
  foamAt(1.3, 5.1, 1.55, 4);
  foamAt(-4.3, 7.4, 2.2, 7);
  foamAt(5.4, 7.2, 2.0, 9);
  foamAt(-6.4, 0.6, 2.0, 3);
  foamAt(6.6, 1.8, 1.8, 5);
  const plaza = paper(blobShape(3.0, 0.13, 10, 2), 0.18, PAL.arena, 0.05);
  plaza.position.set(0.3, TOP, -2.5);
  world.add(plaza);
  const plaza2 = paper(blobShape(2.1, 0.15, 9, 5), 0.1, PAL.arenaCalida, 0.04);
  plaza2.position.set(0.15, TOP + 0.18, -2.7);
  world.add(plaza2);
  const pathSpots: Array<[number, number, number]> = [
    [0.8, 0.2, 1.2],
    [1.1, 1.6, 1.0],
    [1.3, 2.9, 0.85],
    [1.35, 4.0, 0.72],
  ];
  pathSpots.forEach(([x, z, r], i) => {
    const m = paper(blobShape(r, 0.18, 8, i * 3), 0.16, PAL.arena, 0.04);
    m.position.set(x, TOP, z);
    world.add(m);
  });
  // piedras del camino: formas orgánicas a dos tonos sobre la plaza
  const stoneCols = [0xcdb488, 0xf4e8c6, 0xc2a878, 0xefdcae];
  for (let i = 0; i < 12; i++) {
    const st = paper(blobShape(rand(0.2, 0.4), 0.38, 6, i * 1.7), 0.05, stoneCols[i % stoneCols.length], 0.016);
    const a = rand(0, Math.PI * 2);
    const rr = rand(0, 2.2);
    st.position.set(0.3 + Math.cos(a) * rr * 1.05, TOP + 0.31, -2.6 + Math.sin(a) * rr * 0.8);
    st.rotation.z = rand(0, Math.PI * 2);
    st.castShadow = false;
    world.add(st);
  }

  // ── BANCO (templo, arriba-centro) → hotspot "fountain" ────────
  const banco = new THREE.Group();
  {
    const baseB = box(2.6, 0.3, 1.8, 0xd8d2c4);
    baseB.position.y = 0.15;
    banco.add(baseB);
    const backWall = box(2.3, 1.7, 0.18, 0xcfc8b8);
    backWall.position.set(0, 1.15, -0.7);
    banco.add(backWall);
    for (const cx of [-1.05, 1.05]) {
      const col = cyl(0.14, 0.16, 1.7, PAL.blanco, 10);
      col.position.set(cx, 1.15, 0.55);
      banco.add(col);
      const cap = box(0.42, 0.12, 0.42, PAL.blanco);
      cap.position.set(cx, 2.05, 0.55);
      banco.add(cap);
    }
    const ped = new THREE.Shape();
    ped.moveTo(-1.55, 0);
    ped.lineTo(1.55, 0);
    ped.lineTo(0, 0.95);
    ped.closePath();
    const pedM = paper(ped, 0.25, PAL.blanco, 0.03);
    pedM.rotation.x = 0;
    pedM.position.set(0, 2.12, 0.42);
    banco.add(pedM);
    const coin = cyl(0.26, 0.26, 0.1, PAL.amarillo);
    coin.rotation.x = Math.PI / 2;
    coin.position.set(0, 2.55, 0.72);
    (coin.material as THREE.MeshStandardMaterial).emissive = new THREE.Color(0x554400);
    banco.add(coin);
    const counter = box(1.7, 0.55, 0.7, 0xe0dacc);
    counter.position.set(0, 0.55, 0.7);
    banco.add(counter);
    for (let i = 0; i < 3; i++) {
      const bills = box(0.34, 0.07 + i * 0.02, 0.22, 0x6cc06a);
      bills.position.set(-0.5 + i * 0.18, 0.86, 0.65 + (i % 2) * 0.12);
      banco.add(bills);
    }
    for (let i = 0; i < 2; i++) {
      const coins = cyl(0.13, 0.13, 0.16 + i * 0.06, PAL.amarillo);
      coins.position.set(0.45 + i * 0.3, 0.9, 0.7);
      banco.add(coins);
    }
    const s = sign("BANCO", 0.55, PAL.crema, "#7a4e2c");
    s.position.set(0, 2.0, 0.62);
    banco.add(s);
    attendantAnchor(banco, "fountain", 0, 0.3, 0.2);
    addLantern(banco, 0.0, 2.3, 0.85, PAL.amarillo, 0.8, quality, glowingMeshes);
    banco.scale.setScalar(0.92);
    banco.position.set(0.0, TOP + 0.3, -4.6);
    banco.rotation.y = 0.0;
    markStall(banco, "fountain");
    world.add(banco);
  }

  // ── EL RECICLÓN (arriba-derecha) → hotspot "forja" ────────────
  const reciclon = new THREE.Group();
  {
    const counter = box(2.5, 0.8, 1.0, PAL.madera);
    counter.position.y = 0.4;
    reciclon.add(counter);
    const front = box(2.5, 0.5, 0.06, PAL.maderaOscura);
    front.position.set(0, 0.35, 0.52);
    reciclon.add(front);
    for (const px of [-1.1, 1.1]) {
      const post = box(0.12, 2.7, 0.12, PAL.maderaOscura);
      post.position.set(px, 1.35, -0.3);
      reciclon.add(post);
    }
    // toldo alto y casi plano: deja ver al tendero detrás del mostrador
    const awning = box(2.9, 0.12, 1.4, PAL.maderaClara);
    awning.position.set(0, 2.72, 0.0);
    awning.rotation.x = 0.1;
    reciclon.add(awning);
    const s = sign("EL RECICLÓN", 0.75, PAL.maderaClara, "#4a2e12");
    s.position.set(0, 2.62, 0.78);
    s.rotation.x = -0.1;
    reciclon.add(s);
    const cardCols = [PAL.rosa, PAL.teal, PAL.limon, PAL.amarillo, PAL.magenta, PAL.verde];
    for (let i = 0; i < 9; i++) {
      const card = box(0.26, 0.02, 0.36, cardCols[i % cardCols.length]);
      card.position.set(rand(-1.0, 1.0), 0.82, rand(-0.25, 0.3));
      card.rotation.y = rand(-0.5, 0.5);
      reciclon.add(card);
    }
    // Caja contenedora de cartas repetidas para reciclar (estilo concept art)
    const crate = box(0.65, 0.22, 0.65, PAL.maderaOscura);
    crate.position.set(-0.8, 0.93, 0.25);
    reciclon.add(crate);
    for (let i = 0; i < 4; i++) {
      const card = box(0.48, 0.02, 0.48, cardCols[(i + 3) % cardCols.length]);
      card.position.set(-0.8, 1.05 + i * 0.03, 0.25);
      card.rotation.y = rand(-0.15, 0.15);
      reciclon.add(card);
    }
    const s2 = sign("LOTERÍA\nREPETIDA", 0.66, PAL.maderaClara, "#4a2e12");
    s2.position.set(-1.55, 0.65, 0.65);
    s2.rotation.y = 0.25;
    reciclon.add(s2);
    const s3 = sign("CAMBIO DE\nTICKETS", 0.66, PAL.maderaClara, "#4a2e12");
    s3.position.set(1.7, 0.62, 0.7);
    s3.rotation.y = -0.3;
    reciclon.add(s3);
    const s4 = sign("TICKETS", 0.4, PAL.crema, "#b05a1a");
    s4.position.set(0.95, 1.55, 0.35);
    s4.rotation.z = -0.08;
    reciclon.add(s4);
    const slot = box(0.5, 0.18, 0.1, 0x4a3520);
    slot.position.set(0, 0.18, 0.56);
    reciclon.add(slot);
    const ticket = box(0.22, 0.02, 0.3, PAL.crema);
    ticket.position.set(0, 0.12, 0.72);
    ticket.rotation.x = 0.5;
    reciclon.add(ticket);
    attendantAnchor(reciclon, "forja", 0, 0.35, -0.75);
    addLantern(reciclon, 1.1, 2.0, 0.1, PAL.naranja, 0.85, quality, glowingMeshes);
    reciclon.scale.setScalar(0.82);
    reciclon.position.set(2.3, TOP + 0.05, -2.9);
    reciclon.rotation.y = -0.35;
    markStall(reciclon, "forja");
    world.add(reciclon);

    // pulso del Reciclón al fundir (playMeltAnimation)
    let meltUntil = 0;
    reciclon.userData.melt = () => {
      meltUntil = performance.now() + 1600;
    };
    const baseScale = reciclon.scale.x;
    animations.push((t) => {
      if (performance.now() < meltUntil) {
        reciclon.scale.setScalar(baseScale * (1 + Math.sin(t * 14) * 0.04));
      } else if (reciclon.scale.x !== baseScale) {
        reciclon.scale.setScalar(baseScale);
      }
    });
  }

  // ── VENTA DE SOBRECITOS (izquierda) → hotspot "booster" ───────
  const sobrecitos = new THREE.Group();
  {
    const counter = box(2.3, 0.85, 1.0, PAL.maderaOscura);
    counter.position.y = 0.42;
    sobrecitos.add(counter);
    const stripeCols = [PAL.rosa, PAL.naranja, PAL.teal, PAL.amarillo, PAL.magenta, PAL.limon];
    for (let i = 0; i < 6; i++) {
      const st = box(0.36, 0.5, 0.05, stripeCols[i]);
      st.position.set(-0.95 + i * 0.38, 0.3, 0.52);
      sobrecitos.add(st);
    }
    for (const px of [-1.0, 1.0]) {
      const post = box(0.1, 2.6, 0.1, PAL.madera);
      post.position.set(px, 1.3, -0.3);
      sobrecitos.add(post);
    }
    // toldo de festón alto y casi plano con rayas rosas y crema (estilo concept art)
    const awningGroup = new THREE.Group();
    const segments = 8;
    const segW = 2.6 / segments;
    for (let i = 0; i < segments; i++) {
      const col = i % 2 === 0 ? PAL.rosa : PAL.crema;
      const stripe = box(segW, 0.1, 1.3, col);
      stripe.position.set(-1.3 + segW/2 + i * segW, 2.62, -0.1);
      stripe.rotation.x = 0.1;
      awningGroup.add(stripe);
    }
    sobrecitos.add(awningGroup);

    // Decoración festón del toldo colgando al frente
    for (let i = 0; i < 6; i++) {
      const sc = cyl(0.22, 0.22, 0.08, i % 2 ? PAL.teal : PAL.naranja, 12);
      sc.rotation.z = Math.PI / 2;
      sc.rotation.y = 0.1;
      sc.position.set(-1.1 + i * 0.44, 2.52, 0.54);
      sobrecitos.add(sc);
    }

    // Exhibidor/caja para los sobrecitos en el mostrador
    const displayBox = box(2.1, 0.1, 0.9, PAL.madera);
    displayBox.position.set(0, 0.88, 0.1);
    sobrecitos.add(displayBox);

    const packCols = [PAL.magenta, PAL.teal, PAL.amarillo, PAL.limon, PAL.rosa, PAL.naranja, PAL.verde];
    for (let row = 0; row < 2; row++) {
      for (let i = 0; i < 7; i++) {
        const pk = box(0.24, 0.34, 0.05, packCols[(i + row * 3) % packCols.length], 0.15);
        pk.position.set(-0.92 + i * 0.31, 1.0 + row * 0.06, -0.15 + row * 0.34);
        pk.rotation.x = -0.18;
        sobrecitos.add(pk);
      }
    }
    const s = sign("VENTA DE\nSOBRECITOS", 0.78, PAL.maderaClara, "#4a2e12");
    s.position.set(0, 3.1, 0.15);
    s.rotation.x = -0.1;
    s.rotation.z = 0.05;
    sobrecitos.add(s);
    attendantAnchor(sobrecitos, "booster", 0, 0.38, -0.85);
    addLantern(sobrecitos, -1.0, 2.0, 0.3, PAL.rosa, 0.8, quality, glowingMeshes);
    sobrecitos.scale.setScalar(0.85);
    sobrecitos.position.set(-1.7, TOP + 0.05, -1.5);
    sobrecitos.rotation.y = 0.32; // Ajustado levemente para ver la linterna
    markStall(sobrecitos, "booster");
    world.add(sobrecitos);
  }

  // ── WEBITOS ADOPCIÓN (abajo-izquierda) → hotspot "adopcion" ───
  const webitos = new THREE.Group();
  {
    const tbl = box(2.4, 0.14, 1.3, PAL.madera);
    tbl.position.y = 0.72;
    webitos.add(tbl);
    for (const [lx, lz] of [[-1.0, -0.5], [1.0, -0.5], [-1.0, 0.5], [1.0, 0.5]] as const) {
      const leg = box(0.12, 0.72, 0.12, PAL.maderaOscura);
      leg.position.set(lx, 0.36, lz);
      webitos.add(leg);
    }
    const eggCols = [PAL.rosa, PAL.teal, PAL.amarillo, PAL.limon, PAL.magenta, 0x9b6df0];
    const spots: Array<[number, number, "nido" | "tazon"]> = [
      [-0.75, -0.2, "nido"],
      [0.15, 0.25, "tazon"],
      [0.85, -0.25, "nido"],
      [-0.15, -0.35, "tazon"],
    ];
    let eggIdx = 0;
    for (const [ex, ez, kind] of spots) {
      if (kind === "nido") {
        const nest = new THREE.Mesh(
          new THREE.TorusGeometry(0.3, 0.11, 8, 14),
          new THREE.MeshStandardMaterial({ color: 0xb08a55, roughness: 0.95 }),
        );
        nest.rotation.x = -Math.PI / 2;
        nest.position.set(ex, 0.84, ez);
        nest.castShadow = true;
        webitos.add(nest);
      } else {
        const bowl = cyl(0.34, 0.24, 0.2, 0xcfd6de);
        bowl.position.set(ex, 0.9, ez);
        webitos.add(bowl);
      }
      for (let i = 0; i < 4; i++) {
        const egg = new THREE.Mesh(
          new THREE.SphereGeometry(0.11, 10, 8),
          new THREE.MeshStandardMaterial({
            color: eggCols[eggIdx++ % eggCols.length],
            roughness: 0.95,
            emissive: new THREE.Color(eggCols[(eggIdx - 1) % eggCols.length]).multiplyScalar(0.12),
          }),
        );
        egg.scale.y = 1.25;
        egg.castShadow = true;
        egg.position.set(ex + rand(-0.14, 0.14), 0.98, ez + rand(-0.12, 0.12));
        webitos.add(egg);
      }
    }
    const s = sign("WEBITOS\nADOPCIÓN", 0.7, PAL.maderaClara, "#4a2e12");
    s.position.set(0.55, 0.45, 0.75);
    s.rotation.x = -0.25;
    s.rotation.z = -0.07;
    webitos.add(s);
    attendantAnchor(webitos, "adopcion", -0.3, 0.28, -0.95);
    addLantern(webitos, 0.8, 1.6, 0.2, PAL.teal, 0.75, quality, glowingMeshes);
    webitos.scale.setScalar(0.9);
    webitos.position.set(-1.9, TOP + 0.05, 2.4);
    webitos.rotation.y = 0.32;
    markStall(webitos, "adopcion");
    world.add(webitos);
  }

  // ── TRAJINERAS P2P (embarcadero, abajo) → hotspot "p2p" ───────
  const boats: THREE.Group[] = [];
  const dock = new THREE.Group();
  {
    for (let i = 0; i < 5; i++) {
      const plank = box(0.5, 0.1, 2.6, i % 2 ? PAL.madera : PAL.maderaClara);
      plank.position.set(-1.0 + i * 0.52, 0.55, 0);
      dock.add(plank);
    }
    for (const [px, pz] of [[-1.1, -1.1], [1.1, -1.1], [-1.1, 1.1], [1.1, 1.1]] as const) {
      const pile = cyl(0.1, 0.12, 0.85, PAL.maderaOscura, 8);
      pile.position.set(px, 0.22, pz);
      dock.add(pile);
    }
    for (const px of [-1.3, 1.3]) {
      const post = box(0.12, 2.2, 0.12, PAL.maderaOscura);
      post.position.set(px, 1.55, -1.0);
      dock.add(post);
    }
    const s = new THREE.Group();
    const board = box(2.72, 0.85, 0.08, PAL.maderaClara, 0.25);
    s.add(board);
    const txt = textPlane("TRAJINERAS\nP2P", 0.85 * 0.62, "#4a2e12");
    txt.position.z = 0.05;
    s.add(txt);
    s.position.set(0, 2.35, -1.0);
    dock.add(s);
    const goods = box(0.3, 0.18, 0.4, PAL.magenta);
    goods.position.set(0.5, 0.69, 0.4);
    dock.add(goods);
    const bills = box(0.3, 0.08, 0.2, 0x6cc06a);
    bills.position.set(-0.4, 0.65, 0.2);
    dock.add(bills);
    attendantAnchor(dock, "p2p", 0.3, 0.6, 0.3);
    addLantern(dock, 1.3, 1.6, -0.8, PAL.magenta, 0.8, quality, glowingMeshes);
    dock.scale.setScalar(0.9);
    dock.position.set(1.1, TOP, 4.4);
    dock.rotation.y = -0.15;
    markStall(dock, "p2p");
    world.add(dock);
  }
  function trajinera(hullC: number, roofC: number, x: number, z: number, ry: number): void {
    const g = new THREE.Group();
    const hullShape = new THREE.Shape();
    hullShape.moveTo(-1.1, -0.32);
    hullShape.lineTo(1.1, -0.32);
    hullShape.quadraticCurveTo(1.5, -0.3, 1.45, 0.12);
    hullShape.lineTo(-1.45, 0.12);
    hullShape.quadraticCurveTo(-1.5, -0.3, -1.1, -0.32);
    const hull = new THREE.Mesh(
      new THREE.ExtrudeGeometry(hullShape, {
        depth: 0.66,
        bevelEnabled: true,
        bevelThickness: 0.03,
        bevelSize: 0.03,
        bevelSegments: 1,
      }),
      new THREE.MeshStandardMaterial({ color: hullC, roughness: 0.95 }),
    );
    hull.position.set(0, 0.34, -0.33);
    hull.castShadow = true;
    g.add(hull);
    const floor = box(2.2, 0.06, 0.5, PAL.maderaClara);
    floor.position.y = 0.42;
    g.add(floor);
    for (const [vx, vz] of [[-0.85, -0.24], [0.85, -0.24], [-0.85, 0.24], [0.85, 0.24]] as const) {
      const stick = cyl(0.035, 0.035, 0.85, PAL.maderaOscura, 6);
      stick.position.set(vx, 0.85, vz);
      g.add(stick);
    }
    const roof = new THREE.Mesh(
      new THREE.CylinderGeometry(0.48, 0.48, 2.0, 12, 1, false, Math.PI * 0.12, Math.PI * 0.76),
      new THREE.MeshStandardMaterial({ color: roofC, roughness: 0.95 }),
    );
    roof.rotation.z = Math.PI / 2;
    roof.position.y = 1.16;
    roof.castShadow = true;
    g.add(roof);

    // Copete (arco frontal mexicano) en la proa (x = 1.4)
    const archShape = new THREE.Shape();
    archShape.moveTo(-0.28, 0);
    archShape.lineTo(-0.28, 0.25);
    archShape.quadraticCurveTo(-0.28, 0.45, -0.14, 0.45);
    archShape.lineTo(0.14, 0.45);
    archShape.quadraticCurveTo(0.28, 0.45, 0.28, 0.25);
    archShape.lineTo(0.28, 0);
    archShape.lineTo(-0.28, 0);

    const copete = paper(archShape, 0.02, PAL.naranja, 0.008);
    copete.rotation.x = 0;
    copete.rotation.y = Math.PI / 2;
    copete.position.set(1.4, 0.46, 0);
    g.add(copete);

    const txt = textPlane("P2P", 0.32, "#e04a7a");
    txt.rotation.y = Math.PI / 2;
    txt.position.set(1.415, 0.68, 0);
    g.add(txt);

    g.position.set(x, TOP, z);
    g.rotation.y = ry;
    g.userData.phase = rand(0, 6);
    g.userData.stallId = "p2p";
    hotspots.push(g);
    boats.push(g);
    world.add(g);
  }
  // Solo 2 lanchas para dejar ver al axolotito asistente
  trajinera(PAL.magenta, PAL.verde, 2.5, 5.2, 0.55);
  trajinera(0xd0386a, PAL.teal, -1.1, 5.4, -0.35);
  animations.push((t) => {
    for (const b of boats) {
      const phase = b.userData.phase as number;
      b.position.y = TOP + Math.sin(t * 1.1 + phase) * 0.045;
      b.rotation.z = Math.sin(t * 0.9 + phase) * 0.025;
    }
  });

  // Ondas concéntricas: anillos que se expanden y desvanecen alrededor de
  // las barcas y de algunos puntos de orilla.
  const ripples: THREE.Mesh[] = [];
  const rippleAt = (x: number, z: number, r: number, phase: number) => {
    const ring = new THREE.Mesh(
      new THREE.RingGeometry(r * 0.92, r, 26),
      new THREE.MeshBasicMaterial({ color: PAL.aguaClara, transparent: true, opacity: 0 }),
    );
    ring.rotation.x = -Math.PI / 2;
    ring.position.set(x, TOP + 0.006, z);
    ring.userData.phase = phase;
    ripples.push(ring);
    world.add(ring);
  };
  for (const b of boats) {
    rippleAt(b.position.x, b.position.z, 1.55, rand(0, 1));
    rippleAt(b.position.x, b.position.z, 1.55, rand(0, 1) + 0.5);
  }
  rippleAt(0.3, 1.1, 1.2, 0.2); // orilla de la plaza, lado del camino
  rippleAt(-3.4, -2.4, 1.0, 0.7); // orilla oeste de la plaza
  rippleAt(3.6, -1.0, 1.0, 0.45); // orilla este
  animations.push((t) => {
    for (const r of ripples) {
      const p = (t * 0.22 + (r.userData.phase as number)) % 1;
      const s = 0.45 + p * 0.85;
      r.scale.set(s, s, 1);
      (r.material as THREE.MeshBasicMaterial).opacity = Math.sin(Math.PI * p) * 0.35;
    }
  });

  // ── Plantas (algunas bioluminiscentes) ────────────────────────
  plant(world, TOP, -6.9, -3.9, 0x3ee8c0, 1.5, 0.55);
  plant(world, TOP, -6.2, 0.6, 0xe87ad0, 1.0, 0.35);
  plant(world, TOP, -4.8, 5.4, 0x52d0a8, 1.1, 0.2);
  plant(world, TOP, 6.4, -4.2, 0x9b6df0, 1.2, 0.4);
  plant(world, TOP, 6.9, 4.6, 0x3ee8c0, 1.0, 0.45);
  plant(world, TOP, 2.8, 7.6, 0xe87ad0, 0.9, 0.3);
  plant(world, TOP, -1.8, 7.8, 0x52d0a8, 1.0, 0.2);
  plant(world, TOP, 5.6, -1.0, 0xb8d94a, 0.8, 0.1);

  // ── Guirnaldas de papel picado ────────────────────────────────
  const flags: THREE.Mesh[] = [];
  const flagCols = [PAL.magenta, PAL.teal, PAL.rosa, PAL.amarillo, 0xe87ad0];
  function garland(x0: number, x1: number, z: number, y0: number, sag: number, n: number, scale = 1): void {
    for (let i = 0; i < n; i++) {
      const tt = (i + 0.5) / n;
      const c = flagCols[i % flagCols.length];
      const f = paper(picadoShape(0.95 * scale, 0.8 * scale), 0.02, c, 0.006, 0.4);
      (f.material as THREE.MeshStandardMaterial).side = THREE.DoubleSide;
      f.castShadow = false;
      f.rotation.x = 0;
      f.position.set(x0 + (x1 - x0) * tt, y0 - Math.sin(Math.PI * tt) * sag, z);
      f.userData.phase = rand(0, 6);
      flags.push(f);
      world.add(f);
    }
  }
  garland(-4.5, 0.2, -7.2, TOP + 5.6, 0.8, 5, 1.3);
  garland(0.0, 4.5, -7.6, TOP + 5.8, 0.9, 5, 1.3);
  garland(-3.0, 2.5, -6.4, TOP + 4.6, 0.6, 6, 0.9);
  animations.push((t) => {
    for (const f of flags) f.rotation.z = Math.sin(t * 1.3 + (f.userData.phase as number)) * 0.06;
  });

  // ── Etiquetas de esquina removidas por solicitud del usuario ──

  // ── Tenderos: axolotitos billboard en las anclas attendant:<id> ──
  const tenderoSkins: Record<string, { skinColor: string; seed: number }> = {
    fountain: { skinColor: "gray_light", seed: 11 },
    forja: { skinColor: "gold", seed: 23 },
    booster: { skinColor: "pink", seed: 37 },
    adopcion: { skinColor: "astral", seed: 41 },
    p2p: { skinColor: "gray_dark", seed: 53 },
  };
  const billboards: AxolotitoBillboard[] = [];
  world.updateMatrixWorld(true);
  const anchorPos = new THREE.Vector3();
  world.traverse((obj) => {
    if (!obj.name.startsWith("attendant:")) return;
    const id = obj.name.slice("attendant:".length);
    const dna = tenderoSkins[id];
    if (!dna) return;
    obj.getWorldPosition(anchorPos);
    const b = new AxolotitoBillboard(dna, 1.25);
    b.position.copy(anchorPos);
    // el tendero hereda el hotspot de su puesto (tocarlo = tocar el puesto)
    b.userData.stallId = id;
    hotspots.push(b);
    billboards.push(b);
  });
  for (const b of billboards) world.add(b); // fuera del traverse (no mutar durante)

  // ── Transeúntes: axolotitos del usuario deambulando por la plaza ──
  const FLOOR = TOP + 0.3;
  const wanderTarget = () => {
    const a = rand(0, Math.PI * 2);
    const rr = Math.sqrt(rand(0, 1));
    return new THREE.Vector3(0.15 + Math.cos(a) * rr * 1.9, FLOOR, -2.7 + Math.sin(a) * rr * 1.45);
  };
  const visitors: Array<{
    b: AxolotitoBillboard;
    target: THREE.Vector3;
    speed: number;
    pause: number;
  }> = [];
  for (const v of (opts.visitantes ?? []).slice(0, 4)) {
    const b = new AxolotitoBillboard(v, 1.05);
    b.position.copy(wanderTarget());
    world.add(b);
    billboards.push(b);
    visitors.push({ b, target: wanderTarget(), speed: rand(0.45, 0.7), pause: rand(0, 3) });
  }
  animations.push((t, dt) => {
    for (const b of billboards) b.update(t, dt);
    for (const v of visitors) {
      if (v.pause > 0) {
        v.pause -= dt;
        v.b.position.y = FLOOR;
        if (v.pause <= 0) v.target = wanderTarget();
        continue;
      }
      const dx = v.target.x - v.b.position.x;
      const dz = v.target.z - v.b.position.z;
      const dist = Math.hypot(dx, dz);
      if (dist < 0.08) {
        v.pause = rand(1.2, 3.5);
        v.b.setWalk(0, 1); // de frente mientras descansa
        continue;
      }
      const step = Math.min(dist, v.speed * dt);
      v.b.position.x += (dx / dist) * step;
      v.b.position.z += (dz / dist) * step;
      v.b.position.y = FLOOR + Math.abs(Math.sin(t * 7 + v.speed * 20)) * 0.045; // pasitos
      v.b.setWalk(dx, dz);
    }
  });

  // ── Inicialización de Efectos Creativos ──
  
  // 1. Rayos de sol volumétricos de papel picado
  createSunRays(world, TOP, animations);
  
  // 2. Lirios de agua flotantes
  const lilies: THREE.Group[] = [];
  createLily(world, TOP, -4.5, 4.5, 0.0, lilies);
  createLily(world, TOP, 4.0, 3.5, 2.1, lilies);
  createLily(world, TOP, -6.0, -1.5, 4.3, lilies);
  
  animations.push((t) => {
    for (const lily of lilies) {
      const phase = lily.userData.phase as number;
      lily.position.y = TOP + 0.01 + Math.sin(t * 1.2 + phase) * 0.022;
      lily.rotation.z = Math.sin(t * 0.9 + phase) * 0.06;
      lily.rotation.x = Math.cos(t * 0.8 + phase) * 0.04;
      lily.rotation.y = t * 0.08 + phase;
    }
  });

  // 3. Registrar todos los materiales emisivos y configurar el pulso de respiración bioluminiscente + resaltado interactivo
  const stallGroups = [banco, reciclon, sobrecitos, webitos, dock];
  const stallLighting: Array<{
    group: THREE.Object3D;
    light?: THREE.PointLight;
    core?: THREE.Mesh;
    baseScale: number;
  }> = [];

  for (const sg of stallGroups) {
    let light: THREE.PointLight | undefined;
    let core: THREE.Mesh | undefined;
    sg.traverse((child) => {
      if ((child as THREE.PointLight).isPointLight) light = child as THREE.PointLight;
      if (child.name === "lanternCore") core = child as THREE.Mesh;
    });
    stallLighting.push({
      group: sg,
      light,
      core,
      baseScale: sg.scale.x
    });
  }

  world.traverse((obj) => {
    const mesh = obj as THREE.Mesh;
    if (mesh.material && (mesh.material as THREE.MeshStandardMaterial).emissive) {
      const mat = mesh.material as THREE.MeshStandardMaterial;
      if (mat.emissive.getHex() > 0) {
        if (!mesh.userData.baseEmissive) {
          mesh.userData.baseEmissive = mat.emissive.clone();
        }
        // Evitamos meter los lantern cores en el pulso genérico para controlarlos individualmente con el hover
        if (mesh.name !== "lanternCore") {
          glowingMeshes.push(mesh);
        }
      }
    }
  });

  animations.push((t) => {
    // 1. Pulso de respiración genérico (plantas bioluminiscentes, etc.)
    const pulse = 0.8 + Math.sin(t * 1.5) * 0.2;
    for (const m of glowingMeshes) {
      const mat = m.material as THREE.MeshStandardMaterial;
      const baseE = m.userData.baseEmissive as THREE.Color;
      mat.emissive.copy(baseE).multiplyScalar(pulse);
    }

    // 2. Pulso de linternas de puestos + Boost de intensidad cuando el usuario interactúa (hover o click)
    for (const item of stallLighting) {
      const isInteracting = item.group.scale.x > item.baseScale * 1.01;
      
      if (item.light) {
        const targetIntensity = isInteracting ? 3.2 : 1.8;
        item.light.intensity += (targetIntensity - item.light.intensity) * 0.15;
      }
      
      if (item.core) {
        const mat = item.core.material as THREE.MeshStandardMaterial;
        const baseE = item.core.userData.baseEmissive as THREE.Color;
        if (baseE) {
          const interactBoost = isInteracting ? 1.6 : 1.0;
          mat.emissive.copy(baseE).multiplyScalar(pulse * interactBoost);
        }
      }
    }
  });

  // Encuadres de enfoque por puesto (focusStall del motor).
  const stallFocus: Record<string, StallFocus> = {
    fountain: { x: 0.25, z: -3.6, zoom: 0.62 },
    forja: { x: 2.2, z: -1.9, zoom: 0.62 },
    booster: { x: -2.0, z: -0.9, zoom: 0.62 },
    adopcion: { x: -1.8, z: 3.6, zoom: 0.62 },
    p2p: { x: 1.3, z: 5.2, zoom: 0.66 },
  };

  return {
    group: world,
    hotspots,
    animations,
    stallFocus,
    billboards,
    playMelt(): void {
      (reciclon.userData.melt as (() => void) | undefined)?.();
    },
    dispose(): void {
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
}
