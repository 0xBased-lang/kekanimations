import { testImageServer } from './http-server';

/**
 * Global teardown for Playwright tests
 * Stops the HTTP server after all tests complete
 */
async function globalTeardown() {
  console.log('Stopping test HTTP server...');
  await testImageServer.stop();
}

export default globalTeardown;