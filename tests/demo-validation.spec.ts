import { test, expect } from '@playwright/test';
import sharp from 'sharp';
import fs from 'fs/promises';
import path from 'path';

// Test files we have right now
const testFiles = [
  'temp_normie_rgb.png',
  'temp_normie_alpha.png',
];

test.describe('NFT Layer Validation Demo', () => {
  for (const filename of testFiles) {
    test(`Validate ${filename}`, async ({ page }) => {
      const filePath = path.join('/Users/seman/Desktop/kekanimations', filename);

      // 1. File exists check
      const stats = await fs.stat(filePath);
      expect(stats.size).toBeGreaterThan(0);

      // 2. Image validation with sharp
      const image = sharp(filePath);
      const metadata = await image.metadata();

      console.log(`\n${filename}:`);
      console.log(`  Format: ${metadata.format}`);
      console.log(`  Dimensions: ${metadata.width}×${metadata.height}`);
      console.log(`  Size: ${(stats.size / 1024).toFixed(2)} KB`);
      console.log(`  Has Alpha: ${metadata.hasAlpha || false}`);

      // 3. Validate it's a valid image
      expect(metadata.format).toBeTruthy();
      expect(metadata.width).toBeGreaterThan(0);
      expect(metadata.height).toBeGreaterThan(0);

      // 4. Load in browser
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
              flex-direction: column;
              color: white;
              font-family: monospace;
            }
            img {
              border: 2px solid #fff;
              margin: 20px;
              image-rendering: crisp-edges;
            }
            .info {
              background: #333;
              padding: 20px;
              border-radius: 8px;
              margin-top: 20px;
            }
          </style>
        </head>
        <body>
          <h2>${filename}</h2>
          <img id="test-image" src="${process.env.TEST_SERVER_URL || 'http://localhost:8765'}/${filename}" alt="Test Image" />
          <div class="info">
            <div>Format: ${metadata.format}</div>
            <div>Size: ${metadata.width}×${metadata.height}</div>
            <div>File Size: ${(stats.size / 1024).toFixed(2)} KB</div>
          </div>
        </body>
        </html>
      `);

      // 5. Wait for image to load
      await page.waitForSelector('#test-image');
      await page.waitForLoadState('networkidle');

      // 6. Verify it loaded
      const imageLoaded = await page.evaluate(() => {
        const img = document.querySelector('#test-image') as HTMLImageElement;
        return img.complete && img.naturalWidth > 0;
      });

      expect(imageLoaded).toBe(true);

      // 7. Take screenshot
      await page.screenshot({
        path: `test-results/screenshots/${filename.replace('.png', '')}-validation.png`,
        fullPage: true,
      });

      console.log(`  ✅ Browser rendering: OK`);
      console.log(`  ✅ Screenshot saved`);
    });
  }

  test('Summary', async () => {
    console.log('\n' + '='.repeat(60));
    console.log('Demo Validation Complete!');
    console.log('='.repeat(60));
    console.log(`✅ Validated ${testFiles.length} test files`);
    console.log('\nNext steps:');
    console.log('  1. Generate animation in ComfyUI');
    console.log('  2. Run full validation on animated frames');
    console.log('  3. Scale to all 4,200 NFTs');
  });
});
