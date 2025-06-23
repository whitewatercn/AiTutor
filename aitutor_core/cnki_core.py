from playwright.sync_api import sync_playwright
import time
import sys
from csv_tool import create_paper_csv_writer

def extract_paper_info(page):
    """
    从文献列表页面提取每条文献的基本信息，支持多页翻页
    
    Args:
        page: Playwright页面对象
        
    Returns:
        list: 包含文献基本信息的列表
    """
    all_papers = []
    current_page = 1
    
    while True:
        print(f"正在抓取第 {current_page} 页...")
        
        try:
            # 等待搜索结果加载
            page.wait_for_selector(".result-table-list", timeout=10000)
            time.sleep(3)
            
            # 获取当前页的所有文献条目 - 使用更精确的选择器定位tr元素
            paper_rows = page.locator("table.result-table-list tbody tr")
            count = paper_rows.count()
            print(f"第 {current_page} 页找到 {count} 条文献")
            
            if count == 0:
                print("当前页没有找到文献，可能已到最后一页")
                break
            
            # 提取当前页的文献信息
            for i in range(count):
                try:
                    paper_row = paper_rows.nth(i)
                    paper_info = {}
                    
                    # 题名和详情链接 - 使用td.name下的a.fz14选择器
                    title_element = paper_row.locator("td.name a.fz14")
                    if title_element.count() > 0:
                        paper_info['题名'] = title_element.text_content().strip()
                        paper_info['详情链接'] = title_element.get_attribute('href')
                    else:
                        # 备用选择器
                        title_element = paper_row.locator("td.name a")
                        if title_element.count() > 0:
                            paper_info['题名'] = title_element.first.text_content().strip()
                            paper_info['详情链接'] = title_element.first.get_attribute('href')
                        else:
                            continue  # 如果没有题名，跳过这条记录
                    
                    # 作者 - 使用td.author选择器
                    author_element = paper_row.locator("td.author")
                    if author_element.count() > 0:
                        paper_info['作者'] = author_element.text_content().strip()
                    else:
                        paper_info['作者'] = ""
                    
                    # 来源 - 使用td.source选择器
                    source_element = paper_row.locator("td.source")
                    if source_element.count() > 0:
                        paper_info['来源'] = source_element.text_content().strip()
                    else:
                        paper_info['来源'] = ""
                    
                    # 发表时间 - 使用td.date选择器，只保留日期部分
                    date_element = paper_row.locator("td.date")
                    if date_element.count() > 0:
                        full_date = date_element.text_content().strip()
                        # 提取日期部分，去掉时间部分（格式：YYYY-MM-DD HH:MM -> YYYY-MM-DD）
                        if ' ' in full_date:
                            paper_info['发表时间'] = full_date.split(' ')[0]
                        else:
                            paper_info['发表时间'] = full_date
                    else:
                        paper_info['发表时间'] = ""
                    
                    # 数据库 - 使用td.data span选择器
                    data_element = paper_row.locator("td.data span")
                    if data_element.count() > 0:
                        paper_info['数据库'] = data_element.text_content().strip()
                    else:
                        paper_info['数据库'] = ""
                    
                    # 被引次数 - 使用td.quote a.quoteCnt选择器
                    quote_element = paper_row.locator("td.quote a.quoteCnt")
                    if quote_element.count() > 0:
                        paper_info['被引'] = quote_element.text_content().strip()
                    else:
                        paper_info['被引'] = "0"
                    
                    # 下载次数 - 使用td.download a.downloadCnt选择器
                    download_element = paper_row.locator("td.download a.downloadCnt")
                    if download_element.count() > 0:
                        paper_info['下载'] = download_element.text_content().strip()
                    else:
                        paper_info['下载'] = "0"
                    
                    all_papers.append(paper_info)
                    print(f"已提取第 {len(all_papers)} 条文献: {paper_info['题名'][:50]}...")
                    
                except Exception as e:
                    print(f"提取第 {i+1} 条文献信息时出错: {e}")
                    continue
            
            # 检查是否有下一页，并点击下一页按钮
            next_page_button = page.locator("#PageNext, a.pagesnums[title*='下一页'], a[title*='下一页']")
            if next_page_button.count() > 0 and next_page_button.is_enabled():
                try:
                    print(f"正在翻到第 {current_page + 1} 页...")
                    next_page_button.click()
                    time.sleep(3)  # 等待页面加载
                    current_page += 1
                except Exception as e:
                    print(f"翻页时出错: {e}")
                    break
            else:
                print("没有更多页面，抓取完成")
                break
                
        except Exception as e:
            print(f"处理第 {current_page} 页时出错: {e}")
            break
    
    print(f"总共抓取了 {len(all_papers)} 条文献")
    return all_papers

