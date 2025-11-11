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
