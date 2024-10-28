from paddleocr import PaddleOCR, draw_ocr  
import cv2  
import matplotlib.pyplot as plt  
  
# 初始化 PaddleOCR，设置语言为中文和英文（'ch' 表示简体中文和英文）  
ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # lang='en' 如果只识别英文  
  
# 要识别的图片路径  
img_path = './test.jpg'  # 替换为你的图片路径  
  
# 读取图片  
img = cv2.imread(img_path)  
  
# 使用 PaddleOCR 进行文本识别  
result = ocr.ocr(img_path, cls=True)  # cls=True 表示同时进行方向分类  
  
print(result)