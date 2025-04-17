import re

def process_text(text):
    if not text or not isinstance(text, str):
        return ''
    
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F" 
        "\U0001F300-\U0001F5FF" 
        "\U0001F680-\U0001F6FF" 
        "\U0001F700-\U0001F77F"  
        "\U0001F780-\U0001F7FF" 
        "\U0001F800-\U0001F8FF" 
        "\U0001F900-\U0001F9FF" 
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002600-\U000026FF"
        "\U00002700-\U000027BF"
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