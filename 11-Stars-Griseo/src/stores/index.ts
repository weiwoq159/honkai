import { defineStore } from 'pinia'
import { ElLoading } from 'element-plus'
interface StarsState {
  user_name: string,
  loading: any
}
export const useStarsStore = defineStore('stars', {
  state: (): StarsState => ({  // 指定返回类型
    user_name: '',
    loading: null
  }),
  actions: {
    set_user_name(user_name: string) {
      this.user_name = user_name
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
    }
  }
})