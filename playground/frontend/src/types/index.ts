// Type definitions for NFT Animation Playground

export type EffectType =
  | 'breathing'
  | 'rotation'
  | 'glow'
  | 'fire'
  | 'sparkles'
  | 'laser_eyes'
  | 'rainbow'
  | 'bloom'
  | 'glitch'
  | 'hologram'
  | 'psychedelic'
  | 'color_adjust';

export interface EffectConfig {
  type: EffectType | string;
  intensity: number;
  parameters?: {
    // Rotation
    degrees?: number;

    // Glow, Bloom
    color?: [number, number, number];

    // Particles
    particle_count?: number;

    // Laser Eyes
    leftEyeX?: number;
    leftEyeY?: number;
    rightEyeX?: number;
    rightEyeY?: number;

    // Color Adjustments
    brightness?: number;
    contrast?: number;
    saturation?: number;
    hue?: number;

    // Rainbow, Psychedelic
    speed?: number;

    // Any other custom parameters
    [key: string]: any;
  };
}

export interface AnimationRequest {
  image_filename: string;
  effects: EffectConfig[];
  num_frames?: number;
  fps?: number;
  quality_target?: number;
}

export interface PresetConfig {
  name: string;
  description: string;
  effects: EffectConfig[];
  num_frames?: number;
  fps?: number;
}

export interface QualityReport {
  quality_score: number;
  file_size: number;
  frames: number;
  fps: number;
  validation_passed: boolean;
}
