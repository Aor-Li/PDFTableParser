import os
import sys
import fire
import shutil
from icecream import ic
from pathlib import PurePath, Path

FILE = Path(__file__).resolve()
ROOT = str(FILE.parents[1])
ic(ROOT)

sys.path.append(os.path.abspath(ROOT))

import pdf_parser.table_detect as table_detect
import pdf_parser.structure_recognize as structure_recognize
import pdf_parser.cell_ocr as cell_ocr
import pdf_parser.postprocess.merge_bracket as merge_bracket


def main(dir : str):
    table_detect.main(
        weights = ROOT + "/weights/yolov5/total_20240527/best.pt",
        input = dir,
        output = "./results/124"
    )
    structure_recognize.main(
        dir = "./results/124"
    )
    cell_ocr.main(
        dir = "./results/124"
    )
    merge_bracket.process_results(
        dir = "./results/124"
    )


# def process_subdir(subdir, output_root):
#     subdir_name = os.path.basename(subdir)
#     output_dir = os.path.join(output_root, subdir_name)


#     table_detect.main(
#         weights = ROOT + "/weights/yolov5/total_20240527/best.pt",
#         input = subdir,
#         output = output_dir
#     )
#     structure_recognize.main(
#         dir = output_dir
#     )
#     cell_ocr.main(
#         dir = output_dir
#     )
#     merge_bracket.process_results(
#         dir = output_dir
#     )

# def main(dir: str):
#     # 获取主目录下的所有子文件夹
#     subdirs = [os.path.join(dir, subdir) for subdir in os.listdir(dir) if os.path.isdir(os.path.join(dir, subdir))]
#     output_root = "./results"
    
#     for subdir in subdirs:
#         print(f"Processing directory: {subdir}")
#         process_subdir(subdir, output_root)
#         print(f"Finished processing directory: {subdir}")

if __name__ == "__main__":
    fire.Fire(main)
