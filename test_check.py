import os
from paddleocr import PaddleOCR, draw_ocr
import cv2
import matplotlib.pyplot as plt
from matplotlib.image import imread
from itertools import combinations
import logging
import re
import traceback



#logging.basicConfig(level=logging.INFO, filename='ocr_log.txt', filemode='w',  format='%(asctime)s - %(levelname)s - %(message)s')
count = 0
ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # 根据需要修改语言

# 指定图片文件夹路径
image_folder = './image_dir'

def is_four_uppercase_letters(s):
    pattern = r'^[A-Z]{4}$'
    return bool(re.fullmatch(pattern, s))
def is_valid_container_number(text):
    if len(text) == 11 and is_four_uppercase_letters(text[:4]) and check_digit(text):
        return True
    return False

# 定义字符到数字的映射
mapofCode = {
    "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "A": 10, "B": 12, "C": 13, "D": 14, "E": 15, "F": 16, "G": 17, "H": 18, "I": 19, "J": 20,
    "K": 21, "L": 23, "M": 24, "N": 25, "O": 26, "P": 27, "Q": 28, "R": 29, "S": 30, "T": 31,
    "U": 32, "V": 34, "W": 35, "X": 36, "Y": 37, "Z": 38
}


def check_digit(container_number):
    try:
        # 检查容器编号长度是否为11
        if len(container_number) != 11:
            return False

            # 初始化总和
        sum = 0

        # 计算前10个字符的加权和
        for i in range(10):
            sum += mapofCode[container_number[i]] * (2 ** i)

            # 计算校验码（对11取模后再对10取模，防止校验码为10的情况）
        check_digit_calculated = sum % 11 % 10

        # 获取实际的校验码（最后一位字符转换为数字）
        check_digit_actual = int(container_number[10])

        # 比较计算出的校验码和实际校验码
        return check_digit_calculated == check_digit_actual
    except Exception as e:
        print('转换异常')

def get_last_num(container_number):
    for i in range(10):
        if (check_digit(container_number + str(i))):
            return container_number + str(i)
    return None

def is_first_four_uppercase(s):
    pattern = r'^[A-Z]{4}'
    return bool(re.match(pattern, s))


def is_digits_at_positions_5_to_10(s):
    # 检查字符串长度是否至少为10
    if len(s) < 10:
        return False

    # 切片获取第5到第10位的字符（索引4到9）
    slice_5_to_10 = s[4:10]

    # 判断切片是否全部由数字组成
    return slice_5_to_10.isdigit()

def filter_reco_text(recognized_texts,confidence_threshold):
    # 过滤出可信度高于阈值的文本（注意：这里我们仅使用了文本，没有使用置信度进行过滤，
    # 因为组合逻辑需要所有可能的文本。但是，在实际应用中，您可能希望根据置信度对文本进行排序或进一步筛选。）
    # 如果需要使用置信度，可以将recognized_texts改为元组列表，并在这里进行过滤。
    # filtered_texts = [text for text, confidence in recognized_texts if confidence >= confidence_threshold]
    # 但由于组合逻辑的需要，我们暂时保留所有文本。
    # all_texts = [text for text, confidence in recognized_texts]
    filtered_texts = []
    for text, confidence in recognized_texts:
        if confidence >= confidence_threshold:
            text = re.sub(r"\s+", "", text)
            if len(text) >= 4 and all((char in '01') or char.isupper() for char in text[:4]):
                # 只替换前四位中的1为I、0为O
                modified_front = text[:4].replace('0', 'O').replace('1', 'I')
                modified_text = modified_front + text[4:]  # 将修改后的前四位与原始字符串的其余部分合并
                print(modified_text)
                filtered_texts.append(modified_text)
            else:
                # 直接添加不满足特定条件的原始文本
                filtered_texts.append(text)
    print(filtered_texts)
    return filtered_texts

def find_container_number(recognized_texts):
    filtered_texts = filter_reco_text(recognized_texts,confidence_threshold=0.6)
    # 遍历所有可能的文本组合
    arr = []
    for i in range(1, len(filtered_texts) + 1):
        for combo in combinations(filtered_texts, i):
            # 将组合中的文本拼接起来
            possable_com_text = ''.join(combo)

            # 检查拼接后的文本是否符合集装箱箱号的格式要求
            if is_valid_container_number(possable_com_text):
                # 找到符合条件的组合，返回箱号
                return possable_com_text
            else:
                if len(possable_com_text) >= 10 and is_first_four_uppercase(possable_com_text) and is_digits_at_positions_5_to_10(possable_com_text):
                    com_text = get_last_num(possable_com_text[:10])
                    if com_text is not None:
                        #arr.append(com_text)
                        return com_text

    # 如果没有找到符合条件的组合，则返回None
    # if len(arr)!=0:
    #     print(arr)
    #     return arr[0]
    return None


# 遍历文件夹中的每个文件
for idx, filename in enumerate(os.listdir(image_folder)):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif')):
        image_path = os.path.join(image_folder, filename)
        try:
            print(f"开始处理图片 {idx + 1}/{len(os.listdir(image_folder))}: {filename}")
            result = ocr.ocr(image_path, cls=True)
            recognized_texts = []
            for line in result:
                for item in line:
                    recognized_texts.append((item[1][0], item[1][1]))  # (识别文本, 置信度)  
            # print(f"元数据{recognized_texts}")
            container_number = find_container_number(recognized_texts)
            if container_number:
                print(f"找到的集装箱箱号: {container_number}")
                count = count + 1
            else:
                print("未找到符合条件的集装箱箱号")
        except Exception as e:
            # 捕获并处理任何Python异常  
            print(f"处理图片 {filename} 时发生异常: {e}")
            traceback.print_exc()
        finally:
            # 记录图片处理完成（无论是否成功）  
            # print(f"图片 {filename} 处理完成")  
            os.remove(image_path)
    print(f"================================识别成功{count}张图片")