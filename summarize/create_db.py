# coding=UTF-8
import openai
import os
import concurrent.futures
import time
import fitz  # PyMuPDF to extract text from PDF
import sqlite3
import openai
import concurrent.futures
import threading
import time

# Set the OpenAI API key from the environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# グローバルイベントオブジェクト
pause_new_threads_event = threading.Event()

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file using PyMuPDF. 2ページに限定"""
    doc = fitz.open(pdf_path)
    text = ""
    # 最初の２ページのみを抽出
    for page_num in range(2):
        page = doc.load_page(page_num)
        text += page.get_text()
    
    doc.close()
    return text

def get_summary_from_openai(text_content, path):
    """Sends text to the OpenAI Completion API and gets a summary based on detailed requirements."""
    detailed_prompt = (
        f"このPDFに関して、以下の項目について、抽出もしくは翻訳や要約をして、まとめてください。各項目はそれぞれについている制約条件（文字数制限や言語、カンマ区切りなどの形式）を遵守してください。また、概要も省略せず抽出してください。概要や要約では引用符は使用しないでください。万が一概要中にダブルクオテーションがあれば、誤動作の原因になるので、シングルクオテーションに置き換えてください。なお、ダブルクオテーションとカンマのセットで項目を切り分けているので、形式は死守してください。\n"
        "```\n"
        "[\"タイトル（英語）\", \"タイトル（日本語）\", \"著者A, 著者B, 著者C\", \"2022（出版年）\", \"学会/ジャーナル/データベース\", \"10.1145/3544548.3581008（DOI）\", \"サマリー（英語 50ワード以内）\", \"サマリー（日本語 80字以内）\", \"概要（原文）\", \"キーワード（日本語）A, B, C\", \"課題（日本語 180字以内）\", \"手法（日本語 180字以内）\", \"結果（日本語 180字以内）\", \"キーワード（英語）A, B, C\", \"課題（英語 100字以内）\", \"手法（英語 100字以内）\", \"結果（英語 100字以内）\", \"https://doi.org/10.1145/3544548.3581008(論文リンク)\"]\n"
        "```"
        f"\n\n{text_content}"
    )

    try:
        print("Sending request to OpenAI API...")
        summary = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {'role': 'system', 'content': detailed_prompt},
                {'role': 'user', 'content': text_content}
            ],
            temperature=0.25
        )['choices'][0]['message']['content']
        return summary
    except Exception as e:
        print(f"Error in OpenAI API call: {e}")

        # error{timestamp}_openai.txtとしてエラー内容を出力
        error_path = "./summarize/error/"
        os.makedirs(error_path, exist_ok=True)

        # 10秒間新規のスレッドを作成しないようにする
        pause_new_threads_event.set()

        with open(os.path.join(error_path, f"error{time.time()}_openai.txt"), 'w') as f:
            f.write(f"Path: {path}\n\n")
            f.write(f"Error in OpenAI API call: {e}\n\n")
            f.write(f"Text content: {text_content}\n\n")

        return None

def process_single_pdf(path, db_path):
    conn = create_connection(db_path)
    create_table(conn)

    key_visual_url = path + "/key_visual.png"
    pdf_path = os.path.join(path, "paper.pdf")
    if os.path.isfile(pdf_path):
        print("Processing: ", pdf_path)
        text_content = extract_text_from_pdf(pdf_path)
        print("calling get_summary_from_openai")

        summary = get_summary_from_openai(text_content, path)
        if summary:
            
            summary_list = summary.strip('[]').split('", "')  # Split the summary into a list
            # 先頭と末尾の"を削除
            summary_list[0] = summary_list[0].replace('"', '')
            summary_list[-1] = summary_list[-1].replace('"', '')

            summary_list.append(key_visual_url)

            # 挿入時にトラブルが起きたら、例外処理としてerrorファイルを出力（errorフォルダ以下）
            try:
                insert_summary(conn, tuple(summary_list))
                print("Data {} inserted successfully.".format(path))
            except Exception as e:
                print("Error in inserting data: ", e)
                error_path = "error/"
                os.makedirs(error_path, exist_ok=True)
                # error{timestamp}_inserting.txtとしてエラー内容を出力
                with open(os.path.join(error_path, f"error{time.time()}_inserting_{path}.txt"), 'w') as f:
                    # fasiss_index, パス名, error出力とsummary_listの内容を出力
                    f.write(f"Path: {path}\n\n")
                    f.write(f"Error in inserting data: {e}\n\n")
                    f.write(f"Summary list: {summary}\n\n")

    conn.close()

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return conn

def create_table(conn):
    """ create a table to store PDF summaries """
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS pdf_summaries (
                id INTEGER PRIMARY KEY,
                english_title TEXT,
                japanese_title TEXT,
                authors TEXT,
                publication_year TEXT,
                conference TEXT,
                doi TEXT,
                summary_english TEXT,
                summary_japanese TEXT,
                full_abstract TEXT,
                keywords_japanese TEXT,
                problem_japanese TEXT,
                method_japanese TEXT,
                results_japanese TEXT,
                keywords_english TEXT,
                problem_english TEXT,
                method_english TEXT,
                results_english TEXT,
                paper_link TEXT,
                key_visual_url TEXT
            );
        ''')
        conn.commit()
    except Exception as e:
        print(e)

def insert_summary(conn, summary_data):
    summary_data_tuple = tuple(summary_data)
    """ Insert a new row into the pdf_summaries table """
    sql = ''' INSERT INTO pdf_summaries(english_title, japanese_title, authors, publication_year, conference, doi,
              summary_english, summary_japanese, full_abstract, keywords_japanese, problem_japanese, method_japanese,
              results_japanese, keywords_english, problem_english, method_english, results_english, paper_link, key_visual_url)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, summary_data_tuple)
    conn.commit()
    return cur.lastrowid


def worker_thread(path, db_path):
    process_single_pdf(path, db_path)

def check_key_visual_url_exists(conn, key_visual_url):
    """Check if the given key_visual_url already exists in the database."""
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM pdf_summaries WHERE key_visual_url = ?", (key_visual_url,))
        count = cur.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Error checking key_visual_url: {e}")
        return False

def process_pdf_files(directory, db_path):
    conn = create_connection(db_path)
    create_table(conn)
    count = 0
    print("starting process_pdf_files")
    
    paths = []
    for root, dirs, files in os.walk(directory):
        total = len(dirs)
        for dir in dirs:
            full_path = os.path.join("./data", dir)
            key_visual_url = full_path + "/key_visual.png"
            if not check_key_visual_url_exists(conn, key_visual_url):  # 存在しない場合のみ追加
                
                count += 1
                print("Processing PDF {count}/{total}".format(count=count, total=total))
                
                paths.append(full_path)

            else:
                print(f"Skipping {dir} as it already exists in the database.")
    
    conn.close()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for path in paths:
            # 新規スレッドの生成を一時的にブロック
            if pause_new_threads_event.is_set():
                print("Paused creation of new threads due to rate limit error.")
                time.sleep(10)
                pause_new_threads_event.clear()
            else:
                time.sleep(3)
            future = executor.submit(worker_thread, path, db_path)
            futures.append(future)
            

        concurrent.futures.wait(futures)

if __name__ == "__main__":
    database_path = 'summaries.db'
    process_pdf_files('./data', database_path)
