import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  server: {
    watch: {
      // Ignore backend virtualenv and large Python dirs to prevent FS watcher errors on Windows
      ignored: [
        '**/backend/.venv*/**',
        '**/backend/**/site-packages/**',
        '**/backend/models/**',
        '**/backend/static/**',
        '**/__pycache__/**',
      ],
    },
  },
});
