import { CrawlerService } from '../services/CrawlerService'
import { useQuery } from '@tanstack/vue-query'

class CrawlerQueryService extends CrawlerService {
  constructor() {
    super()
  }
  queryFetchWeibo() {
    return useQuery({
      queryKey: ['user'],
      queryFn: this.fetchWeibo,
      staleTime: 5 * 60 * 1000, // 5分钟内不重新请求，可选
    })
  }
}

export const crawlerQueryService = new CrawlerQueryService()
