/**
 * Base Particle Emitter for NFT Animation Effects
 *
 * Provides reusable particle system with object pooling for performance
 */

import * as PIXI from 'pixi.js';

export interface ParticleConfig {
  maxParticles: number;
  emissionRate: number;      // particles per frame
  lifetime: number;           // frames
  startSize: number;
  endSize: number;
  startAlpha: number;
  endAlpha: number;
  startColor: number;
  endColor?: number;
  velocityX: () => number;
  velocityY: () => number;
  gravity?: number;
  blendMode?: PIXI.BLEND_MODES;
}

export class Particle extends PIXI.Graphics {
  public vx: number = 0;
  public vy: number = 0;
  public age: number = 0;
  public maxAge: number = 60;
  public startSize: number = 5;
  public endSize: number = 0;
  public startAlpha: number = 1;
  public endAlpha: number = 0;
  public startColor: number = 0xffffff;
  public endColor: number = 0xffffff;
  public gravity: number = 0;

  constructor() {
    super();
  }

  reset(config: Partial<Particle>) {
    Object.assign(this, config);
    this.age = 0;
    this.alpha = this.startAlpha;
    this.clear();
    this.circle(0, 0, this.startSize);
    this.fill({ color: this.startColor, alpha: this.startAlpha });
  }

  update(): boolean {
    this.age++;

    // Update position
    this.x += this.vx;
    this.y += this.vy;
    this.vy += this.gravity;

    // Calculate interpolation factor
    const t = this.age / this.maxAge;

    // Update size
    const size = this.startSize + (this.endSize - this.startSize) * t;

    // Update alpha
    this.alpha = this.startAlpha + (this.endAlpha - this.startAlpha) * t;

    // Redraw particle with new size and color
    this.clear();
    this.circle(0, 0, size);

    // Interpolate color if endColor is different
    if (this.endColor !== this.startColor) {
      const color = this.interpolateColor(this.startColor, this.endColor, t);
      this.fill({ color, alpha: this.alpha });
    } else {
      this.fill({ color: this.startColor, alpha: this.alpha });
    }

    // Return false if particle is dead
    return this.age < this.maxAge && this.alpha > 0.01;
  }

  private interpolateColor(color1: number, color2: number, t: number): number {
    const r1 = (color1 >> 16) & 0xff;
    const g1 = (color1 >> 8) & 0xff;
    const b1 = color1 & 0xff;

    const r2 = (color2 >> 16) & 0xff;
    const g2 = (color2 >> 8) & 0xff;
    const b2 = color2 & 0xff;

    const r = Math.round(r1 + (r2 - r1) * t);
    const g = Math.round(g1 + (g2 - g1) * t);
    const b = Math.round(b1 + (b2 - b1) * t);

    return (r << 16) | (g << 8) | b;
  }
}

export class ParticleEmitter {
  private particles: Particle[] = [];
  private pool: Particle[] = [];
  private config: ParticleConfig;
  private container: PIXI.Container;
  private emissionCounter: number = 0;
  private isActive: boolean = true;
  protected particleFactory: () => Particle;

  constructor(container: PIXI.Container, config: ParticleConfig, particleFactory?: () => Particle) {
    this.container = container;
    this.config = config;
    this.particleFactory = particleFactory || (() => new Particle());

    // Pre-create particle pool
    for (let i = 0; i < config.maxParticles; i++) {
      const particle = this.particleFactory();
      this.pool.push(particle);
    }
  }

  emit(x: number, y: number) {
    if (!this.isActive) return;

    this.emissionCounter += this.config.emissionRate;

    while (this.emissionCounter >= 1 && this.particles.length < this.config.maxParticles) {
      this.emissionCounter--;

      // Get particle from pool or create new one using factory
      const particle = this.pool.pop() || this.particleFactory();

      // Reset particle with new properties
      particle.reset({
        x,
        y,
        vx: this.config.velocityX(),
        vy: this.config.velocityY(),
        maxAge: this.config.lifetime,
        startSize: this.config.startSize,
        endSize: this.config.endSize,
        startAlpha: this.config.startAlpha,
        endAlpha: this.config.endAlpha,
        startColor: this.config.startColor,
        endColor: this.config.endColor || this.config.startColor,
        gravity: this.config.gravity || 0,
      });

      // Set blend mode
      if (this.config.blendMode !== undefined) {
        particle.blendMode = this.config.blendMode;
      }

      // Add to container and active list
      this.container.addChild(particle);
      this.particles.push(particle);
    }
  }

  update() {
    if (!this.isActive) return;

    // Update all particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const particle = this.particles[i];
      const alive = particle.update();

      if (!alive) {
        // Remove from container
        this.container.removeChild(particle);

        // Return to pool
        this.particles.splice(i, 1);
        this.pool.push(particle);
      }
    }
  }

  setActive(active: boolean) {
    this.isActive = active;
  }

  clear() {
    // Return all particles to pool
    for (const particle of this.particles) {
      this.container.removeChild(particle);
      this.pool.push(particle);
    }
    this.particles = [];
  }

  destroy() {
    this.clear();

    // Destroy all particles in pool
    for (const particle of this.pool) {
      particle.destroy();
    }

    this.pool = [];
  }

  getActiveCount(): number {
    return this.particles.length;
  }
}
