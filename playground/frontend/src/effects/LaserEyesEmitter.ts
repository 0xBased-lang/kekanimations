/**
 * Laser Eyes Emitter
 *
 * Creates dramatic laser beam effects from eyes
 */

import * as PIXI from 'pixi.js';
import { ParticleEmitter, type ParticleConfig } from './ParticleEmitter';

export interface LaserEyeConfig {
  leftEyeX: number;
  leftEyeY: number;
  rightEyeX: number;
  rightEyeY: number;
  intensity?: number;
  color?: number;
}

export function createLaserEyesEmitter(
  container: PIXI.Container,
  config: LaserEyeConfig
): { left: ParticleEmitter; right: ParticleEmitter } {
  const intensity = config.intensity || 2.0;
  const color = config.color || 0xff0000; // Red by default

  const laserConfig: ParticleConfig = {
    maxParticles: Math.floor(30 * intensity),
    emissionRate: 3 * intensity,
    lifetime: 20,
    startSize: 3,
    endSize: 0.5,
    startAlpha: 1.0,
    endAlpha: 0,
    startColor: color,
    endColor: color,
    // Shoot forward
    velocityX: () => 8 + Math.random() * 4,
    velocityY: () => (Math.random() - 0.5) * 2,
    gravity: 0,
    blendMode: 'add' as any,
  };

  const leftEmitter = new ParticleEmitter(container, laserConfig);
  const rightEmitter = new ParticleEmitter(container, laserConfig);

  return { left: leftEmitter, right: rightEmitter };
}

// Helper to estimate eye positions (basic heuristic)
// Note: Assumes sprite is anchored at center (0.5, 0.5)
// spriteX and spriteY are the CENTER of the sprite
// spriteWidth and spriteHeight are already scaled dimensions
export function estimateEyePositions(
  spriteWidth: number,
  spriteHeight: number,
  spriteX: number,
  spriteY: number
): { leftEyeX: number; leftEyeY: number; rightEyeX: number; rightEyeY: number } {
  // For typical NFT Pepe anatomy:
  // - Eyes are about 30-35% down from top of sprite
  // - Since sprite is centered, this is 15-20% UP from center
  // - Eyes are horizontally spaced about 35% of width apart
  // - Each eye is about 17-18% from center

  const eyeY = spriteY - spriteHeight * 0.20; // 20% above center = 30% from top
  const eyeSpacing = spriteWidth * 0.18;       // 18% from center on each side

  return {
    leftEyeX: spriteX - eyeSpacing,
    leftEyeY: eyeY,
    rightEyeX: spriteX + eyeSpacing,
    rightEyeY: eyeY,
  };
}
