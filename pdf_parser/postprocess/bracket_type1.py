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

def extract_info_from_column(column_value):
    """根据新规则提取信息，遇到第二次大写字母或非字母字符停止，并检查G列格式。"""
    if pd.isna(column_value):
        return None, None, None
    column_value = str(column_value)
    word, after_word, c_value = None, None, None
    if '/' in column_value:
        parts = column_value.split('/')
        second_part = parts[1].strip() if len(parts) > 1 else ""
        word = []
        upper_count = 0
        for char in second_part:
            if char.isalpha():
                if char.isupper():
                    upper_count += 1
                if upper_count > 1:
                    break
                word.append(char)
            else:
                break
        word = ''.join(word)
        after_word = second_part[len(word):]
        match_c = re.search(r'(\d+)[x\*](\d+)[x\*](\d+)', after_word)
        c_value = match_c.group(3) if match_c else None
    return word, after_word, c_value

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

# 加载Excel文件
def process_excel(input, output):
    data = pd.read_excel(input, dtype=str)

    # 预处理，找到第一个数字出现的行
    first_numeric = data[0].apply(lambda x: pd.to_numeric(x, errors='coerce')).first_valid_index()

    # 创建一个新的DataFrame来存储结果
    new_df = pd.DataFrame(columns=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M'])

    index = 0
    while index < len(data):
        current_number = pd.to_numeric(data.loc[index, 0], errors='coerce')
        material = determine_material(data.loc[index, 4])
        word, after_word, c_value = extract_info_from_column(data.loc[index, 2])
        translated_word = translation_dict.get(word.lower(), word) if word else word  # 翻译word，并忽略大小写

        column_1_not_na = pd.notna(data.loc[index, 1])
        column_2_not_na = pd.notna(data.loc[index, 2])

        # 检查第一列有数字的行，E列数据不为空的行，以及Column 5和Column 6同时有数字的行
        if pd.notna(current_number) or (word and translated_word) or \
                (pd.notna(pd.to_numeric(data.loc[index, 5], errors='coerce'))) and \
                (pd.notna(pd.to_numeric(data.loc[index, 6], errors='coerce'))):
            new_df = pd.concat([new_df, pd.DataFrame({
                'D': [current_number],
                'E': [word],
                'F': [translated_word],
                'G': [after_word],
                'H': [c_value],
                'I': [data.loc[index, 3]],
                'J': [data.loc[index, 4]],
                'K': [material],
                'L': [data.loc[index, 5]],
                'M': [data.loc[index, 6]]
            })], ignore_index=True)

        index += 1

    # 保存新的DataFrame到Excel文件
    new_df.to_excel(output, index=False)