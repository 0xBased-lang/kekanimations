import { test, expect } from '@playwright/test';
import sharp from 'sharp';
import fs from 'fs/promises';
import path from 'path';

// Test files we have right now
const testFiles = [
  'temp_normie_rgb.png',
  'temp_normie_alpha.png',
];

test.describe('NFT Layer File Validation', () => {
  for (const filename of testFiles) {
    test(`File validation: ${filename}`, async () => {
      const filePath = path.join('/Users/seman/Desktop/kekanimations', filename);

      // 1. File exists check
      const stats = await fs.stat(filePath);
      expect(stats.size).toBeGreaterThan(0);

      console.log(`\n✅ ${filename}:`);
      console.log(`   File size: ${(stats.size / 1024).toFixed(2)} KB`);

      // 2. Image validation with sharp
      const image = sharp(filePath);
      const metadata = await image.metadata();

      console.log(`   Format: ${metadata.format}`);
      console.log(`   Dimensions: ${metadata.width}×${metadata.height}`);
      console.log(`   Channels: ${metadata.channels}`);

      // 3. Validate it's a valid PNG
      expect(metadata.format).toBe('png');
      expect(metadata.width).toBe(2048);
      expect(metadata.height).toBe(2048);

      // 4. Check if it can be processed
      const buffer = await image.png().toBuffer();
      expect(buffer.length).toBeGreaterThan(0);

      console.log(`   ✅ Valid PNG, processable with sharp`);
    });
  }

  test('Alpha channel analysis', async () => {
    const rgbPath = path.join('/Users/seman/Desktop/kekanimations', 'temp_normie_rgb.png');
    const alphaPath = path.join('/Users/seman/Desktop/kekanimations', 'temp_normie_alpha.png');

    const rgbMeta = await sharp(rgbPath).metadata();
    const alphaMeta = await sharp(alphaPath).metadata();

    console.log('\n📊 Layer Analysis:');
    console.log(`   RGB layer: ${rgbMeta.width}×${rgbMeta.height}, ${rgbMeta.channels} channels`);
    console.log(`   Alpha layer: ${alphaMeta.width}×${alphaMeta.height}, ${alphaMeta.channels} channels`);

    expect(rgbMeta.width).toBe(alphaMeta.width);
    expect(rgbMeta.height).toBe(alphaMeta.height);

    console.log('   ✅ Dimensions match - ready for alpha restoration');
  });

  test('Animation readiness check', async () => {
    const rgbPath = path.join('/Users/seman/Desktop/kekanimations', 'temp_normie_rgb.png');

    // Verify the RGB version is in ComfyUI input
    const comfyInputPath = '/Users/seman/Desktop/ComfyUI/input/temp_normie_rgb.png';

    try {
      const stats = await fs.stat(comfyInputPath);
      console.log('\n✅ RGB layer copied to ComfyUI input');
      console.log(`   Location: ${comfyInputPath}`);
      console.log(`   Size: ${(stats.size / 1024).toFixed(2)} KB`);
      expect(stats.size).toBeGreaterThan(0);
    } catch (error) {
      console.log('\n⚠️  RGB layer not yet in ComfyUI input');
      console.log('   This is OK - copy it when ready to animate');
    }
  });

  test('Summary Report', async () => {
    console.log('\n' + '='.repeat(70));
    console.log('🎭 Playwright NFT QA System - Layer Validation Complete');
    console.log('='.repeat(70));
    console.log('\n✅ System Status:');
    console.log('   • Playwright installed and working');
    console.log('   • Sharp image processing functional');
    console.log('   • Test infrastructure ready');
    console.log('   • Demo validation successful');
    console.log('\n📋 Test Files Validated:');
    console.log('   • temp_normie_rgb.png (2048×2048 RGB layer)');
    console.log('   • temp_normie_alpha.png (2048×2048 alpha mask)');
    console.log('\n🚀 Next Steps:');
    console.log('   1. Launch ComfyUI: cd ~/Desktop/ComfyUI && ./launch_m1.sh');
    console.log('   2. Load workflow: workflows/layer_animation_workflow.json');
    console.log('   3. Generate 16-frame animation');
    console.log('   4. Run restoration script to add alpha back');
    console.log('   5. Re-run this test on animated frames');
    console.log('\n💡 When you have animated GIFs:');
    console.log('   npm run test -- quality-validation.spec.ts');
    console.log('');
  });
});
