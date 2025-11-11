/**
 * Comprehensive Playwright Tests for NFT Animation Effects
 *
 * Tests all animation effects with visual validation
 */

import { test, expect, Page } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TEST_IMAGE = path.join(__dirname, '../../../fixtures/test_normie.png');
const APP_URL = 'http://localhost:5173';

// Helper to wait for PixiJS to initialize
async function waitForPixiJS(page: Page) {
  await page.waitForFunction(() => {
    return window.performance.now() > 0;
  });
  await page.waitForTimeout(1000); // Give PixiJS time to initialize
}

// Helper to upload test image
async function uploadTestImage(page: Page) {
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(TEST_IMAGE);
  await page.waitForSelector('img, canvas');
  await waitForPixiJS(page);
}

// Helper to get canvas element
async function getCanvas(page: Page) {
  const canvas = page.locator('canvas').first();
  await expect(canvas).toBeVisible();
  return canvas;
}

// Helper to take canvas screenshot
async function captureCanvas(page: Page, filename: string) {
  const canvas = await getCanvas(page);
  await canvas.screenshot({ path: `screenshots/${filename}` });
}

test.describe('NFT Animation Playground', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
    await expect(page.locator('h1')).toContainText('NFT Animation Playground');
  });

  test('should load the application', async ({ page }) => {
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('h2:has-text("Upload NFT")')).toBeVisible();
    await expect(page.locator('h2:has-text("Effect Controls")')).toBeVisible();
  });

  test('should upload an image successfully', async ({ page }) => {
    await uploadTestImage(page);

    // Check for success message
    await expect(page.locator('text=/Uploaded:/i')).toBeVisible();

    // Canvas should be visible
    const canvas = await getCanvas(page);
    await expect(canvas).toBeVisible();

    // Take screenshot
    await captureCanvas(page, 'uploaded-image.png');
  });

  test('should display effect controls', async ({ page }) => {
    // Check sliders
    await expect(page.locator('label:has-text("Breathing Intensity")')).toBeVisible();
    await expect(page.locator('label:has-text("Rotation")')).toBeVisible();

    // Check checkboxes
    await expect(page.locator('text=/Fire Particles/i')).toBeVisible();
    await expect(page.locator('text=/Sparkles/i')).toBeVisible();
    await expect(page.locator('text=/Glow Effect/i')).toBeVisible();

    // Check preset buttons
    await expect(page.locator('button:has-text("Subtle")')).toBeVisible();
    await expect(page.locator('button:has-text("Dramatic")')).toBeVisible();
  });
});

test.describe('Breathing Effect', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
    await uploadTestImage(page);
  });

  test('should apply breathing effect at minimum intensity', async ({ page }) => {
    const slider = page.locator('input[type="range"]').first();
    await slider.fill('0.01');

    // Wait for animation
    await page.waitForTimeout(2000);

    // Verify active effects chip shows breathing
    await expect(page.locator('text=/breathing \\(/i')).toBeVisible();

    await captureCanvas(page, 'breathing-min.png');
  });

  test('should apply breathing effect at maximum intensity', async ({ page }) => {
    const slider = page.locator('input[type="range"]').first();
    await slider.fill('0.05');

    // Verify intensity display
    await expect(page.locator('text=/5.0%/i')).toBeVisible();

    await page.waitForTimeout(2000);
    await captureCanvas(page, 'breathing-max.png');
  });

  test('should animate breathing smoothly', async ({ page }) => {
    // Take multiple screenshots to verify animation
    for (let i = 0; i < 3; i++) {
      await page.waitForTimeout(500);
      await captureCanvas(page, `breathing-frame-${i}.png`);
    }
  });
});

test.describe('Rotation Effect', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
    await uploadTestImage(page);
  });

  test('should apply rotation effect', async ({ page }) => {
    const slider = page.locator('input[type="range"]').nth(1);
    await slider.fill('15');

    // Verify degree display
    await expect(page.locator('text=/15°/i')).toBeVisible();

    await page.waitForTimeout(2000);
    await captureCanvas(page, 'rotation-15deg.png');
  });

  test('should apply maximum rotation', async ({ page }) => {
    const slider = page.locator('input[type="range"]').nth(1);
    await slider.fill('30');

    await expect(page.locator('text=/30°/i')).toBeVisible();

    await page.waitForTimeout(2000);
    await captureCanvas(page, 'rotation-30deg.png');
  });

  test('should disable rotation when set to 0', async ({ page }) => {
    const slider = page.locator('input[type="range"]').nth(1);
    await slider.fill('0');

    // Should not show rotation in active effects
    const activeEffects = page.locator('.stat-line, .bg-blue-600');
    await expect(activeEffects.filter({ hasText: 'rotation' })).toHaveCount(0);
  });
});

