// Main App - NFT Animation Playground
import { useState, useCallback } from 'react';
import { AnimationCanvas } from './components/AnimationCanvas';
import { EffectControls } from './components/EffectControls';
import { apiService } from './services/api';
import type { EffectConfig } from './types';

function App() {
  const [imageUrl, setImageUrl] = useState<string | undefined>();
  const [uploadedFilename, setUploadedFilename] = useState<string>('');
  const [effects, setEffects] = useState<EffectConfig[]>([
    { type: 'breathing', intensity: 0.02 },
  ]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string>('');

  // Handle file upload
  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError('');

    try {
      // Upload to backend
      const response = await apiService.uploadImage(file);
      setUploadedFilename(response.filename);

      // Create local URL for PixiJS
      const localUrl = URL.createObjectURL(file);
      setImageUrl(localUrl);

      console.log('Image uploaded:', response);
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadError('Failed to upload image. Please try again.');
    } finally {
      setIsUploading(false);
    }
  }, []);

  // Handle effects change from controls
  const handleEffectsChange = useCallback((newEffects: EffectConfig[]) => {
    setEffects(newEffects);
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🎨 NFT Animation Playground
          </h1>
          <p className="text-gray-400 text-lg">
            Artisanal NFT animations with real-time preview
          </p>
        </header>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Canvas */}
          <div className="space-y-4">
            {/* Upload Section */}
            <div className="bg-gray-800 p-6 rounded-lg">
              <h2 className="text-xl font-semibold text-white mb-4">Upload NFT</h2>

              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-600 border-dashed rounded-lg cursor-pointer bg-gray-700 hover:bg-gray-600 transition">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <svg className="w-10 h-10 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="mb-2 text-sm text-gray-400">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-gray-500">PNG, JPG (512×512 recommended)</p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  accept="image/png,image/jpeg"
                  onChange={handleFileUpload}
                  disabled={isUploading}
                />
              </label>

              {isUploading && (
                <div className="mt-4 text-center text-blue-400">
                  Uploading...
                </div>
              )}

              {uploadError && (
                <div className="mt-4 text-center text-red-400">
                  {uploadError}
                </div>
              )}

              {uploadedFilename && (
                <div className="mt-4 text-sm text-green-400">
                  ✓ Uploaded: {uploadedFilename}
                </div>
              )}
            </div>

            {/* Canvas */}
            <div className="bg-gray-800 p-6 rounded-lg">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-white">Preview</h2>
                <div className="text-sm text-gray-400">
                  60 FPS • Real-time
                </div>
              </div>

              {imageUrl ? (
                <AnimationCanvas
                  imageUrl={imageUrl}
                  effects={effects}
                  isPlaying={true}
                />
              ) : (
                <div className="w-full h-[512px] border-2 border-dashed border-gray-700 rounded-lg flex items-center justify-center">
                  <div className="text-center text-gray-500">
                    <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p className="text-lg">Upload an NFT to begin</p>
                  </div>
                </div>
              )}
            </div>

            {/* Active Effects Display */}
            {imageUrl && effects.length > 0 && (
              <div className="bg-gray-800 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-white mb-2">Active Effects</h3>
                <div className="flex flex-wrap gap-2">
                  {effects.map((effect, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-blue-600 text-white text-sm rounded-full"
                    >
                      {effect.type} ({(effect.intensity * 100).toFixed(0)}%)
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Controls */}
          <div>
            <EffectControls
              effects={effects}
              onChange={handleEffectsChange}
            />
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-8 pt-8 border-t border-gray-800 text-center text-gray-500 text-sm">
          <p>NFT Animation Playground • FastAPI + PixiJS + GSAP • Real-time Preview</p>
          <p className="mt-2">Backend API: <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">http://localhost:8000/docs</a></p>
        </footer>
      </div>
    </div>
  );
}

export default App;
