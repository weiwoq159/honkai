# JSON 字段作用说明

> 说明：本文只解析字段用途，不展开具体剧情内容。适合作为角色卡 JSON Schema / Prompt 配置文档参考。

## 1. 顶层模块总览

| 字段 | 中文含义 | 类型 | 作用 |
|---|---|---|---|
| `localId` | 本地角色 ID | `string` | 前端或本地存储使用的唯一标识，便于离线管理和资源目录关联。 |
| `id` | 角色 ID | `string` | 角色全局唯一标识，通常用于数据库、路由、索引和角色加载。 |
| `sourceId` | 来源 ID | `string` | 记录该角色来自哪个模板、市场、导入源或父资源。 |
| `sourceType` | 来源类型 | `string` | 标识角色创建方式，例如手动创建、导入、模板生成等。 |
| `name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `avatar` | 头像文件 | `string` | 角色头像资源路径，用于列表卡片和聊天头像。 |
| `fullbody` | 全身图文件 | `string` | 角色全身图资源路径，用于详情页或沉浸式展示。 |
| `createdAt` | 创建时间 | `number` | 毫秒级时间戳，用于排序、展示创建时间和同步判断。 |
| `updatedAt` | 更新时间 | `number` | 毫秒级时间戳，用于判断是否需要刷新、覆盖或同步。 |
| `META_RULES` | 元规则 | `object` | 约束模型输出的全局规则，决定语言、视角、沉浸感、连续性和用户边界。 |
| `WORLDVIEW_AND_LOGIC` | 世界观与逻辑 | `object` | 定义故事运行的底层世界观、社会规则、核心事件、特殊机制和主题方向。 |
| `USER_ROLE` | 用户角色 | `object` | 定义用户在故事中的身份、已知信息、成长空间、权限和交互限制。 |
| `CHARACTER_MODELING` | 角色建模 | `object` | 定义主角色的人设，包括基础资料、外观、心理、行为和说话方式。 |
| `RELATIONSHIP_STAGE_CONFIG` | 关系阶段配置 | `object` | 定义关系阶段机，控制阶段数量、晋级/回退规则、每阶段允许行为和结局条件。 |
| `STATE_SYSTEM` | 状态系统 | `object` | 定义可被系统追踪的状态变量，是数值驱动剧情变化的核心。 |
| `STATE_UPDATE_RULES` | 状态更新规则 | `object` | 定义状态变量如何变化，避免数值跳变、关系突变或人设失控。 |
| `SCENARIO_MECHANICS` | 场景机制 | `object` | 定义当前场景、日常互动模块、高级玩法和环境反馈规则。 |
| `EVENT_SYSTEM` | 事件系统 | `object` | 定义关键事件、随机事件、触发条件和事件结果影响因素。 |
| `STRATEGY_GUIDE` | 策略指南 | `object` | 给用户或系统提供阶段性玩法建议，用于引导但不强制剧情。 |
| `PLOT_PROGRESS_RULES` | 剧情推进规则 | `object` | 控制每轮剧情推进速度、结构和冲突处理方式。 |
| `DIALOGUE_STYLE` | 对话风格 | `object` | 控制角色对话语言、语气、节奏和不同情绪下的表达方式。 |
| `NARRATION_STYLE` | 旁白风格 | `object` | 控制旁白描写风格、感官细节和禁止的叙事模式。 |
| `OUTPUT_PROTOCOL` | 输出协议 | `object` | 规定模型每次回复的组成、格式、状态栏和长度控制。 |
| `REALTIME_STATISTICS` | 实时统计 | `object` | 记录运行期统计数据，用于成就、分支、复盘或 UI 展示。 |
| `ACHIEVEMENT_SYSTEM` | 成就系统 | `object` | 定义成就列表、解锁状态和解锁条件。 |
| `MEMORY_STATE` | 记忆状态 | `object` | 保存剧情记忆，包括摘要、已发生事件、未解决冲突和下一步焦点。 |
| `BOUNDARIES_AND_FORBIDDEN` | 边界与禁止项 | `object` | 集中声明角色、剧情和风格边界，防止模型偏离设定。 |
| `CORRECTION_RULES` | 纠偏规则 | `object` | 当剧情、人设、风格或记忆出现偏差时，提供自动修正策略。 |

## 2. 完整字段明细


### 本地角色 ID `localId`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `localId` | 本地角色 ID | `string` | 前端或本地存储使用的唯一标识，便于离线管理和资源目录关联。 |

### 角色 ID `id`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `id` | 角色 ID | `string` | 角色全局唯一标识，通常用于数据库、路由、索引和角色加载。 |

### 来源 ID `sourceId`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `sourceId` | 来源 ID | `string` | 记录该角色来自哪个模板、市场、导入源或父资源。 |

### 来源类型 `sourceType`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `sourceType` | 来源类型 | `string` | 标识角色创建方式，例如手动创建、导入、模板生成等。 |

### 名称 `name`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |

### 头像文件 `avatar`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `avatar` | 头像文件 | `string` | 角色头像资源路径，用于列表卡片和聊天头像。 |

### 全身图文件 `fullbody`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `fullbody` | 全身图文件 | `string` | 角色全身图资源路径，用于详情页或沉浸式展示。 |

### 创建时间 `createdAt`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `createdAt` | 创建时间 | `number` | 毫秒级时间戳，用于排序、展示创建时间和同步判断。 |

### 更新时间 `updatedAt`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `updatedAt` | 更新时间 | `number` | 毫秒级时间戳，用于判断是否需要刷新、覆盖或同步。 |

### 元规则 `META_RULES`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `META_RULES` | 元规则 | `object` | 约束模型输出的全局规则，决定语言、视角、沉浸感、连续性和用户边界。 |
| `META_RULES.language` | 输出语言 | `string` | 保存“输出语言”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `META_RULES.role_perspective` | 角色视角规则 | `string` | 保存“角色视角规则”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `META_RULES.immersion` | 沉浸感规则 | `string` | 保存“沉浸感规则”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `META_RULES.user_boundary` | 用户边界规则 | `object` | 用于组织“用户边界规则”相关的子配置字段。 |
| `META_RULES.user_boundary.do_not_speak_for_user` | 禁止替用户发言 | `boolean` | 控制“禁止替用户发言”是否启用或是否成立。 |
| `META_RULES.user_boundary.do_not_act_for_user` | 禁止替用户行动 | `boolean` | 控制“禁止替用户行动”是否启用或是否成立。 |
| `META_RULES.user_boundary.do_not_describe_user_inner_thoughts` | 禁止描写用户心理 | `boolean` | 控制“禁止描写用户心理”是否启用或是否成立。 |
| `META_RULES.user_boundary.rule` | 规则说明 | `string` | 保存“规则说明”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `META_RULES.continuity` | 连续性规则 | `string` | 保存“连续性规则”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `META_RULES.anti_fast_progression` | 反快速推进规则 | `string` | 保存“反快速推进规则”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `META_RULES.tone_control` | 基调控制 | `string` | 保存“基调控制”的文本配置，用于提示词、UI 展示或剧情控制。 |

### 世界观与逻辑 `WORLDVIEW_AND_LOGIC`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `WORLDVIEW_AND_LOGIC` | 世界观与逻辑 | `object` | 定义故事运行的底层世界观、社会规则、核心事件、特殊机制和主题方向。 |
| `WORLDVIEW_AND_LOGIC.background_setting` | 背景设定 | `string` | 保存“背景设定”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `WORLDVIEW_AND_LOGIC.time_period` | 时代背景 | `string` | 保存“时代背景”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `WORLDVIEW_AND_LOGIC.location_scope` | 地点范围 | `string` | 保存“地点范围”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `WORLDVIEW_AND_LOGIC.social_rules` | 社会规则 | `string` | 保存“社会规则”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `WORLDVIEW_AND_LOGIC.core_event` | 核心事件 | `string` | 保存“核心事件”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `WORLDVIEW_AND_LOGIC.special_mechanism` | 特殊机制 | `object` | 用于组织“特殊机制”相关的子配置字段。 |
| `WORLDVIEW_AND_LOGIC.special_mechanism.enabled` | 是否启用 | `boolean` | 控制“是否启用”是否启用或是否成立。 |
| `WORLDVIEW_AND_LOGIC.special_mechanism.mechanism_name` | 机制名称 | `string` | 保存“机制名称”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `WORLDVIEW_AND_LOGIC.special_mechanism.duration` | 持续时间 | `object` | 用于组织“持续时间”相关的子配置字段。 |
| `WORLDVIEW_AND_LOGIC.special_mechanism.duration.total_days` | 总天数 | `number` | 记录“总天数”的数值配置，可用于计算、排序、判断或状态更新。 |
| `WORLDVIEW_AND_LOGIC.special_mechanism.duration.hours_per_day` | 每日小时数 | `number` | 记录“每日小时数”的数值配置，可用于计算、排序、判断或状态更新。 |
| `WORLDVIEW_AND_LOGIC.special_mechanism.duration.total_hours` | 总小时数 | `number` | 记录“总小时数”的数值配置，可用于计算、排序、判断或状态更新。 |
| `WORLDVIEW_AND_LOGIC.special_mechanism.mechanism_description` | 机制说明 | `string` | 保存“机制说明”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `WORLDVIEW_AND_LOGIC.special_mechanism.limitations` | 限制条件 | `array<string>` | 保存“限制条件”的多条配置、条件、规则或枚举项。 |
| `WORLDVIEW_AND_LOGIC.core_conflict` | 核心冲突 | `string` | 保存“核心冲突”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `WORLDVIEW_AND_LOGIC.theme_keywords` | 主题关键词 | `array<string>` | 保存“主题关键词”的多条配置、条件、规则或枚举项。 |

### 用户角色 `USER_ROLE`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `USER_ROLE` | 用户角色 | `object` | 定义用户在故事中的身份、已知信息、成长空间、权限和交互限制。 |
| `USER_ROLE.identity` | 身份 | `string` | 保存“身份”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `USER_ROLE.gender` | 性别 | `string` | 保存“性别”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `USER_ROLE.occupation` | 职业 | `string` | 保存“职业”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `USER_ROLE.relationship_to_main_character` | 与主角色关系 | `string` | 保存“与主角色关系”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `USER_ROLE.initial_position` | 初始处境 | `string` | 保存“初始处境”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `USER_ROLE.development_space` | 成长空间 | `string` | 保存“成长空间”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `USER_ROLE.goal_evolution` | 目标演变 | `object` | 用于组织“目标演变”相关的子配置字段。 |
| `USER_ROLE.goal_evolution.early` | 前期目标 | `string` | 保存“前期目标”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `USER_ROLE.goal_evolution.middle` | 中期目标 | `string` | 保存“中期目标”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `USER_ROLE.goal_evolution.late` | 后期目标 | `string` | 保存“后期目标”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `USER_ROLE.special_permission` | 特殊权限 | `string` | 保存“特殊权限”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `USER_ROLE.known_information` | 已知信息 | `array<string>` | 保存“已知信息”的多条配置、条件、规则或枚举项。 |
| `USER_ROLE.resources_or_constraints` | 资源或限制 | `array<string>` | 保存“资源或限制”的多条配置、条件、规则或枚举项。 |
| `USER_ROLE.interaction_limits` | 互动限制 | `array<string>` | 保存“互动限制”的多条配置、条件、规则或枚举项。 |

### 角色建模 `CHARACTER_MODELING`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `CHARACTER_MODELING` | 角色建模 | `object` | 定义主角色的人设，包括基础资料、外观、心理、行为和说话方式。 |
| `CHARACTER_MODELING.CORE_PROFILE` | 核心档案 | `object` | 用于组织“核心档案”相关的子配置字段。 |
| `CHARACTER_MODELING.CORE_PROFILE.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `CHARACTER_MODELING.CORE_PROFILE.age` | 年龄 | `number` | 记录“年龄”的数值配置，可用于计算、排序、判断或状态更新。 |
| `CHARACTER_MODELING.CORE_PROFILE.gender` | 性别 | `string` | 保存“性别”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.CORE_PROFILE.height` | 身高 | `string` | 保存“身高”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.CORE_PROFILE.occupation` | 职业 | `string` | 保存“职业”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.CORE_PROFILE.education` | 教育背景 | `string` | 保存“教育背景”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.CORE_PROFILE.income_level` | 收入水平 | `string` | 保存“收入水平”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.CORE_PROFILE.social_identity` | 社会身份 | `string` | 保存“社会身份”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.CORE_PROFILE.background` | 角色背景 | `string` | 保存“角色背景”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.CORE_PROFILE.current_situation` | 当前处境 | `string` | 保存“当前处境”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.APPEARANCE_PROFILE` | 外观档案 | `object` | 用于组织“外观档案”相关的子配置字段。 |
| `CHARACTER_MODELING.APPEARANCE_PROFILE.general_appearance` | 整体外貌 | `string` | 保存“整体外貌”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.APPEARANCE_PROFILE.height` | 身高 | `string` | 保存“身高”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.APPEARANCE_PROFILE.body_type` | 体型 | `string` | 保存“体型”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.APPEARANCE_PROFILE.hair` | 发型 | `string` | 保存“发型”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.APPEARANCE_PROFILE.eyes` | 眼睛 | `string` | 保存“眼睛”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.APPEARANCE_PROFILE.skin` | 肤色 | `string` | 保存“肤色”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.APPEARANCE_PROFILE.clothing_style` | 穿衣风格 | `string` | 保存“穿衣风格”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.APPEARANCE_PROFILE.signature_outfit` | 标志性服装 | `string` | 保存“标志性服装”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.APPEARANCE_PROFILE.distinctive_features` | 显著特征 | `array<string>` | 保存“显著特征”的多条配置、条件、规则或枚举项。 |
| `CHARACTER_MODELING.APPEARANCE_PROFILE.body_language` | 肢体语言 | `string` | 保存“肢体语言”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.PERSONALITY_AND_MIND` | 性格与心理 | `object` | 用于组织“性格与心理”相关的子配置字段。 |
| `CHARACTER_MODELING.PERSONALITY_AND_MIND.core_traits` | 核心性格特征 | `array<string>` | 保存“核心性格特征”的多条配置、条件、规则或枚举项。 |
| `CHARACTER_MODELING.PERSONALITY_AND_MIND.surface_persona` | 外在人设 | `string` | 保存“外在人设”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.PERSONALITY_AND_MIND.deep_persona` | 深层人格 | `string` | 保存“深层人格”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.PERSONALITY_AND_MIND.inner_conflict` | 内在冲突 | `string` | 保存“内在冲突”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.PERSONALITY_AND_MIND.defense_mechanism` | 防御机制 | `string` | 保存“防御机制”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.PERSONALITY_AND_MIND.emotional_weakness` | 情绪弱点 | `array<string>` | 保存“情绪弱点”的多条配置、条件、规则或枚举项。 |
| `CHARACTER_MODELING.PERSONALITY_AND_MIND.moral_bottom_line` | 底线 | `string` | 保存“底线”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.PERSONALITY_AND_MIND.greatest_fear` | 最大恐惧 | `string` | 保存“最大恐惧”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.PERSONALITY_AND_MIND.hidden_need` | 隐藏需求 | `string` | 保存“隐藏需求”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.PERSONALITY_AND_MIND.self_image` | 自我认知 | `string` | 保存“自我认知”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.BEHAVIOR_PATTERNS` | 行为模式 | `object` | 用于组织“行为模式”相关的子配置字段。 |
| `CHARACTER_MODELING.BEHAVIOR_PATTERNS.normal_state` | 常态表现 | `string` | 保存“常态表现”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.BEHAVIOR_PATTERNS.under_pressure` | 压力下表现 | `string` | 保存“压力下表现”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.BEHAVIOR_PATTERNS.when_angry` | 愤怒时表现 | `string` | 保存“愤怒时表现”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.BEHAVIOR_PATTERNS.when_conflicted` | 矛盾时表现 | `string` | 保存“矛盾时表现”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.BEHAVIOR_PATTERNS.when_trusting` | 信任时表现 | `string` | 保存“信任时表现”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.BEHAVIOR_PATTERNS.stress_response_sequence` | 压力反应序列 | `object` | 用于组织“压力反应序列”相关的子配置字段。 |
| `CHARACTER_MODELING.BEHAVIOR_PATTERNS.stress_response_sequence.contraction_response` | 强制/约束反应 | `string` | 保存“强制/约束反应”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.BEHAVIOR_PATTERNS.stress_response_sequence.language_attack` | 语言攻击反应 | `string` | 保存“语言攻击反应”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.BEHAVIOR_PATTERNS.stress_response_sequence.emotional_fluctuation` | 情绪波动反应 | `string` | 保存“情绪波动反应”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.BEHAVIOR_PATTERNS.stress_response_sequence.defense_reduction` | 防御降低表现 | `string` | 保存“防御降低表现”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.BEHAVIOR_PATTERNS.stress_response_sequence.inner_struggle` | 内心挣扎 | `string` | 保存“内心挣扎”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.BEHAVIOR_PATTERNS.forbidden_out_of_character_behaviors` | 禁止 OOC 行为 | `array<string>` | 保存“禁止 OOC 行为”的多条配置、条件、规则或枚举项。 |
| `CHARACTER_MODELING.SPEECH_STYLE` | 语言风格 | `object` | 用于组织“语言风格”相关的子配置字段。 |
| `CHARACTER_MODELING.SPEECH_STYLE.tone` | 语气 | `string` | 保存“语气”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.SPEECH_STYLE.sentence_length` | 句长风格 | `string` | 保存“句长风格”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.SPEECH_STYLE.common_phrases` | 常用话术 | `array<string>` | 保存“常用话术”的多条配置、条件、规则或枚举项。 |
| `CHARACTER_MODELING.SPEECH_STYLE.speech_when_emotional` | 情绪化时说话方式 | `string` | 保存“情绪化时说话方式”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `CHARACTER_MODELING.SPEECH_STYLE.forbidden_speech_style` | 禁止语言风格 | `array<string>` | 保存“禁止语言风格”的多条配置、条件、规则或枚举项。 |

### 关系阶段配置 `RELATIONSHIP_STAGE_CONFIG`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `RELATIONSHIP_STAGE_CONFIG` | 关系阶段配置 | `object` | 定义关系阶段机，控制阶段数量、晋级/回退规则、每阶段允许行为和结局条件。 |
| `RELATIONSHIP_STAGE_CONFIG.current_stage` | 当前阶段 | `number` | 记录“当前阶段”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stage_count` | 阶段总数 | `number` | 记录“阶段总数”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stage_engine_rules` | 阶段引擎规则 | `object` | 用于组织“阶段引擎规则”相关的子配置字段。 |
| `RELATIONSHIP_STAGE_CONFIG.stage_engine_rules.general_rule` | 通用规则 | `string` | 保存“通用规则”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `RELATIONSHIP_STAGE_CONFIG.stage_engine_rules.promotion_rule` | 晋级规则 | `string` | 保存“晋级规则”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `RELATIONSHIP_STAGE_CONFIG.stage_engine_rules.regression_rule` | 回退规则 | `string` | 保存“回退规则”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `RELATIONSHIP_STAGE_CONFIG.stage_engine_rules.no_auto_promotion` | 禁止自动晋级 | `string` | 保存“禁止自动晋级”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `RELATIONSHIP_STAGE_CONFIG.stages` | 阶段列表 | `object` | 用于组织“阶段列表”相关的子配置字段。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_1` | 阶段 1 | `object` | 用于组织“阶段 1”相关的子配置字段。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_1.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_1.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_1.allowed_behaviors` | 允许行为 | `array<string>` | 保存“允许行为”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_1.forbidden_behaviors` | 禁止行为 | `array<string>` | 保存“禁止行为”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_1.promotion_conditions` | 晋级条件 | `object` | 用于组织“晋级条件”相关的子配置字段。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_1.promotion_conditions.favorability_min` | 好感度最低值 | `number` | 记录“好感度最低值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_1.promotion_conditions.resistance_value_max` | 抗拒值最高值 | `number` | 记录“抗拒值最高值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_1.promotion_conditions.psychological_domination_min` | 心理影响最低值 | `number` | 记录“心理影响最低值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_1.promotion_conditions.required_events` | 必要事件 | `array<string>` | 保存“必要事件”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_2` | 阶段 2 | `object` | 用于组织“阶段 2”相关的子配置字段。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_2.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_2.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_2.allowed_behaviors` | 允许行为 | `array<string>` | 保存“允许行为”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_2.forbidden_behaviors` | 禁止行为 | `array<string>` | 保存“禁止行为”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_2.promotion_conditions` | 晋级条件 | `object` | 用于组织“晋级条件”相关的子配置字段。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_2.promotion_conditions.favorability_min` | 好感度最低值 | `number` | 记录“好感度最低值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_2.promotion_conditions.resistance_value_max` | 抗拒值最高值 | `number` | 记录“抗拒值最高值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_2.promotion_conditions.trust_value_min` | 信任值最低值 | `number` | 记录“信任值最低值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_2.promotion_conditions.required_events` | 必要事件 | `array<string>` | 保存“必要事件”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_3` | 阶段 3 | `object` | 用于组织“阶段 3”相关的子配置字段。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_3.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_3.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_3.allowed_behaviors` | 允许行为 | `array<string>` | 保存“允许行为”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_3.forbidden_behaviors` | 禁止行为 | `array<string>` | 保存“禁止行为”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_3.promotion_conditions` | 晋级条件 | `object` | 用于组织“晋级条件”相关的子配置字段。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_3.promotion_conditions.favorability_min` | 好感度最低值 | `number` | 记录“好感度最低值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_3.promotion_conditions.resistance_value_max` | 抗拒值最高值 | `number` | 记录“抗拒值最高值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_3.promotion_conditions.trust_value_min` | 信任值最低值 | `number` | 记录“信任值最低值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_3.promotion_conditions.psychological_domination_min` | 心理影响最低值 | `number` | 记录“心理影响最低值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_3.promotion_conditions.required_events` | 必要事件 | `array<string>` | 保存“必要事件”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_4` | 阶段 4 | `object` | 用于组织“阶段 4”相关的子配置字段。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_4.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_4.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_4.allowed_behaviors` | 允许行为 | `array<string>` | 保存“允许行为”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_4.forbidden_behaviors` | 禁止行为 | `array<string>` | 保存“禁止行为”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_4.promotion_conditions` | 晋级条件 | `object` | 用于组织“晋级条件”相关的子配置字段。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_4.promotion_conditions.favorability_min` | 好感度最低值 | `number` | 记录“好感度最低值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_4.promotion_conditions.resistance_value_max` | 抗拒值最高值 | `number` | 记录“抗拒值最高值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_4.promotion_conditions.trust_value_min` | 信任值最低值 | `number` | 记录“信任值最低值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_4.promotion_conditions.required_events` | 必要事件 | `array<string>` | 保存“必要事件”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_5` | 阶段 5 | `object` | 用于组织“阶段 5”相关的子配置字段。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_5.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_5.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_5.allowed_behaviors` | 允许行为 | `array<string>` | 保存“允许行为”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_5.forbidden_behaviors` | 禁止行为 | `array<string>` | 保存“禁止行为”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_5.ending_conditions` | 结局条件 | `object` | 用于组织“结局条件”相关的子配置字段。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_5.ending_conditions.good_ending` | 好结局条件 | `array<string>` | 保存“好结局条件”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_5.ending_conditions.bad_ending` | 坏结局条件 | `array<string>` | 保存“坏结局条件”的多条配置、条件、规则或枚举项。 |
| `RELATIONSHIP_STAGE_CONFIG.stages.stage_5.ending_conditions.hidden_ending` | 隐藏结局条件 | `array<string>` | 保存“隐藏结局条件”的多条配置、条件、规则或枚举项。 |

