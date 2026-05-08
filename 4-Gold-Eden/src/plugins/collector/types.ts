export interface PicaComicCrawlerProgress {
  stage:
    | "preparing"
    | "login"
    | "fetching_detail"
    | "fetching_chapters"
    | "fetching_images"
    | "downloading"
    | "completed"
    | "error";

  percent: number;

  current?: number;
  total?: number;

  chapterOrder?: number;
  chapterTitle?: string;

  message?: string;
}
