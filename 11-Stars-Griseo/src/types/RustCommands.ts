import { type IResponse } from './index'

export type RustCommands = {
  "open_file_dialog": {
    args: any;
    return: IResponse<{
      current_page: string,
      // image_list: Array<string>
    }>
  }
  "fetch_folder_image": {
    args: {
      currentPage: string
    };
    return: IResponse<{
      current_page: string,
      image_list: Array<string>
    }>
  }
  "remove_file": {
    args: {
      imageUrl: string
    };
    return: string;
  },
  "parse_input_url": {
    args: {
      parseUrl: string
    },
    return: IResponse<{ image_list: { Ok: { url: string[], preview_url: string[] } }, user_name: string }>
  }
  "my_custom_command": {
    args: any,
    return: any
  },
  "select_config_tables": {
    args: {
      keys: string
    },
    return: any
  }
  "download_file": {
    args: {
      folderPath: string,
      imageList: Array<string>,
      imageType: string,
      userName: string,
      origin_url: String
    },
    return: IResponse<{
      current_page: string,
      image_list: Array<string>
    }>
  }
}