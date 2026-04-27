// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type ISafeAny = any

export interface IImageList {
  preview_url: string
  url: string
  image_type?: string
  file_name?: string
  download_url: string
}

export interface IMediaItem {
  preview_url: string
  url: string
  media_type?: string | null
  format?: string | null
  blog_id?: string | null
  user_id?: string | null
  created_at?: string | null
  origin_from?: string | null
  is_deleted?: number | null
  file_name?: string | null
  md5_code?: string | null
  download_url?: string | null
}

export interface ICrawler {
  imageList: Array<{ preview_url: string; url: string }>
  originUrl: string
  userName: string
}

export interface IRustResponse<T> {
  data: T
  message: string
  status: number
}
