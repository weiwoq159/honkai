use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct WeiboProfileResp {
    pub ok: u8,
    pub data: WeiboProfileData,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct WeiboProfileData {
    pub user: UserInfo,
    pub tabList: Vec<TabItem>,
    pub blockText: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TabItem {
    pub name: String,
    pub tabName: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UserInfo {
    pub id: u64,
    pub idstr: String,
    pub pc_new: u8,
    pub screen_name: String,
    pub profile_image_url: String,
    pub profile_url: String,
    pub verified: bool,
    pub verified_type: u8,
    pub domain: String,
    pub weihao: String,
    pub verified_type_ext: u8,
    pub status_total_counter: StatusTotalCounter,
    pub avatar_large: String,
    pub avatar_hd: String,
    pub follow_me: bool,
    pub following: bool,
    pub mbrank: u8,
    pub mbtype: u8,
    pub v_plus: u8,
    pub user_ability: i64,
    pub planet_video: bool,
    pub verified_reason: String,
    pub description: String,
    pub location: String,
    pub gender: String,
    pub followers_count: u64,
    pub followers_count_str: String,
    pub friends_count: u64,
    pub statuses_count: u64,
    pub url: String,
    pub svip: u8,
    pub vvip: u8,
    pub cover_image_phone: String,
    pub icon_list: Vec<IconListItem>,
    pub top_user: u8,
    pub user_type: u8,
    pub is_star: String,
    pub is_muteuser: bool,
    pub special_follow: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct StatusTotalCounter {
    pub total_cnt_format: String,
    pub comment_cnt: String,
    pub repost_cnt: String,
    pub like_cnt: String,
    pub total_cnt: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct IconListItem {
    #[serde(rename = "type")]
    pub icon_type: String,
    pub data: IconData,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct IconData {
    pub mbrank: u8,
    pub mbtype: u8,
    pub svip: u8,
    pub vvip: u8,
}
