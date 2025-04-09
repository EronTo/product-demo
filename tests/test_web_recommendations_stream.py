import requests
import sys

def test_web_recommendations_stream():
    # 设置API端点URL
    url = "http://localhost:8000/recommendations/web"
    
    # 设置请求参数
    params = {
        "user_query": "推荐一些性价比高的笔记本电脑",
        "num_products": 3
    }
    
    try:
        # 发送POST请求，设置stream=True以启用流式响应
        response = requests.post(url, params=params, stream=True)
        
        # 检查响应状态码
        if response.status_code != 200:
            print(f"错误: 服务器返回状态码 {response.status_code}")
            return
        
        print("开始接收流式响应...\n")
        
        # 迭代处理流式响应
        for line in response.iter_lines(decode_unicode=True):
            if line:
                # 打印接收到的数据
                print(line, flush=True)
                
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    test_web_recommendations_stream()