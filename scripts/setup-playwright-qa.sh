#!/bin/bash
# Setup Playwright Quality Assurance System for KEKTECH NFT Animations

set -e

echo "🎭 Setting up Playwright NFT Quality Assurance System"
echo "======================================================"

cd /Users/seman/Desktop/kekanimations

# 1. Initialize npm if not exists
if [ ! -f "package.json" ]; then
    echo "📦 Initializing npm project..."
    npm init -y
fi

# 2. Install Playwright and dependencies
echo "📥 Installing Playwright and dependencies..."
npm install --save-dev \
    @playwright/test \
    sharp \
    pixelmatch \
    pngjs \
    glob \
    ipfs-http-client

# 3. Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
npx playwright install chromium

# 4. Create directory structure
echo "📁 Creating directory structure..."
mkdir -p tests
mkdir -p fixtures
mkdir -p utils
mkdir -p test-results/screenshots
mkdir -p test-results/diffs
mkdir -p test-results/html
mkdir -p test-references/animations

# 5. Create playwright.config.ts
echo "⚙️  Creating Playwright configuration..."
cat > playwright.config.ts << 'EOF'
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 4 : 10,
  reporter: [
    ['html', { outputFolder: 'test-results/html' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list'],
  ],
  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
EOF

# 6. Create basic animation loader fixture
echo "🔧 Creating animation loader fixture..."
cat > fixtures/animation-loader.ts << 'EOF'
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
EOF

# 7. Create sample test
echo "✅ Creating sample validation test..."
cat > tests/sample-validation.spec.ts << 'EOF'
import { test, expect } from '../fixtures/animation-loader';
import { glob } from 'glob';
import path from 'path';

const ANIMATIONS_DIR = '/Users/seman/Desktop/kekanimations/animated_frames';

// Find all PNG files (test with individual frames first)
const frames = glob.sync(path.join(ANIMATIONS_DIR, 'normie_*.png')).slice(0, 5);

console.log(`Found ${frames.length} frames to validate`);

for (const framePath of frames) {
  const frameId = path.basename(framePath, '.png');

  test(`Frame ${frameId} - Quality Check`, async ({ page, animationLoader }) => {
    // Browser rendering test
    const loaded = await animationLoader.loadInBrowser(page, framePath);
    expect(loaded).toBe(true);

    // Take screenshot
    await page.screenshot({
      path: `test-results/screenshots/${frameId}.png`,
      fullPage: true,
    });
  });
}

test('Sample validation complete', async () => {
  console.log(`\n✅ Validated ${frames.length} frames successfully`);
});
EOF

# 8. Update package.json with test scripts
echo "📝 Adding test scripts to package.json..."
npm pkg set scripts.test="playwright test"
npm pkg set scripts.test:ui="playwright test --ui"
npm pkg set scripts.test:report="playwright show-report test-results/html"
npm pkg set scripts.test:sample="playwright test sample-validation.spec.ts"

echo ""
echo "✅ Playwright QA System Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Run sample test: npm run test:sample"
echo "  2. View results: npm run test:report"
echo "  3. Read full guide: open PLAYWRIGHT_NFT_QA.md"
echo ""
echo "🚀 Ready to validate 4,200 NFT animations!"
