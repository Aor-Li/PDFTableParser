#将OCR出来的Type2 转换到计算稿格式

import pandas as pd
import re

# 定义英文到中文的映射字典
translation_dict = {
    "anchor": "锚",
    "angle": "角钢",
    "channel": "槽钢",
    "pipe guide": "导向管座",
    "plate": "钢板",
    "section": "方形钢管",
    "lug": "凸耳",
    "i-beam": "工字钢",
    "weld-on bracket": "焊接托架",
    "rigid strut": "刚性支撑",
    "dynamic pipe clamp": "动态管夹",
    "preassembly": "预组装",
    "inlay plate": "镶板",
    "shock absorbers": "减震器",
    "spec.extention": "特殊延伸",
    "s.a.extention": "sa延伸",
    "dynamic riser clamp": "动态立管夹",
    "weld-on clevis w.b.": "u形吊板",
    "eye nut": "环形螺母",
    "threaded stud": "螺纹螺柱",
    "var. spring hanger": "变量弹簧吊架",
    "clevis with pin": "销型吊耳",
    "vertical pipe clamp": "立式管夹",
    "hexagonal nut": "六角螺母",
    "threaded rod": "全螺纹拉杆",
    "preset cost": "预设成本",
    "clamp base": "线夹底座",
    "set up var spring hang": "变量弹簧吊架",
    "base plate for type 25": "25基板",
    "three bolt clamp": "三孔管夹",
    "pipe clamp": "管夹",
    "tie rod": "横拉杆",
    "trapeze": "吊架",
    "two pipe clamp": "双孔管夹",
    "u-bolt": "u型管卡",
    "stop": "止挡块",
    "parallel guide": "平行导轨",
    "strap": "绑带",
    "three way stop": "三路挡块"
}

# 材料类型
def determine_material(material):
    """确定材料类型"""
    stainless_keywords = {"stainless", "08X18H101", "TP321", "1.4571"}
    if pd.isna(material):
        return None
    elif any(keyword.lower() in material.lower() for keyword in stainless_keywords):
        return "不锈钢"
    else:
        return "碳钢"

def process_excel(input, output):
    data = pd.read_excel(input, dtype=str)

    # 创建一个新的DataFrame来存储结果
    new_df = pd.DataFrame(columns=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M'])

    for index, row in data.iterrows():
        current_number = pd.to_numeric(row[0], errors='coerce')
        third_col_content = row[2] if pd.notna(row[2]) else ''

        # 检查条件：第一列有数字或第三列内容前两个字符为数字
        if not pd.isna(current_number) or (len(third_col_content) >= 2 and third_col_content[:2].isdigit()):
            word = row[1]
            translated_word = translation_dict.get(word.lower(), word)  # 翻译word，并忽略大小写
            material = determine_material(row[4])
            new_df = pd.concat([new_df, pd.DataFrame({
                'D': [current_number],
                'E': [word],
                'F': [translated_word],
                'G': [row[2]],
                'I': [row[4]],
                'J': [row[6]],
                'K': [determine_material(row[6])],  # 使用材料类型函数
                'M': [row[5]]
            })], ignore_index=True)

    # 保存新的DataFrame到Excel文件
    new_df.to_excel(output, index=False)

