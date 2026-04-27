import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import path from 'path'
// https://vite.dev/config/
export default defineConfig({
  define: {
    'process.env': process.env,
  },
  base: './',
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    })
  ],
  resolve: {
    alias: {
      '@views': path.resolve(__dirname, 'src/views'),
      "@src": path.resolve(__dirname, 'src'),
      "@routes": path.resolve(__dirname, 'src/routes'),
      "@stores": path.resolve(__dirname, 'src/stores'),
      "@types": path.resolve(__dirname, 'src/types'),
      "@utils": path.resolve(__dirname, 'src/utils'),
      "@components": path.resolve(__dirname, 'src/components'),
      "@assets": path.resolve(__dirname, 'src/assets'),
      "@plugins": path.resolve(__dirname, 'src/plugins'),
      "@router": path.resolve(__dirname, 'src/router'),
      "@store": path.resolve(__dirname, 'src/store'),
    },
  },
})
