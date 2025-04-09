import re

def remove_md_format_to_dots(text):
    """
    去除 Markdown 格式并将换行和空格转为句号
    
    参数:
        text (str): 输入的 Markdown 文本
    
    返回:
        str: 转换后的文本，所有换行和空格都被转换为句号
    """
    # 去除图片链接 ![text](url)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    
    # 去除链接 [text](url)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    
    # 去除标题符号 # 
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    # 去除粗体、斜体 **text** 或 *text* 或 __text__ 或 _text_
    text = re.sub(r'(\*\*|__)(.*?)(\*\*|__)', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)(\*|_)', r'\2', text)
    
    # 去除代码块
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    
    # 去除行内代码
    text = re.sub(r'`(.*?)`', r'\1', text)
    
    # 去除引用符号 >
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'^[\*\-+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'\|.*?\|', '', text)
    text = re.sub(r'^\s*[-:]+\s*$', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'^-{3,}$|^\*{3,}$|^_{3,}$', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'\n+', '\n', text)
    
    text = re.sub(r'\s+', '.', text)
    
    text = re.sub(r'\.+', '.', text)
    
    text = text.strip('.')
    
    return text