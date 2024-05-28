import os
import sys
import fire
import shutil
import comet_ml
from icecream import ic
from datetime import datetime
from pathlib import PurePath, Path

FILE = Path(__file__).resolve()
ROOT = str(FILE.parents[1])
ic(ROOT)

# import yolov5 submodule
sys.path.insert(0, ROOT + "/models/yolov5")
import utils
import train as yolov5_train
import detect as yolov5_detect

def train(
    data       : str,                      # 数据名
    epochs     : int = 3,                  # 训练轮数
    input_name : str = "yolov5tb_last.pt", # 输入权重路径
    output_name: str = "",                 # 输出权重路径
    save_record: str = ""                  # 训练数据保留路径
):
    # excution name
    name = "{}_{}".format(data.split("/")[-1], datetime.now().strftime("%Y%m%d"))

    # set parameters
    params = {}
    params["name"] = name
    params["data"] = os.path.join(data, "data.yaml")
    params["weights"] = os.path.join(ROOT, "weights/yolov5/pretrain", input_name)
    params["epochs"] = epochs
    ic(params)
    
    # change working directory to yolov5
    cwd_path = os.getcwd()
    run_path = ROOT + "/models/yolov5"
    os.chdir(run_path)
    
    # run train
    print("Starting yolov5 train process...")
    comet_ml.init()
    yolov5_train.run(
        **params,
        cache = True,
    )
    print("Training finished, organizing results...")
    
    # copy result weights
    if output_name == "":
        weight_dir = ROOT + "/weights/yolov5/finetune/{}".format(name)
    else:
        weight_dir = output_name
    os.makedirs(weight_dir)

    shutil.copyfile(run_path + "/runs/train/{}/weights/best.pt".format(name),
                    weight_dir + "/best.pt")
    shutil.copyfile(run_path + "/runs/train/{}/weights/last.pt".format(name),
                    weight_dir + "/last.pt")
    # save train data
    if save_record == "":
        shutil.rmtree(run_path + "/runs/train/{}".format(name))
    else:
        shutil.move(run_path + "/runs/train/{}".format(name), save_record)

    # change back to original working directory
    os.chdir(cwd_path)

def detect(
    weights : str,                      # 权重路径
    input   : str,                      # 输入图片路径
    output  : str = "detect_results",   # 输出结果路径
):
    print("Running table detection ...")

    # excution name
    name = datetime.now().strftime("%Y%m%d%H%M%S")
    output = os.path.abspath(output)

    # set parameter
    params = {}
    params["name"] = name
    params["weights"] = os.path.abspath(weights)
    params["source"] = os.path.abspath(input)
    ic(params)

    # change working directory to yolov5
    cwd_path = os.getcwd()
    os.chdir(ROOT + "/models/yolov5")

    # run detect
    print("Starting yolov5 detect process...")
    yolov5_detect.run(
        **params,
        project = "pdf_parser_results",
        save_txt = True,
        save_csv = True,
        save_conf = True,
        save_crop = True
    )
    print("Detection finished, moving results...")
    
    # organzie results
    shutil.move("pdf_parser_results/{}".format(name), output)
    shutil.rmtree("pdf_parser_results")

    # change back to original working directory
    os.chdir(cwd_path)

def organize(
    input        : str, # 输入图片路径
    output       : str = "", # 输出图片路径
    origin       : str = "", # 原始数据路径
):
    print("Running table detection results organizing ...")

    # 创建目标文件夹
    tmp_output = input + ".tmp" if output == "" else output
    if os.path.exists(tmp_output):
        shutil.rmtree(tmp_output)
    os.makedirs(tmp_output)

    # 遍历存储输入图片
    result_files = []
    for result_file in os.listdir(input):
        if not (result_file.endswith(".png") or result_file.endswith(".jpg")):
            continue;
        result_files.append(result_file)
    
    # 需要的数据label
    neededCropNames = ["Bracket_Need_Type1", "Bracket_Need_Type2", "Bracket_Need_Type3", "Pipe_Need_Type1"]
    
    # 分别处理各图片
    for result_file in result_files:
        result_name, result_ext = os.path.splitext(result_file)

        # 创建对应目录
        pageDetectDir = os.path.join(tmp_output, result_name, "detect")
        os.makedirs(pageDetectDir)

        # 复制带标注的图片
        shutil.copyfile(os.path.join(input, result_file),
                        os.path.join(pageDetectDir, "markded" + result_ext))

        # 复制标记文本结果
        shutil.copyfile(os.path.join(input, "labels", result_name + ".txt"),
                        os.path.join(pageDetectDir, "labels.txt"))

        # 复制原始文件
        if origin != "":
            shutil.copyfile(os.path.join(origin, result_file),
                            os.path.join(pageDetectDir, "origin" + result_ext))
    # 移动结果文件夹
    if output == "":
        shutil.rmtree(input)
        shutil.move(tmp_output, input)
    else:
        shutil.move(tmp_output, output)

def main(
    weights: str,
    input  : str,
    output : str = ""
):
    output = "./results" if output == "" else output
    detect(weights=weights, input=input, output=output)
    organize(input=output, origin=input)

if __name__ == "__main__":
    fire.Fire()