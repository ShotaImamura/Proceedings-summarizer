import sys
import fitz
import os
#pymupdfを用いて複数の論文をくっつけたPDFの切れ目がどこにあるかを調べる
# 使い方: python parse.py <pdfファイル名>

import re
from PIL import Image
import io

# 非ASCII文字を除去する関数
def remove_non_ascii(text):
    return re.sub(r'[^\x00-\x7F]', '', text)

def get_half(pdf, num):
    
    page = pdf[num]
    # Get the page as a whole image
    mat = fitz.Matrix(2, 2)  # zoom factor 2 in each direction
    pix = page.get_pixmap(matrix=mat)
    # Convert to a PIL Image
    im = Image.open(io.BytesIO(pix.tobytes()))
    # Get the dimensions of the image
    width, height = im.size
    # Define the box for the upper half (left, upper, right, lower)
    box = (0, height // 20, width, (height // 2) + (height // 20))

    # Crop the image to this box
    im_cropped = im.crop(box)
    return im_cropped


def main():
    if len(sys.argv) != 2:
        print("Usage: python parse.py <pdf file name>")
        return

    pdf = fitz.open(sys.argv[1])
    print("pages: %d" % pdf.page_count)
    page_start = None
    page_end = None
    for i in range(pdf.page_count):
        page = pdf.load_page(i)
        text = page.get_text("text")
        
        if "ABSTRACT" in text or i == pdf.page_count-1:
            if page_start == None:
                page_start = i
            elif (page_start != None and page_end == None):
                print("page_start: {}".format(page_start))    
                page_end = i-1
                print(page_end)
                print("page_end: {}".format(page_end))
                #page_startの最初の二行のテキストを一行にまとめる
                page = pdf.load_page(page_start)
                text = page.get_text("text")
                text_list = text.split("\n")

                #各行にテキストがあるかどうかを確認し、テキストのある最初と次の行を取り出す
                for k in range(len(text_list)):
                    
                    if re.search(r"[a-zA-Z]",text_list[k]) != None:
                        title = text_list[k] + text_list[k+1]
                        title = remove_non_ascii(title)
                        break
                print(title)
                

                #titleの名前でdata以下にディレクトリを作成する
                if not os.path.exists("data"):
                    os.makedirs("data")
                if not os.path.exists("data/{}".format(page_start)):
                    os.makedirs("data/{}".format(page_start),exist_ok=True)
 
                #page_startからpage_endまでをPDFとして保存する
                if page_end != None:
                    pdf_new = fitz.open()
                    try:
                        pdf_new.insert_pdf(pdf,from_page=page_start,to_page=page_end)
                    
                        pdf_new.save("data/{}/paper.pdf".format(page_start))
                    except:
                        pass
                    pdf_new = None
                else:
                    print("page_start, end_error: {}".format(page_start))

                #textをfirst_page_text.txtとして保存する
                with open("data/{}/first_page_text.txt".format(page_start),"w") as f:
                    f.write(text)

                #page_startとpage_endをpage.txtとして保存する
                with open("data/{}/page.txt".format(page_start),"w") as f:
                    f.write("{}\n{}".format(page_start,page_end))

                #titleをtitle.txtとして保存する
                with open("data/{}/title.txt".format(page_start),"w") as f:
                    f.write(title)

                img_cropped = get_half(pdf,page_start)
                img_cropped.save("data/{}/first_page_half.png".format(page_start))

                #page_startとpage_endをNoneに戻す
                page_start = i
                page_end = None

            #次にabstractがあるページの直前のページまでをPDFとして保存する
            

            
        

if __name__ == "__main__":
    main()
