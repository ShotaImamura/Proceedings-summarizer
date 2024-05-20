import sqlite3
import fitz  # PyMuPDF
import os

def create_summary_pdfs(database_path, template_path, output_dir='output', language='japanese', split_files=True, papers_per_file=100):
    # データベース接続を開始
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # データベースから情報を取得
    cursor.execute("SELECT english_title, authors, paper_link, key_visual_url, summary_japanese, problem_japanese, method_japanese, results_japanese FROM pdf_summaries")
    summaries = cursor.fetchall()

    # テンプレートPDFを読み込み
    template_pdf = fitz.open(template_path)
    
    # フォントを読み込み
    fontpath = "./summarize/NotoSansJP-VariableFont_wght.ttf"
    fontname = "NotoSansJP"
    
    # 出力ディレクトリが存在しない場合は作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    count = 0
    total = len(summaries)
    file_index = 1

    if split_files:
        while count < total:
            # 新しいPDFドキュメントを作成
            output_pdf = fitz.open()
            
            for i in range(papers_per_file):
                if count >= total:
                    break

                summary = summaries[count]
                english_title, authors, paper_link, key_visual_url, summary_japanese, problem, method, results = summary

                # テンプレートのページを複製して新しいページを作成
                template_page = template_pdf[0]  # テンプレートの最初のページ
                page = output_pdf.new_page(width=template_page.rect.width, height=template_page.rect.height)
                page.show_pdf_page(page.rect, template_pdf, 0)  # テンプレートの内容を新しいページにコピー

                page.insert_font(fontfile=fontpath, fontname=fontname)

                print(f"Title: {english_title}")
                # キービジュアルを挿入（PNG形式を直接使用）
                if os.path.exists(key_visual_url):
                    pixmap = fitz.Pixmap(key_visual_url)
                    # 画像をページサイズに合わせてスケーリング
                    factor = min((400 / pixmap.width), (260 / pixmap.height))  # スケールファクターを計算
                    scaled_width = int(pixmap.width * factor)
                    scaled_height = int(pixmap.height * factor)
                    page.insert_image(fitz.Rect(50, 200, 50 + scaled_width, 200 + scaled_height), pixmap=pixmap)
                else:
                    print(f"Warning: Key visual file not found at {key_visual_url}")

                text_block = f"{english_title}"
                # 60文字ごとに改行、改行が必要な場合はy＝y+20
                title_gap = 0
                if len(text_block) > 90:
                    title_gap = 20

                text_rect = fitz.Rect(40, 40, 850, 90 + title_gap)
                page.insert_text(fitz.Point(40, 90 + title_gap), f"{authors}", fontsize=14, fontname=fontname)
                summary_rect = fitz.Rect(40, 130 + title_gap, 900, 170 + title_gap)

                page.insert_textbox(text_rect, text_block, fontsize=18, fontname=fontname, fontfile=fontpath)
                page.insert_textbox(summary_rect, f"{summary_japanese}", fontsize=14, fontname=fontname, fontfile=fontpath)

                # ペーパーリンクをハイパーリンクとして追加
                link_rect = fitz.Rect(40, 110 + title_gap, 300, 130 + title_gap)  # リンクの範囲を適切に設定
                try:
                    page.insert_text(fitz.Point(40, 110 + title_gap), paper_link, fontsize=14, fontname=fontname, color=(0, 0, 1), fontfile=fontpath)
                    page.insert_link({"from": link_rect, "uri": paper_link})
                except Exception as e:
                    print(f"Failed to insert link: {e}")

                # 課題、手法、結果をテキストボックスとして挿入
                problem_rect = fitz.Rect(470, 190, 920, 290)
                method_rect = fitz.Rect(470, 310, 920, 410)
                results_rect = fitz.Rect(470, 430, 920, 530)

                # 課題、手法、結果のいずれかが100文字を超える場合は、フォントサイズを小さくする
                if len(problem) > 100 or len(method) > 100 or len(results) > 100:
                    fontsize = 12
                else:
                    fontsize = 14
                page.insert_textbox(problem_rect, f"問題:\n{problem}", fontsize=fontsize, fontname=fontname, fontfile=fontpath)
                page.insert_textbox(method_rect, f"手法:\n{method}", fontsize=fontsize, fontname=fontname, fontfile=fontpath)
                page.insert_textbox(results_rect, f"結果:\n{results}", fontsize=fontsize, fontname=fontname, fontfile=fontpath)

                count += 1
                print(f"Processed {count} of {total} summaries")

            # 新しいPDFを保存
            output_path = os.path.join(output_dir, f"summary_japanese_{file_index}_{count-papers_per_file+1}_to_{count}.pdf")
            output_pdf.save(output_path)
            output_pdf.close()
            
            file_index += 1
    else:
        # 全ての要約を一つのPDFファイルにまとめる
        output_pdf = fitz.open()

        for summary in summaries:
            count += 1
            english_title, authors, paper_link, key_visual_url, summary_japanese, problem, method, results = summary

            # テンプレートのページを複製して新しいページを作成
            template_page = template_pdf[0]  # テンプレートの最初のページ
            page = output_pdf.new_page(width=template_page.rect.width, height=template_page.rect.height)
            page.show_pdf_page(page.rect, template_pdf, 0)  # テンプレートの内容を新しいページにコピー

            page.insert_font(fontfile=fontpath, fontname=fontname)

            print(f"Title: {english_title}")
            # キービジュアルを挿入（PNG形式を直接使用）
            if os.path.exists(key_visual_url):
                pixmap = fitz.Pixmap(key_visual_url)
                # 画像をページサイズに合わせてスケーリング
                factor = min((400 / pixmap.width), (260 / pixmap.height))  # スケールファクターを計算
                scaled_width = int(pixmap.width * factor)
                scaled_height = int(pixmap.height * factor)
                page.insert_image(fitz.Rect(50, 200, 50 + scaled_width, 200 + scaled_height), pixmap=pixmap)
            else:
                print(f"Warning: Key visual file not found at {key_visual_url}")

            text_block = f"{english_title}"
            # 60文字ごとに改行、改行が必要な場合はy＝y+20
            title_gap = 0
            if len(text_block) > 90:
                title_gap = 20

            text_rect = fitz.Rect(40, 40, 850, 90 + title_gap)
            page.insert_text(fitz.Point(40, 90 + title_gap), f"{authors}", fontsize=14, fontname=fontname)
            summary_rect = fitz.Rect(40, 130 + title_gap, 900, 170 + title_gap)

            page.insert_textbox(text_rect, text_block, fontsize=18, fontname=fontname, fontfile=fontpath)
            page.insert_textbox(summary_rect, f"{summary_japanese}", fontsize=14, fontname=fontname, fontfile=fontpath)

            # ペーパーリンクをハイパーリンクとして追加
            link_rect = fitz.Rect(40, 110 + title_gap, 300, 130 + title_gap)  # リンクの範囲を適切に設定
            try:
                page.insert_text(fitz.Point(40, 110 + title_gap), paper_link, fontsize=14, fontname=fontname, color=(0, 0, 1), fontfile=fontpath)
                page.insert_link({"from": link_rect, "uri": paper_link})
            except Exception as e:
                print(f"Failed to insert link: {e}")

            # 課題、手法、結果をテキストボックスとして挿入
            problem_rect = fitz.Rect(470, 190, 920, 290)
            method_rect = fitz.Rect(470, 310, 920, 410)
            results_rect = fitz.Rect(470, 430, 920, 530)

            # 課題、手法、結果のいずれかが100文字を超える場合は、フォントサイズを小さくする
            if len(problem) > 100 or len(method) > 100 or len(results) > 100:
                fontsize = 12
            else:
                fontsize = 14
            page.insert_textbox(problem_rect, f"問題:\n{problem}", fontsize=fontsize, fontname=fontname, fontfile=fontpath)
            page.insert_textbox(method_rect, f"手法:\n{method}", fontsize=fontsize, fontname=fontname, fontfile=fontpath)
            page.insert_textbox(results_rect, f"結果:\n{results}", fontsize=fontsize, fontname=fontname, fontfile=fontpath)

            print(f"Processed {count} of {total} summaries")

        # 新しいPDFを保存
        output_path = os.path.join(output_dir, 'summary_japanese_all.pdf')
        output_pdf.save(output_path)
        output_pdf.close()

    template_pdf.close()
    conn.close()

# 使用例
create_summary_pdfs('summaries.db', 'template.pdf', 'output', split_files=True, papers_per_file=100)  # 分割する場合
create_summary_pdfs('summaries.db', 'template.pdf', 'output', split_files=False)  # 分割しない場合
