/**
 * Rainbow Aura Effect
 *
 * Creates rotating rainbow color effect around NFT
 */

import * as PIXI from 'pixi.js';
import { ColorMatrixFilter } from '@pixi/filter-color-matrix';

export class RainbowAuraEffect {
  private colorFilter: ColorMatrixFilter;
  private hue: number = 0;
  private speed: number;

  constructor(speed: number = 0.02) {
    this.colorFilter = new ColorMatrixFilter();
    this.speed = speed;
  }

  update(): PIXI.Filter {
    // Rotate hue
    this.hue = (this.hue + this.speed) % (Math.PI * 2);

    // Apply hue rotation
    this.colorFilter.hue(this.hue * (180 / Math.PI), false);

    return this.colorFilter as any;
  }

  destroy() {
    this.colorFilter.destroy();
  }
}

// Alternative: Outline-based rainbow aura using Graphics
export class RainbowOutlineAura extends PIXI.Container {
  private graphics: PIXI.Graphics;
  private hue: number = 0;
  private speed: number;
  private radius: number;

  constructor(radius: number, speed: number = 0.02) {
    super();
    this.graphics = new PIXI.Graphics();
    this.addChild(this.graphics);
    this.radius = radius;
    this.speed = speed;
  }

  update(spriteX: number, spriteY: number) {
    this.hue = (this.hue + this.speed) % 360;

    // Convert HSV to RGB
    const rgb = this.hsvToRgb(this.hue, 1.0, 1.0);
    const color = (rgb[0] << 16) | (rgb[1] << 8) | rgb[2];

    // Draw glowing outline
    this.graphics.clear();
    this.graphics.circle(spriteX, spriteY, this.radius);
    this.graphics.stroke({ width: 8, color, alpha: 0.6 });

    // Add second outer ring
    this.graphics.circle(spriteX, spriteY, this.radius + 10);
    this.graphics.stroke({ width: 4, color, alpha: 0.3 });
  }

  private hsvToRgb(h: number, s: number, v: number): [number, number, number] {
    const c = v * s;
    const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
    const m = v - c;

    let r = 0, g = 0, b = 0;

    if (h < 60) { r = c; g = x; b = 0; }
    else if (h < 120) { r = x; g = c; b = 0; }
    else if (h < 180) { r = 0; g = c; b = x; }
    else if (h < 240) { r = 0; g = x; b = c; }
    else if (h < 300) { r = x; g = 0; b = c; }
    else { r = c; g = 0; b = x; }

    return [
      Math.round((r + m) * 255),
      Math.round((g + m) * 255),
      Math.round((b + m) * 255),
    ];
  }

  destroy(options?: any) {
    this.graphics.destroy(options);
    super.destroy(options);
  }
}
