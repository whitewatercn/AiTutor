#!/usr/bin/env python3
"""
增强版AI文献数据分析工具
使用Gemini 2.5 Pro模型分析CNKI导出的文献数据
生成更丰富的可视化HTML报告
"""

import argparse
import csv
import os
import sys
import json
from typing import List, Dict, Any
from openai import OpenAI

class EnhancedGeminiAnalyzer:
    """增强版Gemini文献数据分析器"""
    
    def __init__(self, api_key: str = None, proxy_url: str = "https://yunwu.ai"):
        """
        初始化增强版Gemini分析器
        
        Args:
            api_key: Gemini API密钥
            proxy_url: 代理服务器地址
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.proxy_url = proxy_url.rstrip('/')
        self.model_name = "gemini-2.5-pro"
        
        if not self.api_key:
            print("警告: 未找到GEMINI_API_KEY环境变量，请设置API密钥")
            print("可以通过以下方式设置:")
            print("export GEMINI_API_KEY='your_api_key_here'")
        
        # 初始化OpenAI客户端，使用代理URL
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=f"{self.proxy_url}/v1"
            )
        else:
            self.client = None
    
    def load_csv_data(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """
        从CSV文件加载文献数据
        
        Args:
            csv_file_path: CSV文件路径
            
        Returns:
            文献数据列表
        """
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"CSV文件不存在: {csv_file_path}")
        
        papers = []
        try:
            with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    papers.append(dict(row))
            
            print(f"成功加载 {len(papers)} 条文献数据")
            return papers
            
        except Exception as e:
            raise Exception(f"读取CSV文件时出错: {e}")
    
    def preprocess_data(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        预处理文献数据，生成详细统计信息
        
        Args:
            papers: 文献数据列表
            
        Returns:
            预处理后的统计数据
        """
        stats = {
            'total_papers': len(papers),
            'years': [],
            'year_counts': {},
            'source_counts': {},
            'keyword_counts': {},
            'author_counts': {},
            'citation_stats': {'total': 0, 'max': 0, 'avg': 0, 'distribution': {}},
            'download_stats': {'total': 0, 'max': 0, 'avg': 0, 'distribution': {}},
            'papers_data': []
        }
        
        all_keywords = []
        all_authors = []
        citations = []
        downloads = []
        
        # 处理每篇文献
        for i, paper in enumerate(papers, 1):
            # 提取年份
            date_str = paper.get('发表时间', '')
            year = None
            if date_str and len(date_str) >= 4:
                try:
                    year = int(date_str[:4])
                    if 1900 <= year <= 2030:  # 合理的年份范围
                        stats['years'].append(year)
                        stats['year_counts'][year] = stats['year_counts'].get(year, 0) + 1
                except:
                    pass
            
            # 处理期刊
            source = paper.get('来源', '').strip()
            if source:
                stats['source_counts'][source] = stats['source_counts'].get(source, 0) + 1
            
            # 处理关键词
            keywords_str = paper.get('关键词', '')
            paper_keywords = []
            if keywords_str:
                keywords = [k.strip() for k in keywords_str.replace('；', ';').replace(',', ';').split(';') if k.strip()]
                paper_keywords = keywords
                all_keywords.extend(keywords)
            
            # 处理作者
            authors_str = paper.get('作者', '')
            paper_authors = []
            if authors_str:
                authors = [a.strip() for a in authors_str.replace('；', ';').replace(',', ';').split(';') if a.strip()]
                paper_authors = authors
                all_authors.extend(authors)
            
            # 处理被引和下载次数
            try:
                citation_count = int(paper.get('被引', '0') or '0')
                citations.append(citation_count)
            except:
                citations.append(0)
            
            try:
                download_count = int(paper.get('下载', '0') or '0')
                downloads.append(download_count)
            except:
                downloads.append(0)
            
            # 构建文献数据
            paper_data = {
                'id': i,
                'title': paper.get('题名', 'N/A').strip(),
                'authors': paper.get('作者', 'N/A').strip(),
                'source': source or 'N/A',
                'date': paper.get('发表时间', 'N/A').strip(),
                'year': year,
                'citations': citations[-1],
                'downloads': downloads[-1],
                'keywords': ', '.join(paper_keywords) if paper_keywords else 'N/A',
                'abstract': (paper.get('摘要', '') or '').strip()[:300] + '...' if paper.get('摘要', '') else 'N/A',
                'database': paper.get('数据库', 'N/A').strip(),
                'funding': paper.get('基金资助', 'N/A').strip(),
                'doi': paper.get('DOI', 'N/A').strip()
            }
            stats['papers_data'].append(paper_data)
        
        # 统计关键词和作者
        for keyword in all_keywords:
            stats['keyword_counts'][keyword] = stats['keyword_counts'].get(keyword, 0) + 1
        
        for author in all_authors:
            stats['author_counts'][author] = stats['author_counts'].get(author, 0) + 1
        
        # 计算被引和下载统计
        if citations:
            stats['citation_stats']['total'] = sum(citations)
            stats['citation_stats']['max'] = max(citations)
            stats['citation_stats']['avg'] = round(sum(citations) / len(citations), 2)
            
            # 被引分布
            citation_ranges = {'0': 0, '1-5': 0, '6-10': 0, '11-20': 0, '21-50': 0, '50+': 0}
            for c in citations:
                if c == 0:
                    citation_ranges['0'] += 1
                elif 1 <= c <= 5:
                    citation_ranges['1-5'] += 1
                elif 6 <= c <= 10:
                    citation_ranges['6-10'] += 1
                elif 11 <= c <= 20:
                    citation_ranges['11-20'] += 1
                elif 21 <= c <= 50:
                    citation_ranges['21-50'] += 1
                else:
                    citation_ranges['50+'] += 1
            stats['citation_stats']['distribution'] = citation_ranges
        
        if downloads:
            stats['download_stats']['total'] = sum(downloads)
            stats['download_stats']['max'] = max(downloads)
            stats['download_stats']['avg'] = round(sum(downloads) / len(downloads), 2)
        
        return stats
    
    def generate_enhanced_prompt(self, stats: Dict[str, Any]) -> str:
        """
        生成增强版分析提示词
        
        Args:
            stats: 预处理的统计数据
            
        Returns:
            增强版分析提示词
        """
        # 获取TOP数据
        top_sources = dict(list(sorted(stats['source_counts'].items(), key=lambda x: x[1], reverse=True)[:10]))
        top_keywords = dict(list(sorted(stats['keyword_counts'].items(), key=lambda x: x[1], reverse=True)[:20]))
        top_authors = dict(list(sorted(stats['author_counts'].items(), key=lambda x: x[1], reverse=True)[:10]))
        
        year_range = f"{min(stats['years'])}-{max(stats['years'])}" if stats['years'] else "未知"
        
        # 将papers_data转换为JSON字符串，避免f-string中的复杂表达式
        papers_json_str = json.dumps(stats['papers_data'][:3], ensure_ascii=False, indent=2)
        year_counts_str = json.dumps(dict(sorted(stats['year_counts'].items())), ensure_ascii=False)
        top_sources_str = json.dumps(top_sources, ensure_ascii=False)
        top_keywords_str = json.dumps(top_keywords, ensure_ascii=False)
        top_authors_str = json.dumps(top_authors, ensure_ascii=False)
        citation_dist_str = json.dumps(stats['citation_stats']['distribution'], ensure_ascii=False)
        
        prompt = f"""
作为顶级学术文献数据分析专家和前端可视化工程师，请为以下CNKI文献数据生成一个专业级的、完整的HTML可视化分析报告。

=== 数据统计总览 ===
📊 总文献数量: {stats['total_papers']}篇
📅 发表年份范围: {year_range}
📰 覆盖期刊数量: {len(stats['source_counts'])}种
🔑 关键词总数: {len(stats['keyword_counts'])}个
👥 涉及作者数: {len(stats['author_counts'])}人
📈 总被引次数: {stats['citation_stats']['total']}
⭐ 平均被引次数: {stats['citation_stats']['avg']}
📥 总下载次数: {stats['download_stats']['total']}

=== 详细统计数据 ===

**年度发文统计:**
{year_counts_str}

**期刊分布TOP10:**
{top_sources_str}

**高频关键词TOP20:**
{top_keywords_str}

**高产作者TOP10:**
{top_authors_str}

**被引分布区间:**
{citation_dist_str}

=== HTML报告生成要求 ===

请生成一个完整的、现代化的、可独立运行的HTML学术分析报告，包含以下模块：

## 1. 页面架构与设计
- **框架**: Bootstrap 5.3.0 + 自定义CSS + JavaScript
- **主题**: 深色/浅色主题切换 (默认深色主题)
- **布局**: 响应式设计，支持桌面端和移动端
- **导航**: 固定顶部导航栏，包含5个主要模块
  - 📊 数据概览 (Overview)
  - 📈 图表分析 (Charts) 
  - 📚 文献库 (Literature)
  - 📋 统计报告 (Statistics)
  - 💡 研究建议 (Insights)
- **配色**: 现代化配色方案 (主色调: #3B82F6, 辅色: #10B981, 背景渐变)
- **效果**: 毛玻璃效果、平滑过渡动画、加载动画

## 2. 核心可视化模块 (使用Chart.js 4.4.0)

### A) 发表趋势分析图
- **类型**: 混合图表 (柱状图 + 折线图)
- **数据**: 年度发文量 + 累计趋势
- **交互**: 悬浮显示详细数据

### B) 期刊影响力分析
- **类型**: 水平柱状图
- **数据**: TOP10期刊发文量
- **功能**: 点击查看该期刊的所有文献

### C) 关键词云图
- **库**: wordcloud2.js
- **数据**: 关键词频次
- **交互**: 点击关键词筛选相关文献

### D) 被引分析图表
- **类型**: 分组柱状图 + 散点图
- **内容**: 被引分布区间 + 高被引文献标注
- **功能**: 识别高影响力文献

### E) 作者合作网络
- **类型**: 网络关系图 (简化版)
- **数据**: 高产作者及其合作关系
- **交互**: 节点点击查看作者详情

### F) 研究热点时间轴
- **类型**: 时间轴 + 热力图
- **内容**: 关键词随时间的变化趋势

## 3. 完整文献数据表 (DataTables 1.13.6)

**包含所有 {stats['total_papers']} 篇文献的完整信息:**

**示例数据结构:**
{papers_json_str}

**表格功能:**
- ✅ 全文搜索 (支持中文)
- ✅ 多列排序
- ✅ 分页显示 (每页20条)
- ✅ 列筛选器
- ✅ 导出功能 (CSV/Excel/PDF)
- ✅ 点击标题展开摘要
- ✅ 响应式表格设计

**表格列设计:**
1. 序号 | 2. 题名 | 3. 作者 | 4. 期刊 | 5. 发表时间
6. 被引次数 | 7. 下载次数 | 8. 关键词 | 9. 操作

## 4. 数据仪表盘
**关键指标卡片:**
- 📊 总文献数: {stats['total_papers']}
- 📅 时间跨度: {year_range}
- 📈 总被引数: {stats['citation_stats']['total']}
- ⭐ 平均被引: {stats['citation_stats']['avg']}
- 📰 期刊覆盖: {len(stats['source_counts'])}种
- 🔑 关键词数: {len(stats['keyword_counts'])}个

**动态统计图表:**
- 研究活跃度指数
- 学术影响力评分
- 国际化程度分析

## 5. 深度分析报告

### A) 研究趋势演变
- 发文量年度变化趋势分析
- 研究热点的兴起和衰落
- 学科发展阶段判断

### B) 期刊质量评估
- 核心期刊发文分布
- 期刊影响因子对比
- 期刊专业化程度分析

### C) 学术影响力分析
- 高被引文献特征分析
- 学术贡献度评估
- 引用网络分析

### D) 研究合作模式
- 作者合作网络分析
- 机构合作程度
- 跨学科研究识别

### E) 创新点识别
- 新兴关键词发现
- 研究空白领域识别
- 方法论创新趋势

## 6. 智能研究建议

### A) 未来研究方向
- 基于趋势的热点预测
- 研究空白领域推荐
- 跨学科融合机会

### B) 合作机会分析
- 潜在合作伙伴推荐
- 优势期刊投稿建议
- 研究团队组建建议

### C) 方法论改进
- 研究方法创新建议
- 数据收集优化方案
- 分析框架改进思路

## 技术实现要求:

### HTML结构:
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <!-- Meta标签、标题、CDN链接 -->
</head>
<body>
    <!-- 导航栏 -->
    <!-- 主要内容区域 -->
    <!-- 所有JavaScript代码 -->
</body>
</html>
```

### 必需的CDN链接:
- Bootstrap 5.3.0 (CSS + JS)
- Chart.js 4.4.0
- DataTables 1.13.6 (含中文语言包)
- wordcloud2.js
- Font Awesome 6.4.0 (图标)

### 核心要求:
1. ✅ 完整HTML文档，可直接在浏览器打开
2. ✅ 所有{stats['total_papers']}篇文献数据完整展示
3. ✅ 图表数据准确对应统计结果
4. ✅ 移动端完美适配
5. ✅ 中文字符正确显示
6. ✅ 加载性能优化
7. ✅ 代码结构清晰，便于维护

### 交互体验:
- 🎯 平滑的页面滚动和跳转
- 🎨 优雅的加载动画
- 🔄 主题切换功能
- 📱 移动端手势支持
- 🔍 智能搜索建议
- 💾 数据导出功能

请生成完整的HTML代码，确保专业性、美观性和功能完整性！
"""
        return prompt
    
    def call_gemini_api(self, prompt: str) -> str:
        """
        调用Gemini API进行分析
        
        Args:
            prompt: 分析提示词
            
        Returns:
            分析结果
        """
        if not self.api_key:
            raise Exception("未设置GEMINI_API_KEY，无法调用API")
        
        try:
            print("🚀 正在调用Gemini 2.5 Pro进行深度分析...")
            print("💡 提示：生成完整HTML可视化报告可能需要2-3分钟，请耐心等待...")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位世界顶级的学术文献数据分析专家和全栈开发工程师，擅长使用现代前端技术生成专业级的学术可视化报告。你的任务是创建完整的、可独立运行的HTML文档，包含丰富的交互功能、美观的可视化图表和深度的学术分析内容。请确保生成的HTML代码完整、高质量、符合现代Web标准。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=8000,  # 增加token限制以生成更完整的HTML
                temperature=0.2   # 降低随机性，提高生成质量和一致性
            )
            
            return response.choices[0].message.content
                
        except Exception as e:
            raise Exception(f"API调用失败: {e}")
    
    def save_analysis_report(self, analysis_result: str, output_file: str = None) -> str:
        """
        保存分析报告
        
        Args:
            analysis_result: 分析结果
            output_file: 输出文件路径
            
        Returns:
            保存的文件路径
        """
        if not output_file:
            timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"enhanced_analysis_report_{timestamp}.html"
        
        try:
            # 如果返回的是HTML代码，直接保存
            if analysis_result.strip().startswith('<!DOCTYPE html') or analysis_result.strip().startswith('<html'):
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write(analysis_result)
            else:
                # 如果不是HTML，包装为HTML格式
                html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>增强版文献数据AI分析报告</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            font-family: 'Microsoft YaHei', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
        }}
        .meta-info {{
            background: linear-gradient(45deg, #f39c12, #f1c40f);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .content {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }}
        pre {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 14px;
        }}
        .highlight {{
            background: #3498db;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 增强版文献数据AI分析报告</h1>
        <div class="meta-info">
            <h3>📋 报告信息</h3>
            <p><strong>🕒 生成时间:</strong> {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>🤖 分析模型:</strong> <span class="highlight">{self.model_name}</span></p>
            <p><strong>⚡ 版本:</strong> Enhanced AI Analyzer v2.0</p>
        </div>
        <div class="content">
            <h2>📄 分析内容</h2>
            <pre>{analysis_result}</pre>
        </div>
        <div class="mt-4 text-center">
            <p class="text-muted">💡 提示：如果内容不是HTML格式，请检查API响应或重新生成</p>
        </div>
    </div>
</body>
</html>"""
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write(html_content)
            
            print(f"✅ 分析报告已保存到: {output_file}")
            return output_file
            
        except Exception as e:
            raise Exception(f"保存分析报告时出错: {e}")
    
    def analyze(self, csv_file_path: str, output_file: str = None) -> str:
        """
        执行完整的增强版文献数据分析流程
        
        Args:
            csv_file_path: CSV文件路径
            output_file: 输出文件路径
            
        Returns:
            分析报告文件路径
        """
        try:
            print("🔄 开始增强版文献数据分析...")
            
            # 1. 加载数据
            print("📂 正在加载文献数据...")
            papers = self.load_csv_data(csv_file_path)
            
            if not papers:
                raise Exception("CSV文件中没有有效数据")
            
            # 2. 数据预处理
            print("⚙️ 正在进行数据预处理和统计分析...")
            stats = self.preprocess_data(papers)
            
            # 3. 生成增强版提示词
            print("🎯 正在准备增强版分析提示词...")
            prompt = self.generate_enhanced_prompt(stats)
            
            # 4. 调用AI分析
            analysis_result = self.call_gemini_api(prompt)
            
            # 5. 保存分析报告
            report_file = self.save_analysis_report(analysis_result, output_file)
            
            print("\n" + "="*60)
            print("🎉 增强版分析完成！")
            print("="*60)
            print(f"📊 分析了 {len(papers)} 条文献")
            print(f"📅 年份范围: {min(stats['years']) if stats['years'] else '未知'} - {max(stats['years']) if stats['years'] else '未知'}")
            print(f"📰 涉及期刊: {len(stats['source_counts'])} 种")
            print(f"🔑 关键词数: {len(stats['keyword_counts'])} 个")
            print(f"👥 作者人数: {len(stats['author_counts'])} 人")
            print(f"📈 总被引数: {stats['citation_stats']['total']}")
            print(f"📄 报告文件: {report_file}")
            print("="*60)
            
            return report_file
            
        except Exception as e:
            print(f"❌ 分析过程中出错: {e}")
            sys.exit(1)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='🚀 增强版AI文献数据分析工具 - 使用Gemini 2.5 Pro生成专业可视化报告',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
📖 使用示例:
  python ai_analyze_enhanced.py -i cnki_papers_20250623_214224.csv
  python ai_analyze_enhanced.py -i data.csv -o my_enhanced_report.html
  python ai_analyze_enhanced.py -i data.csv --api-key your_key_here

🌍 环境变量:
  GEMINI_API_KEY    Gemini API密钥

✨ 功能特点:
  • 🎨 现代化可视化界面
  • 📊 丰富的交互式图表
  • 📚 完整的文献数据表格
  • 🔍 智能搜索和筛选
  • 📱 移动端完美适配
  • 🌓 深色/浅色主题切换
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='📂 输入的CSV文件路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='📄 输出分析报告的文件路径（可选，默认自动生成）'
    )
    
    parser.add_argument(
        '--api-key',
        help='🔑 Gemini API密钥（可选，也可通过环境变量GEMINI_API_KEY设置）'
    )
    
    parser.add_argument(
        '--proxy-url',
        default='https://yunwu.ai',
        help='🌐 代理服务器地址（默认: https://yunwu.ai）'
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    print("🚀 增强版AI文献数据分析工具")
    print("="*50)
    print(f"📂 输入文件: {args.input}")
    print(f"🌐 代理地址: {args.proxy_url}")
    print(f"🤖 使用模型: gemini-2.5-pro")
    print(f"⚡ 版本: Enhanced v2.0")
    print("="*50)
    print()
    
    # 创建增强版分析器
    analyzer = EnhancedGeminiAnalyzer(
        api_key=args.api_key,
        proxy_url=args.proxy_url
    )
    
    # 执行分析
    try:
        report_file = analyzer.analyze(args.input, args.output)
        print(f"\n🎊 分析完成！增强版报告已保存到: {report_file}")
        print("💡 提示：用浏览器打开HTML文件查看完整的可视化报告")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断了分析过程")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
