import requests
#获取models的脚本，便于程序员查看
# 设置 API 密钥
fish_api_key = "your fish_api_key"

# 获取所有模型列表的函数
def get_all_models(api_key):
    url = "https://api.fish.audio/model"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    # 发送 GET 请求获取模型列表
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("API 返回的模型信息：")
        print(response.json())  # 打印出API返回的所有内容
    else:
        print(f"获取模型信息失败: {response.status_code}, {response.content}")

# 运行函数并打印模型数据
if __name__ == "__main__":
    get_all_models(fish_api_key)
