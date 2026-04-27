import type { ISafeAny, IRustResponse, IMediaItem } from '@src/types'

export type RustCommands = {
  open_file_dialog: {
    args: ISafeAny
    return: IRustResponse<{ current_page: string }>
  }
  get_images_in_folder: {
    args: {
      folderPath: string
    }
    return: IRustResponse<{ folder_path: string; image_urls: Array<IMediaItem> }>
  }
  reset_folder_images: {
    args: {
      folderPath: string
    }
    return: IRustResponse<{ folder_path: string; image_urls: Array<IMediaItem> }>
  }
  deduplicate_images: {
    args: {
      folderPath: string
    }
    return: IRustResponse<{
      file_list: Array<Array<{ file_path: string; file_size: number; is_select: boolean }>>
    }>
  }
  remove_file: {
    args: {
      filePath: string
    }
    return: IRustResponse<{ filePath: string }>
  }
  parse_url: {
    args: {
      url: string
    }
    return: IRustResponse<{ from: string; imageList: Array<IMediaItem>; userName: string }>
  }
  fetch_yan_image_list: {
    args: ISafeAny
    return: IRustResponse<{ from: string; imageList: Array<IMediaItem>; userName: string }>
  }
  remove_media_item_by_url: {
    args: { url: string }
    return: IRustResponse<{ url: string }>
  }
  download_file: {
    args: {
      folderPath: string
      downloadFileUrl: string[]
      origin: string
      fileType: string
      userName?: string
      fileName?: string
    }
    return: IRustResponse<{ fileUrl: string }>
  }
  fetch_baidu_image_list: {
    args: {
      bdstoken: string
      baiduCookie: string
    }
    return: IRustResponse<{ from: string; imageList: Array<IMediaItem>; userName: string }>
  }
  resolve_media_list: {
    args: ISafeAny
    return: IRustResponse<{ from: string; imageList: Array<IMediaItem>; userName: string }>
  }
  get_all_folder: {
    args: {
      originPath: string
    }
    return: IRustResponse<{ folder_list: Array<{ folder_path: string; folder_name: string }> }>
  }
  move_file: {
    args: {
      originPath: string
      targetPath: string
    }
    return: IRustResponse<{ origin_path: string; target_path: string }>
  }
  make_folder: {
    args: {
      originPath: string
      folderName: string
    }
    return: IRustResponse<{ folder_path: string }>
  }
  select_all_task_list: {
    args: ISafeAny
    return: ISafeAny
  }
  select_all_task_result_list: {
    args: {
      taskId: string
    }
    return: ISafeAny
  }
}
