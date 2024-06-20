# 基础环境
import os
import sys
import fire
import shutil
import comet_ml
import pandas as pd
from tqdm import tqdm
from icecream import ic
from datetime import datetime
from pathlib import PurePath, Path
from PIL import Image, ImageDraw

FILE = Path(__file__).resolve()
ROOT = str(FILE.parents[1])
ic(ROOT)

# 初始化paddle ocr
from paddleocr import PaddleOCR
# paddle_ocr_model_path = ROOT + "/weights/paddle_ocr/ch_PP-OCRv4_det_server_infer/"

#ocr = PaddleOCR(use_angle_cls=True, lang="ch", det_model_dir=paddle_ocr_model_path)
paddle_ocr_model_det_path = ROOT + "/weights/paddle_ocr/ch_PP-OCRv4_det_infer/"
paddle_ocr_model_rec_path = ROOT + "/weights/paddle_ocr/ch_PP-OCRv4_rec_infer/"

ocr = PaddleOCR(use_angle_cls=True, lang='ch',det_model_dir= paddle_ocr_model_det_path,rec_model_dir=paddle_ocr_model_rec_path
               ,table=False,drop_score=0.1,binarize=True,use_gpu=True)



# 识别图片文件后缀
def get_file_extension_in_dir(dir_path: str, file_name: str):
    for file in os.listdir(dir_path):
        name, extension = os.path.splitext(file)
        if name == file_name:
            return extension
    return None

# 读取结构识别结果
def read_structure_data(dir : str):
    struct_data = pd.read_csv(os.path.join(dir, "recognized.csv"), header=0)
    return struct_data

def paddle_ocr(image_path):
    result = ocr.ocr(image_path, cls=True)
    ocr_result = []
    for idx in range(len(result)):
        res = result[idx]
        if res:
            for line in res:
                ocr_result.append(line[1][0])
    return "".join(ocr_result)

def create_cell_img(dir : str):
    # 刷新结果目录
    crop_ocr_dir = os.path.join(dir, "ocr")
    if os.path.exists(crop_ocr_dir):
        shutil.rmtree(crop_ocr_dir)
    os.makedirs(crop_ocr_dir)

    # 数据读取
    df = read_structure_data(dir)
    img_ext = get_file_extension_in_dir(dir, "origin")
    img = Image.open(os.path.join(dir, "origin" + img_ext))

    # 组织结构并在横纵方向排序
    # fixme: 这里是按网格处理，没有真正拿到实际表格结构
    cols = []
    rows = []        
    for idx, box in df.iterrows():
        if box['labels'] == 1:
            cols.append([box["box0"], box["box1"], box["box2"], box["box3"]])
        if box['labels'] == 2:
            rows.append([box["box0"], box["box1"], box["box2"], box["box3"]])
    sorted_cols = sorted(cols, key=lambda x: x[0])
    sorted_rows = sorted(rows, key=lambda x: x[1])

    for row_index, row in enumerate(sorted_rows):
        for col_index, col in enumerate(sorted_cols):
            rect = [int(col[0]), int(row[1]), int(col[2]), int(row[3])]
            cell_image = img.crop(rect)
            cell_image_path = f'{crop_ocr_dir}/cell_{row_index}_{col_index}{img_ext}'
            cell_image.save(cell_image_path)

def ocr_cells(dir : str):
    cell_ocr_dir = os.path.join(dir, "ocr")
    cell_files = os.listdir(cell_ocr_dir)
    if "ocr.xlsx" in cell_files:
        cell_files.remove("ocr.xlsx")

    max_x, max_y = 0, 0
    for file in cell_files:
        cell_name = file.split(".")[0]
        x, y = [int(_) for _ in cell_name.split("_")[1:]]
        max_x = max(x, max_x)
        max_y = max(y, max_y)

    ocr_result = [["" for _ in range(max_y + 1)] for _ in range(max_x + 1)]
    for file in cell_files:
        cell_name = file.split(".")[0]
        x, y = [int(_) for _ in cell_name.split("_")[1:]]
        
        cell_img_dir = os.path.join(cell_ocr_dir, file)
        cell_text = paddle_ocr(cell_img_dir)
        ocr_result[x][y] = cell_text

    df = pd.DataFrame(ocr_result)
    excel_path = os.path.join(cell_ocr_dir, "ocr.xlsx")
    df.to_excel(excel_path, index=False)

def ocr_page(page_dir : str):
    # 重建目标文件夹
    ocr_dir = os.path.join(page_dir, "ocr")
    if os.path.exists(ocr_dir):
        shutil.rmtree(ocr_dir)
    os.makedirs(ocr_dir)

    # 遍历目标crop目录处理
    recognize_dir = os.path.join(page_dir, "recognize")
    crop_names = os.listdir(recognize_dir)
    
    for crop_name in crop_names:
        crop_dir = os.path.join(recognize_dir, crop_name)
        create_cell_img(crop_dir)
        ocr_cells(crop_dir)
        shutil.move(os.path.join(crop_dir, "ocr"),
                    os.path.join(page_dir, "ocr", crop_name))

def ocr_pages(dir : str):
    print("Running OCR ...")

    page_names = os.listdir(dir)
    for page_name in tqdm(page_names):
        ic(page_name)
        ocr_page(os.path.join(dir, page_name))


def main(dir : str):
    ocr_pages(dir)

if __name__ == "__main__":
    fire.Fire(main)