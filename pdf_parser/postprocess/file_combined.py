import os
import shutil

def extract_and_rename_files(source_dir, target_dir):
    # 确保目标文件夹存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 遍历源文件夹中的所有子文件夹
    for subdir, _, files in os.walk(source_dir):
        # 检查是否有名为 final_combined_bracket.xlsx 的文件
        if 'final_combined_bracket.xlsx' in files:
            source_file_path = os.path.join(subdir, 'final_combined_bracket.xlsx')
            # 获取子文件夹的名字
            subdir_name = os.path.basename(subdir)
            # 构建目标文件的路径和名字
            target_file_path = os.path.join(target_dir, f"{subdir_name}.xlsx")
            # 复制并重命名文件
            shutil.copy(source_file_path, target_file_path)
            print(f"Copied and renamed {source_file_path} to {target_file_path}")

# 使用示例
source_directory = '/home/aurora/eldsich_backup/results'  # 请将此路径替换为实际的源文件夹路径
target_directory = '/home/aurora/eldsich_backup/final_combined/'  # 请将此路径替换为实际的目标文件夹路径

extract_and_rename_files(source_directory, target_directory)