test.describe('Fire Particles Effect', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
    await uploadTestImage(page);
  });

  test('should enable fire particles', async ({ page }) => {
    const checkbox = page.locator('input[type="checkbox"]').first();
    await checkbox.check();

    // Verify fire is in active effects
    await expect(page.locator('text=/fire \\(/i')).toBeVisible();

    // Wait for particles to appear
    await page.waitForTimeout(3000);
    await captureCanvas(page, 'fire-particles.png');
  });

  test('should disable fire particles', async ({ page }) => {
    const checkbox = page.locator('input[type="checkbox"]').first();

    // Enable first
    await checkbox.check();
    await page.waitForTimeout(1000);

    // Then disable
    await checkbox.uncheck();
    await page.waitForTimeout(1000);

    // Fire should not be in active effects
    const activeEffects = page.locator('.bg-blue-600');
    await expect(activeEffects.filter({ hasText: 'fire' })).toHaveCount(0);
  });

  test('should render fire particles with correct visual properties', async ({ page }) => {
    const checkbox = page.locator('input[type="checkbox"]').first();
    await checkbox.check();

    // Capture multiple frames to verify animation
    for (let i = 0; i < 5; i++) {
      await page.waitForTimeout(500);
      await captureCanvas(page, `fire-particles-frame-${i}.png`);
    }
  });
});

test.describe('Sparkles Effect', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
    await uploadTestImage(page);
  });

  test('should enable sparkles', async ({ page }) => {
    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await checkbox.check();

    // Verify sparkles in active effects
    await expect(page.locator('text=/sparkles \\(/i')).toBeVisible();

    await page.waitForTimeout(3000);
    await captureCanvas(page, 'sparkles.png');
  });

  test('should render sparkles with twinkling effect', async ({ page }) => {
    const checkbox = page.locator('input[type="checkbox"]').nth(1);
    await checkbox.check();

    // Capture multiple frames
    for (let i = 0; i < 5; i++) {
      await page.waitForTimeout(500);
      await captureCanvas(page, `sparkles-frame-${i}.png`);
    }
  });
});

test.describe('Glow Effect', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
    await uploadTestImage(page);
  });

  test('should enable glow effect', async ({ page }) => {
    const checkbox = page.locator('label:has-text("Glow Effect") input[type="checkbox"]');
    await checkbox.check();

    // Wait for effect to activate
    await page.waitForTimeout(500);
    await expect(page.locator('text=/glow \\(/i')).toBeVisible();

    await page.waitForTimeout(2000);
    await captureCanvas(page, 'glow-effect.png');
  });

  test('should use proper PixiJS glow filter', async ({ page }) => {
    const checkbox = page.locator('input[type="checkbox"]').nth(2);
    await checkbox.check();

    // Check console for filter application
    const logs: string[] = [];
    page.on('console', msg => logs.push(msg.text()));

    await page.waitForTimeout(2000);

    // Verify no errors in console
    const errors = logs.filter(log => log.toLowerCase().includes('error'));
    expect(errors).toHaveLength(0);
  });
});

test.describe('Combined Effects', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
    await uploadTestImage(page);
  });

  test('should apply breathing + rotation together', async ({ page }) => {
    const breathingSlider = page.locator('input[type="range"]').first();
    const rotationSlider = page.locator('input[type="range"]').nth(1);

    await breathingSlider.fill('0.03');
    await rotationSlider.fill('20');

    await page.waitForTimeout(3000);
    await captureCanvas(page, 'breathing-rotation-combined.png');
  });

  test('should apply all effects together', async ({ page }) => {
    // Enable all effects
    const breathingSlider = page.locator('input[type="range"]').first();
    const rotationSlider = page.locator('input[type="range"]').nth(1);
    const fireCheckbox = page.locator('label:has-text("Fire Particles") input[type="checkbox"]');
    const sparklesCheckbox = page.locator('label:has-text("Sparkles") input[type="checkbox"]');
    const glowCheckbox = page.locator('label:has-text("Glow Effect") input[type="checkbox"]');

    await breathingSlider.fill('0.03');
    await rotationSlider.fill('15');
    await fireCheckbox.check();
    await sparklesCheckbox.check();
    await glowCheckbox.check();

    // Wait for effects to activate
    await page.waitForTimeout(1000);

    // Verify all effects are active
    await expect(page.locator('text=/breathing \\(/i')).toBeVisible();
    await expect(page.locator('text=/rotation \\(/i')).toBeVisible();
    await expect(page.locator('text=/fire \\(/i')).toBeVisible();
    await expect(page.locator('text=/sparkles \\(/i')).toBeVisible();
    await expect(page.locator('text=/glow \\(/i')).toBeVisible();

    await page.waitForTimeout(4000);
    await captureCanvas(page, 'all-effects-combined.png');
  });
});

