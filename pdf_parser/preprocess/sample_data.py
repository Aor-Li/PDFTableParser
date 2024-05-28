import os
import random
import shutil
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('input_dir', type=str, help='The input directory')
    parser.add_argument('train_ratio', type=float, help='The ratio of the training set')
    parser.add_argument('valid_ratio', type=float, help='The ratio of the validation set')
    return parser.parse_args()

def sample_data(input_dir, train_ratio, valid_ratio):
    if not os.path.exists(os.path.join(input_dir, "images", "total")):
        raise ValueError(f"The input directory [{input_dir}] does not exist.")

    # 重建输出目录
    if os.path.exists(os.path.join(input_dir, "images", "train")):
        shutil.rmtree(os.path.join(input_dir, "images", "train"))
    if os.path.exists(os.path.join(input_dir, "images", "valid")):
        shutil.rmtree(os.path.join(input_dir, "images", "valid"))
    if os.path.exists(os.path.join(input_dir, "images", "test")):
        shutil.rmtree(os.path.join(input_dir, "images", "test"))
    if os.path.exists(os.path.join(input_dir, "labels", "train")):
        shutil.rmtree(os.path.join(input_dir, "labels", "train"))
    if os.path.exists(os.path.join(input_dir, "labels", "valid")):
        shutil.rmtree(os.path.join(input_dir, "labels", "valid"))
    if os.path.exists(os.path.join(input_dir, "labels", "test")):
        shutil.rmtree(os.path.join(input_dir, "labels", "test"))
    os.makedirs(os.path.join(input_dir, "images", "train"))
    os.makedirs(os.path.join(input_dir, "images", "valid"))
    os.makedirs(os.path.join(input_dir, "images", "test"))
    os.makedirs(os.path.join(input_dir, "labels", "train"))
    os.makedirs(os.path.join(input_dir, "labels", "valid"))
    os.makedirs(os.path.join(input_dir, "labels", "test"))

    # 获取图片文件路径
    fig_names = os.listdir(os.path.join(input_dir, "images", "total"))
    
    # 随机打乱图片路径
    random.shuffle(fig_names)
    
    # 划分数据集
    train_num = int(len(fig_names) * train_ratio)
    valid_num = int(len(fig_names) * valid_ratio)
    test_num = len(fig_names) - train_num - valid_num
    
    train_names = fig_names[:train_num]
    valid_names = fig_names[train_num:train_num + valid_num]
    test_names = fig_names[train_num + valid_num:]
    
    # 将数据集复制到对应目录
    for idx, fig_name in enumerate(train_names):
        base, ext = fig_name.split('.')
        fig_path = os.path.join(input_dir, "images/total", fig_name)
        lab_path = os.path.join(input_dir, "labels/total", base + ".txt")
        shutil.copy(fig_path, os.path.join(input_dir, f"images/train/{idx}.{ext}"))
        shutil.copy(lab_path, os.path.join(input_dir, f"labels/train/{idx}.txt"))
    
    for idx, fig_name in enumerate(valid_names):
        base, ext = fig_name.split('.')
        fig_path = os.path.join(input_dir, "images/total", fig_name)
        lab_path = os.path.join(input_dir, "labels/total", base + ".txt")
        shutil.copy(fig_path, os.path.join(input_dir, f"images/valid/{idx}.{ext}"))
        shutil.copy(lab_path, os.path.join(input_dir, f"labels/valid/{idx}.txt"))
    
    for idx, fig_name in enumerate(test_names):
        base, ext = fig_name.split('.')
        fig_path = os.path.join(input_dir, "images/total", fig_name)
        lab_path = os.path.join(input_dir, "labels/total", base + ".txt")
        shutil.copy(fig_path, os.path.join(input_dir, f"images/test/{idx}.{ext}"))
        shutil.copy(lab_path, os.path.join(input_dir, f"labels/test/{idx}.txt"))
    
    print("Total images: {}".format(len(fig_names)))
    print("Train images: {}".format(len(train_names)))
    print("Valid images: {}".format(len(valid_names)))
    print("Test images: {}".format(len(test_names)))

if __name__ == "__main__":
    args = get_args()
    sample_data(args.input_dir, args.train_ratio, args.valid_ratio)

