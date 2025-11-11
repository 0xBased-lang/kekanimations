/**
 * GIF Export Utility
 *
 * Captures PixiJS canvas frames and exports as animated GIF
 */

import GIF from 'gif.js';

export interface GifExportOptions {
  width?: number;
  height?: number;
  quality?: number;
  fps?: number;
  frames?: number;
  workerScript?: string;
}

export async function exportCanvasToGif(
  canvas: HTMLCanvasElement,
  options: GifExportOptions = {}
): Promise<Blob> {
  const {
    width = 512,
    height = 512,
    quality = 10,
    fps = 12,
    frames = 24,
  } = options;

  return new Promise((resolve, reject) => {
    const gif = new GIF({
      workers: 2,
      quality,
      width,
      height,
      workerScript: '/gif.worker.js', // We'll need to copy this to public
    });

    let frameCount = 0;
    const frameDelay = 1000 / fps;

    // Capture frames
    const captureFrame = () => {
      if (frameCount >= frames) {
        // Finished capturing
        gif.render();
        return;
      }

      // Add current canvas frame
      gif.addFrame(canvas, { copy: true, delay: frameDelay });
      frameCount++;

      // Capture next frame
      requestAnimationFrame(captureFrame);
    };

    gif.on('finished', (blob) => {
      resolve(blob);
    });

    // Note: gif.js may not have 'error' event in types, handle errors via try/catch
    try {
      (gif as any).on('error', (error: any) => {
        reject(error);
      });
    } catch (e) {
      // Ignore if error event not supported
    }

    // Start capturing
    requestAnimationFrame(captureFrame);
  });
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export async function exportAndDownloadGif(
  canvas: HTMLCanvasElement,
  filename: string = 'nft-animation.gif',
  options: GifExportOptions = {}
): Promise<void> {
  try {
    const blob = await exportCanvasToGif(canvas, options);
    downloadBlob(blob, filename);
  } catch (error) {
    console.error('Failed to export GIF:', error);
    throw error;
  }
}

// Alternative: Record frames manually with better control
export class FrameRecorder {
  private frames: ImageData[] = [];
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D | null;
  private maxFrames: number;

  constructor(canvas: HTMLCanvasElement, maxFrames: number = 24) {
    this.canvas = canvas;
    this.ctx = document.createElement('canvas').getContext('2d');
    this.maxFrames = maxFrames;

    if (this.ctx) {
      this.ctx.canvas.width = canvas.width;
      this.ctx.canvas.height = canvas.height;
    }
  }

  captureFrame() {
    if (!this.ctx || this.frames.length >= this.maxFrames) return;

    // Draw current canvas to temp canvas
    this.ctx.drawImage(this.canvas, 0, 0);

    // Get image data
    const imageData = this.ctx.getImageData(
      0,
      0,
      this.canvas.width,
      this.canvas.height
    );

    this.frames.push(imageData);
  }

  async exportToGif(options: GifExportOptions = {}): Promise<Blob> {
    const {
      quality = 10,
      fps = 12,
    } = options;

    return new Promise((resolve, reject) => {
      const gif = new GIF({
        workers: 2,
        quality,
        width: this.canvas.width,
        height: this.canvas.height,
        workerScript: '/gif.worker.js',
      });

      const frameDelay = 1000 / fps;

      // Add all captured frames
      for (const imageData of this.frames) {
        // Create temporary canvas for this frame
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = imageData.width;
        tempCanvas.height = imageData.height;
        const tempCtx = tempCanvas.getContext('2d');

        if (tempCtx) {
          tempCtx.putImageData(imageData, 0, 0);
          gif.addFrame(tempCanvas, { copy: true, delay: frameDelay });
        }
      }

      gif.on('finished', (blob) => {
        resolve(blob);
      });

      try {
        (gif as any).on('error', (error: any) => {
          reject(error);
        });
      } catch (e) {
        // Ignore if error event not supported
      }

      gif.render();
    });
  }

  reset() {
    this.frames = [];
  }

  get frameCount() {
    return this.frames.length;
  }

  get isComplete() {
    return this.frames.length >= this.maxFrames;
  }
}
