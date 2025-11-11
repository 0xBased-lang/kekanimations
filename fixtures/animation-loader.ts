import { test as base } from '@playwright/test';
import sharp from 'sharp';
import fs from 'fs/promises';

type AnimationFixtures = {
  animationLoader: AnimationLoader;
};

class AnimationLoader {
  async validate(gifPath: string) {
    const stats = await fs.stat(gifPath);
    const fileSizeMB = stats.size / (1024 * 1024);

    if (fileSizeMB < 1 || fileSizeMB > 6) {
      throw new Error(`File size ${fileSizeMB.toFixed(2)}MB outside range (1-6MB)`);
    }

    const image = sharp(gifPath);
    const metadata = await image.metadata();

    if (metadata.width !== 512 || metadata.height !== 512) {
      throw new Error(`Invalid dimensions: ${metadata.width}×${metadata.height}, expected 512×512`);
    }

    if (metadata.format !== 'gif') {
      throw new Error(`Invalid format: ${metadata.format}, expected gif`);
    }

    return {
      valid: true,
      fileSize: fileSizeMB,
      dimensions: `${metadata.width}×${metadata.height}`,
      format: metadata.format,
      frames: metadata.pages || 16,
      hasAlpha: metadata.hasAlpha || false,
    };
  }

  async loadInBrowser(page: any, gifPath: string) {
    await page.setContent(`
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          body {
            margin: 0;
            background: #222;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
          }
          img {
            border: 2px solid #fff;
            image-rendering: crisp-edges;
          }
        </style>
      </head>
      <body>
        <img id="nft" src="file://${gifPath}" alt="NFT Animation" />
      </body>
      </html>
    `);

    await page.waitForSelector('#nft');
    await page.waitForLoadState('networkidle');

    const isLoaded = await page.evaluate(() => {
      const img = document.querySelector('#nft') as HTMLImageElement;
      return img.complete && img.naturalWidth > 0;
    });

    if (!isLoaded) {
      throw new Error('Animation failed to load in browser');
    }

    return true;
  }
}

export const test = base.extend<AnimationFixtures>({
  animationLoader: async ({}, use) => {
    const loader = new AnimationLoader();
    await use(loader);
  },
});

export { expect } from '@playwright/test';
