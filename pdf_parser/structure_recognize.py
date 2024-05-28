# 基础环境
import os
import sys
import fire
import shutil
import comet_ml
from tqdm import tqdm
from icecream import ic
from datetime import datetime
from pathlib import PurePath, Path

FILE = Path(__file__).resolve()
ROOT = str(FILE.parents[1])
ic(ROOT)

# 初始化结构识别工具
import torch
import pandas as pd
from PIL import Image, ImageDraw
from transformers import AutoImageProcessor
from transformers import DetrFeatureExtractor
from transformers import TableTransformerForObjectDetection
structure_model = TableTransformerForObjectDetection.from_pretrained(ROOT + "/weights/table_transformer/table-transformer-structure-recognition-v1.1-all")
feature_extractor = DetrFeatureExtractor()

# 常量数据和辅助函数
label_types = [
    "Bracket_Need_Type1",
    "Bracket_Need_Type2",
    "Bracket_Need_Type3",
    "Bracket_Abort_Type1",
    "Bracket_Abort_Type2",
    "Pipe_Need_Type1",
    "Pipe_Abort_Type1"
]

required_labels = [
    "Bracket_Need_Type1",
    "Bracket_Need_Type2",
    "Bracket_Need_Type3",
    "Pipe_Need_Type1",
]

# 识别图片文件后缀
def get_file_extension_in_dir(dir_path: str, file_name: str):
    for file in os.listdir(dir_path):
        name, extension = os.path.splitext(file)
        if name == file_name:
            return extension
    return None

# 读取detect标记数据
def get_labeled_data(label_path : str):
    data = pd.read_csv(label_path, header=None, sep=" ", names=["label_id", "x", "y", "w", "h", "conf"])
    return data

# 截取识别的图片
def get_crops(dir : str):
    # 删除原有的文件夹
    crop_dir = os.path.join(dir, "crops")
    if os.path.exists(crop_dir):
        shutil.rmtree(crop_dir)
    os.makedirs(crop_dir)

    # 读取图片数据
    img_ext = get_file_extension_in_dir(os.path.join(dir, "detect"), "origin")
    img_path = os.path.join(dir, f"detect/origin{img_ext}")
    img = Image.open(img_path)
    img_w, img_y = img.size

    # 读取标记数据
    label_path = os.path.join(dir, "detect/labels.txt")
    label_data = get_labeled_data(label_path)

    # 遍历识别子图
    for idx, row in label_data.iterrows():
        label_id, x, y, w, h = row["label_id"], row["x"], row["y"], row["w"], row["h"]
        label_name = label_types[int(label_id)]

        # 跳过不需要的标记
        if label_name not in required_labels:
            continue

        # 截图
        crop = img.crop(((x - 0.5 * w) * img_w,
                         (y - 0.5 * h) * img_y,
                         (x + 0.5 * w) * img_w,
                         (y + 0.5 * h) * img_y))
        # crop.save(os.path.join(crop_dir, f"{label_name}-{idx}.{img_ext}"))
        crop.save(os.path.join(crop_dir, f"{label_name}-{idx}.png"))

# 对截取图片进行结构识别
def structure_recognition(dir : str):    
    # 重建recognize文件夹
    recognize_dir = os.path.join(dir, "recognize")
    if os.path.exists(recognize_dir):
        shutil.rmtree(recognize_dir)
    os.makedirs(recognize_dir)

    # 读取图片数据
    crop_dir = os.path.join(dir, "crops")
    crop_files = os.listdir(crop_dir)
    crop_names = [file.split(".")[0] for file in crop_files]
    crops = [Image.open(os.path.join(crop_dir, file)).convert("RGB") for file in crop_files]

    for crop_idx in range(len(crops)):
        crop_name = crop_names[crop_idx]
        crop_img = crops[crop_idx]

        # 创建识别结果目录
        crop_recognize_dir = os.path.join(recognize_dir, crop_name)
        os.makedirs(crop_recognize_dir)

        # 执行结构识别
        encoding = feature_extractor(images=crop_img, return_tensors="pt")
        with torch.no_grad():
            outputs = structure_model(**encoding)
        target_sizes = [crop_img.size[::-1]]
        results = feature_extractor.post_process_object_detection(outputs,
                                                                  threshold = 0.5,
                                                                  target_sizes=target_sizes)[0]
        
        # 调整结果格式
        recognized = {}
        recognized["scores"] = results["scores"].tolist()
        recognized["labels"] = results["labels"].tolist()

        boxes = results["boxes"].tolist()
        recognized["box0"] = [box[0] for box in boxes]
        recognized["box1"] = [box[1] for box in boxes]
        recognized["box2"] = [box[2] for box in boxes]
        recognized["box3"] = [box[3] for box in boxes]

        # 保存结果
        recognized_df = pd.DataFrame(recognized)
        recognized_df.to_csv(os.path.join(crop_recognize_dir, "recognized.csv"), index=False)

        # 绘制并保存识别结果
        mark_img = crop_img.copy()
        draw = ImageDraw.Draw(mark_img)
        for i in range(len(results["boxes"])):
            box = [int(_) for _ in results["boxes"][i].tolist()]
            draw.rectangle(box, outline="red", width=2)
        mark_img.save(os.path.join(crop_recognize_dir, "marked.jpg"))
        crop_img.save(os.path.join(crop_recognize_dir, "origin.jpg"))

# 识别图片结构
def recognize(dir : str):
    print("Running structure recognition ...")

    page_names = os.listdir(dir)
    for page_name in tqdm(page_names):
        page_dir = os.path.join(dir, page_name)
        get_crops(page_dir)
        structure_recognition(page_dir)

def main(dir : str):
    recognize(dir)

if __name__ == "__main__":
    fire.Fire(main)