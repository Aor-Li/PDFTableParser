import os
import re
import sys
import fire
import pandas as pd
from pathlib import Path

from pdf_parser.postprocess.bracket_type1 import process_excel as process_bracket_type1
from pdf_parser.postprocess.bracket_type2 import process_excel as process_bracket_type2

def natural_sort_key(s):
    """用于自然排序的key函数."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def process_page(dir):
    page_name = dir.split("/")[-1]
    
    # check ocr results
    ocr_dir = os.path.join(dir, "ocr")
    if not os.path.exists(ocr_dir):
        print(f"Page {page_name} ocr not finished.")
        return
    
    # check bracket1 and bracket2 data
    ocr_tables = os.listdir(ocr_dir)
    type1_bracket_files = list(filter(lambda x: x.startswith("Bracket_Need_Type1"), ocr_tables))
    type2_bracket_files = list(filter(lambda x: x.startswith("Bracket_Need_Type2"), ocr_tables))
    type3_bracket_files = list(filter(lambda x: x.startswith("Bracket_Need_Type3"), ocr_tables))

    if  len(type3_bracket_files) == 0:
        print(f"Page {page_name}  bracket3 not detected.")
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

    elif type2_exist and not type1_exist:
        df2 = pd.read_excel(os.path.join(ocr_dir, type2_bracket_files[0], "processed.xlsx"),
                            skiprows=1,
                            header=None)
        combined_df = df2.copy()
        combined_df.to_excel(os.path.join(ocr_dir, "bracket.xlsx"), index=False, header=False)
    
    else:
        print("No bracket data type1 and type2 to process.")
        return
    
    # 处理并合入sheet
    try: 
        try:
            sheet_data = str(sheet_df.iloc[1, 0])
        except IndexError:
            sheet_data = ""
            print("读取sheet第一列第二行失败，使用默认空字符串。")

        # 查找连续出现两个数字的位置
        match = re.search(r'\d{2}', sheet_data)
        if match:
            start_index = match.start()
            # 检查sheet_data的长度，确保不会超出范围
            if len(sheet_data) >= start_index + 13:
                extracted_data1 = sheet_data[start_index:start_index + 13]
            else:
                extracted_data1 = sheet_data[start_index:]  # 提取从start_index到字符串末尾的部分
                extracted_data1 = extracted_data1.ljust(13)  # 填充空格到13个字符
        else:
            extracted_data1 = "".ljust(13)  # 如果没有匹配项，使用空格填充到13个字符
        print(f"Extracted data 1: {extracted_data1}")

        # 读取A表格第三列第四行的信息
        try:
            extracted_data2 = sheet_df.iloc[3, 2]
            if pd.isna(extracted_data2):
                extracted_data2 = ""
                print("A表格第三列第四行为空白，使用默认空字符串。")
        except IndexError:
            extracted_data2 = ""
            print("读取A表格第三列第四行失败，使用默认空字符串。")
        print(f"Extracted data 2: {extracted_data2}")

        # 更新merged表格的第一列和第二列
        for i in range(len(combined_df)):
            combined_df.iloc[i, 0] = extracted_data1
            combined_df.iloc[i, 1] = extracted_data2

        # 保存新的表格
        combined_df.to_excel(os.path.join(ocr_dir, "bracket_final.xlsx"), index=False, header=False)
    except:
        print(f"Page {page_name} merged bracket process failed.")
        return

    print(f"Page {page_name} process finished.")

def process_results(dir: str):
    all_combined_df = pd.DataFrame()
    page_dirs = sorted(os.listdir(dir), key=natural_sort_key)
    for page_name in page_dirs:
        process_page(os.path.join(dir, page_name))
        final_bracket_path = os.path.join(dir, page_name, "ocr", "bracket_final.xlsx")
        if os.path.exists(final_bracket_path):
            df = pd.read_excel(final_bracket_path, header=None)
            all_combined_df = pd.concat([all_combined_df, df], ignore_index=True)

    # 对第7列中的形如“数字 * 数字*数字”的内容进行替换
    if not all_combined_df.empty:
        all_combined_df[6] = all_combined_df[6].apply(lambda x: re.sub(r'(\d)\s*[*xX]\s*(\d)\s*[*xX]\s*(\d)', r'\1*\2*\3', str(x)))

    final_output_path = os.path.join(dir, "final_combined_bracket.xlsx")
    all_combined_df.to_excel(final_output_path, index=False, header=False)
    print(f"Final combined bracket file saved to {final_output_path}")

if __name__ == "__main__":
    fire.Fire(process_results)
