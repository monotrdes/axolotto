import * as THREE from "three";
import type { SceneAnimation, World3DScene, StallFocus } from "./ThreeWorldEngine";
import {
  PAL,
  blobShape,
  box,
  cyl,
  ellipseShape,
  paper,
  picadoShape,
  plant,
  rand,
  roundedRectShape,
  sign,
  terraceStack,
  textPlane,
} from "./paperPrimitives";

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

export function buildTianguisScene3D(): World3DScene {
  const world = new THREE.Group();
  const animations: SceneAnimation[] = [];
  const hotspots: THREE.Object3D[] = [];

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

  // ── Base de agua ──────────────────────────────────────────────
  const base = new THREE.Group();
  let baseY = 0;
  const baseLayers = [
    { w: 19.5, c: 0x241e3c, h: 0.4 },
    { w: 18.8, c: 0x123f55, h: 0.4 },
    { w: 18.2, c: PAL.aguaProfunda, h: 0.4 },
    { w: 17.8, c: PAL.agua, h: 0.32 },
  ];
  for (const L of baseLayers) {
    const m = paper(roundedRectShape(L.w, L.w * 1.34, 2.4), L.h, L.c, 0.05);
    m.position.y = baseY;
    base.add(m);
    baseY += L.h;
  }
  const TOP = baseY;
  // el agua emite un poco de luz propia (cyan vivo de la referencia)
  (base.children[3] as THREE.Mesh & { material: THREE.MeshStandardMaterial }).material.emissive =
    new THREE.Color(0x0c6e80);
  world.add(base);

  // Corrientes del río: vetas claras onduladas
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
  animations.push((t) => {
    for (const s of streaks) {
      const phase = s.userData.phase as number;
      s.position.x += Math.sin(t * 0.5 + phase) * 0.0012;
      (s.material as THREE.MeshStandardMaterial).opacity = 0.35 + Math.sin(t * 0.8 + phase) * 0.15;
    }
  });

  // ── Colinas del fondo y rocas laterales ───────────────────────
  terraceStack(world, TOP, -2.6, -7.6, 2.2, 5, [PAL.arenaCalida, PAL.durazno, PAL.arena], 0.26, 0.14, 0.5);
  terraceStack(world, TOP, 0.6, -8.0, 2.6, 6, [PAL.arena, PAL.arenaCalida, PAL.crema], 0.26, 0.12, 0.5);
  terraceStack(world, TOP, 3.4, -7.4, 2.0, 5, [PAL.durazno, PAL.arena, PAL.arenaCalida], 0.26, 0.15, 0.5);
  terraceStack(world, TOP, -5.0, -6.6, 1.9, 6, [PAL.tealRoca, PAL.salvia, PAL.oliva], 0.24, 0.18, 0.6);
  terraceStack(world, TOP, 5.6, -6.2, 1.8, 5, [PAL.oliva, PAL.tealRoca, PAL.salvia], 0.24, 0.18, 0.6);
  terraceStack(world, TOP, -4.6, -3.6, 1.3, 6, [PAL.tealOscuro, PAL.tealRoca, PAL.salvia], 0.2, 0.2);
  terraceStack(world, TOP, -6.4, 0.6, 1.7, 4, [PAL.salvia, PAL.oliva, PAL.pasto], 0.22, 0.2);
  terraceStack(world, TOP, -4.3, 7.4, 1.9, 5, [PAL.tealRoca, PAL.oliva, PAL.salvia], 0.22, 0.2);
  terraceStack(world, TOP, 5.4, 7.2, 1.7, 4, [PAL.oliva, PAL.pasto, PAL.arena], 0.22, 0.2);
  terraceStack(world, TOP, 6.6, 1.8, 1.5, 3, [PAL.salvia, PAL.pasto], 0.22, 0.2);

  // ── Plaza central + camino al embarcadero ─────────────────────
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
  for (let i = 0; i < 14; i++) {
    const st = paper(blobShape(rand(0.18, 0.34), 0.2, 7, i), 0.04, 0xf0dfba, 0.012);
    const a = rand(0, Math.PI * 2);
    const rr = rand(0, 2.3);
    st.position.set(0.3 + Math.cos(a) * rr * 1.05, TOP + 0.31, -2.6 + Math.sin(a) * rr * 0.8);
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
    banco.scale.setScalar(0.92);
    banco.position.set(0.25, TOP + 0.3, -4.9);
    banco.rotation.y = -0.06;
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
    attendantAnchor(reciclon, "forja", 0, 0, -0.1);
    reciclon.scale.setScalar(0.82);
    reciclon.position.set(2.6, TOP + 0.05, -3.1);
    reciclon.rotation.y = -0.4;
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
    // toldo de festón alto y casi plano (tendero visible debajo)
    const awn = box(2.6, 0.1, 1.3, PAL.rosa);
    awn.position.set(0, 2.62, -0.1);
    awn.rotation.x = 0.1;
    sobrecitos.add(awn);
    for (let i = 0; i < 6; i++) {
      const sc = cyl(0.22, 0.22, 0.08, i % 2 ? PAL.teal : PAL.naranja, 12);
      sc.rotation.z = Math.PI / 2;
      sc.rotation.y = 0.1;
      sc.position.set(-1.1 + i * 0.44, 2.52, 0.54);
      sobrecitos.add(sc);
    }
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
    attendantAnchor(sobrecitos, "booster", 0, 0, -0.55);
    sobrecitos.scale.setScalar(0.85);
    sobrecitos.position.set(-2.6, TOP + 0.05, -2.1);
    sobrecitos.rotation.y = 0.42;
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
    attendantAnchor(webitos, "adopcion", -0.3, 0, -0.95);
    webitos.scale.setScalar(0.9);
    webitos.position.set(-2.3, TOP + 0.05, 2.8);
    webitos.rotation.y = 0.35;
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
    const s = sign("TRAJINERAS\nP2P", 0.85, PAL.maderaClara, "#4a2e12");
    s.position.set(0, 2.35, -0.95);
    dock.add(s);
    const goods = box(0.3, 0.18, 0.4, PAL.magenta);
    goods.position.set(0.5, 0.69, 0.4);
    dock.add(goods);
    const bills = box(0.3, 0.08, 0.2, 0x6cc06a);
    bills.position.set(-0.4, 0.65, 0.2);
    dock.add(bills);
    attendantAnchor(dock, "p2p", 0.3, 0.6, 0.3);
    dock.scale.setScalar(0.9);
    dock.position.set(1.3, TOP, 5.1);
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
    g.position.set(x, TOP, z);
    g.rotation.y = ry;
    g.userData.phase = rand(0, 6);
    g.userData.stallId = "p2p";
    hotspots.push(g);
    boats.push(g);
    world.add(g);
  }
  trajinera(PAL.magenta, PAL.verde, 3.3, 4.4, 0.55);
  trajinera(0xd0386a, PAL.teal, -1.3, 6.1, -0.35);
  trajinera(PAL.naranja, PAL.limon, 2.4, 6.8, 0.15);
  animations.push((t) => {
    for (const b of boats) {
      const phase = b.userData.phase as number;
      b.position.y = TOP + Math.sin(t * 1.1 + phase) * 0.045;
      b.rotation.z = Math.sin(t * 0.9 + phase) * 0.025;
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

  // ── Etiquetas de esquina (señalética diegética) ───────────────
  {
    const zl = paper(picadoShape(2.2, 1.7), 0.03, PAL.magenta, 0.01, 0.35);
    zl.rotation.x = 0.55;
    zl.rotation.y = 0.5;
    zl.position.set(-3.0, TOP + 1.5, 6.9);
    world.add(zl);
    const zlt = textPlane("EL BARRIL", 0.34, "#5c1030");
    zlt.position.set(-2.85, TOP + 1.65, 7.3);
    zlt.rotation.x = -0.4;
    zlt.rotation.z = 0.4;
    world.add(zlt);
    const zr = paper(picadoShape(2.2, 1.7), 0.03, PAL.amarillo, 0.01, 0.35);
    zr.rotation.x = 0.55;
    zr.rotation.y = -0.5;
    zr.position.set(3.2, TOP + 1.5, 6.9);
    world.add(zr);
    const zrt = textPlane("EL FRIJOLITO", 0.34, "#6e4e08");
    zrt.position.set(3.05, TOP + 1.65, 7.3);
    zrt.rotation.x = -0.4;
    zrt.rotation.z = -0.4;
    world.add(zrt);
  }

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
