import requests

url = "https://www.cftc.gov/strike-price-xls?col=ExchId%2CContractName&dir=ASC%2CASC"

response = requests.get(url)

# 检查请求是否成功
if response.status_code == 200:
    # 存储下载的文件
    with open('downloaded_file.xls', 'wb') as file:
        file.write(response.content)
    print("文件下载成功，已保存为 'downloaded_file.xls'")
else:
    print(f"请求失败，状态码：{response.status_code}")
