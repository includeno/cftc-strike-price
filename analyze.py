import requests
import pandas as pd
from datetime import datetime
import os

class FileData:
    def __init__(self, file_path, date):
        self.file_path = file_path
        self.date = date

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f'Downloaded {filename}')

def fetch_release(date):
    url = f'https://github.com/includeno/cftc-strike-price/releases/download/cftc-{date}/downloaded_file.xls'
    filename = f'downloaded_file_{date}.xls'
    download_file(url, filename)
    return filename

def analyze_data(new_file, old_file, new_date, old_date):
    new_data = pd.read_excel(new_file)
    new_date
    old_data = pd.read_excel(old_file)
    old_date
    
    # 删除不需要分析的列 'Actual' 和 'Format'
    new_data = new_data.drop(columns=['Actual', 'Format'])
    old_data = old_data.drop(columns=['Actual', 'Format'])

    # 使用'Exchange ID'、'Comm. Code'和'ContractName'作为组合键
    keys = ['Exchange ID', 'Comm. Code', 'ContractName']
    new_data['key'] = new_data[keys].astype(str).agg('-'.join, axis=1)
    old_data['key'] = old_data[keys].astype(str).agg('-'.join, axis=1)

    # 找出新增的数据
    new_rows = new_data[~new_data['key'].isin(old_data['key'])]
    # 找出删除的数据
    deleted_rows = old_data[~old_data['key'].isin(new_data['key'])]

    # 找出可能修改的数据（仅监控'ReportingLevel'字段的变化）
    common_new = new_data[new_data['key'].isin(old_data['key'])].set_index('key')
    common_old = old_data[old_data['key'].isin(new_data['key'])].set_index('key')

    # 对比'ReportingLevel'的变化
    modified_data = pd.merge(common_new[keys + ['ReportingLevel']], common_old[keys + ['ReportingLevel']], on=keys, suffixes=(f'_{new_date}', f'_{old_date}'))
    modified_data = modified_data[modified_data[f'ReportingLevel_{new_date}'] != modified_data[f'ReportingLevel_{old_date}']]

    # 保存结果到不同的sheet中
    with pd.ExcelWriter(f'result_{old_date}_to_{new_date}.xlsx') as writer:
        new_rows.to_excel(writer, sheet_name='New Data', index=False)
        deleted_rows.to_excel(writer, sheet_name='Deleted Data', index=False)
        modified_data.to_excel(writer, sheet_name='Modified Data', index=False)
    print('Analysis results are saved in separate sheets.')

if __name__ == '__main__':
    # 获取当前日期
    # today = datetime.now().strftime("%Y-%m-%d")
    # new_file = fetch_release(today)
    new_file='downloaded_file_2024-05-18.xls'
    # # 获取前一天的日期
    # yesterday = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")
    # print(yesterday)
    # old_file = f'downloaded_file_{yesterday}.xls'
    old_file = 'downloaded_file_2024-05-17.xls'
    
    if os.path.exists(old_file):
        result_file = analyze_data(new_file, old_file, '2024-05-18', '2024-05-17')
        print(f'Analysis result saved to {result_file}')
    else:
        print(f'Old data file not found: {old_file}')
    
    # 为下一次分析准备当前下载的文件
    print(f'{new_file} has been downloaded and analyzed')
