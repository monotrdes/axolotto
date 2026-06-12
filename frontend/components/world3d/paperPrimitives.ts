import * as THREE from "three";

/**
 * Primitivas del mundo-diorama 3D de papel (decisión 2026-06-12: mundo 3D
 * extruido tipo "maqueta en caja"; los axolotitos serán billboards 2D).
 * Todo es procedural — cuando exista arte, las formas/texturas se sustituyen
 * sin cambiar la composición de las escenas.
 */

const rand = (a: number, b: number) => a + Math.random() * (b - a);

/** Paleta del Tianguis (muestreada del concept art 2026-06-12). */
export const PAL = {
  agua: 0x1aa6bc,
  aguaProfunda: 0x1090a8,
  aguaClara: 0xa8e4e0,
  arena: 0xe8d3a8,
  arenaCalida: 0xe8b88a,
  durazno: 0xe8a87c,
  salvia: 0x7fa86e,
  oliva: 0x9dbe8a,
  pasto: 0xc7d9a8,
  tealRoca: 0x2e7d7a,
  tealOscuro: 0x1d5f66,
  madera: 0x9c6b3f,
  maderaOscura: 0x7a4e2c,
  maderaClara: 0xc59a64,
  crema: 0xf2e4c8,
  blanco: 0xf5efe2,
  magenta: 0xe04a7a,
  amarillo: 0xf2c23e,
  teal: 0x2fb8b0,
  naranja: 0xe8893a,
  rosa: 0xf08aac,
  limon: 0xb8d94a,
  verde: 0x6cc06a,
  fondoPapel: 0x342b52,
} as const;

export function paperMat(color: number, emissive = 0): THREE.MeshStandardMaterial {
  return new THREE.MeshStandardMaterial({
    color,
    roughness: 0.95,
    metalness: 0,
    emissive: new THREE.Color(color).multiplyScalar(emissive),
  });
}

/** Blob orgánico suave (terrazas, rocas, charcos). */
export function blobShape(r: number, irr = 0.16, n = 9, seed = Math.random() * 10): THREE.Shape {
  const pts: THREE.Vector2[] = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2;
    const rad = r * (1 + Math.sin(a * 3 + seed) * irr * rand(0.5, 1));
    pts.push(new THREE.Vector2(Math.cos(a) * rad, Math.sin(a) * rad));
  }
  const s = new THREE.Shape();
  s.moveTo(pts[0].x, pts[0].y);
  s.splineThru(pts.slice(1).concat([pts[0]]));
  return s;
}

export function circleShape(r: number): THREE.Shape {
  const s = new THREE.Shape();
  s.absarc(0, 0, r, 0, Math.PI * 2, false);
  return s;
}

export function ellipseShape(rx: number, ry: number): THREE.Shape {
  const s = new THREE.Shape();
  s.absellipse(0, 0, rx, ry, 0, Math.PI * 2, false, 0);
  return s;
}

export function roundedRectShape(w: number, h: number, r: number): THREE.Shape {
  const s = new THREE.Shape();
  const x = -w / 2;
  const y = -h / 2;
  s.moveTo(x + r, y);
  s.lineTo(x + w - r, y);
  s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r);
  s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h);
  s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r);
  s.quadraticCurveTo(x, y, x + r, y);
  return s;
}

/** Banderín de papel picado con borde inferior dentado. */
export function picadoShape(w: number, h: number): THREE.Shape {
  const s = new THREE.Shape();
  s.moveTo(-w / 2, h);
  s.lineTo(w / 2, h);
  s.lineTo(w / 2, 0.18 * h);
  const n = 4;
  for (let i = 0; i <= n; i++) {
    const x = w / 2 - (i / n) * w;
    s.lineTo(x, i % 2 === 0 ? 0.18 * h : 0);
  }
  s.closePath();
  return s;
}

/**
 * Capa de papel: forma 2D extruida con canto biselado, acostada en el suelo
 * (rotation.x=-PI/2 → la extrusión apunta hacia arriba). Para piezas
 * verticales (banderines, hojas), resetear `rotation.x = 0` tras crearla.
 */
