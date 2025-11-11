// API service for backend communication
import axios from 'axios';
import type { AnimationRequest, PresetConfig, QualityReport } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Upload NFT image
  uploadImage: async (file: File): Promise<{ filename: string; path: string }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    return response.data;
  },

  // Get all presets
  getPresets: async (): Promise<Record<string, PresetConfig>> => {
    const response = await api.get('/api/presets');
    return response.data.presets;
  },

  // Get specific preset
  getPreset: async (name: string): Promise<PresetConfig> => {
    const response = await api.get(`/api/presets/${name}`);
    return response.data;
  },

  // Generate preview (fast, low-res)
  generatePreview: async (request: AnimationRequest): Promise<Blob> => {
    const response = await api.post('/api/effects/preview', request, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Apply breathing effect
  applyBreathing: async (request: AnimationRequest): Promise<any> => {
    const response = await api.post('/api/effects/breathing', request);
    return response.data;
  },

  // Export final GIF
  exportGif: async (request: AnimationRequest): Promise<QualityReport & { download_url: string }> => {
    const response = await api.post('/api/export/gif', request);
    return response.data;
  },

  // Download file
  downloadFile: async (filename: string): Promise<Blob> => {
    const response = await api.get(`/api/download/${filename}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<any> => {
    const response = await api.get('/health');
    return response.data;
  },
};
