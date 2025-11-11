// PixiJS Animation Canvas - Real-time 60 FPS preview with ALL effects
import { useEffect, useRef, useState } from 'react';
import * as PIXI from 'pixi.js';
import { GlowFilter } from '@pixi/filter-glow';
import type { EffectConfig } from '../types';
import { createFireEmitter } from '../effects/FireEmitter';
import { createSparkleEmitter } from '../effects/SparkleEmitter';
import { createLaserEyesEmitter, estimateEyePositions } from '../effects/LaserEyesEmitter';
import { ParticleEmitter } from '../effects/ParticleEmitter';
import { RainbowOutlineAura } from '../effects/RainbowAura';
import {
  createBloomFilter,
  createColorAdjustmentFilter,
  GlitchEffect,
  HologramEffect,
  createHologramColorFilter,
  PsychedelicEffect,
} from '../effects/AdvancedFilters';

interface AnimationCanvasProps {
  imageUrl?: string;
  effects: EffectConfig[];
  isPlaying?: boolean;
}

export function AnimationCanvas({ imageUrl, effects, isPlaying = true }: AnimationCanvasProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<PIXI.Application | null>(null);
  const spriteRef = useRef<PIXI.Sprite | null>(null);
  const particleContainerRef = useRef<PIXI.Container | null>(null);
  const effectsContainerRef = useRef<PIXI.Container | null>(null);
  const emittersRef = useRef<Map<string, ParticleEmitter | { left: ParticleEmitter; right: ParticleEmitter }>>(new Map());
  const effectInstancesRef = useRef<Map<string, any>>(new Map());
  const [isLoading, setIsLoading] = useState(false);

  // Initialize PixiJS application
  useEffect(() => {
    if (!canvasRef.current) return;

    let mounted = true;

    // Create PixiJS app
    (async () => {
      const app = new PIXI.Application();

      await app.init({
        width: 512,
        height: 512,
        backgroundColor: 0x1a1a1a,
        antialias: true,
        preserveDrawingBuffer: true, // For GIF export
      });

      if (canvasRef.current && mounted) {
        // PixiJS v8 uses app.canvas
        const canvas = app.canvas as HTMLCanvasElement;
        canvasRef.current.innerHTML = ''; // Clear any existing content
        canvasRef.current.appendChild(canvas);
        appRef.current = app;

        // Create containers (layer order matters!)
        const particleContainer = new PIXI.Container();
        const effectsContainer = new PIXI.Container();

        app.stage.addChild(effectsContainer);
        app.stage.addChild(particleContainer);

        particleContainerRef.current = particleContainer;
        effectsContainerRef.current = effectsContainer;

        console.log('PixiJS app initialized', { canvas, stage: app.stage });
      }
    })();

    // Cleanup
    return () => {
      mounted = false;
      if (appRef.current) {
        try {
          // Destroy all emitters
          emittersRef.current.forEach(emitter => {
            if ('destroy' in emitter) {
              emitter.destroy();
            } else {
              emitter.left.destroy();
              emitter.right.destroy();
            }
          });
          emittersRef.current.clear();

          // Destroy effect instances
          effectInstancesRef.current.forEach(instance => {
            if (instance && typeof instance.destroy === 'function') {
              instance.destroy();
            }
          });
          effectInstancesRef.current.clear();

          appRef.current.destroy(true);
        } catch (e) {
          console.error('Error destroying PixiJS app:', e);
        }
        appRef.current = null;
        particleContainerRef.current = null;
        effectsContainerRef.current = null;
      }
    };
  }, []);

  // Load image when URL changes OR when app becomes ready
  useEffect(() => {
    if (!imageUrl) {
      console.log('No image URL provided');
      return;
    }

    // Wait for app to be ready
    const loadImage = () => {
      if (!appRef.current) {
        console.log('PixiJS app not initialized yet, waiting...');
        // Retry after a short delay
        setTimeout(loadImage, 100);
        return;
      }

      console.log('Loading image:', imageUrl);
      setIsLoading(true);

      // Remove old sprite if exists
      if (spriteRef.current) {
        console.log('Removing old sprite');
        appRef.current.stage.removeChild(spriteRef.current);
        spriteRef.current.destroy();
        spriteRef.current = null;
      }

      // Load image using HTMLImageElement first (more reliable with blob URLs)
      const img = new Image();
      img.crossOrigin = 'anonymous';

      img.onload = () => {
        console.log('Image loaded via HTMLImageElement:', { width: img.width, height: img.height });

        if (!appRef.current || !particleContainerRef.current) {
          console.log('App destroyed before image loaded');
          setIsLoading(false);
          return;
        }

        // Create texture from loaded image
        const texture = PIXI.Texture.from(img);

        console.log('Creating texture from loaded image');

        // Create sprite
        const sprite = new PIXI.Sprite(texture);
        sprite.anchor.set(0.5);
        sprite.x = 256;
        sprite.y = 256;

        // Scale to fit canvas
        const scale = Math.min(512 / img.width, 512 / img.height);
        sprite.scale.set(scale);

        console.log('Adding sprite to stage:', { width: img.width, height: img.height, scale });

        // Add sprite BEFORE particle container so particles render on top
        const particleIndex = appRef.current.stage.getChildIndex(particleContainerRef.current);
        appRef.current.stage.addChildAt(sprite, particleIndex);
        spriteRef.current = sprite;
        setIsLoading(false);
      };

      img.onerror = (error) => {
        console.error('Failed to load image:', error);
        setIsLoading(false);
      };

      img.src = imageUrl;
    };

    loadImage();
  }, [imageUrl]);

  // Apply effects with animation loop
  useEffect(() => {
    if (!appRef.current || !spriteRef.current || !particleContainerRef.current || !effectsContainerRef.current || !isPlaying) return;

    let animationFrame = 0;
    const totalFrames = 24;
    const app = appRef.current;
    const sprite = spriteRef.current;
    const particleContainer = particleContainerRef.current;
    const effectsContainer = effectsContainerRef.current;

    // Store original properties
    const originalScale = sprite.scale.x;
    const originalRotation = sprite.rotation;

    // Track active effects
    const activeEffects = new Set(effects.map(e => e.type));

    // Create/destroy emitters and effect instances based on effects
    const updateEffectInstances = () => {
      // Fire emitter
      if (activeEffects.has('fire')) {
        if (!emittersRef.current.has('fire')) {
          const fireEffect = effects.find(e => e.type === 'fire');
          const intensity = fireEffect?.intensity || 1.5;
          const emitter = createFireEmitter(particleContainer, intensity);
          emittersRef.current.set('fire', emitter);
          console.log('Created fire emitter');
        }
      } else {
        if (emittersRef.current.has('fire')) {
          (emittersRef.current.get('fire') as ParticleEmitter).destroy();
          emittersRef.current.delete('fire');
          console.log('Destroyed fire emitter');
        }
      }

      // Sparkle emitter
      if (activeEffects.has('sparkles')) {
        if (!emittersRef.current.has('sparkles')) {
          const sparkleEffect = effects.find(e => e.type === 'sparkles');
          const intensity = sparkleEffect?.intensity || 0.5;
          const emitter = createSparkleEmitter(particleContainer, intensity);
          emittersRef.current.set('sparkles', emitter);
          console.log('Created sparkle emitter');
        }
      } else {
        if (emittersRef.current.has('sparkles')) {
          (emittersRef.current.get('sparkles') as ParticleEmitter).destroy();
          emittersRef.current.delete('sparkles');
          console.log('Destroyed sparkle emitter');
        }
      }

      // Laser Eyes emitter
      if (activeEffects.has('laser_eyes')) {
        if (!emittersRef.current.has('laser_eyes')) {
          const laserEffect = effects.find(e => e.type === 'laser_eyes');
          const intensity = laserEffect?.intensity || 2.0;

          // Estimate eye positions if not provided
          const eyePositions = laserEffect?.parameters?.leftEyeX
            ? {
                leftEyeX: laserEffect.parameters.leftEyeX,
                leftEyeY: laserEffect.parameters.leftEyeY!,
                rightEyeX: laserEffect.parameters.rightEyeX!,
                rightEyeY: laserEffect.parameters.rightEyeY!,
              }
            : estimateEyePositions(
                sprite.width * sprite.scale.x,
                sprite.height * sprite.scale.y,
                sprite.x,
                sprite.y
              );

          const emitters = createLaserEyesEmitter(particleContainer, {
            ...eyePositions,
            intensity,
          });
          emittersRef.current.set('laser_eyes', emitters);
          console.log('Created laser eyes emitters', eyePositions);
        }
      } else {
        if (emittersRef.current.has('laser_eyes')) {
          const emitters = emittersRef.current.get('laser_eyes') as { left: ParticleEmitter; right: ParticleEmitter };
          emitters.left.destroy();
          emitters.right.destroy();
          emittersRef.current.delete('laser_eyes');
          console.log('Destroyed laser eyes emitters');
        }
      }

      // Rainbow Aura effect
      if (activeEffects.has('rainbow')) {
        if (!effectInstancesRef.current.has('rainbow')) {
          const rainbowEffect = effects.find(e => e.type === 'rainbow');
          const speed = rainbowEffect?.parameters?.speed || 0.02;
          // Use proportional radius (110% of sprite radius for nice outline)
          const spriteRadius = (sprite.width * sprite.scale.x) / 2;
          const radius = spriteRadius * 1.10;
          const instance = new RainbowOutlineAura(radius, speed);
          effectsContainer.addChild(instance);
          effectInstancesRef.current.set('rainbow', instance);
          console.log('Created rainbow aura');
        }
      } else {
        if (effectInstancesRef.current.has('rainbow')) {
          const instance = effectInstancesRef.current.get('rainbow');
          effectsContainer.removeChild(instance);
          instance.destroy();
          effectInstancesRef.current.delete('rainbow');
          console.log('Destroyed rainbow aura');
        }
      }

      // Hologram effect
      if (activeEffects.has('hologram')) {
        if (!effectInstancesRef.current.has('hologram')) {
          const speed = effects.find(e => e.type === 'hologram')?.parameters?.speed || 2;
          const instance = new HologramEffect(512, 512, speed);
          effectsContainer.addChild(instance);
          effectInstancesRef.current.set('hologram', instance);
          console.log('Created hologram effect');
        }
      } else {
        if (effectInstancesRef.current.has('hologram')) {
          const instance = effectInstancesRef.current.get('hologram');
          effectsContainer.removeChild(instance);
          instance.destroy();
          effectInstancesRef.current.delete('hologram');
          console.log('Destroyed hologram effect');
        }
      }

      // Glitch effect (doesn't need persistent instance for simple version)
      // Psychedelic effect (doesn't need persistent instance for simple version)
    };

    updateEffectInstances();

    // Animation loop
    const ticker = () => {
      animationFrame = (animationFrame + 1) % totalFrames;
      const phase = (animationFrame / totalFrames) * Math.PI * 2;

      // Reset to original state
      sprite.scale.set(originalScale);
      sprite.rotation = originalRotation;
      sprite.alpha = 1.0;
      sprite.filters = null;

      const filters: any[] = [];

      // Apply each effect
      effects.forEach((effect) => {
        switch (effect.type) {
          case 'breathing': {
            // Sinusoidal breathing
            const scaleDelta = Math.sin(phase) * effect.intensity;
            const scale = originalScale * (1 + scaleDelta);
            sprite.scale.set(scale);
            break;
          }

          case 'rotation': {
            // Rotation animation
            const degrees = effect.parameters?.degrees || 10;
            const maxRotation = (degrees * Math.PI) / 180;
            const rotation = Math.sin(phase) * maxRotation;
            sprite.rotation = originalRotation + rotation;
            break;
          }

          case 'glow': {
            // TRUE GLOW FILTER (not just alpha!)
            const glowIntensity = effect.intensity || 2.0;
            const glowColor = effect.parameters?.color || [255, 0, 0];
            const colorValue = (glowColor[0] << 16) | (glowColor[1] << 8) | glowColor[2];

            const glowFilter = new GlowFilter({
              distance: 15 * glowIntensity,
              outerStrength: 2 * glowIntensity,
              innerStrength: 1,
              color: colorValue,
              quality: 0.5,
            });

            // Add pulsing
            glowFilter.outerStrength = (1 + Math.sin(phase) * 0.5) * 2 * glowIntensity;

            filters.push(glowFilter);
            break;
          }

          case 'bloom': {
            const intensity = effect.intensity || 1.0;
            const bloomFilter = createBloomFilter(intensity);
            filters.push(bloomFilter);
            break;
          }

          case 'color_adjust': {
            const adjustments = {
              brightness: effect.parameters?.brightness,
              contrast: effect.parameters?.contrast,
              saturation: effect.parameters?.saturation,
            };
            const colorFilter = createColorAdjustmentFilter(adjustments);
            filters.push(colorFilter);
            break;
          }

          case 'hologram': {
            // Apply color tint filter
            const hologramFilter = createHologramColorFilter();
            filters.push(hologramFilter);

            // Update scan lines
            const hologramEffect = effectInstancesRef.current.get('hologram');
            if (hologramEffect) {
              hologramEffect.update(
                sprite.x,
                sprite.y,
                sprite.width * sprite.scale.x,
                sprite.height * sprite.scale.y
              );
            }
            break;
          }

          case 'glitch': {
            // Periodic glitch bursts
            if (animationFrame % 30 === 0 && Math.random() < effect.intensity) {
              const glitchEffect = new GlitchEffect(effect.intensity);
              const glitchFilter = glitchEffect.update();
              if (glitchFilter) {
                filters.push(glitchFilter);
              }
            }
            break;
          }

          case 'psychedelic': {
            const speed = effect.parameters?.speed || 0.05;
            if (!effectInstancesRef.current.has('psychedelic')) {
              effectInstancesRef.current.set('psychedelic', new PsychedelicEffect(speed));
            }
            const psychEffect = effectInstancesRef.current.get('psychedelic');
            const psychFilter = psychEffect.update();
            filters.push(psychFilter);
            break;
          }

          case 'fire': {
            // Emit fire particles from bottom of sprite
            const fireEmitter = emittersRef.current.get('fire') as ParticleEmitter;
            if (fireEmitter) {
              // Emit from bottom center of sprite
              // Use proportional offset (5% from bottom edge inward)
              const spriteHeight = sprite.height * sprite.scale.y;
              const emitX = sprite.x;
              const emitY = sprite.y + spriteHeight / 2 - spriteHeight * 0.05;
              fireEmitter.emit(emitX, emitY);
              fireEmitter.update();
            }
            break;
          }

          case 'sparkles': {
            // Emit sparkles around sprite
            const sparkleEmitter = emittersRef.current.get('sparkles') as ParticleEmitter;
            if (sparkleEmitter) {
              // Emit from random positions around sprite
              const angle = Math.random() * Math.PI * 2;
              const radius = (sprite.width * sprite.scale.x) / 2 + 20;
              const emitX = sprite.x + Math.cos(angle) * radius;
              const emitY = sprite.y + Math.sin(angle) * radius;
              sparkleEmitter.emit(emitX, emitY);
              sparkleEmitter.update();
            }
            break;
          }

          case 'laser_eyes': {
            // Emit laser beams from eyes
            const laserEmitters = emittersRef.current.get('laser_eyes') as { left: ParticleEmitter; right: ParticleEmitter };
            if (laserEmitters) {
              const laserEffect = effects.find(e => e.type === 'laser_eyes');
              const eyePositions = laserEffect?.parameters?.leftEyeX
                ? {
                    leftEyeX: laserEffect.parameters.leftEyeX,
                    leftEyeY: laserEffect.parameters.leftEyeY!,
                    rightEyeX: laserEffect.parameters.rightEyeX!,
                    rightEyeY: laserEffect.parameters.rightEyeY!,
                  }
                : estimateEyePositions(
                    sprite.width * sprite.scale.x,
                    sprite.height * sprite.scale.y,
                    sprite.x,
                    sprite.y
                  );

              laserEmitters.left.emit(eyePositions.leftEyeX, eyePositions.leftEyeY);
              laserEmitters.left.update();

              laserEmitters.right.emit(eyePositions.rightEyeX, eyePositions.rightEyeY);
              laserEmitters.right.update();
            }
            break;
          }

          case 'rainbow': {
            // Update rainbow aura
            const rainbowAura = effectInstancesRef.current.get('rainbow');
            if (rainbowAura) {
              rainbowAura.update(sprite.x, sprite.y);
            }
            break;
          }
        }
      });

      // Apply all filters at once
      if (filters.length > 0) {
        sprite.filters = filters;
      }
    };

    // Add ticker
    app.ticker.add(ticker);

    // Cleanup
    return () => {
      app.ticker.remove(ticker);

      // Reset sprite to original state
      sprite.scale.set(originalScale);
      sprite.rotation = originalRotation;
      sprite.alpha = 1.0;
      sprite.filters = [];

      // Clear all emitters
      emittersRef.current.forEach(emitter => {
        if ('clear' in emitter) {
          emitter.clear();
        }
      });
    };
  }, [effects, isPlaying]);

  return (
    <div className="relative">
      <div
        ref={canvasRef}
        className="border-2 border-gray-700 rounded-lg overflow-hidden"
        style={{ width: '512px', height: '512px' }}
      />
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 rounded-lg">
          <div className="text-white text-lg">Loading...</div>
        </div>
      )}
    </div>
  );
}
