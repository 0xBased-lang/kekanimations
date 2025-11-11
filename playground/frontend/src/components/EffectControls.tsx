// Interactive effect controls with sliders and toggles
import { useState } from 'react';
import type { EffectConfig } from '../types';

interface EffectControlsProps {
  effects: EffectConfig[];
  onChange: (effects: EffectConfig[]) => void;
}

export function EffectControls({ onChange }: EffectControlsProps) {
  // Basic effects
  const [breathingIntensity, setBreathingIntensity] = useState(0.02);
  const [rotationDegrees, setRotationDegrees] = useState(10);

  // Particle effects
  const [enableFire, setEnableFire] = useState(false);
  const [enableSparkles, setEnableSparkles] = useState(false);
  const [enableLaserEyes, setEnableLaserEyes] = useState(false);

  // Visual effects
  const [enableGlow, setEnableGlow] = useState(false);
  const [enableRainbow, setEnableRainbow] = useState(false);
  const [enableBloom, setEnableBloom] = useState(false);

  // Advanced effects
  const [enableGlitch, setEnableGlitch] = useState(false);
  const [enableHologram, setEnableHologram] = useState(false);
  const [enablePsychedelic, setEnablePsychedelic] = useState(false);

  // Color adjustments
  const [brightness, setBrightness] = useState(1.0);
  const [contrast, setContrast] = useState(1.0);
  const [saturation, setSaturation] = useState(1.0);

  // Update effects when controls change
  const updateEffects = (updates: Partial<{
    breathing: number;
    rotation: number;
    fire: boolean;
    sparkles: boolean;
    laserEyes: boolean;
    glow: boolean;
    rainbow: boolean;
    bloom: boolean;
    glitch: boolean;
    hologram: boolean;
    psychedelic: boolean;
    brightness: number;
    contrast: number;
    saturation: number;
  }>) => {
    const newEffects: EffectConfig[] = [];

    // Breathing (always enabled)
    const breathValue = updates.breathing ?? breathingIntensity;
    newEffects.push({
      type: 'breathing',
      intensity: breathValue,
    });

    // Rotation
    if (updates.rotation !== undefined || rotationDegrees > 0) {
      const rotValue = updates.rotation ?? rotationDegrees;
      if (rotValue > 0) {
        newEffects.push({
          type: 'rotation',
          intensity: 1.0,
          parameters: { degrees: rotValue },
        });
      }
    }

    // Fire
    if (updates.fire ?? enableFire) {
      newEffects.push({
        type: 'fire',
        intensity: 1.5,
        parameters: { particle_count: 50 },
      });
    }

    // Sparkles
    if (updates.sparkles ?? enableSparkles) {
      newEffects.push({
        type: 'sparkles',
        intensity: 0.5,
        parameters: { particle_count: 20 },
      });
    }

    // Laser Eyes
    if (updates.laserEyes ?? enableLaserEyes) {
      newEffects.push({
        type: 'laser_eyes',
        intensity: 2.0,
        parameters: {
          // Auto-estimate eye positions
        },
      });
    }

    // Glow
    if (updates.glow ?? enableGlow) {
      newEffects.push({
        type: 'glow',
        intensity: 2.0,
        parameters: { color: [255, 0, 0] },
      });
    }

    // Rainbow Aura
    if (updates.rainbow ?? enableRainbow) {
      newEffects.push({
        type: 'rainbow',
        intensity: 1.0,
        parameters: { speed: 0.02 },
      });
    }

    // Bloom
    if (updates.bloom ?? enableBloom) {
      newEffects.push({
        type: 'bloom',
        intensity: 1.5,
      });
    }

    // Glitch
    if (updates.glitch ?? enableGlitch) {
      newEffects.push({
        type: 'glitch',
        intensity: 0.3,
      });
    }

    // Hologram
    if (updates.hologram ?? enableHologram) {
      newEffects.push({
        type: 'hologram',
        intensity: 1.0,
        parameters: { speed: 2 },
      });
    }

    // Psychedelic
    if (updates.psychedelic ?? enablePsychedelic) {
      newEffects.push({
        type: 'psychedelic',
        intensity: 1.0,
        parameters: { speed: 0.05 },
      });
    }

    // Color Adjustments (if any are not at default)
    const brightnessValue = updates.brightness ?? brightness;
    const contrastValue = updates.contrast ?? contrast;
    const saturationValue = updates.saturation ?? saturation;

    if (brightnessValue !== 1.0 || contrastValue !== 1.0 || saturationValue !== 1.0) {
      newEffects.push({
        type: 'color_adjust',
        intensity: 1.0,
        parameters: {
          brightness: brightnessValue,
          contrast: contrastValue,
          saturation: saturationValue,
        },
      });
    }

    onChange(newEffects);
  };

  return (
    <div className="space-y-6 p-6 bg-gray-800 rounded-lg max-h-[800px] overflow-y-auto">
      <h2 className="text-2xl font-bold text-white mb-4">Effect Controls</h2>

      {/* Breathing Intensity */}
      <div className="space-y-2">
        <label className="text-white flex justify-between">
          <span>Breathing Intensity</span>
          <span className="text-gray-400">{(breathingIntensity * 100).toFixed(1)}%</span>
        </label>
        <input
          type="range"
          min="0.01"
          max="0.05"
          step="0.001"
          value={breathingIntensity}
          onChange={(e) => {
            const value = parseFloat(e.target.value);
            setBreathingIntensity(value);
            updateEffects({ breathing: value });
          }}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
        />
      </div>

      {/* Rotation */}
      <div className="space-y-2">
        <label className="text-white flex justify-between">
          <span>Rotation</span>
          <span className="text-gray-400">{rotationDegrees}°</span>
        </label>
        <input
          type="range"
          min="0"
          max="30"
          step="1"
          value={rotationDegrees}
          onChange={(e) => {
            const value = parseInt(e.target.value);
            setRotationDegrees(value);
            updateEffects({ rotation: value });
          }}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
        />
      </div>

      {/* Particle Effects */}
      <div className="space-y-3 pt-4 border-t border-gray-700">
        <h3 className="text-lg font-semibold text-white">🎆 Particle Effects</h3>

        {/* Fire */}
        <label className="flex items-center justify-between p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">🔥</span>
            <div>
              <div className="text-white font-medium">Fire Particles</div>
              <div className="text-sm text-gray-400">Rising flames from bottom</div>
            </div>
          </div>
          <input
            type="checkbox"
            checked={enableFire}
            onChange={(e) => {
              setEnableFire(e.target.checked);
              updateEffects({ fire: e.target.checked });
            }}
            className="w-5 h-5 accent-orange-500"
          />
        </label>

        {/* Sparkles */}
        <label className="flex items-center justify-between p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">✨</span>
            <div>
              <div className="text-white font-medium">Sparkles</div>
              <div className="text-sm text-gray-400">Twinkling star particles</div>
            </div>
          </div>
          <input
            type="checkbox"
            checked={enableSparkles}
            onChange={(e) => {
              setEnableSparkles(e.target.checked);
              updateEffects({ sparkles: e.target.checked });
            }}
            className="w-5 h-5 accent-yellow-500"
          />
        </label>

        {/* Laser Eyes */}
        <label className="flex items-center justify-between p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">👁️</span>
            <div>
              <div className="text-white font-medium">Laser Eyes</div>
              <div className="text-sm text-gray-400">Epic laser beams</div>
            </div>
          </div>
          <input
            type="checkbox"
            checked={enableLaserEyes}
            onChange={(e) => {
              setEnableLaserEyes(e.target.checked);
              updateEffects({ laserEyes: e.target.checked });
            }}
            className="w-5 h-5 accent-red-600"
          />
        </label>
      </div>

      {/* Visual Effects */}
      <div className="space-y-3 pt-4 border-t border-gray-700">
        <h3 className="text-lg font-semibold text-white">💫 Visual Effects</h3>

        {/* Glow */}
        <label className="flex items-center justify-between p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">💫</span>
            <div>
              <div className="text-white font-medium">Glow Effect</div>
              <div className="text-sm text-gray-400">Pulsing outer glow</div>
            </div>
          </div>
          <input
            type="checkbox"
            checked={enableGlow}
            onChange={(e) => {
              setEnableGlow(e.target.checked);
              updateEffects({ glow: e.target.checked });
            }}
            className="w-5 h-5 accent-red-500"
          />
        </label>

        {/* Rainbow Aura */}
        <label className="flex items-center justify-between p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">🌈</span>
            <div>
              <div className="text-white font-medium">Rainbow Aura</div>
              <div className="text-sm text-gray-400">Rotating rainbow outline</div>
            </div>
          </div>
          <input
            type="checkbox"
            checked={enableRainbow}
            onChange={(e) => {
              setEnableRainbow(e.target.checked);
              updateEffects({ rainbow: e.target.checked });
            }}
            className="w-5 h-5 accent-pink-500"
          />
        </label>

        {/* Bloom */}
        <label className="flex items-center justify-between p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">✨</span>
            <div>
              <div className="text-white font-medium">Bloom Filter</div>
              <div className="text-sm text-gray-400">Ethereal soft glow</div>
            </div>
          </div>
          <input
            type="checkbox"
            checked={enableBloom}
            onChange={(e) => {
              setEnableBloom(e.target.checked);
              updateEffects({ bloom: e.target.checked });
            }}
            className="w-5 h-5 accent-blue-400"
          />
        </label>
      </div>

      {/* Advanced Effects */}
      <div className="space-y-3 pt-4 border-t border-gray-700">
        <h3 className="text-lg font-semibold text-white">🎨 Advanced Effects</h3>

        {/* Glitch */}
        <label className="flex items-center justify-between p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">📺</span>
            <div>
              <div className="text-white font-medium">Glitch Effect</div>
              <div className="text-sm text-gray-400">RGB channel split</div>
            </div>
          </div>
          <input
            type="checkbox"
            checked={enableGlitch}
            onChange={(e) => {
              setEnableGlitch(e.target.checked);
              updateEffects({ glitch: e.target.checked });
            }}
            className="w-5 h-5 accent-green-500"
          />
        </label>

        {/* Hologram */}
        <label className="flex items-center justify-between p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">🔷</span>
            <div>
              <div className="text-white font-medium">Hologram</div>
              <div className="text-sm text-gray-400">Sci-fi scan lines</div>
            </div>
          </div>
          <input
            type="checkbox"
            checked={enableHologram}
            onChange={(e) => {
              setEnableHologram(e.target.checked);
              updateEffects({ hologram: e.target.checked });
            }}
            className="w-5 h-5 accent-cyan-500"
          />
        </label>

        {/* Psychedelic */}
        <label className="flex items-center justify-between p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">🌀</span>
            <div>
              <div className="text-white font-medium">Psychedelic</div>
              <div className="text-sm text-gray-400">Rapid color cycling</div>
            </div>
          </div>
          <input
            type="checkbox"
            checked={enablePsychedelic}
            onChange={(e) => {
              setEnablePsychedelic(e.target.checked);
              updateEffects({ psychedelic: e.target.checked });
            }}
            className="w-5 h-5 accent-purple-600"
          />
        </label>
      </div>

      {/* Color Adjustments */}
      <div className="space-y-3 pt-4 border-t border-gray-700">
        <h3 className="text-lg font-semibold text-white">🎨 Color Adjustments</h3>

        {/* Brightness */}
        <div className="space-y-2">
          <label className="text-white flex justify-between">
            <span>Brightness</span>
            <span className="text-gray-400">{brightness.toFixed(2)}</span>
          </label>
          <input
            type="range"
            min="0.5"
            max="1.5"
            step="0.05"
            value={brightness}
            onChange={(e) => {
              const value = parseFloat(e.target.value);
              setBrightness(value);
              updateEffects({ brightness: value });
            }}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-yellow-500"
          />
        </div>

        {/* Contrast */}
        <div className="space-y-2">
          <label className="text-white flex justify-between">
            <span>Contrast</span>
            <span className="text-gray-400">{contrast.toFixed(2)}</span>
          </label>
          <input
            type="range"
            min="0.5"
            max="1.5"
            step="0.05"
            value={contrast}
            onChange={(e) => {
              const value = parseFloat(e.target.value);
              setContrast(value);
              updateEffects({ contrast: value });
            }}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-orange-500"
          />
        </div>

        {/* Saturation */}
        <div className="space-y-2">
          <label className="text-white flex justify-between">
            <span>Saturation</span>
            <span className="text-gray-400">{saturation.toFixed(2)}</span>
          </label>
          <input
            type="range"
            min="0"
            max="2"
            step="0.1"
            value={saturation}
            onChange={(e) => {
              const value = parseFloat(e.target.value);
              setSaturation(value);
              updateEffects({ saturation: value });
            }}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-pink-500"
          />
        </div>

        {/* Reset Color Adjustments */}
        <button
          onClick={() => {
            setBrightness(1.0);
            setContrast(1.0);
            setSaturation(1.0);
            updateEffects({ brightness: 1.0, contrast: 1.0, saturation: 1.0 });
          }}
          className="w-full px-3 py-2 bg-gray-600 hover:bg-gray-500 text-white text-sm rounded-lg transition"
        >
          Reset Colors
        </button>
      </div>

      {/* Quick Presets */}
      <div className="pt-4 border-t border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-3">⚡ Quick Presets</h3>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => {
              setBreathingIntensity(0.015);
              setRotationDegrees(0);
              setEnableFire(false);
              setEnableSparkles(true);
              setEnableLaserEyes(false);
              setEnableGlow(false);
              setEnableRainbow(false);
              setEnableBloom(true);
              setEnableGlitch(false);
              setEnableHologram(false);
              setEnablePsychedelic(false);
              setBrightness(1.0);
              setContrast(1.0);
              setSaturation(1.0);
              updateEffects({
                breathing: 0.015, rotation: 0,
                fire: false, sparkles: true, laserEyes: false,
                glow: false, rainbow: false, bloom: true,
                glitch: false, hologram: false, psychedelic: false,
                brightness: 1.0, contrast: 1.0, saturation: 1.0
              });
            }}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
          >
            ✨ Subtle
          </button>
          <button
            onClick={() => {
              setBreathingIntensity(0.02);
              setRotationDegrees(10);
              setEnableFire(true);
              setEnableSparkles(false);
              setEnableLaserEyes(false);
              setEnableGlow(true);
              setEnableRainbow(false);
              setEnableBloom(false);
              setEnableGlitch(false);
              setEnableHologram(false);
              setEnablePsychedelic(false);
              setBrightness(1.0);
              setContrast(1.0);
              setSaturation(1.0);
              updateEffects({
                breathing: 0.02, rotation: 10,
                fire: true, sparkles: false, laserEyes: false,
                glow: true, rainbow: false, bloom: false,
                glitch: false, hologram: false, psychedelic: false,
                brightness: 1.0, contrast: 1.0, saturation: 1.0
              });
            }}
            className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition"
          >
            🔥 Dramatic
          </button>
          <button
            onClick={() => {
              setBreathingIntensity(0.02);
              setRotationDegrees(5);
              setEnableFire(false);
              setEnableSparkles(false);
              setEnableLaserEyes(true);
              setEnableGlow(true);
              setEnableRainbow(false);
              setEnableBloom(false);
              setEnableGlitch(false);
              setEnableHologram(false);
              setEnablePsychedelic(false);
              setBrightness(1.1);
              setContrast(1.2);
              setSaturation(1.3);
              updateEffects({
                breathing: 0.02, rotation: 5,
                fire: false, sparkles: false, laserEyes: true,
                glow: true, rainbow: false, bloom: false,
                glitch: false, hologram: false, psychedelic: false,
                brightness: 1.1, contrast: 1.2, saturation: 1.3
              });
            }}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
          >
            👁️ Laser Pepe
          </button>
          <button
            onClick={() => {
              setBreathingIntensity(0.02);
              setRotationDegrees(15);
              setEnableFire(false);
              setEnableSparkles(true);
              setEnableLaserEyes(false);
              setEnableGlow(false);
              setEnableRainbow(true);
              setEnableBloom(true);
              setEnableGlitch(false);
              setEnableHologram(false);
              setEnablePsychedelic(false);
              setBrightness(1.1);
              setContrast(1.0);
              setSaturation(1.5);
              updateEffects({
                breathing: 0.02, rotation: 15,
                fire: false, sparkles: true, laserEyes: false,
                glow: false, rainbow: true, bloom: true,
                glitch: false, hologram: false, psychedelic: false,
                brightness: 1.1, contrast: 1.0, saturation: 1.5
              });
            }}
            className="px-4 py-2 bg-pink-600 hover:bg-pink-700 text-white rounded-lg transition"
          >
            🌈 Rainbow
          </button>
          <button
            onClick={() => {
              setBreathingIntensity(0.01);
              setRotationDegrees(0);
              setEnableFire(false);
              setEnableSparkles(false);
              setEnableLaserEyes(false);
              setEnableGlow(false);
              setEnableRainbow(false);
              setEnableBloom(false);
              setEnableGlitch(true);
              setEnableHologram(false);
              setEnablePsychedelic(false);
              setBrightness(1.0);
              setContrast(1.2);
              setSaturation(0.8);
              updateEffects({
                breathing: 0.01, rotation: 0,
                fire: false, sparkles: false, laserEyes: false,
                glow: false, rainbow: false, bloom: false,
                glitch: true, hologram: false, psychedelic: false,
                brightness: 1.0, contrast: 1.2, saturation: 0.8
              });
            }}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition"
          >
            📺 Glitch Art
          </button>
          <button
            onClick={() => {
              setBreathingIntensity(0.015);
              setRotationDegrees(20);
              setEnableFire(false);
              setEnableSparkles(false);
              setEnableLaserEyes(false);
              setEnableGlow(false);
              setEnableRainbow(false);
              setEnableBloom(false);
              setEnableGlitch(false);
              setEnableHologram(false);
              setEnablePsychedelic(true);
              setBrightness(1.1);
              setContrast(1.0);
              setSaturation(1.8);
              updateEffects({
                breathing: 0.015, rotation: 20,
                fire: false, sparkles: false, laserEyes: false,
                glow: false, rainbow: false, bloom: false,
                glitch: false, hologram: false, psychedelic: true,
                brightness: 1.1, contrast: 1.0, saturation: 1.8
              });
            }}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
          >
            🌀 Trippy
          </button>
        </div>
      </div>
    </div>
  );
}
