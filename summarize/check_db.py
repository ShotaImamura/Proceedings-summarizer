import sqlite3

def view_db_contents(db_name):
    # データベースに接続
    conn = sqlite3.connect(db_name)

    # カーソルを取得
    cursor = conn.cursor()

    # データベース内のすべてのテーブル名を取得
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # 各テーブルの内容を表示

    # 各テーブルのレコード数を表示
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
        count = cursor.fetchone()[0]
        print(f"Table: {table[0]}")
        print(f"Number of records: {count}")

    """#20件に制限して各テーブルの内容を表示
    tables = tables[:10]
    for table in tables:
        print(f"Table: {table[0]}")
        cursor.execute(f"SELECT * FROM {table[0]};")
        rows = cursor.fetchall()
        for row in rows:
            print(row)"""

    # 接続を閉じる
    conn.close()

# 使用例
database_path = 'summaries.db'
view_db_contents(database_path)