/**
 * Sparkle Particle Emitter
 *
 * Creates magical twinkling sparkle effect
 */

import * as PIXI from 'pixi.js';
import { ParticleEmitter, type ParticleConfig, Particle } from './ParticleEmitter';

// Custom sparkle particle with twinkling
export class SparkleParticle extends Particle {
  private twinklePhase: number = Math.random() * Math.PI * 2;
  private twinkleSpeed: number = 0.1 + Math.random() * 0.1;

  update(): boolean {
    this.age++;

    // Update position
    this.x += this.vx;
    this.y += this.vy;
    this.vy += this.gravity;

    // Calculate interpolation factor
    const t = this.age / this.maxAge;

    // Twinkling effect
    this.twinklePhase += this.twinkleSpeed;
    const twinkle = (Math.sin(this.twinklePhase) + 1) / 2; // 0 to 1

    // Update size with twinkle
    const baseSize = this.startSize + (this.endSize - this.startSize) * t;
    const size = baseSize * (0.5 + twinkle * 0.5);

    // Update alpha with twinkle
    const baseAlpha = this.startAlpha + (this.endAlpha - this.startAlpha) * t;
    this.alpha = baseAlpha * twinkle;

    // Redraw particle
    this.clear();

    // Draw star shape
    this.drawCustomStar(0, 0, 5, size, size * 0.5);
    this.fill({ color: this.startColor, alpha: this.alpha });

    // Return false if particle is dead
    return this.age < this.maxAge && this.alpha > 0.01;
  }

  private drawCustomStar(x: number, y: number, points: number, outerRadius: number, innerRadius: number) {
    const step = Math.PI / points;
    this.moveTo(x, y - outerRadius);

    for (let i = 0; i < points * 2; i++) {
      const radius = i % 2 === 0 ? outerRadius : innerRadius;
      const angle = i * step - Math.PI / 2;
      this.lineTo(
        x + Math.cos(angle) * radius,
        y + Math.sin(angle) * radius
      );
    }

    this.closePath();
  }
}

export function createSparkleEmitter(container: PIXI.Container, intensity: number = 0.5): ParticleEmitter {
  const config: ParticleConfig = {
    maxParticles: Math.floor(20 * (intensity + 0.5)),
    emissionRate: 0.5 * intensity,
    lifetime: 60,
    startSize: 4,
    endSize: 1,
    startAlpha: 1.0,
    endAlpha: 0,
    startColor: 0xffff00,  // Yellow
    endColor: 0xffffff,    // White
    velocityX: () => (Math.random() - 0.5) * 1,
    velocityY: () => (Math.random() - 0.5) * 1,
    gravity: 0,
    blendMode: 'add' as any,
  };

  // Create emitter with sparkle particle factory
  const sparkleFactory = () => new SparkleParticle();
  const emitter = new ParticleEmitter(container, config, sparkleFactory);

  return emitter;
}

export function createSparkleEmitterAdvanced(
  container: PIXI.Container,
  options: {
    intensity?: number;
    particleCount?: number;
    spread?: number;
  } = {}
): ParticleEmitter {
  const {
    intensity = 0.5,
    particleCount = 20,
    spread = 100,
  } = options;

  const config: ParticleConfig = {
    maxParticles: particleCount,
    emissionRate: 0.5 * intensity,
    lifetime: 60,
    startSize: 4,
    endSize: 1,
    startAlpha: 1.0,
    endAlpha: 0,
    startColor: 0xffff00,
    endColor: 0xffffff,
    velocityX: () => (Math.random() - 0.5) * (spread / 50),
    velocityY: () => (Math.random() - 0.5) * (spread / 50),
    gravity: 0,
    blendMode: 'add' as any,
  };

  return new ParticleEmitter(container, config);
}