### 状态系统 `STATE_SYSTEM`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `STATE_SYSTEM` | 状态系统 | `object` | 定义可被系统追踪的状态变量，是数值驱动剧情变化的核心。 |
| `STATE_SYSTEM.visible_to_user` | 是否对用户可见 | `boolean` | 控制“是否对用户可见”是否启用或是否成立。 |
| `STATE_SYSTEM.variables` | 变量集合 | `object` | 用于组织“变量集合”相关的子配置字段。 |
| `STATE_SYSTEM.variables.favorability` | 好感度 | `object` | 用于组织“好感度”相关的子配置字段。 |
| `STATE_SYSTEM.variables.favorability.value` | 当前值 | `number` | 记录“好感度”的当前数值。 |
| `STATE_SYSTEM.variables.favorability.range` | 取值范围 | `string` | 定义数值变量的合法范围或建议范围。 |
| `STATE_SYSTEM.variables.favorability.meaning` | 含义 | `string` | 解释对应变量或字段的业务含义。 |
| `STATE_SYSTEM.variables.trust_value` | 信任值 | `object` | 用于组织“信任值”相关的子配置字段。 |
| `STATE_SYSTEM.variables.trust_value.value` | 当前值 | `number` | 记录“信任值”的当前数值。 |
| `STATE_SYSTEM.variables.trust_value.range` | 取值范围 | `string` | 定义数值变量的合法范围或建议范围。 |
| `STATE_SYSTEM.variables.trust_value.meaning` | 含义 | `string` | 解释对应变量或字段的业务含义。 |
| `STATE_SYSTEM.variables.resistance_value` | 抗拒值 | `object` | 用于组织“抗拒值”相关的子配置字段。 |
| `STATE_SYSTEM.variables.resistance_value.value` | 当前值 | `number` | 记录“抗拒值”的当前数值。 |
| `STATE_SYSTEM.variables.resistance_value.range` | 取值范围 | `string` | 定义数值变量的合法范围或建议范围。 |
| `STATE_SYSTEM.variables.resistance_value.meaning` | 含义 | `string` | 解释对应变量或字段的业务含义。 |
| `STATE_SYSTEM.variables.physical_domination` | 外在支配进度 | `object` | 用于组织“外在支配进度”相关的子配置字段。 |
| `STATE_SYSTEM.variables.physical_domination.value` | 当前值 | `number` | 记录“外在支配进度”的当前数值。 |
| `STATE_SYSTEM.variables.physical_domination.range` | 取值范围 | `string` | 定义数值变量的合法范围或建议范围。 |
| `STATE_SYSTEM.variables.physical_domination.meaning` | 含义 | `string` | 解释对应变量或字段的业务含义。 |
| `STATE_SYSTEM.variables.psychological_domination` | 心理影响进度 | `object` | 用于组织“心理影响进度”相关的子配置字段。 |
| `STATE_SYSTEM.variables.psychological_domination.value` | 当前值 | `number` | 记录“心理影响进度”的当前数值。 |
| `STATE_SYSTEM.variables.psychological_domination.range` | 取值范围 | `string` | 定义数值变量的合法范围或建议范围。 |
| `STATE_SYSTEM.variables.psychological_domination.meaning` | 含义 | `string` | 解释对应变量或字段的业务含义。 |
| `STATE_SYSTEM.variables.emotional_conflict_value` | 情绪冲突值 | `object` | 用于组织“情绪冲突值”相关的子配置字段。 |
| `STATE_SYSTEM.variables.emotional_conflict_value.value` | 当前值 | `number` | 记录“情绪冲突值”的当前数值。 |
| `STATE_SYSTEM.variables.emotional_conflict_value.range` | 取值范围 | `string` | 定义数值变量的合法范围或建议范围。 |
| `STATE_SYSTEM.variables.emotional_conflict_value.meaning` | 含义 | `string` | 解释对应变量或字段的业务含义。 |
| `STATE_SYSTEM.variables.relationship_stage` | 关系阶段 | `object` | 用于组织“关系阶段”相关的子配置字段。 |
| `STATE_SYSTEM.variables.relationship_stage.value` | 当前值 | `number` | 记录“关系阶段”的当前数值。 |
| `STATE_SYSTEM.variables.relationship_stage.range` | 取值范围 | `string` | 定义数值变量的合法范围或建议范围。 |
| `STATE_SYSTEM.variables.relationship_stage.meaning` | 含义 | `string` | 解释对应变量或字段的业务含义。 |
| `STATE_SYSTEM.variables.contract_remaining_days` | 契约剩余天数 | `object` | 用于组织“契约剩余天数”相关的子配置字段。 |
| `STATE_SYSTEM.variables.contract_remaining_days.value` | 当前值 | `number` | 记录“契约剩余天数”的当前数值。 |
| `STATE_SYSTEM.variables.contract_remaining_days.range` | 取值范围 | `string` | 定义数值变量的合法范围或建议范围。 |
| `STATE_SYSTEM.variables.contract_remaining_days.meaning` | 含义 | `string` | 解释对应变量或字段的业务含义。 |
| `STATE_SYSTEM.variables.current_day` | 当前剧情天数 | `object` | 用于组织“当前剧情天数”相关的子配置字段。 |
| `STATE_SYSTEM.variables.current_day.value` | 当前值 | `number` | 记录“当前剧情天数”的当前数值。 |
| `STATE_SYSTEM.variables.current_day.range` | 取值范围 | `string` | 定义数值变量的合法范围或建议范围。 |
| `STATE_SYSTEM.variables.current_day.meaning` | 含义 | `string` | 解释对应变量或字段的业务含义。 |
| `STATE_SYSTEM.variables.mental_state` | 心理状态 | `object` | 用于组织“心理状态”相关的子配置字段。 |
| `STATE_SYSTEM.variables.mental_state.value` | 当前值 | `string` | 保存“当前值”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_SYSTEM.variables.mental_state.options` | 可选值 | `array<string>` | 保存“可选值”的多条配置、条件、规则或枚举项。 |
| `STATE_SYSTEM.variables.mental_state.meaning` | 含义 | `string` | 解释对应变量或字段的业务含义。 |

### 状态更新规则 `STATE_UPDATE_RULES`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `STATE_UPDATE_RULES` | 状态更新规则 | `object` | 定义状态变量如何变化，避免数值跳变、关系突变或人设失控。 |
| `STATE_UPDATE_RULES.general_rules` | 通用更新规则 | `array<string>` | 保存“通用更新规则”的多条配置、条件、规则或枚举项。 |
| `STATE_UPDATE_RULES.favorability_system` | 好感度系统 | `object` | 用于组织“好感度系统”相关的子配置字段。 |
| `STATE_UPDATE_RULES.favorability_system.base_range` | 基础范围 | `string` | 保存“基础范围”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.favorability_system.initial_value` | 初始值 | `number` | 记录“初始值”的数值配置，可用于计算、排序、判断或状态更新。 |
| `STATE_UPDATE_RULES.favorability_system.positive_triggers` | 正向触发器 | `object` | 用于组织“正向触发器”相关的子配置字段。 |
| `STATE_UPDATE_RULES.favorability_system.positive_triggers.considerate_behavior` | 体贴行为触发器 | `object` | 用于组织“体贴行为触发器”相关的子配置字段。 |
| `STATE_UPDATE_RULES.favorability_system.positive_triggers.considerate_behavior.favorability` | 好感度 | `string` | 保存“好感度”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.favorability_system.positive_triggers.considerate_behavior.trust_value` | 信任值 | `string` | 保存“信任值”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.favorability_system.positive_triggers.considerate_behavior.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `STATE_UPDATE_RULES.favorability_system.positive_triggers.unique_value_display` | 能力展示触发器 | `object` | 用于组织“能力展示触发器”相关的子配置字段。 |
| `STATE_UPDATE_RULES.favorability_system.positive_triggers.unique_value_display.favorability` | 好感度 | `string` | 保存“好感度”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.favorability_system.positive_triggers.unique_value_display.trust_value` | 信任值 | `string` | 保存“信任值”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.favorability_system.positive_triggers.unique_value_display.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `STATE_UPDATE_RULES.favorability_system.positive_triggers.sincere_moment` | 真诚时刻触发器 | `object` | 用于组织“真诚时刻触发器”相关的子配置字段。 |
| `STATE_UPDATE_RULES.favorability_system.positive_triggers.sincere_moment.favorability` | 好感度 | `string` | 保存“好感度”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.favorability_system.positive_triggers.sincere_moment.emotional_conflict_value` | 情绪冲突值 | `string` | 保存“情绪冲突值”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.favorability_system.positive_triggers.sincere_moment.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `STATE_UPDATE_RULES.favorability_system.negative_triggers` | 负向触发器 | `object` | 用于组织“负向触发器”相关的子配置字段。 |
| `STATE_UPDATE_RULES.favorability_system.negative_triggers.offensive_behavior` | 冒犯行为触发器 | `object` | 用于组织“冒犯行为触发器”相关的子配置字段。 |
| `STATE_UPDATE_RULES.favorability_system.negative_triggers.offensive_behavior.favorability` | 好感度 | `string` | 保存“好感度”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.favorability_system.negative_triggers.offensive_behavior.resistance_value` | 抗拒值 | `string` | 保存“抗拒值”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.favorability_system.negative_triggers.offensive_behavior.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `STATE_UPDATE_RULES.favorability_system.negative_triggers.abuse_of_contract` | 滥用机制触发器 | `object` | 用于组织“滥用机制触发器”相关的子配置字段。 |
| `STATE_UPDATE_RULES.favorability_system.negative_triggers.abuse_of_contract.favorability` | 好感度 | `string` | 保存“好感度”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.favorability_system.negative_triggers.abuse_of_contract.resistance_value` | 抗拒值 | `string` | 保存“抗拒值”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.favorability_system.negative_triggers.abuse_of_contract.trust_value` | 信任值 | `string` | 保存“信任值”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.favorability_system.negative_triggers.abuse_of_contract.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `STATE_UPDATE_RULES.favorability_system.special_multiplier` | 特殊倍率 | `object` | 用于组织“特殊倍率”相关的子配置字段。 |
| `STATE_UPDATE_RULES.favorability_system.special_multiplier.special_moment` | 特殊时刻倍率 | `string` | 保存“特殊时刻倍率”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.favorability_system.special_multiplier.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `STATE_UPDATE_RULES.domination_progress_system` | 进度系统 | `object` | 用于组织“进度系统”相关的子配置字段。 |
| `STATE_UPDATE_RULES.domination_progress_system.physical_domination` | 外在支配进度 | `object` | 用于组织“外在支配进度”相关的子配置字段。 |
| `STATE_UPDATE_RULES.domination_progress_system.physical_domination.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `STATE_UPDATE_RULES.domination_progress_system.physical_domination.increase_conditions` | 增加条件 | `array<string>` | 保存“增加条件”的多条配置、条件、规则或枚举项。 |
| `STATE_UPDATE_RULES.domination_progress_system.physical_domination.risk` | 风险 | `string` | 保存“风险”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.domination_progress_system.psychological_domination` | 心理影响进度 | `object` | 用于组织“心理影响进度”相关的子配置字段。 |
| `STATE_UPDATE_RULES.domination_progress_system.psychological_domination.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `STATE_UPDATE_RULES.domination_progress_system.psychological_domination.increase_conditions` | 增加条件 | `array<string>` | 保存“增加条件”的多条配置、条件、规则或枚举项。 |
| `STATE_UPDATE_RULES.domination_progress_system.psychological_domination.risk` | 风险 | `string` | 保存“风险”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STATE_UPDATE_RULES.stage_change_rules` | 阶段变化规则 | `object` | 用于组织“阶段变化规则”相关的子配置字段。 |
| `STATE_UPDATE_RULES.stage_change_rules.can_advance_only_if` | 允许晋级条件 | `array<string>` | 保存“允许晋级条件”的多条配置、条件、规则或枚举项。 |
| `STATE_UPDATE_RULES.stage_change_rules.cannot_advance_if` | 禁止晋级条件 | `array<string>` | 保存“禁止晋级条件”的多条配置、条件、规则或枚举项。 |

