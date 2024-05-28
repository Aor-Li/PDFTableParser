import os
import re
import sys
import fire
import pandas as pd
from pathlib import PurePath, Path

from pdf_parser.postprocess.bracket_type1 import process_excel as process_bracket_type1
from pdf_parser.postprocess.bracket_type2 import process_excel as process_bracket_type2

def process_page(dir : str):
        page_name = dir.split("/")[-1]
        
        # check ocr results
        ocr_dir = os.path.join(dir, "ocr")
        if not os.path.exists(ocr_dir):
            ic(ocr_dir)
            print(f"Page {page_name} ocr not finished.")
            return
        
        # check bracket1 and bracket2 data
        ocr_tables = os.listdir(ocr_dir)
        type1_bracket_files = list(filter(lambda x: x.startswith("Bracket_Need_Type1"), ocr_tables))
        type2_bracket_files = list(filter(lambda x: x.startswith("Bracket_Need_Type2"), ocr_tables))
        type3_bracket_files = list(filter(lambda x: x.startswith("Bracket_Need_Type3"), ocr_tables))

        if len(type1_bracket_files) == 0 or len(type3_bracket_files) == 0:
            print(f"Page {page_name} bracket1 or bracket3 not detected.")
            return
        
        # 处理bracket数据
        type1_exist = True
        try:
            process_bracket_type1(os.path.join(ocr_dir, type1_bracket_files[0], "ocr.xlsx"),
                                  os.path.join(ocr_dir, type1_bracket_files[0], "processed.xlsx"))
        except:
            print(f"Page {page_name} bracket1 process failed.")
            type1_exist = False

        type2_exist = True
        try:
            process_bracket_type2(os.path.join(ocr_dir, type2_bracket_files[0], "ocr.xlsx"),
                                  os.path.join(ocr_dir, type2_bracket_files[0], "processed.xlsx"))
        except:
            print(f"Page {page_name} bracket2 process failed.")
            type2_exist = False

        type3_exist = True
        try:
            sheet_df = pd.read_excel(os.path.join(ocr_dir, type3_bracket_files[0], "ocr.xlsx"), header=None)
        except:
            print(f"Page {page_name} bracket3 process failed.")
            type3_exist = False


        # 合并处理后表格
        if type1_exist and type2_exist:
            # merge
            df1 = pd.read_excel(os.path.join(ocr_dir, type1_bracket_files[0], "processed.xlsx"),
                                skiprows=1,
                                header=None)
            df2 = pd.read_excel(os.path.join(ocr_dir, type2_bracket_files[0], "processed.xlsx"),
                                skiprows=1,
                                header=None)
            combined_df = pd.concat([df1, df2], ignore_index=True)
            combined_df.to_excel(os.path.join(ocr_dir, "bracket.xlsx"), index=False, header=False)

        elif type1_exist and not type2_exist:
            df1 = pd.read_excel(os.path.join(ocr_dir, type1_bracket_files[0], "processed.xlsx"),
                                skiprows=1,
                                header=None)
            combined_df = df1.copy()
            combined_df.to_excel(os.path.join(ocr_dir, "bracket.xlsx"), index=False, header=False)
        
        else:
            print("No bracket data type1 and type2 to process.")
            return
        
        # 处理并合入sheet
        if not type3_exist:
            return
        try: 
            # 从sheet第一列第二行读取数据
            sheet_data = str(sheet_df.iloc[1, 0])

            # 查找连续出现两个数字的位置
            match = re.search(r'\d{2}', sheet_data)
            if match:
                start_index = match.start()
                # 从起始位置读取连续13个字母或数字
                extracted_data1 = sheet_data[start_index:start_index + 13]
            else:
                extracted_data1 = ""

            # 读取A表格第三列第四行的信息
            extracted_data2 = sheet_df.iloc[3, 2]

            # 更新merged表格的第一列和第二列
            # combined_df = pd.read_excel(os.path.join(ocr_dir, "bracket.xlsx"))
            for i in range(len(combined_df)):
                combined_df.iloc[i, 0] = extracted_data1
                combined_df.iloc[i, 1] = extracted_data2
            
            # 保存新的表格
            combined_df.to_excel(os.path.join(ocr_dir, "bracket_final.xlsx"), index=False, header=False)
        except:
            print(f"Page {page_name} merged bracket process failed.")
            return

        print(f"Page {page_name} process finished.")

def process_results(dir : str):
    for page_name in sorted(os.listdir(dir)):
        process_page(os.path.join(dir, page_name))

if __name__ == "__main__":
    fire.Fire(process_results)