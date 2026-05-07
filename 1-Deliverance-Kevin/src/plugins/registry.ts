import type { ToolPlugin } from "@plugins/types";
import { folderFlattenPlugin } from "@features/folder-flatten/plugin";
import { folderTreePlugin } from "@features/folder-tree/plugin";
import { folderStatsPlugin } from "@features/folder-stats/plugin";
import { emptyFolderCleanerPlugin } from "@features/empty-folder-cleaner/plugin";
import { largeFileScannerPlugin } from "@features/large-file-scanner/plugin";
import { fileTypeStatsPlugin } from "@features/file-type-stats/plugin";
import { duplicateFilenameScannerPlugin } from "@features/duplicate-filename-scanner/plugin";
import { fileTypeOrganizerPlugin } from "@features/file-type-organizer/plugin";
import { batchFileRenamerPlugin } from "@features/batch-file-renamer/plugin";
import { imageInfoScannerPlugin } from "@features/image-info-scanner/plugin";
import { brokenImageDetectorPlugin } from "@features/broken-image-detector/plugin";
import { duplicateImageScannerPlugin } from "@features/duplicate-image-scanner/plugin";
import { macroFishingBombPlugin } from "@features/macro-fishing-bomb/plugin";
import { macroPoisonFarmPlugin } from "@features/macro-poison-farm/plugin";
import { macroLockFarmPlugin } from "@features/macro-lock-farm/plugin";
import { picaComicCrawlerPlugin } from "@features/pica-comic-crawler/plugin";

export const plugins: ToolPlugin[] = [
  picaComicCrawlerPlugin,
  macroLockFarmPlugin,
  macroPoisonFarmPlugin,
  macroFishingBombPlugin,
  duplicateImageScannerPlugin,
  brokenImageDetectorPlugin,
  imageInfoScannerPlugin,
  batchFileRenamerPlugin,
  fileTypeOrganizerPlugin,
  duplicateFilenameScannerPlugin,
  fileTypeStatsPlugin,
  largeFileScannerPlugin,
  emptyFolderCleanerPlugin,
  folderFlattenPlugin,
  folderStatsPlugin,
  folderTreePlugin,
];
