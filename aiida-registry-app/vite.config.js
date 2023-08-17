import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
const currentPath = process.env.VITE_PR_PREVIEW_PATH || "/aiida-registry/";

// https://vitejs.dev/config/
export default defineConfig({
  base: currentPath,
  plugins: [react()],
})
