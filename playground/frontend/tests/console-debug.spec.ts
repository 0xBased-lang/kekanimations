/**
 * Console Debug - Capture what's actually happening
 */
import { test } from '@playwright/test';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const TEST_IMAGE_PATH = path.resolve(__dirname, '../../../fixtures/test_normie.png');

test('Console debug - check what fires when effects enabled', async ({ page }) => {
  const consoleLogs: string[] = [];
  const consoleErrors: string[] = [];

  // Capture all console messages
  page.on('console', msg => {
    const text = msg.text();
    consoleLogs.push(`[${msg.type()}] ${text}`);
    if (msg.type() === 'error') {
      consoleErrors.push(text);
    }
  });

  await page.goto('http://localhost:5173');
  await page.waitForTimeout(1000);

  // Upload image
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(TEST_IMAGE_PATH);
  await page.waitForTimeout(2000);

  console.log('\n=== AFTER IMAGE UPLOAD ===');
  consoleLogs.forEach(log => console.log(log));
  consoleLogs.length = 0;

  // Enable fire
  const fireCheckbox = page.locator('label:has-text("Fire Particles") input[type="checkbox"]');
  await fireCheckbox.check();
  await page.waitForTimeout(3000);

  console.log('\n=== AFTER ENABLING FIRE ===');
  consoleLogs.forEach(log => console.log(log));
  consoleLogs.length = 0;

  // Enable sparkles
  const sparklesCheckbox = page.locator('label:has-text("Sparkles") input[type="checkbox"]');
  await sparklesCheckbox.check();
  await page.waitForTimeout(3000);

  console.log('\n=== AFTER ENABLING SPARKLES ===');
  consoleLogs.forEach(log => console.log(log));

  console.log('\n=== CONSOLE ERRORS ===');
  if (consoleErrors.length > 0) {
    consoleErrors.forEach(err => console.log('ERROR:', err));
  } else {
    console.log('No console errors');
  }
});