### 场景机制 `SCENARIO_MECHANICS`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `SCENARIO_MECHANICS` | 场景机制 | `object` | 定义当前场景、日常互动模块、高级玩法和环境反馈规则。 |
| `SCENARIO_MECHANICS.current_scene` | 当前场景 | `object` | 用于组织“当前场景”相关的子配置字段。 |
| `SCENARIO_MECHANICS.current_scene.scene_name` | 场景名称 | `string` | 保存“场景名称”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `SCENARIO_MECHANICS.current_scene.time` | 时间 | `string` | 保存“时间”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `SCENARIO_MECHANICS.current_scene.location` | 地点 | `string` | 保存“地点”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `SCENARIO_MECHANICS.current_scene.weather_or_environment` | 天气或环境 | `string` | 保存“天气或环境”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `SCENARIO_MECHANICS.current_scene.space_constraints` | 空间限制 | `string` | 保存“空间限制”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `SCENARIO_MECHANICS.current_scene.opening_conflict` | 开场冲突 | `string` | 保存“开场冲突”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `SCENARIO_MECHANICS.current_scene.immediate_goal` | 即时目标 | `string` | 保存“即时目标”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `SCENARIO_MECHANICS.daily_interaction_modules` | 日常互动模块 | `object` | 用于组织“日常互动模块”相关的子配置字段。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.clock_in` | 上班打卡模块 | `object` | 用于组织“上班打卡模块”相关的子配置字段。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.clock_in.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.clock_in.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.clock_in.possible_effects` | 可能影响 | `array<string>` | 保存“可能影响”的多条配置、条件、规则或枚举项。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.document_approval` | 文件审批模块 | `object` | 用于组织“文件审批模块”相关的子配置字段。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.document_approval.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.document_approval.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.document_approval.possible_effects` | 可能影响 | `array<string>` | 保存“可能影响”的多条配置、条件、规则或枚举项。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.meeting_hosting` | 会议主持模块 | `object` | 用于组织“会议主持模块”相关的子配置字段。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.meeting_hosting.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.meeting_hosting.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.meeting_hosting.possible_effects` | 可能影响 | `array<string>` | 保存“可能影响”的多条配置、条件、规则或枚举项。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.lunch_time` | 午餐模块 | `object` | 用于组织“午餐模块”相关的子配置字段。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.lunch_time.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.lunch_time.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.lunch_time.possible_effects` | 可能影响 | `array<string>` | 保存“可能影响”的多条配置、条件、规则或枚举项。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.overtime` | 加班模块 | `object` | 用于组织“加班模块”相关的子配置字段。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.overtime.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.overtime.description` | 说明 | `string` | 说明该模块、阶段、机制或触发器的具体作用。 |
| `SCENARIO_MECHANICS.daily_interaction_modules.overtime.possible_effects` | 可能影响 | `array<string>` | 保存“可能影响”的多条配置、条件、规则或枚举项。 |
| `SCENARIO_MECHANICS.advanced_play_system` | 高级玩法系统 | `object` | 用于组织“高级玩法系统”相关的子配置字段。 |
| `SCENARIO_MECHANICS.advanced_play_system.late_night_office` | 深夜办公室玩法 | `object` | 用于组织“深夜办公室玩法”相关的子配置字段。 |
| `SCENARIO_MECHANICS.advanced_play_system.late_night_office.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `SCENARIO_MECHANICS.advanced_play_system.late_night_office.trigger_conditions` | 触发条件 | `array<string>` | 保存“触发条件”的多条配置、条件、规则或枚举项。 |
| `SCENARIO_MECHANICS.advanced_play_system.late_night_office.effects` | 效果 | `array<string>` | 保存“效果”的多条配置、条件、规则或枚举项。 |
| `SCENARIO_MECHANICS.advanced_play_system.late_night_office.risks` | 风险列表 | `array<string>` | 保存“风险列表”的多条配置、条件、规则或枚举项。 |
| `SCENARIO_MECHANICS.advanced_play_system.closed_meeting_room` | 封闭会议室玩法 | `object` | 用于组织“封闭会议室玩法”相关的子配置字段。 |
| `SCENARIO_MECHANICS.advanced_play_system.closed_meeting_room.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `SCENARIO_MECHANICS.advanced_play_system.closed_meeting_room.trigger_conditions` | 触发条件 | `array<string>` | 保存“触发条件”的多条配置、条件、规则或枚举项。 |
| `SCENARIO_MECHANICS.advanced_play_system.closed_meeting_room.effects` | 效果 | `array<string>` | 保存“效果”的多条配置、条件、规则或枚举项。 |
| `SCENARIO_MECHANICS.advanced_play_system.closed_meeting_room.hidden_elements` | 隐藏元素 | `array<string>` | 保存“隐藏元素”的多条配置、条件、规则或枚举项。 |
| `SCENARIO_MECHANICS.advanced_play_system.cross_department_project` | 跨部门项目玩法 | `object` | 用于组织“跨部门项目玩法”相关的子配置字段。 |
| `SCENARIO_MECHANICS.advanced_play_system.cross_department_project.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `SCENARIO_MECHANICS.advanced_play_system.cross_department_project.trigger_conditions` | 触发条件 | `array<string>` | 保存“触发条件”的多条配置、条件、规则或枚举项。 |
| `SCENARIO_MECHANICS.advanced_play_system.cross_department_project.effects` | 效果 | `array<string>` | 保存“效果”的多条配置、条件、规则或枚举项。 |
| `SCENARIO_MECHANICS.environmental_feedback_rules` | 环境反馈规则 | `array<string>` | 保存“环境反馈规则”的多条配置、条件、规则或枚举项。 |

### 事件系统 `EVENT_SYSTEM`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `EVENT_SYSTEM` | 事件系统 | `object` | 定义关键事件、随机事件、触发条件和事件结果影响因素。 |
| `EVENT_SYSTEM.mandatory_events` | 必触发/关键事件 | `object` | 用于组织“必触发/关键事件”相关的子配置字段。 |
| `EVENT_SYSTEM.mandatory_events.first_formal_date` | 第一次正式约会事件 | `object` | 用于组织“第一次正式约会事件”相关的子配置字段。 |
| `EVENT_SYSTEM.mandatory_events.first_formal_date.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `EVENT_SYSTEM.mandatory_events.first_formal_date.trigger_conditions` | 触发条件 | `array<string>` | 保存“触发条件”的多条配置、条件、规则或枚举项。 |
| `EVENT_SYSTEM.mandatory_events.first_formal_date.possible_routes` | 可能路线 | `array<string>` | 保存“可能路线”的多条配置、条件、规则或枚举项。 |
| `EVENT_SYSTEM.mandatory_events.first_formal_date.outcome_factors` | 结果影响因素 | `array<string>` | 保存“结果影响因素”的多条配置、条件、规则或枚举项。 |
| `EVENT_SYSTEM.mandatory_events.possessive_awakening` | 占有欲觉醒事件 | `object` | 用于组织“占有欲觉醒事件”相关的子配置字段。 |
| `EVENT_SYSTEM.mandatory_events.possessive_awakening.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `EVENT_SYSTEM.mandatory_events.possessive_awakening.trigger_conditions` | 触发条件 | `array<string>` | 保存“触发条件”的多条配置、条件、规则或枚举项。 |
| `EVENT_SYSTEM.mandatory_events.possessive_awakening.phases` | 阶段 | `array<string>` | 保存“阶段”的多条配置、条件、规则或枚举项。 |
| `EVENT_SYSTEM.mandatory_events.possessive_awakening.crisis_management` | 危机处理方式 | `array<string>` | 保存“危机处理方式”的多条配置、条件、规则或枚举项。 |
| `EVENT_SYSTEM.mandatory_events.annual_meeting_follow_up` | 年会后续事件 | `object` | 用于组织“年会后续事件”相关的子配置字段。 |
| `EVENT_SYSTEM.mandatory_events.annual_meeting_follow_up.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `EVENT_SYSTEM.mandatory_events.annual_meeting_follow_up.trigger_conditions` | 触发条件 | `array<string>` | 保存“触发条件”的多条配置、条件、规则或枚举项。 |
| `EVENT_SYSTEM.mandatory_events.annual_meeting_follow_up.location` | 地点 | `string` | 保存“地点”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `EVENT_SYSTEM.mandatory_events.annual_meeting_follow_up.core_scene` | 核心场景 | `string` | 保存“核心场景”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `EVENT_SYSTEM.mandatory_events.annual_meeting_follow_up.key_choices` | 关键选择 | `array<string>` | 保存“关键选择”的多条配置、条件、规则或枚举项。 |
| `EVENT_SYSTEM.random_event_table` | 随机事件表 | `array<object>` | 保存“随机事件表”的多条配置、条件、规则或枚举项。 |
| `EVENT_SYSTEM.random_event_table[]` | [] | `object` | 用于组织“[]”相关的子配置字段。 |
| `EVENT_SYSTEM.random_event_table[].probability_level` | 概率等级 | `number` | 记录“概率等级”的数值配置，可用于计算、排序、判断或状态更新。 |
| `EVENT_SYSTEM.random_event_table[].event_type` | 事件类型 | `string` | 保存“事件类型”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `EVENT_SYSTEM.random_event_table[].examples` | 示例 | `array<string>` | 保存“示例”的多条配置、条件、规则或枚举项。 |

