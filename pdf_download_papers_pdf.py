import os
import json
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
from tqdm import tqdm

class SciHubDownloader:
    def __init__(self):
        # Sci-Hub镜像站点列表（需要定期更新）
        self.scihub_mirrors = [
            "https://sci-hub.se/",
            "https://sci-hub.st/",
            "https://sci-hub.ru/",
            # 添加更多可用的镜像站点
        ]
        
        # 设置请求头，模拟浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 创建下载目录
        self.base_dir = "PDF_PAPERS"
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def get_random_mirror(self):
        """随机选择一个镜像站点"""
        return random.choice(self.scihub_mirrors)

    def get_real_pdf_url(self, html_content, base_url):
        """从Sci-Hub页面提取真实的PDF下载链接"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 尝试多种可能的PDF链接位置
        pdf_url = None
        
        # 1. 尝试找iframe
        iframe = soup.find('iframe', id='pdf')
        if iframe and iframe.get('src'):
            pdf_url = iframe.get('src')
        
        # 2. 尝试找embed标签
        if not pdf_url:
            embed = soup.find('embed', type='application/pdf')
            if embed and embed.get('src'):
                pdf_url = embed.get('src')
        
        # 3. 尝试找特定的下载按钮或链接
        if not pdf_url:
            download_link = soup.find('a', string=lambda s: s and 'download' in s.lower())
            if download_link and download_link.get('href'):
                pdf_url = download_link.get('href')
        
        # 4. 尝试找object标签
        if not pdf_url:
            obj = soup.find('object', type='application/pdf')
            if obj and obj.get('data'):
                pdf_url = obj.get('data')

        # 确保URL是完整的
        if pdf_url:
            if pdf_url.startswith('//'):
                pdf_url = 'https:' + pdf_url
            elif not pdf_url.startswith('http'):
                pdf_url = urljoin(base_url, pdf_url)
            
            return pdf_url
        
        return None

    def download_pdf(self, doi, paper_info, max_retries=3):
        """下载单篇论文的PDF"""
        if not doi:
            return False

        # 创建会议特定的目录
        conf_dir = os.path.join(self.base_dir, paper_info['conference'], str(paper_info['year']))
        if not os.path.exists(conf_dir):
            os.makedirs(conf_dir)

        # 构建文件名：标题_作者.pdf
        first_author = paper_info['authors'][0]['name'] if paper_info['authors'] else 'Unknown'
        safe_title = "".join(x for x in paper_info['title'][:50] if x.isalnum() or x in (' ', '-', '_'))
        filename = f"{safe_title}_{first_author}.pdf".replace(' ', '_')
        filepath = os.path.join(conf_dir, filename)

        # 如果文件已存在，跳过
        if os.path.exists(filepath):
            print(f"文件已存在: {filepath}")
            return True

        # 尝试从不同镜像下载
        for attempt in range(max_retries):
            try:
                mirror = self.get_random_mirror()
                url = f"{mirror}{doi}"
                
                # 获取Sci-Hub页面
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                # 提取真实的PDF链接
                pdf_url = self.get_real_pdf_url(response.text, url)
                if not pdf_url:
                    print(f"无法找到PDF下载链接")
                    return False
                
                print(f"找到PDF链接: {pdf_url}")
                
                # 下载PDF
                pdf_response = requests.get(pdf_url, headers=self.headers, timeout=30)
                pdf_response.raise_for_status()
                
                # 验证是否是PDF文件
                content_type = pdf_response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and not pdf_response.content.startswith(b'%PDF'):
                    print(f"下载的文件不是PDF格式: {content_type}")
                    return False
                
                # 保存PDF
                with open(filepath, 'wb') as f:
                    f.write(pdf_response.content)
                
                print(f"成功下载: {filepath}")
                return True
                
            except Exception as e:
                print(f"尝试 {attempt + 1}/{max_retries} 失败: {str(e)}")
                if attempt < max_retries - 1:
                    delay = random.uniform(3, 6)  # 重试延迟增加到3-6秒
                    print(f"等待 {delay:.1f} 秒后重试...")
                    time.sleep(delay)
                continue
        
        return False

def load_papers(jsonl_file):
    """加载论文信息"""
    papers = []
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            paper = json.loads(line.strip())
            if paper.get('doi') or paper.get('ee'):  # 确保有DOI或其他链接
                papers.append(paper)
    return papers

def main():
    # 配置
    input_file = "papers.jsonl"
    
    # 加载论文数据
    print("加载论文数据...")
    papers = load_papers(input_file)
    print(f"找到 {len(papers)} 篇论文")
    
    # 初始化下载器
    downloader = SciHubDownloader()
    
    # 统计
    success_count = 0
    fail_count = 0
    
    # 开始下载
    print("\n开始下载PDF文件...")
    for paper in tqdm(papers):
        # 优先使用DOI，如果没有则使用ee链接
        identifier = paper.get('doi', '') or paper.get('ee', '')
        
        if identifier:
            if downloader.download_pdf(identifier, paper):
                success_count += 1
                # 成功后等待时间增加到10-15秒
                delay = random.uniform(10, 15)
                print(f"下载成功，等待 {delay:.1f} 秒后继续...")
                time.sleep(delay)
            else:
                fail_count += 1
                # 失败后等待时间增加到5-8秒
                delay = random.uniform(5, 8)
                print(f"下载失败，等待 {delay:.1f} 秒后继续...")
                time.sleep(delay)
    
    # 打印统计信息
    print(f"\n下载完成！")
    print(f"成功: {success_count} 篇")
    print(f"失败: {fail_count} 篇")

if __name__ == "__main__":
    print("注意：本插件的使用要有有效的代理！！！！！！！！SCIHUB代理才能访问")
    print("注意：请确保使用Sci-Hub下载论文符合您所在地区的法律法规。")
    print("      建议：优先考虑通过合法途径（如学校图书馆、作者主页等）获取论文。")
    response = input("是否继续？(y/n): ")
    if response.lower() == 'y':
        main()
    else:
        print("已取消下载。") 