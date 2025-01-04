import os
import requests
import time
from urllib.parse import quote

def download_sigmod_papers(year):
    # 创建保存文件的文件夹
    output_dir = "SIGMOD_PAPER"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 构建URL
    base_url = "https://dblp.org/search/publ/api"
    
    # 根据不同年份构建不同的查询字符串
    if year >= 2023:
        # 2023年及以后添加'c'
        query = f"toc:db/conf/sigmod/sigmod{year}c.bht:"
    elif year < 2000:
        # 2000年之前只用后两位年份
        year_suffix = str(year)[-2:]  # 获取年份的后两位
        query = f"toc:db/conf/sigmod/sigmod{year_suffix}.bht:"
    else:
        # 2000-2022年的正常处理
        query = f"toc:db/conf/sigmod/sigmod{year}.bht:"
    
    params = {
        'q': query,
        'h': '1000',
        'format': 'xml',
        'rd': '1'
    }
    
    try:
        # 发送请求
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # 检查请求是否成功
        
        # 保存文件
        output_file = os.path.join(output_dir, f"sigmod_{year}.xml")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"成功下载 SIGMOD {year} 年的论文引用文件到 {output_file}")
        return True
        
    except requests.RequestException as e:
        print(f"下载失败: {e}")
        return False

def download_sigmod_papers_range(start_year, end_year):
    print(f"开始下载 {start_year} 到 {end_year} 年的SIGMOD论文引用文件...")
    success_count = 0
    fail_count = 0
    
    for year in range(start_year, end_year + 1):
        print(f"\n正在处理 {year} 年的数据...")
        if download_sigmod_papers(year):
            success_count += 1
            if year != end_year:  # 如果不是最后一年，则等待10秒
                print(f"下载成功，等待10秒后继续下载下一年...")
                time.sleep(10)
        else:
            fail_count += 1
            if year != end_year:  # 如果不是最后一年，则等待1秒
                print("下载失败，等待1秒后继续尝试下一年...")
                time.sleep(1)
    
    print(f"\n下载完成！成功: {success_count} 个文件，失败: {fail_count} 个文件")
    return success_count, fail_count

if __name__ == "__main__":
    try:
        # 获取年份范围
        start_year = int(input("请输入起始年份: "))
        end_year = int(input("请输入结束年份: "))
        
        # 验证输入
        if start_year > end_year:
            print("错误：起始年份不能大于结束年份！")
        elif start_year < 1975:  # SIGMOD始于1975年
            print("警告：建议从1975年开始下载SIGMOD论文数据。")
        elif end_year > 2024:
            print("警告：结束年份超过当前年份，可能没有数据。")
            
        # 执行下载
        download_sigmod_papers_range(start_year, end_year)
        
    except ValueError:
        print("错误：请输入有效的年份数字！") 