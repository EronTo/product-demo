import re

def process_text(text):
    """
    
    处理内容包括:
    1. 删除表情符号
    2. 保留价格信息、货币符号和折扣信息
    3. 保留商品名称和规格信息
    4. 删除多余的特殊字符
    5. 将连续多个换行替换为单个换行
    6. 将连续多个空格替换为单个空格
    7. 删除空行
    
    Args:
        text (str): 需要处理的促销文本
        
    Returns:
        str: 处理后的文本
    """
    if not text or not isinstance(text, str):
        return ''
    
    # 删除表情符号
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # 表情
        "\U0001F300-\U0001F5FF"  # 符号和图形
        "\U0001F680-\U0001F6FF"  # 交通和地图符号
        "\U0001F700-\U0001F77F"  # 炼金术符号
        "\U0001F780-\U0001F7FF"  # 几何图形
        "\U0001F800-\U0001F8FF"  # 补充箭头C
        "\U0001F900-\U0001F9FF"  # 补充符号和图形
        "\U0001FA00-\U0001FA6F"  # 象棋符号
        "\U0001FA70-\U0001FAFF"  # 符号和图形扩展A
        "\U00002600-\U000026FF"  # 杂项符号
        "\U00002700-\U000027BF"  # 装饰符号
        "]", 
        flags=re.UNICODE
    )
    
    punctuation_pattern = re.compile(r'[*_~`|\\^-]')
    
    promo_words = re.compile(r'(超多|补货|速抢|必买|必抢|断货|热卖|限量|独家|上新|返场)')
    
    result = text
    result = emoji_pattern.sub('', result)  
    result = punctuation_pattern.sub('', result)  
    result = promo_words.sub('', result) 
    
    result = re.sub(r'\n{2,}', '\n', result)
    
    lines = result.split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            processed_line = re.sub(r'\s+', ' ', line)
            processed_lines.append(processed_line)

    result = '\n'.join(processed_lines)
    
    return result