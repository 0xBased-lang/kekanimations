/**
 * Playwright Script to Inspect localhost:5173 Animation Interface
 */

const { chromium } = require('playwright');

async function inspectLocalhost5173() {
    console.log('🔍 Connecting to localhost:5173...\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 300
    });

    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 }
    });

    const page = await context.newPage();

    // Enable detailed console logging
    page.on('console', msg => {
        const type = msg.type();
        const text = msg.text();
        console.log(`[${type.toUpperCase()}]`, text);
    });

    // Log network requests
    page.on('request', request => {
        console.log('→', request.method(), request.url());
    });

    // Log errors
    page.on('pageerror', error => {
        console.error('PAGE ERROR:', error.message);
    });

    try {
        console.log('📄 Loading http://localhost:5173/...');
        await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
        await page.waitForTimeout(2000);

        const title = await page.title();
        console.log(`\n📋 Page Title: ${title}\n`);

        // Get page structure
        console.log('🏗️  Analyzing page structure...\n');

        const pageInfo = await page.evaluate(() => {
            const info = {
                url: window.location.href,
                title: document.title,
                bodyClasses: document.body.className,
                mainElements: [],
                canvases: [],
                images: [],
                videos: [],
                buttons: [],
                inputs: [],
                textareas: [],
                selects: [],
                scripts: [],
                styles: []
            };

            // Get main structural elements
            const main = document.querySelector('main');
            if (main) {
                info.mainElements.push({
                    tag: 'main',
                    id: main.id,
                    classes: main.className,
                    innerHTML: main.innerHTML.substring(0, 500)
                });
            }

            // Check for canvases (animation rendering)
            document.querySelectorAll('canvas').forEach(canvas => {
                info.canvases.push({
                    id: canvas.id,
                    width: canvas.width,
                    height: canvas.height,
                    classes: canvas.className
                });
            });

            // Check for images
            document.querySelectorAll('img').forEach(img => {
                info.images.push({
                    src: img.src,
                    alt: img.alt,
                    width: img.naturalWidth,
                    height: img.naturalHeight
                });
            });

            // Check for videos/gifs
            document.querySelectorAll('video, source').forEach(vid => {
                info.videos.push({
                    tag: vid.tagName,
                    src: vid.src,
                    type: vid.type
                });
            });

            // Get all buttons and their text
            document.querySelectorAll('button').forEach(btn => {
                info.buttons.push({
                    text: btn.textContent.trim(),
                    id: btn.id,
                    classes: btn.className,
                    disabled: btn.disabled
                });
            });

            // Get all input fields
            document.querySelectorAll('input').forEach(input => {
                info.inputs.push({
                    type: input.type,
                    id: input.id,
                    name: input.name,
                    placeholder: input.placeholder,
                    value: input.value
                });
            });

            // Get textareas
            document.querySelectorAll('textarea').forEach(ta => {
                info.textareas.push({
                    id: ta.id,
                    name: ta.name,
                    placeholder: ta.placeholder
                });
            });

            // Get select dropdowns
            document.querySelectorAll('select').forEach(sel => {
                const options = Array.from(sel.options).map(opt => ({
                    value: opt.value,
                    text: opt.text,
                    selected: opt.selected
                }));
                info.selects.push({
                    id: sel.id,
                    name: sel.name,
                    options: options
                });
            });

            // Get script sources
            document.querySelectorAll('script[src]').forEach(script => {
                info.scripts.push(script.src);
            });

            // Get stylesheet links
            document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
                info.styles.push(link.href);
            });

            return info;
        });

        console.log('📊 Page Analysis Results:');
        console.log('═══════════════════════════════════════\n');

        console.log('🎨 Canvases:', pageInfo.canvases.length);
        pageInfo.canvases.forEach((canvas, i) => {
            console.log(`  ${i + 1}. ID: ${canvas.id || 'none'} | ${canvas.width}×${canvas.height} | Classes: ${canvas.classes || 'none'}`);
        });

        console.log('\n🖼️  Images:', pageInfo.images.length);
        pageInfo.images.slice(0, 5).forEach((img, i) => {
            console.log(`  ${i + 1}. ${img.src.substring(0, 60)}... | ${img.width}×${img.height}`);
        });

        console.log('\n🎬 Videos/Sources:', pageInfo.videos.length);
        pageInfo.videos.forEach((vid, i) => {
            console.log(`  ${i + 1}. ${vid.tag}: ${vid.src || 'no src'}`);
        });

        console.log('\n🔘 Buttons:', pageInfo.buttons.length);
        pageInfo.buttons.forEach((btn, i) => {
            console.log(`  ${i + 1}. "${btn.text}" | ID: ${btn.id || 'none'} | Disabled: ${btn.disabled}`);
        });

        console.log('\n📝 Input Fields:', pageInfo.inputs.length);
        pageInfo.inputs.forEach((input, i) => {
            console.log(`  ${i + 1}. Type: ${input.type} | ID: ${input.id || 'none'} | Placeholder: ${input.placeholder || 'none'}`);
        });

        console.log('\n📋 Textareas:', pageInfo.textareas.length);
        pageInfo.textareas.forEach((ta, i) => {
            console.log(`  ${i + 1}. ID: ${ta.id || 'none'} | Placeholder: ${ta.placeholder || 'none'}`);
        });

        console.log('\n🎛️  Select Dropdowns:', pageInfo.selects.length);
        pageInfo.selects.forEach((sel, i) => {
            console.log(`  ${i + 1}. ID: ${sel.id || 'none'} | Options: ${sel.options.length}`);
            sel.options.slice(0, 5).forEach(opt => {
                console.log(`      - ${opt.text} (${opt.value}) ${opt.selected ? '✓' : ''}`);
            });
        });

        // Check for React/Vue/other frameworks
        console.log('\n🔧 Framework Detection:');
        const frameworks = await page.evaluate(() => {
            return {
                react: !!(window.React || document.querySelector('[data-reactroot], [data-reactid]')),
                vue: !!window.Vue,
                angular: !!window.angular,
                svelte: !!window.__SVELTE__,
                pixiJS: !!window.PIXI,
                threeJS: !!window.THREE,
                gsap: !!window.gsap
            };
        });
        console.log(frameworks);

        // Check for animation libraries
        console.log('\n🎭 Animation Libraries:');
        const animationLibs = await page.evaluate(() => {
            return {
                PixiJS: !!window.PIXI,
                ThreeJS: !!window.THREE,
                GSAP: !!window.gsap,
                AnimeJS: !!window.anime,
                BodyMovin: !!window.bodymovin,
                Lottie: !!window.lottie
            };
        });
        console.log(animationLibs);

        // Take screenshot
        await page.screenshot({
            path: 'screenshots/localhost_5173_full.png',
            fullPage: true
        });
        console.log('\n📸 Screenshot saved: screenshots/localhost_5173_full.png');

        // Get any custom window properties
        console.log('\n🔍 Custom Window Properties:');
        const windowProps = await page.evaluate(() => {
            const props = {};
            for (let key in window) {
                if (!key.startsWith('_') &&
                    typeof window[key] === 'object' &&
                    window[key] !== null &&
                    !['document', 'location', 'history', 'navigator', 'screen'].includes(key)) {
                    props[key] = typeof window[key];
                }
            }
            return props;
        });
        console.log(Object.keys(windowProps).slice(0, 20));

        console.log('\n✨ Inspection complete! Browser will stay open for manual inspection.');
        console.log('Press Ctrl+C to close.\n');

        // Keep browser open
        await page.waitForTimeout(300000);

    } catch (error) {
        console.error('❌ Error:', error.message);
        await page.screenshot({ path: 'screenshots/localhost_5173_error.png' });
    } finally {
        await browser.close();
    }
}

inspectLocalhost5173().catch(console.error);
