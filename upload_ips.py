import requests
import csv
import os
from github import Github
from bs4 import BeautifulSoup

# GitHub 配置
github_token = os.getenv("MY_GITHUB_TOKEN")
repo_name = "jzhou9096/jilianip"  # 替换为你的 GitHub 仓库路径
file_path = "bzgj.txt"  # 存储 IP 列表的文件路径
commit_message = "Update bestcf IP list"

# 自定义前缀和后缀
custom_prefix = "可"  # 自定义前缀加在 IP# 后面
custom_suffix = "变"  # 自定义后缀加在国家代码后面

# URL 列表，包括 CSV 和 HTML 链接
urls = [
    # "https://ipdb.030101.xyz/api/bestcf.csv",  # CSV 数据源
    "https://ip.164746.xyz/ipTop10.html"  # HTML 数据源
]

limit_count = 10  # 限制提取前 10 个 IP

def download_csv(url):
    """下载 CSV 数据并返回内容"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return ""

def extract_ips_from_csv(csv_content):
    """从 CSV 内容提取 IP 地址"""
    ips = []
    reader = csv.reader(csv_content.splitlines())
    for row in reader:
        try:
            if row and len(row) > 1 and row[0].count('.') == 3:  # 简单检查 IPv4 地址格式
                ip_with_port = row[0]
                port_index = ip_with_port.rfind(':')
                if port_index != -1:
                    ip, port = ip_with_port[:port_index], ip_with_port[port_index+1:]
                else:
                    ip = ip_with_port
                    port = '443'  # 默认端口
                ips.append((ip, port))
                if len(ips) >= limit_count:  # 达到限制数量后停止
                    break
        except Exception as e:
            print(f"Error processing row {row}: {e}")
    return ips

def download_html(url):
    """下载 HTML 页面内容"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return ""

def extract_ips_from_html(html_content):
    """从 HTML 页面提取 IP 地址"""
    ips = []
    soup = BeautifulSoup(html_content, 'html.parser')

    # 假设 IP 地址是以逗号分隔的字符串在一个 div 中
    ip_string = soup.find('div', class_='ip-list')  # 根据实际 HTML 标签调整
    if ip_string:
        # 获取 IP 地址字符串并分割成 IP 地址列表
        ip_list = ip_string.get_text().strip()
        ips = ip_list.split(',')
    
    # 假设 IP 地址没有端口信息，默认端口 443
    ips_with_ports = [(ip.strip(), '443') for ip in ips]
    
    return ips_with_ports

def annotate_ips(ips):
    """给 IP 地址添加注释"""
    annotated_ips = []
    for ip, port in ips:
        annotated_ips.append(f"{ip}:{port}#{custom_prefix}{custom_suffix}")
    return annotated_ips

def upload_to_github(token, repo_name, file_path, content, commit_message):
    """将结果上传到 GitHub 仓库"""
    g = Github(token)
    repo = g.get_repo(repo_name)
    try:
        file = repo.get_contents(file_path)
        repo.update_file(file.path, commit_message, content, file.sha)
    except:
        repo.create_file(file_path, commit_message, content)

def main():
    all_ips = []
    
    # 遍历所有的 URL
    for url in urls:
        print(f"Downloading data from: {url}")
        
        if url.endswith(".csv"):  # 如果是 CSV 文件
            csv_content = download_csv(url)
            if csv_content:
                ip_list = extract_ips_from_csv(csv_content)
                all_ips.extend(ip_list)  # 将当前 URL 提取的 IP 添加到总列表中
        elif url.endswith(".html"):  # 如果是 HTML 页面
            html_content = download_html(url)
            if html_content:
                ip_list = extract_ips_from_html(html_content)
                all_ips.extend(ip_list)  # 将当前 URL 提取的 IP 添加到总列表中
    
    # 标注 IP 地址并格式化
    annotated_ips = annotate_ips(all_ips)
    
    # 合并所有 IP 列表为一个字符串
    file_content = "\n".join(annotated_ips)
    
    # 上传到 GitHub
    upload_to_github(github_token, repo_name, file_path, file_content, commit_message)
    print("Upload completed.")

if __name__ == "__main__":
    main()