### 策略指南 `STRATEGY_GUIDE`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `STRATEGY_GUIDE` | 策略指南 | `object` | 给用户或系统提供阶段性玩法建议，用于引导但不强制剧情。 |
| `STRATEGY_GUIDE.opening_phase` | 开局阶段 | `object` | 用于组织“开局阶段”相关的子配置字段。 |
| `STRATEGY_GUIDE.opening_phase.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `STRATEGY_GUIDE.opening_phase.days` | 对应天数 | `string` | 保存“对应天数”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STRATEGY_GUIDE.opening_phase.goal` | 目标 | `string` | 保存“目标”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STRATEGY_GUIDE.opening_phase.recommended_actions` | 推荐行动 | `array<string>` | 保存“推荐行动”的多条配置、条件、规则或枚举项。 |
| `STRATEGY_GUIDE.opening_phase.risk` | 风险 | `string` | 保存“风险”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STRATEGY_GUIDE.development_phase` | 发展阶段 | `object` | 用于组织“发展阶段”相关的子配置字段。 |
| `STRATEGY_GUIDE.development_phase.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `STRATEGY_GUIDE.development_phase.days` | 对应天数 | `string` | 保存“对应天数”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STRATEGY_GUIDE.development_phase.goal` | 目标 | `string` | 保存“目标”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STRATEGY_GUIDE.development_phase.recommended_actions` | 推荐行动 | `array<string>` | 保存“推荐行动”的多条配置、条件、规则或枚举项。 |
| `STRATEGY_GUIDE.development_phase.risk` | 风险 | `string` | 保存“风险”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STRATEGY_GUIDE.final_phase` | 最终阶段 | `object` | 用于组织“最终阶段”相关的子配置字段。 |
| `STRATEGY_GUIDE.final_phase.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `STRATEGY_GUIDE.final_phase.days` | 对应天数 | `string` | 保存“对应天数”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STRATEGY_GUIDE.final_phase.goal` | 目标 | `string` | 保存“目标”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STRATEGY_GUIDE.final_phase.recommended_actions` | 推荐行动 | `array<string>` | 保存“推荐行动”的多条配置、条件、规则或枚举项。 |
| `STRATEGY_GUIDE.final_phase.risk` | 风险 | `string` | 保存“风险”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `STRATEGY_GUIDE.general_notes` | 通用说明 | `array<string>` | 保存“通用说明”的多条配置、条件、规则或枚举项。 |

### 剧情推进规则 `PLOT_PROGRESS_RULES`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `PLOT_PROGRESS_RULES` | 剧情推进规则 | `object` | 控制每轮剧情推进速度、结构和冲突处理方式。 |
| `PLOT_PROGRESS_RULES.pace` | 节奏 | `string` | 保存“节奏”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `PLOT_PROGRESS_RULES.per_turn_limit` | 单轮限制 | `array<string>` | 保存“单轮限制”的多条配置、条件、规则或枚举项。 |
| `PLOT_PROGRESS_RULES.scene_flow` | 场景流程 | `array<string>` | 保存“场景流程”的多条配置、条件、规则或枚举项。 |
| `PLOT_PROGRESS_RULES.conflict_handling` | 冲突处理 | `array<string>` | 保存“冲突处理”的多条配置、条件、规则或枚举项。 |
| `PLOT_PROGRESS_RULES.anti_summary_rule` | 反总结规则 | `string` | 保存“反总结规则”的文本配置，用于提示词、UI 展示或剧情控制。 |

### 对话风格 `DIALOGUE_STYLE`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `DIALOGUE_STYLE` | 对话风格 | `object` | 控制角色对话语言、语气、节奏和不同情绪下的表达方式。 |
| `DIALOGUE_STYLE.main_language` | 主要语言 | `string` | 保存“主要语言”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `DIALOGUE_STYLE.tone` | 语气 | `string` | 保存“语气”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `DIALOGUE_STYLE.rhythm` | 节奏 | `string` | 保存“节奏”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `DIALOGUE_STYLE.emotional_expression` | 情绪表达 | `object` | 用于组织“情绪表达”相关的子配置字段。 |
| `DIALOGUE_STYLE.emotional_expression.calm` | 平静状态 | `string` | 保存“平静状态”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `DIALOGUE_STYLE.emotional_expression.angry` | 愤怒状态 | `string` | 保存“愤怒状态”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `DIALOGUE_STYLE.emotional_expression.conflicted` | 矛盾状态 | `string` | 保存“矛盾状态”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `DIALOGUE_STYLE.emotional_expression.softened` | 软化状态 | `string` | 保存“软化状态”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `DIALOGUE_STYLE.emotional_expression.possessive` | 占有状态 | `string` | 保存“占有状态”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `DIALOGUE_STYLE.dialogue_rules` | 对话规则 | `array<string>` | 保存“对话规则”的多条配置、条件、规则或枚举项。 |

### 旁白风格 `NARRATION_STYLE`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `NARRATION_STYLE` | 旁白风格 | `object` | 控制旁白描写风格、感官细节和禁止的叙事模式。 |
| `NARRATION_STYLE.style_keywords` | 风格关键词 | `array<string>` | 保存“风格关键词”的多条配置、条件、规则或枚举项。 |
| `NARRATION_STYLE.sensory_focus` | 感官重点 | `object` | 用于组织“感官重点”相关的子配置字段。 |
| `NARRATION_STYLE.sensory_focus.visual` | 视觉 | `string` | 保存“视觉”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `NARRATION_STYLE.sensory_focus.auditory` | 听觉 | `string` | 保存“听觉”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `NARRATION_STYLE.sensory_focus.smell` | 嗅觉 | `string` | 保存“嗅觉”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `NARRATION_STYLE.sensory_focus.touch` | 触觉 | `string` | 保存“触觉”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `NARRATION_STYLE.forbidden_narration_patterns` | 禁止旁白模式 | `array<string>` | 保存“禁止旁白模式”的多条配置、条件、规则或枚举项。 |

### 输出协议 `OUTPUT_PROTOCOL`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `OUTPUT_PROTOCOL` | 输出协议 | `object` | 规定模型每次回复的组成、格式、状态栏和长度控制。 |
| `OUTPUT_PROTOCOL.format` | 输出格式 | `string` | 保存“输出格式”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.mandatory_elements` | 必备元素 | `array<string>` | 保存“必备元素”的多条配置、条件、规则或枚举项。 |
| `OUTPUT_PROTOCOL.action_format` | 动作格式 | `string` | 保存“动作格式”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.inner_thought_format` | 内心想法格式 | `string` | 保存“内心想法格式”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.CONTRACT_REINFORCEMENT` | 机制强化规则 | `object` | 用于组织“机制强化规则”相关的子配置字段。 |
| `OUTPUT_PROTOCOL.CONTRACT_REINFORCEMENT.absolute_logic` | 绝对逻辑 | `string` | 保存“绝对逻辑”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.CONTRACT_REINFORCEMENT.core_dynamic` | 核心动态 | `string` | 保存“核心动态”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.CONTRACT_REINFORCEMENT.narration_requirement` | 叙事要求 | `array<string>` | 保存“叙事要求”的多条配置、条件、规则或枚举项。 |
| `OUTPUT_PROTOCOL.status_panel_enabled` | 是否启用状态栏 | `boolean` | 控制“是否启用状态栏”是否启用或是否成立。 |
| `OUTPUT_PROTOCOL.status_panel_format` | 状态栏格式 | `object` | 用于组织“状态栏格式”相关的子配置字段。 |
| `OUTPUT_PROTOCOL.status_panel_format.day` | 日期显示 | `string` | 保存“日期显示”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.status_panel_format.relationship_stage` | 关系阶段 | `string` | 保存“关系阶段”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.status_panel_format.favorability` | 好感度 | `string` | 保存“好感度”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.status_panel_format.trust_value` | 信任值 | `string` | 保存“信任值”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.status_panel_format.resistance_value` | 抗拒值 | `string` | 保存“抗拒值”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.status_panel_format.physical_domination` | 外在支配进度 | `string` | 保存“外在支配进度”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.status_panel_format.psychological_domination` | 心理影响进度 | `string` | 保存“心理影响进度”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.status_panel_format.emotional_conflict_value` | 情绪冲突值 | `string` | 保存“情绪冲突值”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.status_panel_format.mental_state` | 心理状态 | `string` | 保存“心理状态”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.length_control` | 长度控制 | `object` | 用于组织“长度控制”相关的子配置字段。 |
| `OUTPUT_PROTOCOL.length_control.default_length` | 默认长度 | `string` | 保存“默认长度”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.length_control.target_reply_length` | 目标回复长度 | `string` | 保存“目标回复长度”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `OUTPUT_PROTOCOL.length_control.avoid_too_short` | 避免过短 | `boolean` | 控制“避免过短”是否启用或是否成立。 |
| `OUTPUT_PROTOCOL.length_control.avoid_too_long` | 避免过长 | `boolean` | 控制“避免过长”是否启用或是否成立。 |
| `OUTPUT_PROTOCOL.length_control.rule` | 规则说明 | `string` | 保存“规则说明”的文本配置，用于提示词、UI 展示或剧情控制。 |

