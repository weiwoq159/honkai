use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
struct WatermarkInfo {
    cdn_url: String,
    is_uploader: bool,
}
#[derive(Debug, Deserialize, Serialize)]
pub struct ImageItem {
    width: u32,
    height: u32,
    cdn_url: String,
    show_watermark: bool,
    bottom_right_brightness: f32,
    watermark_info: WatermarkInfo,
}