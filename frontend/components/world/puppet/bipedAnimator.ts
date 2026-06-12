import type { BipedRigRefs } from "./bipedRig";
import { RIG_CENTER_Y } from "./bipedRig";
import type { MotionProfile } from "./motionProfiles";

/**
 * Animador procedural del rig bípedo (plan puppet bípedo §C). Función pura:
 * la comparten el axolotito orgánico (elapsed continuo) y el Robo-Axolote
 * (elapsed cuantizado en ticks para el tic-tac mecánico).
 */
export function applyBipedPose(rig: BipedRigRefs, p: MotionProfile, elapsed: number): void {
  const phase = elapsed * p.stepRate * Math.PI * 2;

  // Piernas alternadas; brazos contralaterales (frontal con pierna trasera).
  rig.legFront.rotation = Math.sin(phase) * p.legSwing;
  rig.legBack.rotation = Math.sin(phase + Math.PI) * p.legSwing;
  rig.armFront.rotation = Math.sin(phase + Math.PI) * p.armSwing;
  rig.armBack.rotation = Math.sin(phase) * p.armSwing;

  // Bob: 2 apoyos por ciclo de paso → |cos| duplica la frecuencia.
  const bob = -Math.abs(Math.cos(phase)) * p.bobAmp;

  // Inclinación (nado/sueño) + balanceo de peso en idle.
  rig.rigRoot.rotation = p.tilt + Math.sin(elapsed * 1.3) * p.sway;
  const float = p.lift > 0 ? Math.sin(elapsed * 1.8) * 5 : 0;
  rig.rigRoot.position.y = RIG_CENTER_Y - p.lift + bob + float;

  // Torso: lean al caminar + respiración con pivote en caderas
  // (volumen atenuado, no la conservación 2-breath del rig viejo).
  rig.torso.rotation = p.lean;
  const breath = 1 + Math.sin(elapsed * p.breathRate) * p.breathAmp;
  rig.torso.scale.set(1 - (breath - 1) * 0.6, breath);

  // Cola: cae con curva y se propulsa al nadar.
  rig.tail.rotation = 0.45 + Math.sin(elapsed * p.tailRate) * p.tailAmp;

  // Branquias: ondulación desfasada por pieza (el alma del axolote).
  rig.gills.forEach((gill, i) => {
    const base = gill.scale.x < 0 ? -1 : 1;
    gill.rotation =
      base * (-0.5 + (i % 3) * 0.45) +
      Math.sin(elapsed * p.gillSpeed + i * 0.9) * 0.16 * base;
  });

  // Sombra: encoge y se desvanece cuando el cuerpo flota.
  rig.shadow.alpha = p.shadowAlpha;
  rig.shadow.scale.set(1 - (p.lift / 60) * 0.45 - (-bob / 40) * 0.12, 1);
}