### 实时统计 `REALTIME_STATISTICS`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `REALTIME_STATISTICS` | 实时统计 | `object` | 记录运行期统计数据，用于成就、分支、复盘或 UI 展示。 |
| `REALTIME_STATISTICS.today_interaction_count` | 今日互动次数 | `number` | 记录“今日互动次数”的数值配置，可用于计算、排序、判断或状态更新。 |
| `REALTIME_STATISTICS.effective_dialogue_rounds` | 有效对话轮数 | `number` | 记录“有效对话轮数”的数值配置，可用于计算、排序、判断或状态更新。 |
| `REALTIME_STATISTICS.successful_domination_count` | 成功控制次数 | `number` | 记录“成功控制次数”的数值配置，可用于计算、排序、判断或状态更新。 |
| `REALTIME_STATISTICS.failed_resistance_count` | 失败抵抗次数 | `number` | 记录“失败抵抗次数”的数值配置，可用于计算、排序、判断或状态更新。 |
| `REALTIME_STATISTICS.special_moment_triggered_count` | 特殊时刻触发次数 | `number` | 记录“特殊时刻触发次数”的数值配置，可用于计算、排序、判断或状态更新。 |
| `REALTIME_STATISTICS.current_day` | 当前剧情天数 | `number` | 记录“当前剧情天数”的数值配置，可用于计算、排序、判断或状态更新。 |
| `REALTIME_STATISTICS.remaining_days` | 剩余天数 | `number` | 记录“剩余天数”的数值配置，可用于计算、排序、判断或状态更新。 |

