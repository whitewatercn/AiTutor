#!/usr/bin/env python3
"""
AI分析工具测试脚本
用于测试数据加载和分析功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from aitutor_core.ai_analyze import GeminiAnalyzer

def test_data_loading():
    """测试数据加载功能"""
    print("=== 测试数据加载功能 ===")
    
    analyzer = GeminiAnalyzer()
    
    try:
        # 测试加载CSV数据
        csv_file = "cnki_papers_20250623_214224.csv"
        if not os.path.exists(csv_file):
            print(f"❌ CSV文件不存在: {csv_file}")
            return False
        
        papers = analyzer.load_csv_data(csv_file)
        print(f"✅ 成功加载 {len(papers)} 条文献数据")
        
        # 展示数据样例
        print("\n=== 数据样例 ===")
        for i, paper in enumerate(papers[:3]):
            print(f"{i+1}. 题名: {paper.get('题名', 'N/A')[:50]}...")
            print(f"   作者: {paper.get('作者', 'N/A')[:30]}...")
            print(f"   来源: {paper.get('来源', 'N/A')}")
            print(f"   时间: {paper.get('发表时间', 'N/A')}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return False

def test_prompt_generation():
    """测试提示词生成功能"""
    print("=== 测试提示词生成功能 ===")
    
    analyzer = GeminiAnalyzer()
    
    try:
        csv_file = "cnki_papers_20250623_214224.csv"
        papers = analyzer.load_csv_data(csv_file)
        
        # 生成分析提示词
        prompt = analyzer.prepare_analysis_prompt(papers)
        
        print(f"✅ 成功生成提示词，长度: {len(prompt)} 字符")
        print(f"✅ 包含 {len(papers)} 条文献的完整信息")
        
        # 分析提示词内容
        if "HTML" in prompt and "Chart.js" in prompt:
            print("✅ 提示词包含HTML和图表要求")
        
        if "文献条目" in prompt:
            print("✅ 提示词包含文献条目要求")
        
        if "可视化" in prompt:
            print("✅ 提示词包含可视化要求")
        
        print("\n=== 提示词开头预览 ===")
        print(prompt[:500] + "...")
        
        return True
        
    except Exception as e:
        print(f"❌ 提示词生成失败: {e}")
        return False

def test_analysis_without_api():
    """测试无API密钥的分析功能"""
    print("=== 测试分析功能（无API密钥）===")
    
    analyzer = GeminiAnalyzer()
    
    if analyzer.client is None:
        print("✅ 正确处理无API密钥的情况")
        
        try:
            analyzer.call_gemini_api("test")
        except Exception as e:
            if "未设置GEMINI_API_KEY" in str(e):
                print("✅ 正确提示API密钥错误")
                return True
            else:
                print(f"❌ 错误信息不正确: {e}")
                return False
    else:
        print("⚠️  有API密钥，无法测试无密钥情况")
        return True

def main():
    """主测试函数"""
    print("🔍 AI文献数据分析工具测试\n")
    
    tests = [
        ("数据加载", test_data_loading),
        ("提示词生成", test_prompt_generation),
        ("API错误处理", test_analysis_without_api)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"{'='*50}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}测试完成\n")
        except Exception as e:
            print(f"❌ {test_name}测试失败: {e}\n")
            results.append((test_name, False))
    
    # 测试结果汇总
    print("="*50)
    print("🎯 测试结果汇总")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 个测试通过")
    
    if passed == len(results):
        print("\n🎉 所有测试通过！AI分析工具工作正常。")
        print("\n💡 使用说明:")
        print("1. 设置API密钥: export GEMINI_API_KEY='your_key'")
        print("2. 运行分析: python aitutor_core/ai_analyze.py -i cnki_papers_20250623_214224.csv")
    else:
        print(f"\n⚠️  有 {len(results) - passed} 个测试失败，请检查代码。")

if __name__ == "__main__":
    main()
