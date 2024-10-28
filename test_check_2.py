import os
from paddleocr import PaddleOCR, draw_ocr
import cv2
import matplotlib.pyplot as plt
from matplotlib.image import imread
from itertools import combinations
import logging
import re
import traceback

count = 0
ocr = PaddleOCR(use_angle_cls=True, lang='ch',
rec_model_dir='./ch_PP-OCRv4_rec_infer',
rec_algorithm='SVTR_LCNet',
use_gpu=True, gpu_mem=400,
# rec_batch_num = 10,
show_log=True)

image_folder = './image_dir'


def is_four_uppercase_letters(s):
    pattern = r'^[A-Z]{4}$'
    return bool(re.fullmatch(pattern, s))


def is_valid_container_number(text):
    if len(text) == 11 and is_four_uppercase_letters(text[:4]) and check_digit(text):
        return True
    return False


mapofCode = {
    "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "A": 10, "B": 12, "C": 13, "D": 14, "E": 15, "F": 16, "G": 17, "H": 18, "I": 19, "J": 20,
    "K": 21, "L": 23, "M": 24, "N": 25, "O": 26, "P": 27, "Q": 28, "R": 29, "S": 30, "T": 31,
    "U": 32, "V": 34, "W": 35, "X": 36, "Y": 37, "Z": 38
}

count = 0

def check_digit(container_number):
    try:
        if len(container_number) != 11:
            return False

        sum = 0

        # 计算前10个字符的加权和
        for i in range(10):
            sum += mapofCode[container_number[i]] * (2 ** i)

        # 计算校验码（对11取模后再对10取模，防止校验码为10的情况）
        check_digit_calculated = sum % 11 % 10

        # 获取实际的校验码（最后一位字符转换为数字）
        check_digit_actual = int(container_number[10])

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
    if len(s) < 10:
        return False

    slice_5_to_10 = s[4:10]

    return slice_5_to_10.isdigit()


def filter_reco_text(recognized_texts, confidence_threshold):
    # filtered_texts = [text for text, confidence in recognized_texts if confidence >= confidence_threshold]
    filtered_texts = []
    for text, confidence in recognized_texts:
        if confidence < confidence_threshold:
            continue
        text = re.sub(r"\s+", "", text)
        if len(text) >= 4 and all((char in '01丨|！') or char.isupper() for char in text[:4]):
            modified_front = re.sub(r'[1丨|！]', 'I', text[:4])
            modified_front = re.sub(r'[0]', 'O', modified_front)
            modified_text = modified_front + text[4:]  # 将修改后的前四位与原始字符串的其余部分合并
            print(modified_text)
            filtered_texts.append(modified_text)
        else:
            # 直接添加不满足特定条件的原始文本
            filtered_texts.append(text)
    print(filtered_texts)
    return filtered_texts


def find_container_number(recognized_texts):
    filtered_texts = filter_reco_text(recognized_texts, confidence_threshold=0.7)
    arr = []
    for i in range(1, len(filtered_texts) + 1):
        for combo in combinations(filtered_texts, i):
            possable_com_text = ''.join(combo)
            if is_valid_container_number(possable_com_text):
                return possable_com_text
            else:
                if len(possable_com_text) >= 10 and len(possable_com_text) <= 12 and is_first_four_uppercase(
                        possable_com_text) and is_digits_at_positions_5_to_10(possable_com_text):
                    com_text = get_last_num(possable_com_text[:10])
                    if com_text is not None:
                        # arr.append(com_text)
                        return com_text

    # if len(arr)!=0:
    #     print(arr)
    #     return arr[0]
    return None

def start_app():
    count = 0
    for idx, filename in enumerate(os.listdir(image_folder)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
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
                print(f"================================识别{idx + 1}张图片,成功{count}张=================")
            except Exception as e:
                # 捕获并处理任何Python异常
                print(f"处理图片 {filename} 时发生异常: {e}")
                traceback.print_exc()
            finally:
                os.remove(image_path)
                # 记录图片处理完成（无论是否成功）
                # print(f"图片 {filename} 处理完成")


start_app()