export function paper(
  shape: THREE.Shape,
  depth: number,
  color: number,
  bevel = 0.035,
  emissive = 0,
): THREE.Mesh {
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth,
    bevelEnabled: true,
    bevelThickness: bevel,
    bevelSize: bevel,
    bevelSegments: 1,
    curveSegments: 14,
  });
  const m = new THREE.Mesh(geo, paperMat(color, emissive));
  m.rotation.x = -Math.PI / 2;
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}

export function box(w: number, h: number, d: number, color: number, emissive = 0): THREE.Mesh {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), paperMat(color, emissive));
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}

export function cyl(r1: number, r2: number, h: number, color: number, seg = 14): THREE.Mesh {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r1, r2, h, seg), paperMat(color));
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}

function textTexture(
  text: string,
  color: string,
  size = 80,
  weight = 900,
): { tex: THREE.CanvasTexture; aspect: number } {
  const c = document.createElement("canvas");
  const pad = 26;
  const font = `${weight} ${size}px system-ui, sans-serif`;
  let ctx = c.getContext("2d")!;
  ctx.font = font;
  const lines = text.split("\n");
  const wMax = Math.max(...lines.map((l) => ctx.measureText(l).width));
  c.width = Math.ceil(wMax) + pad * 2;
  c.height = size * 1.15 * lines.length + pad * 2;
  ctx = c.getContext("2d")!;
  ctx.font = font;
  ctx.fillStyle = color;
  ctx.textBaseline = "middle";
  ctx.textAlign = "center";
  lines.forEach((l, i) => ctx.fillText(l, c.width / 2, pad + size * 1.15 * (i + 0.5)));
  return { tex: new THREE.CanvasTexture(c), aspect: c.width / c.height };
}

export function textPlane(text: string, h: number, color: string): THREE.Mesh {
  const { tex, aspect } = textTexture(text, color);
  return new THREE.Mesh(
    new THREE.PlaneGeometry(h * aspect, h),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true }),
  );
}

/** Letrero de madera: tabla con canto + texto, listo para inclinarse a cámara. */
export function sign(
  text: string,
  h: number,
  boardColor: number = 0xd9b98c,
  textColor = "#5c3a1a",
): THREE.Group {
  const g = new THREE.Group();
  const t = textPlane(text, h * 0.62, textColor);
  const w = (t.geometry as THREE.PlaneGeometry).parameters.width + h * 0.35;
  const board = box(w, h, 0.08, boardColor, 0.25);
  g.add(board);
  t.position.z = 0.05;
  g.add(t);
  return g;
}

/** Pila topográfica de terrazas de papel apiladas. */
export function terraceStack(
  parent: THREE.Object3D,
  topY: number,
  x: number,
  z: number,
  r0: number,
  n: number,
  pal: number[],
  h = 0.24,
  irr = 0.16,
  squash = 1,
): THREE.Group {
  const g = new THREE.Group();
  let y = 0;
  for (let i = 0; i < n; i++) {
    const m = paper(blobShape(r0 * (1 - i * 0.13), irr), h, pal[i % pal.length]);
    m.position.set(rand(-0.12, 0.12), y, rand(-0.12, 0.12));
    g.add(m);
    y += h;
  }
  g.userData.top = y;
  g.position.set(x, topY, z);
  g.scale.z = squash;
  parent.add(g);
  return g;
}

/** Planta de papel de 3 hojas verticales (glow > 0 = bioluminiscente). */
export function plant(
  parent: THREE.Object3D,
  topY: number,
  x: number,
  z: number,
  color: number,
  s = 1,
  glow = 0,
): THREE.Group {
  const g = new THREE.Group();
  for (let i = 0; i < 3; i++) {
    const leaf = paper(ellipseShape(0.13, 0.5), 0.04, color, 0.01, glow);
    leaf.rotation.x = 0;
    leaf.position.y = 0.45;
    const holder = new THREE.Group();
    holder.add(leaf);
    holder.rotation.y = (i / 3) * Math.PI;
    holder.rotation.z = rand(-0.3, 0.3);
    g.add(holder);
  }
  g.position.set(x, topY, z);
  g.scale.setScalar(s);
  parent.add(g);
  return g;
}

export { rand };
