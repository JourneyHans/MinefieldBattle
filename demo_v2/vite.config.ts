import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@game': path.resolve(__dirname, './src/game'),
      '@rendering': path.resolve(__dirname, './src/rendering'),
      '@storage': path.resolve(__dirname, './src/storage'),
      '@config': path.resolve(__dirname, './src/config'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@types': path.resolve(__dirname, './src/types'),
      '@utils': path.resolve(__dirname, './src/utils'),
    },
  },
  server: {
    port: 3000,
    open: true,
    strictPort: false,
  },
  build: {
    target: 'esnext',
    minify: 'esbuild',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'pixi': ['pixi.js', '@pixi/react'],
          'vendor': ['react', 'react-dom'],
          'zustand': ['zustand'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['pixi.js', '@pixi/react', 'zustand'],
  },
})
