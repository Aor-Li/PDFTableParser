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
        weights = ROOT + "/weights/yolov5/finetune/20240527/best.pt",
        input = dir,
        output = "./results"
    )
    structure_recognize.main(
        dir = "./results"
    )
    cell_ocr.main(
        dir = "./results"
    )
    merge_bracket.process_results(
        dir = "./results"
    )

if __name__ == "__main__":
    fire.Fire(main)