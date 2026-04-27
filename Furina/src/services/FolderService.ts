import { invokeRust } from '@src/services/invoke'
class FolderService {
  constructor() { }
  async openFileDialog() {
    const res = await invokeRust('open_file_dialog', {})
    return res
  }
  async getFolderImage(folderPath: string) {
    const res = await invokeRust('get_images_in_folder', { folderPath })
    return res
  }
  async reset_folder_images(folderPath: string) {
    const res = await invokeRust('reset_folder_images', { folderPath })
    return res
  }
  async removeFile(filePath: string) {
    const res = await invokeRust('remove_file', { filePath })
    return res
  }
  async deduplicate_images(folderPath: string) {
    const res = await invokeRust('deduplicate_images', { folderPath })
    return res
  }
  async get_all_folder(originPath: string) {
    const res = await invokeRust('get_all_folder', { originPath })
    return res
  }
  async move_file(originPath: string, targetPath: string) {
    const res = await invokeRust('move_file', { originPath, targetPath })
    return res
  }
  async make_folder(originPath: string, folderName: string) {
    const res = await invokeRust('make_folder', { originPath, folderName })
    return res
  }
  async select_all_task_list() {
    const res = await invokeRust('select_all_task_list', {})
    return res
  }
  async select_all_task_result_list(taskId: string) {
    console.log(taskId);
    const res = await invokeRust('select_all_task_result_list', { taskId })
    return res
  }
}

export const folderService = new FolderService()
