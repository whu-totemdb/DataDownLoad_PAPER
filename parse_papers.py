import os
import json
import xml.etree.ElementTree as ET
from glob import glob
from datetime import datetime

def parse_author(author_elem):
    """解析作者信息"""
    return {
        'name': author_elem.text,
        'pid': author_elem.get('pid', '')
    }

def parse_paper(entry, conference, year, volume=None):
    """解析单篇论文信息"""
    info = entry.find('.//info')
    if info is None:
        return None
        
    paper = {
        'conference': conference,
        'year': year,
        'volume': volume,
        'title': info.find('title').text if info.find('title') is not None else '',
        'authors': [parse_author(author) for author in info.findall('.//author')],
        'doi': info.find('doi').text if info.find('doi') is not None else '',
        'url': info.find('url').text if info.find('url') is not None else '',
        'pages': info.find('pages').text if info.find('pages') is not None else '',
        'type': info.find('type').text if info.find('type') is not None else '',
        'key': info.find('key').text if info.find('key') is not None else '',
        'venue': info.find('venue').text if info.find('venue') is not None else '',
    }
    
    # 提取可能存在的额外信息
    if info.find('year') is not None:
        paper['published_year'] = info.find('year').text
    if info.find('access') is not None:
        paper['access'] = info.find('access').text
    if info.find('ee') is not None:
        paper['ee'] = info.find('ee').text
    
    return paper

def process_xml_file(file_path):
    """处理单个XML文件"""
    try:
        # 从文件名解析会议信息
        filename = os.path.basename(file_path)
        if filename.startswith('icde_'):
            conference = 'ICDE'
            year = int(filename.split('_')[1].split('.')[0])
            volume = None
        elif filename.startswith('sigmod_'):
            conference = 'SIGMOD'
            year = int(filename.split('_')[1].split('.')[0])
            volume = None
        elif filename.startswith('vldb_'):
            conference = 'VLDB'
            year = int(filename.split('_')[1])
            volume = int(filename.split('vol')[1].split('.')[0])
        else:
            return []

        # 解析XML文件
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # 提取所有论文信息
        papers = []
        for hit in root.findall('.//hit'):
            try:
                paper = parse_paper(hit, conference, year, volume)
                if paper is not None:
                    papers.append(paper)
            except Exception as e:
                print(f"解析论文时出错 {file_path}: {str(e)}")
                continue
                
        return papers
        
    except Exception as e:
        print(f"处理文件时出错 {file_path}: {str(e)}")
        return []

def main():
    # 输出文件
    output_file = "papers.jsonl"
    
    # 获取所有XML文件
    xml_files = []
    xml_files.extend(glob("ICDE_PAPER/*.xml"))
    xml_files.extend(glob("SIGMOD_PAPER/*.xml"))
    xml_files.extend(glob("VLDB_PAPER/*.xml"))
    
    total_papers = 0
    
    # 处理所有文件并写入JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for xml_file in sorted(xml_files):
            print(f"正在处理: {xml_file}")
            papers = process_xml_file(xml_file)
            for paper in papers:
                json.dump(paper, f, ensure_ascii=False)
                f.write('\n')
            total_papers += len(papers)
            print(f"已解析 {len(papers)} 篇论文")
    
    print(f"\n处理完成！")
    print(f"总共处理了 {len(xml_files)} 个文件")
    print(f"总共解析了 {total_papers} 篇论文")
    print(f"结果已保存到: {output_file}")

if __name__ == "__main__":
    main() 