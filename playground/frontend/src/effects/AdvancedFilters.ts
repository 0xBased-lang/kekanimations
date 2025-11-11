/**
 * Advanced Filter Effects
 *
 * Bloom, Glitch, Hologram, and Color Adjustment effects
 */

import * as PIXI from 'pixi.js';
import { BloomFilter } from '@pixi/filter-bloom';
import { AdjustmentFilter } from '@pixi/filter-adjustment';
import { ColorMatrixFilter } from '@pixi/filter-color-matrix';

// ============================================================
// BLOOM EFFECT
// ============================================================

export function createBloomFilter(intensity: number = 1.0): BloomFilter {
  const filter = new BloomFilter();
  filter.blur = 4 * intensity;
  // Note: PixiJS v8 BloomFilter API may differ
  return filter;
}

// ============================================================
// COLOR ADJUSTMENTS
// ============================================================

export interface ColorAdjustments {
  brightness?: number;   // 0.5 to 1.5, default 1.0 (absolute value, not offset)
  contrast?: number;     // 0.5 to 1.5, default 1.0 (absolute value, not offset)
  saturation?: number;   // 0.0 to 2.0, default 1.0 (absolute value, not offset)
  hue?: number;          // 0 to 360, default 0
}

export function createColorAdjustmentFilter(adjustments: ColorAdjustments): AdjustmentFilter {
  // UI sends absolute values (1.0 = normal), use them directly
  const filter = new AdjustmentFilter({
    brightness: adjustments.brightness || 1.0,
    contrast: adjustments.contrast || 1.0,
    saturation: adjustments.saturation || 1.0,
  });
  return filter;
}

// ============================================================
// GLITCH EFFECT
// ============================================================

export class GlitchEffect {
  private glitchIntensity: number;
  private glitchTimer: number = 0;

  constructor(intensity: number = 0.5) {
    this.glitchIntensity = intensity;
  }

  update(): PIXI.Filter | null {
    this.glitchTimer++;

    // Random glitch bursts
    if (this.glitchTimer % 30 === 0 && Math.random() < this.glitchIntensity) {
      return this.createRGBSplitFilter();
    }

    return null;
  }

  private createRGBSplitFilter(): PIXI.Filter {
    const colorMatrix = new ColorMatrixFilter();

    // Offset red and blue channels
    const offset = 5 * this.glitchIntensity;
    const matrix = [
      1, 0, 0, 0, offset,     // Red channel shifted
      0, 1, 0, 0, 0,          // Green normal
      0, 0, 1, 0, -offset,    // Blue channel shifted opposite
      0, 0, 0, 1, 0,
    ];

    colorMatrix.matrix = matrix as any;
    return colorMatrix as any;
  }

  destroy() {
    // Cleanup if needed
  }
}

// ============================================================
// HOLOGRAM EFFECT
// ============================================================

export class HologramEffect extends PIXI.Container {
  private scanLines: PIXI.Graphics;
  private scanY: number = 0;
  private speed: number;

  constructor(_canvasWidth: number, _canvasHeight: number, speed: number = 2) {
    super();
    this.speed = speed;
    this.scanLines = new PIXI.Graphics();
    this.addChild(this.scanLines);
    this.blendMode = 'screen' as any;
  }

  update(spriteX: number, spriteY: number, spriteWidth: number, spriteHeight: number) {
    this.scanY = (this.scanY + this.speed) % spriteHeight;

    // Redraw scan lines
    this.scanLines.clear();

    // Horizontal scan lines
    for (let y = 0; y < spriteHeight; y += 4) {
      const alpha = y === Math.floor(this.scanY) ? 0.3 : 0.1;
      this.scanLines.rect(
        spriteX - spriteWidth / 2,
        spriteY - spriteHeight / 2 + y,
        spriteWidth,
        2
      );
      this.scanLines.fill({ color: 0x00ffff, alpha });
    }

    // Moving scan line
    this.scanLines.rect(
      spriteX - spriteWidth / 2,
      spriteY - spriteHeight / 2 + this.scanY,
      spriteWidth,
      3
    );
    this.scanLines.fill({ color: 0x00ffff, alpha: 0.5 });
  }

  destroy(options?: any) {
    this.scanLines.destroy(options);
    super.destroy(options);
  }
}

export function createHologramColorFilter(): ColorMatrixFilter {
  const filter = new ColorMatrixFilter();

  // Blue/cyan tint
  const matrix = [
    0.5, 0, 0, 0, 0,
    0, 0.7, 0, 0, 0,
    0, 0, 1.2, 0, 0,
    0, 0, 0, 0.9, 0,
  ];

  filter.matrix = matrix as any;
  return filter;
}

// ============================================================
// PSYCHEDELIC EFFECT
// ============================================================

export class PsychedelicEffect {
  private hue: number = 0;
  private speed: number;
  private filter: ColorMatrixFilter;

  constructor(speed: number = 0.05) {
    this.speed = speed;
    // Create filter once and reuse it (prevents memory leak)
    this.filter = new ColorMatrixFilter();
  }

  update(): ColorMatrixFilter {
    this.hue = (this.hue + this.speed) % (Math.PI * 2);

    // Reset and update the same filter instance
    this.filter.reset();
    this.filter.hue(this.hue * (180 / Math.PI), false);
    this.filter.saturate(1.5, false);

    return this.filter;
  }

  destroy() {
    // Destroy the filter to free GPU memory
    if (this.filter) {
      this.filter.destroy();
    }
  }
}
