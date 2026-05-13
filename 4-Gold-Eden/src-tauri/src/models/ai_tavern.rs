use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TavernCharacterSummary {
    pub id: String,
    pub name: String,
    pub avatar_path: Option<String>,
    pub character_path: String,
    pub description: Option<String>,
    pub updated_at: Option<i64>,
}
