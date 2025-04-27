from playwright.sync_api import sync_playwright
import time
import sys

def launch_cnki(search_formula=None):
    """
    使用Playwright启动cnki.net网站并保持浏览器开启状态
    
    Args:
        search_formula (str): 要填入搜索框的检索式
    """
    if not search_formula:
        print("错误：未提供搜索式")
        return
        
    print("将使用以下检索式:")
    print(search_formula)
    
    with sync_playwright() as p:
        # 启动浏览器（默认使用chromium）
        browser = p.chromium.launch(headless=False)
        
        # 创建新的上下文和页面
        context = browser.new_context()
        page = context.new_page()
        
        # 导航到cnki.net
        page.goto("https://kns.cnki.net/kns8s/AdvSearch")
        print("成功导航到cnki.net")
        
        # 切换到专业检索
        major_search = page.locator("li[name='majorSearch']")
        major_search.click()
        
        # 定位文本框并输入搜索式
        text_area = page.locator("textarea.textarea-major.majorSearch.ac_input")
        text_area.fill(search_formula)
    
        # 点击检索按钮
        search_button = page.locator("input.btn-search")
        search_button.click()
        # 保持浏览器开启直到用户按下回车键
        print("按下回车键关闭浏览器...")
        input()
        
        # 关闭浏览器
        browser.close()
        print("浏览器已关闭")

if __name__ == "__main__":
    # 如果直接运行此脚本并提供搜索式作为命令行参数
    if len(sys.argv) > 1:
        search_formula = sys.argv[1]
        launch_cnki(search_formula)
    else:
        print("请提供搜索式作为参数")