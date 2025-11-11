/**
 * Fire Particle Emitter
 *
 * Creates dramatic fire particle effect
 */

import * as PIXI from 'pixi.js';
import { ParticleEmitter, type ParticleConfig } from './ParticleEmitter';

export function createFireEmitter(container: PIXI.Container, intensity: number = 1.5): ParticleEmitter {
  const config: ParticleConfig = {
    maxParticles: Math.floor(50 * intensity),
    emissionRate: 2 * intensity,
    lifetime: 40,
    startSize: 8 + Math.random() * 4,
    endSize: 2,
    startAlpha: 0.9,
    endAlpha: 0,
    startColor: 0xff6600,  // Orange
    endColor: 0xff0000,    // Red
    velocityX: () => (Math.random() - 0.5) * 2,
    velocityY: () => -2 - Math.random() * 2,  // Upward
    gravity: 0.05,  // Slight upward acceleration
    blendMode: 'add' as any,  // Additive blending for fire glow
  };

  return new ParticleEmitter(container, config);
}

export function createFireEmitterAdvanced(
  container: PIXI.Container,
  options: {
    intensity?: number;
    particleCount?: number;
    color?: number;
  } = {}
): ParticleEmitter {
  const {
    intensity = 1.5,
    particleCount = 50,
    color = 0xff6600,
  } = options;

  const config: ParticleConfig = {
    maxParticles: particleCount,
    emissionRate: 2 * intensity,
    lifetime: 40,
    startSize: 8 + Math.random() * 4,
    endSize: 2,
    startAlpha: 0.9,
    endAlpha: 0,
    startColor: color,
    endColor: 0xff0000,
    velocityX: () => (Math.random() - 0.5) * 2,
    velocityY: () => -2 - Math.random() * 2,
    gravity: 0.05,
    blendMode: 'add' as any,
  };

  return new ParticleEmitter(container, config);
}
