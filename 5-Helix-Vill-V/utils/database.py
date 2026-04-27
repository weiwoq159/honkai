import sqlite3

class HelixDatabase:
    def __init__(self):
        try:
            # 尝试连接到 SQLite 数据库
            self.conn = sqlite3.connect('../data.db')
            self.cursor = self.conn.cursor()
            # 创建必要的表
            self._create_all_tables()
        except sqlite3.OperationalError as e:
            # 处理数据库连接错误
            print(f"数据库连接错误: {e}")
            self.conn = None

    def __del__(self):
        # 确保数据库连接在对象销毁时关闭
        if self.conn:
            self.conn.close()

    def _create_all_tables(self):
        # 调用创建用户详情表和作品表的方法
        self.create_user_detail_table()
        self.create_REDnote_list()
        # self.create_work_table()
        # self.create_weibo_user_detail_table()
        # self.create_weibo_blog_list_table()


    def create_user_detail_table(self):
        # 创建用户详情表的 SQL 语句
        sql = """
            CREATE TABLE IF NOT EXISTS users_table (
                username TEXT PRIMARY KEY,   -- 直接以用户名作为主键
                TikTok_id TEXT,       -- 其他ID作为唯一字段
                MicroBlog_id TEXT,
                REDnote_id TEXT
            );
        """
        self._execute_sql(sql)

    def upsert_user_details(self, username, TikTok_id=None, MicroBlog_id=None, REDnote_id=None):
        # 步骤1: 查询用户是否存在
        query = "SELECT rowid FROM users_table WHERE username = ?"
        result = self._execute_sql(query, (username,))

        if result:  # 用户存在，执行增量更新
            # 构建动态SET子句和参数列表
            set_clauses = []
            params = []

            if TikTok_id is not None:
                set_clauses.append("TikTok_id = ?")
                params.append(TikTok_id)
            if MicroBlog_id is not None:
                set_clauses.append("MicroBlog_id = ?")
                params.append(MicroBlog_id)
            if REDnote_id is not None:
                set_clauses.append("REDnote_id = ?")
                params.append(REDnote_id)

            # 如果没有提供任何ID参数，直接返回
            if not set_clauses:
                return

            # 构建完整的UPDATE语句
            set_clause = ", ".join(set_clauses)
            sql = f"UPDATE users_table SET {set_clause} WHERE username = ?"
            params.append(username)  # 最后一个参数是WHERE条件

            self._execute_sql(sql, params)

        else:  # 用户不存在，插入新记录
            sql = """
                  INSERT INTO users_table
                      (username, TikTok_id, MicroBlog_id, REDnote_id)
                  VALUES (?, ?, ?, ?) \
                  """
            self._execute_sql(sql, (username, TikTok_id, MicroBlog_id, REDnote_id))


    def create_REDnote_list(self):
        sql = """
            CREATE TABLE IF NOT EXISTS rednote_list (
                node_id INTEGER PRIMARY KEY,
                title TEXT,
                user_id INTEGER NOT NULL,
                desc TEXT NOT NULL,
                create_time INTEGER NOT NULL,
                url TEXT NOT NULL,
                type TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users_table (REDnote_id)
                    ON DELETE CASCADE
                    ON UPDATE RESTRICT,
                UNIQUE (user_id, desc)
            );
        """
        self._execute_sql(sql)
    def insert_Rednote_list(self, node_id, title, user_id, desc, create_time, url, note_type):
        print(id, title, user_id, desc, create_time, url, type)
        sql = """
            INSERT INTO rednote_list (node_id, title, user_id, desc, create_time, url, note_type) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self._execute_sql(sql, ( node_id, title, user_id, desc, create_time, url, note_type))

    # def create_user_detail_table(self):
    #     # 创建用户详情表的 SQL 语句
    #     sql = """
    #         CREATE TABLE IF NOT EXISTS users (
    #             tiktok_id TEXT PRIMARY KEY,
    #             weibo_id TEXT,
    #             redNote_id TEXT,
    #             username TEXT UNIQUE NOT NULL
    #         );
    #     """
    #     self._execute_sql(sql)
    #
    # def add_user(self, user_name, user_id):
    #     print(user_name, user_id)
    #     # 插入用户的 SQL 语句
    #     sql = "INSERT INTO users (id, username) VALUES (?, ?)"
    #     return self._execute_sql(sql, (user_id, user_name))
    #
    # def select_user_name_by_id(self, user_id):
    #     sql = "SELECT username FROM users WHERE id = ?"
    #     return self._execute_sql(sql, (user_id,))
    #
    # def create_work_table(self):
    #     # 创建作品表的 SQL 语句
    #     sql = """
    #         CREATE TABLE IF NOT EXISTS aweme_list (
    #             id INTEGER PRIMARY KEY,
    #             user_id INTEGER NOT NULL,
    #             desc TEXT NOT NULL,
    #             create_time INTEGER NOT NULL,
    #             url TEXT NOT NULL,
    #             type TEXT NOT NULL,
    #             FOREIGN KEY (user_id) REFERENCES users (id)
    #                 ON DELETE CASCADE
    #                 ON UPDATE RESTRICT,
    #             UNIQUE (user_id, desc)
    #         );
    #     """
    #     self._execute_sql(sql)
    #
    # def insert_aweme_item(self, id, user_id, desc, create_time, url, type):
    #     # 插入作品项的 SQL 语句
    #     sql = "INSERT INTO aweme_list (id, user_id, desc, create_time, url, type) VALUES (?, ?, ?, ?, ?, ?)"
    #     return self._execute_sql(sql, (id, user_id, desc, create_time, url, type))
    #
    # def select_aweme_item(self, id):
    #     sql = "SELECT * FROM aweme_list WHERE id = ?"
    #     return self._execute_sql(sql, (id, ))
    #
    # def select_aweme_list(self, user_id):
    #     sql = "SELECT * FROM aweme_list WHERE user_id = ? ORDER BY create_time DESC;"
    #     return self._execute_sql(sql, (user_id, ))
    #
    # # 微博用户表创建
    # def create_weibo_user_detail_table(self):
    #     # 创建用户详情表的 SQL 语句
    #     sql = """
    #         CREATE TABLE IF NOT EXISTS weibo_user_detail (
    #             uid INTEGER PRIMARY KEY,
    #             screen_name TEXT UNIQUE NOT NULL
    #         );
    #     """
    #     self._execute_sql(sql)
    # # 微博用户表新增
    # def add_weibo_user(self, uid, screen_name):
    #     sql = "INSERT INTO weibo_user_detail (uid, screen_name) VALUES (?, ?)"
    #     return self._execute_sql(sql, (uid, screen_name))
    #
    # # 微博用户表查询
    # def select_weibo_user_name_by_id(self, uid):
    #     sql = "SELECT screen_name FROM users WHERE uid = ?"
    #     return self._execute_sql(sql, (uid,))
    # #微博文章列表
    # def create_weibo_blog_list_table(self):
    #     sql = """
    #         CREATE TABLE IF NOT EXISTS blog_list (
    #             id INTEGER PRIMARY KEY,
    #             uid INTEGER NOT NULL,
    #             text_raw TEXT NOT NULL,
    #             created_at INTEGER NOT NULL,
    #             image_list TEXT NOT NULL,
    #             FOREIGN KEY (uid) REFERENCES users (uid)
    #                 ON DELETE CASCADE
    #                 ON UPDATE RESTRICT,
    #             UNIQUE (uid, text_raw)
    #         );
    #     """
    #     self._execute_sql(sql)
    #
    # def insert_weibo_blog_item(self, id, uid, created_at, image_list, text_raw):
    #     # 插入作品项的 SQL 语句
    #     sql = "INSERT INTO blog_list (id, uid, created_at, image_list, text_raw) VALUES (?, ?, ?, ?, ?)"
    #     return self._execute_sql(sql, (id, uid, created_at, image_list, text_raw))
    #
    # def select_weibo_blog_list_item(self, id):
    #     sql = "SELECT * FROM blog_list WHERE id = ?"
    #     return self._execute_sql(sql, (id, ))
    #
    # def select_weibo_blog_list_by_uid(self, user_id):
    #     sql = "SELECT * FROM blog_list WHERE uid = ? ORDER BY created_at DESC;"
    #     return self._execute_sql(sql, (user_id, ))
    # def select_weibo_blog_item_by_uid(self, user_id, title):
    #     sql = "SELECT * FROM blog_list WHERE uid = ? AND  text_raw LIKE ? ORDER BY created_at DESC;"
    #     return self._execute_sql(sql, (user_id, title ))





    def _execute_sql(self, sql, params=None):
        """执行 SQL 语句并处理异常"""
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            # 对于 SELECT 语句，使用 fetchall 获取查询结果
            if sql.strip().upper().startswith('SELECT'):
                result = self.cursor.fetchall()
            else:
                self.conn.commit()
                result = True
            return result
        except sqlite3.Error as e:
            # 处理 SQL 执行错误
            print(f"SQL 执行错误: {e}")
            self.conn.rollback()
            return False