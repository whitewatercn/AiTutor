import csv
import os
from datetime import datetime

class PaperCSVWriter:
    """文献CSV文件写入器，支持逐条写入数据"""
    
    def __init__(self, filename=None):
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cnki_papers_{timestamp}.csv"
        
        # 确保文件保存在项目根目录
        project_root = os.path.dirname(os.path.dirname(__file__))
        self.filepath = os.path.join(project_root, filename)
        
        # CSV列名
        self.fieldnames = [
            '题名', '作者', '来源', '发表时间', '数据库', '被引', '下载',
            '摘要', '关键词', '基金资助', '专辑', '专题', '分类号', 'DOI'
        ]
        
        self.paper_count = 0
        self._initialize_csv()
    
    def _initialize_csv(self):
        """初始化CSV文件，写入表头"""
        try:
            with open(self.filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()
            print(f"CSV文件已创建: {self.filepath}")
        except Exception as e:
            print(f"初始化CSV文件时出错: {e}")
            raise
    
    def write_paper(self, paper_data):
        """写入单条文献数据到CSV文件"""
        try:
            with open(self.filepath, 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                
                # 确保所有字段都存在
                row = {}
                for field in self.fieldnames:
                    row[field] = paper_data.get(field, "")
                
                writer.writerow(row)
                self.paper_count += 1
                print(f"已保存第 {self.paper_count} 条文献到CSV: {paper_data.get('题名', 'N/A')[:50]}...")
                
        except Exception as e:
            print(f"写入CSV文件时出错: {e}")
    
    def get_filepath(self):
        """获取CSV文件路径"""
        return self.filepath
    
    def get_count(self):
        """获取已写入的文献数量"""
        return self.paper_count
    
    def close(self):
        """关闭CSV写入器（清理资源）"""
        print(f"CSV写入完成，共保存 {self.paper_count} 条文献记录")
        print(f"文件位置: {self.filepath}")

def create_paper_csv_writer(filename=None):
    """
    创建文献CSV写入器的工厂函数
    
    Args:
        filename: 可选的文件名，如果不提供则自动生成
        
    Returns:
        PaperCSVWriter: CSV写入器实例
    """
    return PaperCSVWriter(filename)

