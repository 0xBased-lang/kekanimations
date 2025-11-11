import { createServer } from 'http';
import { readFile } from 'fs/promises';
import { join, extname } from 'path';
import { Server } from 'http';

/**
 * Simple HTTP server for serving test images to Playwright
 * Fixes the file:// protocol loading issues in headless Chrome
 */
export class TestImageServer {
  private server: Server | null = null;
  private port: number = 8765;
  private baseDir: string;

  constructor(baseDir: string = process.cwd()) {
    this.baseDir = baseDir;
  }

  /**
   * Start the HTTP server
   */
  async start(port: number = 8765): Promise<void> {
    this.port = port;

    return new Promise((resolve, reject) => {
      this.server = createServer(async (req, res) => {
        try {
          // Remove leading slash and decode URL
          const filePath = decodeURIComponent(req.url?.slice(1) || '');
          if (!filePath) {
            res.statusCode = 404;
            res.end('Not found');
            return;
          }

          // Security: prevent directory traversal
          if (filePath.includes('..')) {
            res.statusCode = 403;
            res.end('Forbidden');
            return;
          }

          // Read the file
          const fullPath = join(this.baseDir, filePath);
          const data = await readFile(fullPath);

          // Set appropriate content type
          const ext = extname(filePath).toLowerCase();
          const contentTypes: Record<string, string> = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.html': 'text/html',
            '.json': 'application/json',
          };

          res.setHeader('Content-Type', contentTypes[ext] || 'application/octet-stream');
          res.setHeader('Access-Control-Allow-Origin', '*'); // Allow CORS
          res.statusCode = 200;
          res.end(data);
        } catch (error) {
          console.error(`Error serving file: ${error}`);
          res.statusCode = 404;
          res.end('File not found');
        }
      });

      this.server.listen(this.port, () => {
        console.log(`Test image server running at http://localhost:${this.port}`);
        resolve();
      });

      this.server.on('error', reject);
    });
  }

  /**
   * Stop the HTTP server
   */
  async stop(): Promise<void> {
    return new Promise((resolve) => {
      if (this.server) {
        this.server.close(() => {
          console.log('Test image server stopped');
          resolve();
        });
      } else {
        resolve();
      }
    });
  }

  /**
   * Get the URL for a file
   */
  getUrl(filePath: string): string {
    return `http://localhost:${this.port}/${filePath}`;
  }
}

// Export singleton instance
export const testImageServer = new TestImageServer();