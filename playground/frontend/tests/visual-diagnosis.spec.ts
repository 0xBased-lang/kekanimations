/**
 * Visual Diagnosis - Show what's actually happening
 */
import { test } from '@playwright/test';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const TEST_IMAGE_PATH = path.resolve(__dirname, '../../../fixtures/test_normie.png');

test('Visual diagnosis - capture current state', async ({ page }) => {
  await page.goto('http://localhost:5173');

  // Upload image
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(TEST_IMAGE_PATH);
  await page.waitForTimeout(1000);

  // Take screenshot of initial state
  await page.screenshot({ path: 'DIAGNOSIS-01-initial.png', fullPage: true });

  // Enable sparkles
  const sparklesCheckbox = page.locator('label:has-text("Sparkles") input[type="checkbox"]');
  await sparklesCheckbox.check();
  await page.waitForTimeout(2000);

  // Take screenshot with sparkles
  await page.screenshot({ path: 'DIAGNOSIS-02-sparkles.png', fullPage: true });

  // Enable fire
  const fireCheckbox = page.locator('label:has-text("Fire Particles") input[type="checkbox"]');
  await fireCheckbox.check();
  await page.waitForTimeout(2000);

  // Take screenshot with fire
  await page.screenshot({ path: 'DIAGNOSIS-03-fire.png', fullPage: true });

  // Enable laser eyes
  const laserCheckbox = page.locator('label:has-text("Laser Eyes") input[type="checkbox"]');
  await laserCheckbox.check();
  await page.waitForTimeout(2000);

  // Take screenshot with laser eyes
  await page.screenshot({ path: 'DIAGNOSIS-04-laser-eyes.png', fullPage: true });

  console.log('Screenshots saved:');
  console.log('  DIAGNOSIS-01-initial.png');
  console.log('  DIAGNOSIS-02-sparkles.png');
  console.log('  DIAGNOSIS-03-fire.png');
  console.log('  DIAGNOSIS-04-laser-eyes.png');
});
