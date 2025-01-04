import json
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

def load_papers(jsonl_file):
    """加载论文数据"""
    papers = {}
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            paper = json.loads(line.strip())
            # 使用DOI作为主键，如果没有DOI则使用URL
            key = paper.get('doi', '') or paper.get('url', '')
            if key:
                papers[key] = paper
    return papers

def create_paper_text(paper):
    """将论文信息组合成文本"""
    # 组合标题、作者和venue信息
    text_parts = []
    
    # 添加标题
    if paper.get('title'):
        text_parts.append(paper['title'])
    
    # 添加作者
    authors = [author['name'] for author in paper.get('authors', [])]
    if authors:
        text_parts.append("Authors: " + ", ".join(authors))
    
    # 添加会议信息
    if paper.get('conference'):
        text_parts.append(f"Conference: {paper['conference']} {paper.get('year', '')}")
    
    # 添加venue信息
    if paper.get('venue'):
        text_parts.append(f"Venue: {paper['venue']}")
    
    return " | ".join(text_parts)

def generate_embeddings(papers, model_name='all-MiniLM-L6-v2', batch_size=32):
    """生成论文嵌入"""
    # 加载模型
    print(f"加载模型: {model_name}")
    model = SentenceTransformer(model_name)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)
    
    # 准备数据
    keys = list(papers.keys())
    texts = [create_paper_text(papers[key]) for key in keys]
    
    # 生成嵌入
    print("生成嵌入...")
    embeddings = {}
    
    # 使用批处理来提高效率
    for i in tqdm(range(0, len(texts), batch_size)):
        batch_texts = texts[i:i + batch_size]
        batch_keys = keys[i:i + batch_size]
        
        # 生成当前批次的嵌入
        batch_embeddings = model.encode(batch_texts, convert_to_tensor=True)
        
        # 将张量转换为列表并保存
        for key, embedding in zip(batch_keys, batch_embeddings):
            embeddings[key] = embedding.cpu().numpy().tolist()
    
    return embeddings

def save_embeddings(embeddings, output_file):
    """保存嵌入到JSON文件"""
    print(f"保存嵌入到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(embeddings, f, ensure_ascii=False, indent=2)

def main():
    # 配置
    input_file = "papers.jsonl"
    output_file = "paper_embeddings.json"
    model_name = 'all-MiniLM-L6-v2'  # 使用轻量级模型
    batch_size = 32
    
    # 加载论文数据
    print(f"加载论文数据从: {input_file}")
    papers = load_papers(input_file)
    print(f"加载了 {len(papers)} 篇论文")
    
    # 生成嵌入
    embeddings = generate_embeddings(papers, model_name, batch_size)
    print(f"生成了 {len(embeddings)} 个嵌入")
    
    # 保存结果
    save_embeddings(embeddings, output_file)
    print("完成！")

if __name__ == "__main__":
    print("【所有下载程序都简单验证过】该嵌入文件没有运行过，如果有bug请自行修改！")
    main() 