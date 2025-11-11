import { test, expect } from '@playwright/test';
import { QualityScorer } from './fixtures/quality-scorer';
import path from 'path';
import fs from 'fs/promises';

test.describe('NFT Animation Quality Validation', () => {
  const scorer = new QualityScorer();

  test('Quality check: normie_8frames_SUCCESS.gif', async () => {
    const animationPath = path.join(process.cwd(), 'final_output/normie_8frames_SUCCESS.gif');
    const originalPath = path.join(process.cwd(), 'temp_normie_rgb.png');

    // Check files exist
    try {
      await fs.access(animationPath);
      await fs.access(originalPath);
    } catch (error) {
      console.log('⚠️  Test files not found - skipping quality validation');
      console.log(`   Animation: ${animationPath}`);
      console.log(`   Original: ${originalPath}`);
      test.skip();
      return;
    }

    // Score the animation
    const score = await scorer.scoreAnimation(animationPath, originalPath, 70);

    // Print detailed report
    console.log(scorer.formatReport(score));

    // Save JSON report
    const reportPath = path.join('test-results', `quality-report-${Date.now()}.json`);
    await fs.mkdir('test-results', { recursive: true });
    await fs.writeFile(reportPath, JSON.stringify(score, null, 2));
    console.log(`\n📄 Detailed report saved: ${reportPath}`);

    // Assertions
    expect(score.total).toBeGreaterThan(0);
    expect(score.breakdown.technical).toBeLessThanOrEqual(40);
    expect(score.breakdown.preservation).toBeLessThanOrEqual(30);
    expect(score.breakdown.motion).toBeLessThanOrEqual(20);
    expect(score.breakdown.efficiency).toBeLessThanOrEqual(10);

    // Quality threshold check
    if (!score.passesThreshold) {
      console.log(`\n⚠️  Score ${score.total}/100 below threshold ${70}`);
      console.log('This animation should be regenerated with adjusted parameters.');
    }

    // Expect at least 60/100 (acceptable quality)
    expect(score.total).toBeGreaterThanOrEqual(60);
  });

  test('Batch quality summary', async () => {
    const outputDir = path.join(process.cwd(), 'final_output');

    try {
      const files = await fs.readdir(outputDir);
      const gifFiles = files.filter(f => f.endsWith('.gif'));

      console.log('\n' + '='.repeat(60));
      console.log(`📊 BATCH QUALITY SUMMARY`);
      console.log('='.repeat(60));
      console.log(`Total animations found: ${gifFiles.length}\n`);

      if (gifFiles.length === 0) {
        console.log('⚠️  No GIF files found in final_output directory');
        console.log('Generate animations first before running batch analysis.\n');
      } else {
        console.log('Files found:');
        gifFiles.forEach(file => console.log(`  - ${file}`));
        console.log('\n💡 Run individual quality tests to analyze each animation');
      }

      console.log('='.repeat(60));
    } catch (error) {
      console.log('⚠️  Output directory not found - create animations first');
    }
  });
});
