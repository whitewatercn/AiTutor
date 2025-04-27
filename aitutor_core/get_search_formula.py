import argparse
import aitutor_core 
def parse_search_arguments():
    """
    通过命令行参数获取用户输入的作者(AU)和作者单位(AF)信息
    
    Returns:
        argparse.Namespace: 包含用户输入参数的命名空间
    """
    parser = argparse.ArgumentParser(description='CNKI高级检索参数工具')
    
    # 添加作者参数，可选
    parser.add_argument('-AU', '--author', type=str, 
                        help='输入作者姓名，例如: 张三')
    
    # 添加作者单位参数，可选
    parser.add_argument('-AF', '--affiliation', type=str,
                        help='输入作者单位，例如: 北京大学')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    return args

def generate_search_formula(args):
    """
    根据用户输入生成检索式
    
    Args:
        args: 命令行参数
        
    Returns:
        str: 生成的检索式
    """
    formula_parts = []
    
    if args.author:
        formula_parts.append(f"AU='{args.author}'")
    
    if args.affiliation:
        formula_parts.append(f"AF='{args.affiliation}'")
    
    # 如果没有提供任何参数
    if not formula_parts:
        return "请提供至少一个检索条件"
    
    # 使用AND连接多个检索条件
    search_formula = " AND ".join(formula_parts)
    return search_formula

def main():
    """主函数"""
    args = parse_search_arguments()
    search_formula = generate_search_formula(args)
    
    print("生成的检索式:")
    print(search_formula)
    
    aitutor_core.launch_cnki(search_formula)

if __name__ == "__main__":
    main()