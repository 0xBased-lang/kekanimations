import { testImageServer } from './http-server';

/**
 * Global setup for Playwright tests
 * Starts the HTTP server for serving test images
 */
async function globalSetup() {
  console.log('Starting test HTTP server...');
  await testImageServer.start(8765);

  // Store the server URL in environment variable for tests
  process.env.TEST_SERVER_URL = 'http://localhost:8765';

  return async () => {
    // This will be called during teardown
    await testImageServer.stop();
  };
}

export default globalSetup;