def extract_paper_details(page, detail_url):
    """
    从文献详情页面提取详细信息
    
    Args:
        page: Playwright页面对象
        detail_url: 文献详情页面URL
        
    Returns:
        dict: 包含文献详细信息的字典
    """
    details = {}
    
    try:
        # 导航到详情页面
        if not detail_url.startswith('http'):
            detail_url = "https://kns.cnki.net" + detail_url
        
        page.goto(detail_url)
        page.wait_for_load_state()
        time.sleep(2)
        
        # 摘要 - 优先使用ChDivSummary ID选择器
        abstract_element = page.locator("#ChDivSummary")
        if abstract_element.count() > 0:
            # 检查是否有"更多"按钮，如果有则点击获取完整摘要
            more_button = page.locator("#ChDivSummaryMore")
            if more_button.count() > 0 and more_button.is_visible():
                try:
                    print("发现摘要'更多'按钮，正在点击获取完整摘要...")
                    more_button.click()
                    time.sleep(1)  # 等待内容加载
                except Exception as e:
                    print(f"点击'更多'按钮时出错: {e}")
            
            # 获取摘要内容
            details['摘要'] = abstract_element.first.text_content().strip()
        else:
            # 备用选择器
            abstract_element = page.locator(".abstract-text, .brief")
            if abstract_element.count() > 0:
                details['摘要'] = abstract_element.first.text_content().strip()
            else:
                details['摘要'] = ""
        
        # 关键词 - 优先使用ChDivKeyWord ID选择器
        keywords_element = page.locator("#ChDivKeyWord")
        if keywords_element.count() > 0:
            details['关键词'] = keywords_element.first.text_content().strip()
        else:
            # 备用选择器
            keywords_element = page.locator(".keywords, .keyword")
            if keywords_element.count() > 0:
                details['关键词'] = keywords_element.first.text_content().strip()
            else:
                details['关键词'] = ""

        # 基金资助 - 使用li元素中包含"基金"或"资助"的选择器
        fund_element = page.locator("li.top-space:has-text('基金') p, li.top-space:has-text('资助') p")
        if fund_element.count() > 0:
            details['基金资助'] = fund_element.first.text_content().strip()
        else:
            # 备用选择器
            fund_element = page.locator("#ChDivFund")
            if fund_element.count() > 0:
                details['基金资助'] = fund_element.first.text_content().strip()
            else:
                details['基金资助'] = ""

        # 专辑 - 使用li元素中包含"专辑"的选择器
        album_element = page.locator("li.top-space:has-text('专辑：') p")
        if album_element.count() > 0:
            details['专辑'] = album_element.first.text_content().strip()
        else:
            details['专辑'] = ""

        # 专题 - 使用li元素中包含"专题"的选择器  
        topic_element = page.locator("li.top-space:has-text('专题：') p")
        if topic_element.count() > 0:
            details['专题'] = topic_element.first.text_content().strip()
        else:
            details['专题'] = ""

        # 分类号 - 使用li元素中包含"分类号"的选择器
        classification_element = page.locator("li.top-space:has-text('分类号：') p")
        if classification_element.count() > 0:
            details['分类号'] = classification_element.first.text_content().strip()
        else:
            # 备用选择器
            classification_element = page.locator("#ChDivClassNo")
            if classification_element.count() > 0:
                details['分类号'] = classification_element.first.text_content().strip()
            else:
                details['分类号'] = ""

        # DOI - 使用li元素中包含"DOI"的选择器
        doi_element = page.locator("li.top-space:has-text('DOI：') p")
        if doi_element.count() > 0:
            details['DOI'] = doi_element.first.text_content().strip()
        else:
            details['DOI'] = ""
            
    except Exception as e:
        print(f"提取文献详细信息时出错: {e}")
        details = {
            '摘要': "",
            '关键词': "",
            '基金资助': "",
            '专辑': "",
            '专题': "",
            '分类号': "",
            'DOI': ""
        }
    
    return details

