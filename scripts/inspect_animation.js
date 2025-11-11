/**
 * Playwright Script to Inspect NFT Animation Effects
 *
 * This script will:
 * 1. Open the ComfyUI interface
 * 2. Analyze the current workflow and nodes
 * 3. Identify what effects are available and working
 * 4. Create a comprehensive feature plan
 */

const { chromium } = require('playwright');
const path = require('path');

async function inspectAnimationEffects() {
    console.log('🔍 Launching Playwright to inspect animation effects...\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 500
    });

    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 }
    });

    const page = await context.newPage();

    // Enable console logging from the page
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));

    try {
        // Step 1: Open the HTML viewer to see the current animation
        console.log('📄 Opening HTML animation viewer...');
        const viewerPath = path.join(__dirname, '../view_animation.html');
        await page.goto(`file://${viewerPath}`);
        await page.waitForTimeout(2000);

        // Take screenshot of viewer
        await page.screenshot({ path: 'screenshots/viewer_current.png', fullPage: true });
        console.log('✅ Screenshot saved: screenshots/viewer_current.png\n');

        // Step 2: Open ComfyUI interface
        console.log('🎨 Opening ComfyUI interface...');
        await page.goto('http://127.0.0.1:8188');
        await page.waitForTimeout(3000);

        // Check if ComfyUI loaded successfully
        const title = await page.title();
        console.log(`📋 Page title: ${title}\n`);

        // Step 3: Analyze the workflow nodes
        console.log('🔍 Analyzing workflow nodes and effects...\n');

        // Get all nodes in the workflow
        const workflowData = await page.evaluate(() => {
            // ComfyUI stores workflow in window.app
            if (window.app && window.app.graph) {
                const nodes = window.app.graph._nodes || [];
                return {
                    nodeCount: nodes.length,
                    nodes: nodes.map(node => ({
                        id: node.id,
                        type: node.type,
                        title: node.title,
                        widgets: node.widgets ? node.widgets.map(w => ({
                            name: w.name,
                            type: w.type,
                            value: w.value
                        })) : []
                    }))
                };
            }
            return { error: 'ComfyUI app not found' };
        });

        console.log('📊 Workflow Analysis:');
        console.log(JSON.stringify(workflowData, null, 2));

        // Step 4: Check available custom nodes
        const customNodes = await page.evaluate(() => {
            if (window.app && window.app.extensionManager) {
                return {
                    extensions: Object.keys(window.app.extensionManager.extensions || {}),
                    nodeTypes: window.LiteGraph ? Object.keys(window.LiteGraph.registered_node_types || {}) : []
                };
            }
            return { error: 'Extension manager not found' };
        });

        console.log('\n🔌 Available Extensions & Nodes:');
        console.log(JSON.stringify(customNodes, null, 2));

        // Step 5: Take screenshot of ComfyUI
        await page.screenshot({ path: 'screenshots/comfyui_current.png', fullPage: true });
        console.log('\n✅ Screenshot saved: screenshots/comfyui_current.png\n');

        // Step 6: Analyze the queue and execution status
        const queueInfo = await page.evaluate(() => {
            if (window.app) {
                return {
                    queueSize: window.app.queueSize || 0,
                    isExecuting: window.app.runningNodeId !== null
                };
            }
            return { error: 'App not found' };
        });

        console.log('⏳ Queue Status:');
        console.log(JSON.stringify(queueInfo, null, 2));

        console.log('\n✨ Inspection complete! Review the screenshots and data above.\n');

        // Keep browser open for manual inspection
        console.log('🔍 Browser will stay open for manual inspection. Press Ctrl+C to close.');
        await page.waitForTimeout(300000); // Wait 5 minutes

    } catch (error) {
        console.error('❌ Error during inspection:', error);
        await page.screenshot({ path: 'screenshots/error_state.png' });
    } finally {
        await browser.close();
    }
}

// Run the inspection
inspectAnimationEffects().catch(console.error);
