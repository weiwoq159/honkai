use crate::models::ai_tavern::TavernCharacterSummary;
use crate::models::response::ApiResponse;
use crate::services::ai_tavern::character_service::list_tavern_characters as service_list_tavern_characters;

use tauri::AppHandle;

#[tauri::command]
pub fn list_tavern_characters(
    app: AppHandle,
) -> Result<ApiResponse<Vec<TavernCharacterSummary>>, String> {
    println!("[command] list_tavern_characters called");

    let list: Vec<TavernCharacterSummary> = service_list_tavern_characters(app)?;

    println!("[command] list len: {}", list.len());
    println!("[command] list: {:#?}", list);

    Ok(ApiResponse::success(list))
}
