#!/usr/bin/env python3
"""
AI文献数据分析工具
使用Gemini 2.5 Pro模型分析CNKI导出的文献数据
"""

import argparse
import csv
import os
import sys
from typing import List, Dict, Any
from openai import OpenAI

class GeminiAnalyzer:
    """使用Gemini 2.5 Pro进行文献数据分析"""
    
    def __init__(self, api_key: str = None, proxy_url: str = "https://yunwu.ai"):
        """
        初始化Gemini分析器
        
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
    
    def prepare_analysis_prompt(self, papers: List[Dict[str, Any]]) -> str:
        """
        准备分析提示词
        
        Args:
            papers: 文献数据列表
            
        Returns:
            分析提示词
        """
        # 统计基本信息
        total_papers = len(papers)
        
        # 提取关键信息用于分析
        titles = [paper.get('题名', '') for paper in papers if paper.get('题名')]
        keywords_list = [paper.get('关键词', '') for paper in papers if paper.get('关键词')]
        abstracts = [paper.get('摘要', '') for paper in papers if paper.get('摘要')]
        sources = [paper.get('来源', '') for paper in papers if paper.get('来源')]
        authors = [paper.get('作者', '') for paper in papers if paper.get('作者')]
        years = []
        
        # 提取发表年份
        for paper in papers:
            date_str = paper.get('发表时间', '')
            if date_str and len(date_str) >= 4:
                try:
                    year = date_str[:4]
                    if year.isdigit():
                        years.append(int(year))
                except:
                    pass
        
        # 统计数据
        year_counts = {}
        for year in years:
            year_counts[year] = year_counts.get(year, 0) + 1
        
        source_counts = {}
        for source in sources:
            if source:
                source_counts[source] = source_counts.get(source, 0) + 1
        
        # 创建文献条目列表
        papers_list = []
        for i, paper in enumerate(papers, 1):
            paper_info = f"{i}. {paper.get('题名', 'N/A')} - {paper.get('作者', 'N/A')} - {paper.get('来源', 'N/A')} - {paper.get('发表时间', 'N/A')}"
            papers_list.append(paper_info)
        
        # 构建分析提示词
        prompt = f"""
请分析以下学术文献数据，并生成一个完整的可视化HTML报告：

=== 数据概览 ===
总文献数量: {total_papers}篇
发表年份范围: {min(years) if years else '未知'} - {max(years) if years else '未知'}
主要期刊: {', '.join(list(source_counts.keys())[:5])}

=== 年份分布数据 ===
{str(dict(sorted(year_counts.items())))}

=== 期刊分布数据 ===
{str(dict(sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]))}

=== 文献标题样例 ===
{chr(10).join(titles[:15])}

=== 关键词样例 ===
{chr(10).join([kw for kw in keywords_list[:15] if kw])}

=== 分析要求 ===
请生成一个完整的HTML网页报告，包含以下内容：

1. **HTML页面结构**
   - 使用现代化的CSS样式和布局
   - 包含导航栏和侧边栏
   - 响应式设计
   - 使用Bootstrap或原生CSS

2. **可视化图表**
   - 使用Chart.js创建可交互图表
   - 发表年份趋势图（柱状图或折线图）
   - 期刊分布饼图
   - 关键词频次图
   - 被引次数分布图（如果有数据）

3. **数据分析内容**
   - 研究主题词云和主题分析
   - 时间趋势深度分析
   - 期刊影响因子和质量分析
   - 研究方法论分析
   - 作者合作网络
   - 创新点和研究热点识别

4. **文献条目清单**
   - 完整的文献表格，包含以下所有{total_papers}篇文献：
{chr(10).join(papers_list)}
   - 支持搜索、排序、筛选功能
   - 显示题名、作者、期刊、发表时间、被引次数等

5. **统计汇总**
   - 核心作者统计
   - 高产期刊统计
   - 研究热度变化
   - 跨学科合作程度

6. **研究建议和展望**
   - 基于数据的未来研究方向
   - 研究空白识别
   - 合作机会分析

请生成完整的HTML代码，包括：
- 完整的HTML文档结构
- 内嵌的CSS样式
- JavaScript交互代码
- Chart.js图表实现
- 数据表格和搜索功能

确保HTML可以独立运行，包含所有必要的CDN链接。请使用中文内容，确保分析深入、数据可视化美观清晰。
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
            print("正在调用Gemini API进行分析...")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.7
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
            output_file = f"analysis_report_{timestamp}.html"
        
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
    <title>文献数据AI分析报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .meta-info {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>文献数据AI分析报告</h1>
        <div class="meta-info">
            <p><strong>生成时间:</strong> {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>分析模型:</strong> {self.model_name}</p>
        </div>
        <div class="content">
            <pre>{analysis_result}</pre>
        </div>
    </div>
</body>
</html>"""
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write(html_content)
            
            print(f"分析报告已保存到: {output_file}")
            return output_file
            
        except Exception as e:
            raise Exception(f"保存分析报告时出错: {e}")
    
    def analyze(self, csv_file_path: str, output_file: str = None) -> str:
        """
        执行完整的文献数据分析流程
        
        Args:
            csv_file_path: CSV文件路径
            output_file: 输出文件路径
            
        Returns:
            分析报告文件路径
        """
        try:
            # 1. 加载数据
            print("正在加载文献数据...")
            papers = self.load_csv_data(csv_file_path)
            
            if not papers:
                raise Exception("CSV文件中没有有效数据")
            
            # 2. 准备分析提示词
            print("正在准备分析提示词...")
            prompt = self.prepare_analysis_prompt(papers)
            
            # 3. 调用AI分析
            analysis_result = self.call_gemini_api(prompt)
            
            # 4. 保存分析报告
            report_file = self.save_analysis_report(analysis_result, output_file)
            
            print("\n=== 分析完成 ===")
            print(f"分析了 {len(papers)} 条文献")
            print(f"报告文件: {report_file}")
            
            return report_file
            
        except Exception as e:
            print(f"分析过程中出错: {e}")
            sys.exit(1)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='使用Gemini 2.5 Pro分析CNKI文献数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python ai_analyze.py -i cnki_papers_20250623_213611.csv
  python ai_analyze.py -i data.csv -o my_analysis.md
  python ai_analyze.py -i data.csv --api-key your_key_here

环境变量:
  GEMINI_API_KEY    Gemini API密钥
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='输入的CSV文件路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出分析报告的文件路径（可选，默认自动生成）'
    )
    
    parser.add_argument(
        '--api-key',
        help='Gemini API密钥（可选，也可通过环境变量GEMINI_API_KEY设置）'
    )
    
    parser.add_argument(
        '--proxy-url',
        default='https://yunwu.ai',
        help='代理服务器地址（默认: https://yunwu.ai）'
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    print("=== AI文献数据分析工具 ===")
    print(f"输入文件: {args.input}")
    print(f"代理地址: {args.proxy_url}")
    print(f"使用模型: gemini-2.5-pro")
    print()
    
    # 创建分析器
    analyzer = GeminiAnalyzer(
        api_key=args.api_key,
        proxy_url=args.proxy_url
    )
    
    # 执行分析
    try:
        report_file = analyzer.analyze(args.input, args.output)
        print(f"\n✅ 分析完成！报告已保存到: {report_file}")
        
    except KeyboardInterrupt:
        print("\n用户中断了分析过程")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()