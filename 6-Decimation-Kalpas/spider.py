# import  requests
# import json
# headers = {
#     "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 18_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) BossZhipin/13.070/1004 Screen/430X932 CustomOS/iPhone zci/rRdg8pBsCA4cEgnoq7w48iyMJhGjXed9pBU8Vkd4hnQQYozNHIPgw9vWUedXIEbS4aW_QDOfCG8LNEIS5vipiUDAc90m9UIJMF06ZsJ80dpBtu-9sSw5m6SqR7ho8qtAqCPjB3SVkAKEPDUl73e5Ogr9AAKYaX27d_K4sliVdIGQEB4M9oJUmhf9FtGZSdrFcgSXva04xgKYOvppbz3sqApMKbonB7XPxrmfj0CAo7bmEKbZQgecu8X5j7HsxahyE4Xhbh_jJ-ttIDFFRd75xrnxNVEeWdr_mtbFOZdiD0qSngJHDX_ntvKYAVyxl2AHtblX2REXvA7IkbX_WzH0A7w8S4tcVONgB3f-fqjSfxBagPHId3ShSgkLaVZXQy52AROsSFoOrTnD9v7C87k9s3cqnVtaELwV-p6EYPSSKyy36jX-sRcl1TKcLGH64cXBzoMqoK5JWJrL87lEJ6_-7Wl9lujK87qNbWZdws8h3ZPQPi5REdiRW6JyAwM7naplL_1GxQayDB3i8HUrR_wboy-zEx74o7Fyp038sr01Ki1BH0XtCq39RWzwN6sDO63scHFJ91taox4~",
#     "Referer": 'https://m.zhipin.com/mpa/v3/html/get/interview/detail-question?securityFormId=fd64171d87df8d4brhV939i5&source=1&positionCode=100208,100901,100903&sortType=1&type=1&page=1',
#     "Cookie": "bst=V2Qt4gGeX_01ZgXdJtxxoZISuw7D7UzA~~|Qt4gGeX_01ZgXdJtxxoZISuw7DrVwA~~; __a=52942355.1746588038.1746724116.1747834094.4.3.1.4; __c=1747834094; __g=-; __l=l=%2Fm.zhipin.com%2Fmpa%2Fhtml%2Fget%2Finterview%2Fdetail-answer%3FsecurityFormId%3De9c67999a383f0e2pgp72dS5GA~~%26source%3D2&r=; t2=DCF580xKo2znTEFGhsNgn2F2RAFlYnT7zqlM53P4gINmhKDFY7PHVd9MRu0N-2kQxatQn-kWv3R8XrfWuC-zz2A~~; zp_at=jVPWuWVuP_GXFLRO0JITDgzAcPxFU3HsLYsIVhE4Xxo~"
# }
#
#
# current_index = 1
# while True:
#     url = f'https://m.zhipin.com/wapi/moment/interview/question/list?securityFormId=fd64171d87df8d4brhV939i5&source=1&positionCode=100208,100901,100903&sortType=1&type=1&page={current_index}&_t=1747834442989%20HTTP/1.1'
#     res = requests.get(url, headers=headers)
#
#     list = res.json().get('zpData').get('list')
#     for item in list:
#         print(item.get('questionInfo').get('content'))
#         title = item.get('questionInfo').get('content')
#         with open("result.txt", "a", encoding="utf-8") as f:
#             f.write(title + "\n")
#     current_index += 1


import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
from sklearn.pipeline import make_pipeline
import re
from pathlib import Path
# 1. 定义分类标签和关键词库
categories = {
    'JavaScript': ['JS', 'JavaScript', 'Promise', 'var', 'let', 'null', '内存泄漏', '事件流', '数字精度'],
    '浏览器': ['渲染过程', 'history模式', '服务器支持', 'DOM', 'CSSOM'],
    'Vue.js': ['Vue', '组件通信', '生命周期', 'Vuex', 'provide/inject'],
    'React': ['React'],
    'CSS': ['CSS', '选择器', '布局', '样式'],
    '网络': ['AJAX', 'axios', 'HTTP', '跨域', 'fetch'],
    'ES6+': ['ES6', 'Module', 'Iterator', '箭头函数', '解构赋值']
}


# 2. 关键词匹配分类函数
def keyword_based_classification(question):
    for category, keywords in categories.items():
        if any(keyword in question for keyword in keywords):
            return category
    return '其他'


# 3. 准备训练数据
questions = [
    "为什么要用 AJAX",
    "开发过程中遇到内存泄露的情况，该如何解决",
    "为什么 history 模式需要服务器支持",
    "ES6 中有了 var 为什么还要用 let",
    "JS 脚本延迟加载的方式有哪些",
    "ES6 中的 Module 和 CommonJS 模块有什么区别",
    "Vue 组件通信有哪些方式",
    "说说你对 Vue 生命周期的理解",
    "JS 的事件流模型有哪些",
    "简述浏览器渲染过程",
    "promise 中常用的方法有哪些",
    "说一下 CSS 选择器有哪些",
    "为什么 typeof null 是 Object",
    "说说 axios 的特点有哪些",
    "Vue 中常规的通信方案有哪些",
    "ES6 中的 Iterator 是什么，有什么作用",
    "说说 JS 数字精度丢失的问题，如何解决"
]

# 手动标注的分类结果（实际应用中需要更多数据）
labels = [
    "网络", "JavaScript", "浏览器", "ES6+", "JavaScript",
    "ES6+", "Vue.js", "Vue.js", "JavaScript", "浏览器",
    "JavaScript", "CSS", "JavaScript", "网络", "Vue.js",
    "ES6+", "JavaScript"
]

# 4. 创建机器学习分类模型
df = pd.DataFrame({'question': questions, 'category': labels})


# 数据预处理函数
def preprocess_text(text):
    text = text.lower()  # 转换为小写
    text = re.sub(r'[^\w\s]', '', text)  # 移除标点符号
    return text


df['question'] = df['question'].apply(preprocess_text)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    df['question'], df['category'], test_size=0.2, random_state=42
)

# 创建分类流水线
model = make_pipeline(
    TfidfVectorizer(stop_words=None),  # 中文可能不需要停用词
    MultinomialNB()
)

# 训练模型
model.fit(X_train, y_train)

# 评估模型
y_pred = model.predict(X_test)
print("模型评估报告：")
print(classification_report(y_test, y_pred))


# 5. 综合分类函数：先关键词匹配，再模型分类
def classify_question(question):
    # 先尝试关键词匹配
    keyword_category = keyword_based_classification(question)
    if keyword_category != '其他':
        return keyword_category

    # 关键词匹配失败时使用模型分类
    processed_question = preprocess_text(question)
    return model.predict([processed_question])[0]


# 6. 测试分类器
with open('result.txt', 'r', encoding='utf-8') as f:
    new_questions = f.readlines()

print("\n分类结果示例：")
for q in new_questions:
    Path(classify_question(q)).mkdir(parents=True, exist_ok=True)
    with open(f'{classify_question(q)}/result.txt', 'a', encoding='utf-8') as f:
        f.write(q + '\n')
    print(f"问题：{q} → 分类：{classify_question(q)}")

