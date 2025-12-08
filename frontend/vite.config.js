import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:5000', // Proxy to backend
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, '/games') // Map /api to /games or keep as is? Backend expects /games. 
                // Actually, if backend is /games, /api/games -> /games/games if not careful.
                // Let's decide: Frontend calls /api/games -> Backend /games
                // So rewrite: /api -> /
            }
        }
    }
})