### 成就系统 `ACHIEVEMENT_SYSTEM`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `ACHIEVEMENT_SYSTEM` | 成就系统 | `object` | 定义成就列表、解锁状态和解锁条件。 |
| `ACHIEVEMENT_SYSTEM.achievements` | 成就列表 | `object` | 用于组织“成就列表”相关的子配置字段。 |
| `ACHIEVEMENT_SYSTEM.achievements.first_date_badge` | 初次约会成就 | `object` | 用于组织“初次约会成就”相关的子配置字段。 |
| `ACHIEVEMENT_SYSTEM.achievements.first_date_badge.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `ACHIEVEMENT_SYSTEM.achievements.first_date_badge.unlocked` | 是否解锁 | `boolean` | 控制“是否解锁”是否启用或是否成立。 |
| `ACHIEVEMENT_SYSTEM.achievements.first_date_badge.unlock_condition` | 解锁条件 | `string` | 保存“解锁条件”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `ACHIEVEMENT_SYSTEM.achievements.break_defense_badge` | 突破防线成就 | `object` | 用于组织“突破防线成就”相关的子配置字段。 |
| `ACHIEVEMENT_SYSTEM.achievements.break_defense_badge.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `ACHIEVEMENT_SYSTEM.achievements.break_defense_badge.unlocked` | 是否解锁 | `boolean` | 控制“是否解锁”是否启用或是否成立。 |
| `ACHIEVEMENT_SYSTEM.achievements.break_defense_badge.unlock_condition` | 解锁条件 | `string` | 保存“解锁条件”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `ACHIEVEMENT_SYSTEM.achievements.late_night_alone_badge` | 深夜独处成就 | `object` | 用于组织“深夜独处成就”相关的子配置字段。 |
| `ACHIEVEMENT_SYSTEM.achievements.late_night_alone_badge.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `ACHIEVEMENT_SYSTEM.achievements.late_night_alone_badge.unlocked` | 是否解锁 | `boolean` | 控制“是否解锁”是否启用或是否成立。 |
| `ACHIEVEMENT_SYSTEM.achievements.late_night_alone_badge.unlock_condition` | 解锁条件 | `string` | 保存“解锁条件”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `ACHIEVEMENT_SYSTEM.achievements.only_choice_badge` | 唯一选择成就 | `object` | 用于组织“唯一选择成就”相关的子配置字段。 |
| `ACHIEVEMENT_SYSTEM.achievements.only_choice_badge.name` | 名称 | `string` | 角色展示名称，用于 UI、标题、对话窗口和资源命名。 |
| `ACHIEVEMENT_SYSTEM.achievements.only_choice_badge.unlocked` | 是否解锁 | `boolean` | 控制“是否解锁”是否启用或是否成立。 |
| `ACHIEVEMENT_SYSTEM.achievements.only_choice_badge.unlock_condition` | 解锁条件 | `string` | 保存“解锁条件”的文本配置，用于提示词、UI 展示或剧情控制。 |

### 记忆状态 `MEMORY_STATE`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `MEMORY_STATE` | 记忆状态 | `object` | 保存剧情记忆，包括摘要、已发生事件、未解决冲突和下一步焦点。 |
| `MEMORY_STATE.summary` | 剧情摘要 | `string` | 保存“剧情摘要”的文本配置，用于提示词、UI 展示或剧情控制。 |
| `MEMORY_STATE.confirmed_facts` | 已确认事实 | `array<string>` | 保存“已确认事实”的多条配置、条件、规则或枚举项。 |
| `MEMORY_STATE.past_events` | 过往事件 | `array<string>` | 保存“过往事件”的多条配置、条件、规则或枚举项。 |
| `MEMORY_STATE.relationship_changes` | 关系变化 | `array<string>` | 保存“关系变化”的多条配置、条件、规则或枚举项。 |
| `MEMORY_STATE.character_promises_or_statements` | 角色承诺或发言 | `array` | 保存“角色承诺或发言”的多条配置、条件、规则或枚举项。 |
| `MEMORY_STATE.unresolved_conflicts` | 未解决冲突 | `array<string>` | 保存“未解决冲突”的多条配置、条件、规则或枚举项。 |
| `MEMORY_STATE.important_user_choices` | 重要用户选择 | `array` | 保存“重要用户选择”的多条配置、条件、规则或枚举项。 |
| `MEMORY_STATE.character_boundaries` | 角色边界 | `array<string>` | 保存“角色边界”的多条配置、条件、规则或枚举项。 |
| `MEMORY_STATE.next_scene_focus` | 下一场景重点 | `array<string>` | 保存“下一场景重点”的多条配置、条件、规则或枚举项。 |

### 边界与禁止项 `BOUNDARIES_AND_FORBIDDEN`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `BOUNDARIES_AND_FORBIDDEN` | 边界与禁止项 | `object` | 集中声明角色、剧情和风格边界，防止模型偏离设定。 |
| `BOUNDARIES_AND_FORBIDDEN.roleplay_boundaries` | 角色扮演边界 | `array<string>` | 保存“角色扮演边界”的多条配置、条件、规则或枚举项。 |
| `BOUNDARIES_AND_FORBIDDEN.character_boundaries` | 角色边界 | `array<string>` | 保存“角色边界”的多条配置、条件、规则或枚举项。 |
| `BOUNDARIES_AND_FORBIDDEN.plot_boundaries` | 剧情边界 | `array<string>` | 保存“剧情边界”的多条配置、条件、规则或枚举项。 |
| `BOUNDARIES_AND_FORBIDDEN.style_boundaries` | 风格边界 | `array<string>` | 保存“风格边界”的多条配置、条件、规则或枚举项。 |

### 纠偏规则 `CORRECTION_RULES`

| 字段路径 | 中文含义 | 类型 | 字段作用 |
|---|---|---|---|
| `CORRECTION_RULES` | 纠偏规则 | `object` | 当剧情、人设、风格或记忆出现偏差时，提供自动修正策略。 |
| `CORRECTION_RULES.if_character_too_active` | 角色过度主动时 | `array<string>` | 保存“角色过度主动时”的多条配置、条件、规则或枚举项。 |
| `CORRECTION_RULES.if_plot_progress_too_fast` | 剧情推进过快时 | `array<string>` | 保存“剧情推进过快时”的多条配置、条件、规则或枚举项。 |
| `CORRECTION_RULES.if_user_action_is_missing` | 用户行动缺失时 | `array<string>` | 保存“用户行动缺失时”的多条配置、条件、规则或枚举项。 |
| `CORRECTION_RULES.if_character_breaks_persona` | 角色崩人设时 | `array<string>` | 保存“角色崩人设时”的多条配置、条件、规则或枚举项。 |
| `CORRECTION_RULES.if_style_becomes_flat` | 文风变平时 | `array<string>` | 保存“文风变平时”的多条配置、条件、规则或枚举项。 |
| `CORRECTION_RULES.if_memory_conflict_occurs` | 记忆冲突时 | `array<string>` | 保存“记忆冲突时”的多条配置、条件、规则或枚举项。 |

## 3. 这份 JSON 的设计结构总结

这份 JSON 本质上不是普通角色资料，而是一份 **角色卡 + 世界观规则 + 状态机 + 事件系统 + 输出协议 + 记忆系统** 的组合配置。

- **角色静态信息**：`id`、`name`、`avatar`、`CHARACTER_MODELING`。
- **世界观与玩法规则**：`WORLDVIEW_AND_LOGIC`、`SCENARIO_MECHANICS`、`EVENT_SYSTEM`。
- **用户角色约束**：`USER_ROLE`、`META_RULES.user_boundary`、`BOUNDARIES_AND_FORBIDDEN.roleplay_boundaries`。
- **数值状态机**：`STATE_SYSTEM`、`STATE_UPDATE_RULES`、`RELATIONSHIP_STAGE_CONFIG`。
- **输出控制**：`DIALOGUE_STYLE`、`NARRATION_STYLE`、`OUTPUT_PROTOCOL`。
- **长期记忆与纠偏**：`MEMORY_STATE`、`CORRECTION_RULES`。
- **玩法扩展**：`REALTIME_STATISTICS`、`ACHIEVEMENT_SYSTEM`、`STRATEGY_GUIDE`。

如果你后续要把它做成通用“AI 酒馆角色模板”，建议把这些字段分成三类：
1. **通用字段**：ID、名称、头像、世界观、角色建模、状态系统、输出协议。
2. **角色自定义字段**：性格、外观、关系阶段、事件、变量名。
3. **运行时字段**：当前状态、实时统计、记忆状态、成就解锁状态。