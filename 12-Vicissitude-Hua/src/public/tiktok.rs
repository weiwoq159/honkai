#[derive(Debug)]
#[allow(dead_code)]  // ✅ 允许未使用的字段（后续可能会用到）
pub struct DouyinUrls {
    // 首页推荐
    pub tab_feed: &'static str,
    // 用户信息
    pub user_short_info: &'static str,
    pub user_detail: &'static str,
    // 作品相关
    pub user_post: &'static str,
    pub post_detail: &'static str,
    // 用户喜好
    pub user_favorite_a: &'static str,
    pub user_favorite_b: &'static str,
    pub user_history: &'static str,
    pub user_collection: &'static str,
    // 社交
    pub comment: &'static str,
    pub friend_feed: &'static str,
    pub follow_feed: &'static str,
    // 合集
    pub user_mix: &'static str,
    pub user_mix_list: &'static str,
    // 直播
    pub live: &'static str,
    pub live2: &'static str,
    // 音乐
    pub music: &'static str,
    // 微博
    pub weibo_user_info: &'static str,
    pub weibo_blog_list: &'static str,
}

impl Default for DouyinUrls {
    fn default() -> Self {
        Self {
            tab_feed: "https://www.douyin.com/aweme/v1/web/tab/feed/?",
            user_short_info: "https://www.douyin.com/aweme/v1/web/im/user/info/?",
            user_detail: "https://www.douyin.com/aweme/v1/web/user/profile/other/?",
            user_post: "https://www.douyin.com/aweme/v1/web/aweme/post/?",
            post_detail: "https://www.douyin.com/aweme/v1/web/aweme/detail/?",
            user_favorite_a: "https://www.douyin.com/aweme/v1/web/aweme/favorite/?",
            user_favorite_b: "https://www.iesdouyin.com/web/api/v2/aweme/like/?",
            user_history: "https://www.douyin.com/aweme/v1/web/history/read/?",
            user_collection: "https://www.douyin.com/aweme/v1/web/aweme/listcollection/?",
            comment: "https://www.douyin.com/aweme/v1/web/comment/list/?",
            friend_feed: "https://www.douyin.com/aweme/v1/web/familiar/feed/?",
            follow_feed: "https://www.douyin.com/aweme/v1/web/follow/feed/?",
            user_mix: "https://www.douyin.com/aweme/v1/web/mix/aweme/?",
            user_mix_list: "https://www.douyin.com/aweme/v1/web/mix/list/?",
            live: "https://live.douyin.com/webcast/room/web/enter/?",
            live2: "https://webcast.amemv.com/webcast/room/reflow/info/?",
            music: "https://www.douyin.com/aweme/v1/web/music/aweme/?",
            weibo_user_info: "https://weibo.com/ajax/profile/info",
            weibo_blog_list: "https://www.weibo.com/ajax/statuses/mymblog",
        }
    }
}
