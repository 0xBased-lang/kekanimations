import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('NFT Animation Playground', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to playground
    await page.goto('http://localhost:5173');

    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test('should display playground UI', async ({ page }) => {
    // Check header
    const header = page.locator('h1');
    await expect(header).toContainText('NFT Animation Playground');

    // Check upload section
    const uploadSection = page.locator('text=Upload NFT');
    await expect(uploadSection).toBeVisible();

    // Check effect controls
    const controls = page.locator('text=Effect Controls');
    await expect(controls).toBeVisible();

    // Check sliders
    const breathingSlider = page.locator('input[type="range"]').first();
    await expect(breathingSlider).toBeVisible();

    console.log('✅ All UI elements visible');
  });

  test('should upload and display NFT', async ({ page }) => {
    // Path to test image
    const testImagePath = path.join(__dirname, '..', 'temp_normie_rgb_1024.png');

    // Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testImagePath);

    // Wait for upload
    await page.waitForTimeout(2000);

    // Check for success message
    const successMsg = page.locator('text=Uploaded:');
    await expect(successMsg).toBeVisible({ timeout: 5000 });

    // Check canvas is visible
    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible();

    console.log('✅ NFT uploaded and displayed successfully');
  });

  test('should adjust breathing intensity', async ({ page }) => {
    // Upload test image first
    const testImagePath = path.join(__dirname, '..', 'temp_normie_rgb_1024.png');
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testImagePath);
    await page.waitForTimeout(2000);

    // Get breathing slider
    const breathingSlider = page.locator('input[type="range"]').first();

    // Get initial value
    const initialValue = await breathingSlider.inputValue();
    console.log('Initial breathing value:', initialValue);

    // Change slider value
    await breathingSlider.fill('0.03');
    await page.waitForTimeout(500);

    // Verify value changed
    const newValue = await breathingSlider.inputValue();
    console.log('New breathing value:', newValue);
    expect(newValue).toBe('0.03');

    // Check that effect is shown in active effects
    const activeEffects = page.locator('text=Active Effects').locator('..');
    await expect(activeEffects).toContainText('breathing');

    console.log('✅ Breathing slider works');
  });

  test('should toggle fire effect', async ({ page }) => {
    // Upload test image
    const testImagePath = path.join(__dirname, '..', 'temp_normie_rgb_1024.png');
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testImagePath);
    await page.waitForTimeout(2000);

    // Find fire toggle
    const fireToggle = page.locator('text=Fire Particles').locator('..').locator('input[type="checkbox"]');

    // Toggle on
    await fireToggle.check();
    await page.waitForTimeout(500);

    // Verify it's checked
    await expect(fireToggle).toBeChecked();

    // Check active effects
    const activeEffects = page.locator('text=Active Effects').locator('..');
    await expect(activeEffects).toContainText('fire');

    console.log('✅ Fire toggle works');
  });

  test('should apply dramatic preset', async ({ page }) => {
    // Upload test image
    const testImagePath = path.join(__dirname, '..', 'temp_normie_rgb_1024.png');
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testImagePath);
    await page.waitForTimeout(2000);

    // Click dramatic preset
    const dramaticButton = page.locator('button:has-text("Dramatic")');
    await dramaticButton.click();
    await page.waitForTimeout(500);

    // Check that multiple effects are active
    const activeEffects = page.locator('text=Active Effects').locator('..');
    await expect(activeEffects).toContainText('breathing');
    await expect(activeEffects).toContainText('rotation');
    await expect(activeEffects).toContainText('fire');
    await expect(activeEffects).toContainText('glow');

    console.log('✅ Dramatic preset works');
  });

  test('should check backend API health', async ({ page }) => {
    // Navigate to API docs
    await page.goto('http://localhost:8000/docs');

    // Check Swagger UI loaded
    const swagger = page.locator('.swagger-ui');
    await expect(swagger).toBeVisible({ timeout: 5000 });

    console.log('✅ Backend API is healthy');
  });

  test('should test backend health endpoint directly', async ({ request }) => {
    // Call health endpoint
    const response = await request.get('http://localhost:8000/health');

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data.presets_available).toContain('dramatic');
    expect(data.presets_available).toContain('subtle');

    console.log('✅ Backend health check passed:', data);
  });

  test('should test backend presets endpoint', async ({ request }) => {
    // Get all presets
    const response = await request.get('http://localhost:8000/api/presets');

    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.presets).toBeDefined();
    expect(data.presets.dramatic).toBeDefined();
    expect(data.presets.subtle).toBeDefined();
    expect(data.presets.psychedelic).toBeDefined();

    console.log('✅ Presets endpoint passed');
    console.log('Available presets:', Object.keys(data.presets));
  });
});
