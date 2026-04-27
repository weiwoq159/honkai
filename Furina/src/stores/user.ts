import { defineStore } from 'pinia'
import { ElLoading } from 'element-plus'
import type { ISafeAny } from '@src/types'

interface StarsState {
  user_name: string
  loading: ISafeAny
  current_page: string
  download_path: string
  baidu_bdstoken: string
  baidu_cookie: string
}
export const useCrawlerState = defineStore('crawler', {
  state: (): StarsState => ({
    // 指定返回类型
    user_name: '',
    loading: null,
    current_page: '',
    download_path: '',
    baidu_bdstoken: '',
    baidu_cookie: ''
  }),
  actions: {
    set_current_page(current_page: string) {
      this.current_page = current_page
    },
    set_user_name(user_name: string) {
      this.user_name = user_name
    },
    setDownloadPath(download_path: string) {
      this.download_path = download_path
    },
    setBaiduBdstoken(baidu_bdstoken: string) {
      this.baidu_bdstoken = baidu_bdstoken
    },
    setBaiduCookie(cookies: string) {
      this.baidu_cookie = cookies
    },
    startLoading() {
      this.loading = ElLoading.service({
        lock: true,
        text: 'Loading',
        background: 'rgba(0, 0, 0, 0.7)',
      })
    },
    closeLoading() {
      this.loading.close()
      this.loading = null
    },
  },
  persist: true,
})
