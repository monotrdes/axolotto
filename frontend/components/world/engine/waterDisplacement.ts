import { Texture, Sprite, DisplacementFilter } from "pixi.js";

/**
 * Genera una textura de ruido caótico procedural en un canvas y crea un
 * DisplacementFilter para simular caustics de agua bioluminiscente
 * (plan task-84 §7, Sprint 2). Sin descargar assets de red.
 */
export function setupWaterDisplacement(
  width = 512,
  height = 512
): { filter: DisplacementFilter; sprite: Sprite; update: (dt: number) => void; destroy: () => void } {
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  if (ctx) {
    ctx.fillStyle = "#808080";
    ctx.fillRect(0, 0, width, height);

    const imgData = ctx.getImageData(0, 0, width, height);
    const data = imgData.data;
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = (y * width + x) * 4;
        
        // Suma de 3 osciladores con frecuencias y desfases orgánicos
        const n1 = Math.sin((x / width) * Math.PI * 4) * Math.cos((y / height) * Math.PI * 4);
        const n2 = Math.sin((x / width) * Math.PI * 8 + (y / height) * Math.PI * 6) * 0.5;
        const n3 = Math.cos((x / width) * Math.PI * 12 - (y / height) * Math.PI * 10) * 0.25;
        
        const val = 128 + Math.round((n1 + n2 + n3) * 55);
        
        data[idx] = val;     // R -> Desplazamiento horizontal
        data[idx + 1] = val; // G -> Desplazamiento vertical
        data[idx + 2] = 128; // B
        data[idx + 3] = 255; // A
      }
    }
    ctx.putImageData(imgData, 0, 0);
  }

  const texture = Texture.from(canvas);
  texture.source.addressMode = "repeat";

  const sprite = new Sprite(texture);
  const filter = new DisplacementFilter({
    sprite,
    scale: { x: 22, y: 22 },
  });

  let elapsed = 0;
  const update = (dt: number) => {
    elapsed += dt;
    // Desplazamiento constante diagonal lento para simular la corriente del cenote
    sprite.x = elapsed * 15;
    sprite.y = elapsed * 10;
  };

  const destroy = () => {
    // Liberar recursos de la GPU agresivamente (plan §7)
    sprite.destroy();
    texture.destroy(true);
  };

  return { filter, sprite, update, destroy };
}