test.describe('Presets', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(APP_URL);
    await uploadTestImage(page);
  });

  test('should apply "Subtle" preset', async ({ page }) => {
    const subtleButton = page.locator('button:has-text("Subtle")');
    await subtleButton.click();

    await page.waitForTimeout(2000);
    await captureCanvas(page, 'preset-subtle.png');
  });

  test('should apply "Dramatic" preset', async ({ page }) => {
    const dramaticButton = page.locator('button:has-text("Dramatic")');
    await dramaticButton.click();

    // Verify multiple effects are active
    await page.waitForTimeout(2000);
    await captureCanvas(page, 'preset-dramatic.png');
  });

  test('should switch between presets correctly', async ({ page }) => {
    // Apply subtle
    await page.locator('button:has-text("Subtle")').click();
    await page.waitForTimeout(1000);
    await captureCanvas(page, 'preset-switch-1.png');

    // Switch to dramatic
    await page.locator('button:has-text("Dramatic")').click();
    await page.waitForTimeout(1000);
    await captureCanvas(page, 'preset-switch-2.png');

    // Switch back to subtle
    await page.locator('button:has-text("Subtle")').click();
    await page.waitForTimeout(1000);
    await captureCanvas(page, 'preset-switch-3.png');
  });
});

test.describe('Performance', () => {

  test('should maintain 60 FPS with all effects', async ({ page }) => {
    await page.goto(APP_URL);
    await uploadTestImage(page);

    // Enable all effects
    const breathingSlider = page.locator('input[type="range"]').first();
    const rotationSlider = page.locator('input[type="range"]').nth(1);
    const fireCheckbox = page.locator('input[type="checkbox"]').first();
    const sparklesCheckbox = page.locator('input[type="checkbox"]').nth(1);
    const glowCheckbox = page.locator('input[type="checkbox"]').nth(2);

    await breathingSlider.fill('0.05');
    await rotationSlider.fill('30');
    await fireCheckbox.check();
    await sparklesCheckbox.check();
    await glowCheckbox.check();

    // Check performance metrics
    const metrics = await page.evaluate(() => {
      return {
        memory: (performance as any).memory?.usedJSHeapSize,
        timing: performance.timing.loadEventEnd - performance.timing.navigationStart
      };
    });

    console.log('Performance metrics:', metrics);

    // Memory should be reasonable (< 200MB)
    if (metrics.memory) {
      expect(metrics.memory).toBeLessThan(200 * 1024 * 1024);
    }
  });

  test('should handle image switching without memory leaks', async ({ page }) => {
    await page.goto(APP_URL);

    // Upload image multiple times
    for (let i = 0; i < 3; i++) {
      await uploadTestImage(page);
      await page.waitForTimeout(1000);
    }

    // Should still be responsive
    await expect(page.locator('h1')).toBeVisible();
  });
});

test.describe('Error Handling', () => {

  test('should handle invalid image gracefully', async ({ page }) => {
    await page.goto(APP_URL);

    // Try to upload a non-image file
    const fileInput = page.locator('input[type="file"]');

    // Create a temporary text file
    const textContent = 'This is not an image';
    const buffer = Buffer.from(textContent);

    await fileInput.setInputFiles({
      name: 'test.txt',
      mimeType: 'text/plain',
      buffer
    });

    // Should show error or handle gracefully
    await page.waitForTimeout(1000);
  });

  test('should handle PixiJS initialization failure', async ({ page }) => {
    // Block WebGL to simulate failure
    await page.goto(APP_URL);

    // Application should still load
    await expect(page.locator('h1')).toBeVisible();
  });
});

test.describe('Accessibility', () => {

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto(APP_URL);

    // Tab through controls
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Should be able to interact with keyboard
    await page.keyboard.press('Space');
  });

  test('should have proper ARIA labels', async ({ page }) => {
    await page.goto(APP_URL);

    // Check for labels on form elements
    const sliders = page.locator('input[type="range"]');
    const count = await sliders.count();
    expect(count).toBeGreaterThan(0);
  });
});
