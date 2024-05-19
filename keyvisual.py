from PIL import Image
import glob
import os
import shutil
import fitz
import time


def get_unique_colors(image_path):
    image = Image.open(image_path).convert("RGBA")
    return len(set(image.getdata()))

def compare_and_select_key_visual(imgdir):
    first_image_path = os.path.join(imgdir, "first_image.png")
    first_page_half_path = os.path.join(imgdir, "first_page_half.png")

    if not os.path.exists(first_image_path):
        if not os.path.exists(first_page_half_path):
            print(f"Either first_image.png or first_page_half.png does not exist in {imgdir}")
            return
        else:
            #first_page_half.pngをkey_visual.pngにコピー
            shutil.copy(first_page_half_path, os.path.join(imgdir, "key_visual.png"))
            return

    unique_colors_first_image = get_unique_colors(first_image_path)
    unique_colors_first_page_half = get_unique_colors(first_page_half_path)

    key_visual_path = os.path.join(imgdir, "key_visual.png")

    if unique_colors_first_image > unique_colors_first_page_half:
        shutil.copy(first_image_path, key_visual_path)
    else:
        shutil.copy(first_page_half_path, key_visual_path)

    return




def recoverpix(doc, item):
    xref = item[0]
    smask = item[1]
    if smask > 0:
        pix0 = fitz.Pixmap(doc.extract_image(xref)["image"])
        if pix0.alpha:
            pix0 = fitz.Pixmap(pix0, 0)
        mask = fitz.Pixmap(doc.extract_image(smask)["image"])
        try:
            pix = fitz.Pixmap(pix0, mask)
        except:
            pix = fitz.Pixmap(doc.extract_image(xref)["image"])
        if pix0.n > 3:
            ext = "pam"
        else:
            ext = "png"
        return {"ext": ext, "colorspace": pix.colorspace.n, "image": pix.tobytes(ext)}


def extract_first_image_from_pdf(pdf_path, imgdir):
    doc = fitz.open(pdf_path)
    first_image_extracted = False
    for pno in range(len(doc)):
        imglist = doc.get_page_images(pno)
        for img in imglist:
            xref = img[0]
            try:
                img_obj = recoverpix(doc, img)
                if img_obj is None:
                    continue
                img_data = img_obj["image"]
                if img_data is None:
                    continue

                img_ext = img_obj["ext"]
                img_name = f"first_image.{img_ext}"
                img_file_path = os.path.join(imgdir, img_name)

                with open(img_file_path, "wb") as f_out:
                    f_out.write(img_data)
                first_image_extracted = True
                break  # Break the inner loop after the first image is saved
            except Exception as e:
                print(f"Error extracting image: {e}")
                continue
        if first_image_extracted:
            break  # Break the outer loop if an image has already been saved

    if not first_image_extracted:
        # If no image is extracted successfully, use the fallback image if it exists
        fallback_image_path = os.path.join(imgdir, "first_page_half.png")
        if os.path.exists(fallback_image_path):
            key_visual_path = os.path.join(imgdir, "key_visual.png")
            shutil.copy(fallback_image_path, key_visual_path)



# フォルダリストを取得（同一階層にあるdataディレクトリ以下のディレクトリを取得）
dirs = glob.glob("data/*")

# 全体のdir数
num_dirs = len(dirs)
counter = 0

for dir in dirs:

    # dirのpaper.pdfを取得
    pdf_path = os.path.join(dir, "paper.pdf")

    # dir内にkey_visual.pngが存在する場合はスキップ
    if os.path.exists(os.path.join(dir, "key_visual.png")):
        counter += 1
        print(f"Processed {counter}/{num_dirs} directories")

        continue

    # extract_first_image_from_pdfを実行
    extract_first_image_from_pdf(pdf_path, dir)

    compare_and_select_key_visual(dir)

    counter += 1

    print(f"Processed {counter}/{num_dirs} directories")
