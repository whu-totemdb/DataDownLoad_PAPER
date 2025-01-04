import os
import requests
import time
from urllib.parse import quote

def get_volume_number(year):
    """
    将年份转换为VLDB的卷号
    从2024年开始是第17卷，每减少一年卷号减1
    """
    volume = 17 - (2024 - year)
    if volume < 1:
        return None
    return volume

def download_vldb_papers(year):
    # 创建保存文件的文件夹
    output_dir = "VLDB_PAPER"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 构建URL
    base_url = "https://dblp.org/search/publ/api"
    
    if year >= 2008:
        # 2008年及以后使用期刊格式
        volume = get_volume_number(year)
        if volume is None:
            print("从 2008 年起，VLDB 社区决定：采用'期刊式'论文集出版模式。PVLDB只支持下载2008年后的论文")
            return False
        query = f"toc:db/journals/pvldb/pvldb{volume}.bht:"
    else:
        # 2008年之前使用会议格式
        print(f"注意：{year}年的论文使用传统会议论文集格式")
        if year < 2000:
            # 2000年前使用两位数年份
            year_suffix = str(year)[-2:]
            query = f"toc:db/conf/vldb/vldb{year_suffix}.bht:"
        else:
            query = f"toc:db/conf/vldb/vldb{year}.bht:"
    
    params = {
        'q': query,
        'h': '1000',
        'format': 'xml'
    }
    
    try:
        # 发送请求
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # 检查请求是否成功
        
        # 保存文件
        if year >= 2008:
            output_file = os.path.join(output_dir, f"vldb_{year}_vol{get_volume_number(year)}.xml")
        else:
            output_file = os.path.join(output_dir, f"vldb_{year}.xml")
            
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"成功下载 VLDB {year} 年的论文引用文件到 {output_file}")
        return True
        
    except requests.RequestException as e:
        print(f"下载失败: {e}")
        return False

def download_vldb_papers_range(start_year, end_year):
    print(f"开始下载 {start_year} 到 {end_year} 年的VLDB论文引用文件...")
    success_count = 0
    fail_count = 0
    
    for year in range(start_year, end_year + 1):
        print(f"\n正在处理 {year} 年的数据...")
        if download_vldb_papers(year):
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
        elif end_year > 2024:
            print("警告：结束年份超过当前年份，可能没有数据。")
        else:
            # 执行下载
            download_vldb_papers_range(start_year, end_year)
        
    except ValueError:
        print("错误：请输入有效的年份数字！") 