import os
import shutil
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('input_dir', type=str, help='The input directory')
    parser.add_argument('output_dir', type=str, help='The output directory')
    return parser.parse_args()

def process_raw_data(input_dir, output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        os.makedirs(os.path.join(output_dir, "images/total"))
        os.makedirs(os.path.join(output_dir, "labels/total"))

    # 遍历输入目录及子目录中的所有图片文件
    fig_paths = set()
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if not (filename.endswith('.png') or filename.endswith('.jpg')):
                continue
            fig_paths.add(os.path.join(root, filename))
    
    # 遍历输入图片路径，检查是否有对应label文件
    valid_paths = dict()
    for fig_path in fig_paths:
        label_path = fig_path.replace('.png', '.txt').replace('.jpg', '.txt')
        if os.path.exists(label_path):
            valid_paths[fig_path] = label_path
    
    # 将有效图片文件复制到输出目录
    for idx, fig_path in enumerate(valid_paths):
        ext = fig_path.split('.')[-1]
        label_path = valid_paths[fig_path]
        shutil.copy(fig_path, os.path.join(output_dir, "images/total", str(idx) + "." + ext))
        shutil.copy(label_path, os.path.join(output_dir, "labels/total", str(idx) + ".txt"))

    print("Total images: {}".format(len(valid_paths)))

if __name__ == "__main__":
    args = get_args()
    process_raw_data(args.input_dir, args.output_dir)