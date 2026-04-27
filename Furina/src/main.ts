import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import App from './App.vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import '@assets/styles/global.scss'
import router from '@routes/index'
import { VueQueryPlugin } from '@tanstack/vue-query'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.use(ElementPlus)
app.use(VueQueryPlugin)
app.use(pinia)
app.use(router)
app.mount('#app')
