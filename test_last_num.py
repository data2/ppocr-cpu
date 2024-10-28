
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

print(get_last_num('MSCU983672'))