def launch_cnki(search_formula=None):
    """
    使用Playwright启动cnki.net网站，搜索并提取文献信息
    
    Args:
        search_formula (str): 要填入搜索框的检索式
    """
    if not search_formula:
        print("错误：未提供搜索式")
        return
        
    print("将使用以下检索式:")
    print(search_formula)
    
    # 初始化CSV写入器
    csv_writer = create_paper_csv_writer()
    
    with sync_playwright() as p:
        # 启动浏览器（默认使用chromium）
        browser = p.chromium.launch(headless=False)
        
        # 创建新的上下文和页面
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 导航到cnki.net
            page.goto("https://kns.cnki.net/kns8s/AdvSearch")
            print("成功导航到cnki.net")
            
            # 等待页面加载
            time.sleep(3)
            
            # 切换到专业检索
            major_search = page.locator("li[name='majorSearch']")
            if major_search.count() > 0:
                major_search.click()
                time.sleep(1)
            
            # 定位文本框并输入搜索式
            text_area = page.locator("textarea.textarea-major.majorSearch.ac_input")
            if text_area.count() > 0:
                text_area.fill(search_formula)
                time.sleep(1)
        
                # 点击检索按钮
                search_button = page.locator("input.btn-search")
                search_button.click()
                
                print("正在搜索...")
                time.sleep(5)  # 等待搜索结果加载
                
                # 提取文献基本信息
                papers = extract_paper_info(page)
                
                if not papers:
                    print("未找到文献，请检查搜索条件")
                    return
                
                print(f"\n开始提取 {len(papers)} 条文献的详细信息...")
                
                # 为每条文献提取详细信息并立即写入CSV
                for i, paper in enumerate(papers):
                    print(f"\n处理第 {i+1}/{len(papers)} 条文献...")
                    
                    if paper.get('详情链接'):
                        details = extract_paper_details(page, paper['详情链接'])
                        # 合并基本信息和详细信息
                        paper.update(details)
                    
                    # 移除详情链接字段（不需要保存到CSV）
                    paper.pop('详情链接', None)
                    
                    # 立即写入CSV文件
                    csv_writer.write_paper(paper)
                    
                    # 添加延时，避免请求过于频繁
                    time.sleep(1)
                
                print(f"\n数据提取完成！")
                print(f"共处理 {csv_writer.get_count()} 条文献")
                print(f"CSV文件保存位置: {csv_writer.get_filepath()}")
                print("按下回车键关闭浏览器...")
                input()
            else:
                print("未找到搜索文本框")
                
        except Exception as e:
            print(f"执行过程中出错: {e}")
            print(f"已保存 {csv_writer.get_count()} 条文献到CSV文件")
        
        finally:
            # 关闭浏览器
            browser.close()
            print("浏览器已关闭")

if __name__ == "__main__":
    # 如果直接运行此脚本并提供搜索式作为命令行参数
    if len(sys.argv) > 1:
        search_formula = sys.argv[1]
        launch_cnki(search_formula)
    else:
        print("请通过运行search_formula.py提供搜索式作为参数")