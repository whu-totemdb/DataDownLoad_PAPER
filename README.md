# 数据库顶会论文下载与分析工具

这个项目提供了一套工具，用于下载和分析ICDE、SIGMOD和VLDB这三个数据库领域顶级会议的论文信息。项目包含论文数据下载、解析和语义向量生成等功能。（PDF全文运行下载文件50小时则可拿到全文）

## 功能特点

- 支持三大顶会论文信息的批量下载：
  - ICDE (IEEE International Conference on Data Engineering)
  - SIGMOD (ACM Special Interest Group on Management of Data)
  - VLDB (International Conference on Very Large Data Bases)
- 自动处理不同年份的特殊格式
- 支持XML格式的数据解析
- 使用Sentence-BERT生成论文的语义向量
- 支持GPU加速（如果可用）

## 项目结构

```
.
├── download_icde_papers.py    # ICDE论文下载脚本
├── download_sigmod_papers.py  # SIGMOD论文下载脚本
├── download_vldb_papers.py    # VLDB论文下载脚本
├── parse_papers.py           # XML解析脚本
├── generate_embeddings.py    # 语义向量生成脚本
├── requirements.txt         # 项目依赖
└── README.md               # 项目说明文档
```

## 安装

1. 克隆项目到本地
2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用说明

### 1. 下载论文数据

#### ICDE论文下载
```bash
python download_icde_papers.py
```
- 支持1984年至今的论文
- 2000年前使用两位数年份格式
- 下载的文件保存在 `ICDE_PAPER` 目录

#### SIGMOD论文下载
```bash
python download_sigmod_papers.py
```
- 支持1975年至今的论文
- 2000年前使用两位数年份格式
- 2023年后使用特殊格式
- 下载的文件保存在 `SIGMOD_PAPER` 目录

#### VLDB论文下载
```bash
python download_vldb_papers.py
```
- 支持2008年后的论文（PVLDB格式）
- 使用卷号系统（如2024年对应第17卷）
- 下载的文件保存在 `VLDB_PAPER` 目录

### 2. 解析论文数据

```bash
python parse_papers.py
```
- 将所有XML文件解析为统一的JSONL格式
- 提取标题、作者、DOI等信息
- 输出文件：`papers.jsonl`

### 3. 生成语义向量

```bash
python generate_embeddings.py
```
- 使用Sentence-BERT生成论文的语义向量
- 支持GPU加速
- 使用DOI作为主键
- 输出文件：`paper_embeddings.json`

## 输出文件格式

### papers.jsonl
每行一个JSON对象，包含以下字段：
```json
{
    "conference": "会议名称",
    "year": "年份",
    "volume": "卷号(仅VLDB)",
    "title": "论文标题",
    "authors": [
        {
            "name": "作者名",
            "pid": "作者ID"
        }
    ],
    "doi": "DOI",
    "url": "DBLP URL",
    "pages": "页码",
    "type": "论文类型",
    "venue": "会议venue",
    "published_year": "出版年份",
    "access": "访问类型",
    "ee": "电子版链接"
}
```

### paper_embeddings.json
使用DOI作为键的向量映射：
```json
{
    "10.1109/...": [0.123, 0.456, ...],
    "https://...": [0.789, 0.012, ...]
}
```

## 注意事项

1. 下载间隔
   - 每次成功下载后等待10秒
   - 下载失败后等待1秒
   - 避免对服务器造成压力

2. 存储空间
   - XML文件和JSONL文件需要一定存储空间
   - 向量文件可能较大，建议确保足够磁盘空间

3. GPU支持
   - 如果有GPU，生成向量时会自动使用
   - 无GPU则使用CPU处理

4. 错误处理
   - 程序会自动处理和跳过错误
   - 详细的错误信息会被打印出来

## 可能的应用

- 论文相似度计算
- 论文聚类分析
- 研究主题趋势分析
- 作者合作关系分析
- 论文推荐系统

## 依赖版本

- requests==2.31.0
- sentence-transformers==2.2.2
- torch==2.1.0
- tqdm==4.66.1

## 许可证

MIT License 
