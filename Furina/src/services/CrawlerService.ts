import axios from 'axios'
import type { ICrawler } from '@src/types'

import { invokeRust } from '@src/services/invoke'

export class CrawlerService {
  constructor() {
    // 初始化逻辑
  }

  async fetchWeibo() {
    const { data } = await axios.get<ICrawler>('/test.json') // data 是字符串
    return data
  }
  async parse_url(url: string) {
    const { data } = await invokeRust('parse_url', { url })
    return data
  }
  // folder_path: String,
  //   download_file_url: Vec<String>,
  //   origin: String,
  //   user_name: Option<String>,
  //   file_name: Option<String>,
  //   file_type: String,
  async download_file({
    folderPath,
    downloadFileUrl,
    origin,
    userName,
    fileType,
    fileName,
  }: {
    downloadFileUrl: string[]
    folderPath: string
    origin: string
    fileType: string
    fileName?: string
    userName?: string
  }) {
    console.log({ downloadFileUrl, folderPath, origin, fileType, fileName, userName })
    const { data } = await invokeRust('download_file', {
      downloadFileUrl,
      folderPath,
      origin,
      fileType,
      fileName,
      userName,
    })
    return data
  }
  async fetch_yan_image() {
    const { data } = await invokeRust('fetch_yan_image_list', {})
    return data
  }
  async remove_image_db(url: string) {
    const { data } = await invokeRust('remove_media_item_by_url', { url })
    return data
  }
  async fetch_baidu_image_list(bdstoken: string, baiduCookie: string) {
    const { data } = await invokeRust('fetch_baidu_image_list', { bdstoken, baiduCookie })
    return data
  }
  async resolve_media_list(bdstoken: string) {
    const { data } = await invokeRust('resolve_media_list', { bdstoken })
    return data
  }
}

export const crawlerService = new CrawlerService()
