import requests
import csv
import os
from github import Github

# GitHub 配置
github_token = os.getenv("MY_GITHUB_TOKEN")
repo_name = "jzhou9096/jilianip"  # 替换为你的 GitHub 仓库路径
file_path = "bzgj.txt"  # 存储 IP 列表的文件路径
commit_message = "Update bestcf IP list"

# 自定义前缀和后缀
custom_prefix = "可"  # 自定义前缀加在 IP# 后面
custom_suffix = "变"  # 自定义后缀加在国家代码后面

# 多个 API 地址
csv_urls = [
    "https://ipdb.030101.xyz/api/bestcf.csv",  # 第一个链接
    ""  # 第二个链接
    # 可以添加更多链接
]
limit_count = 10  # 限制提取前 10 个 IP

def download_csv(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return ""

def extract_ips(csv_content):
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

def annotate_ips(ips):
    annotated_ips = []
    for ip, port in ips:
        annotated_ips.append(f"{ip}:{port}#{custom_prefix}{custom_suffix}")
    return annotated_ips

def upload_to_github(token, repo_name, file_path, content, commit_message):
    g = Github(token)
    repo = g.get_repo(repo_name)
    try:
        file = repo.get_contents(file_path)
        repo.update_file(file.path, commit_message, content, file.sha)
    except:
        repo.create_file(file.path, commit_message, content)

def main():
    all_ips = []
    for url in csv_urls:
        print(f"Downloading data from: {url}")
        csv_content = download_csv(url)
        if csv_content:
            ip_list = extract_ips(csv_content)
            all_ips.extend(ip_list)  # 将当前 URL 提取的 IP 添加到总列表中
    
    # 标注IP地理位置
    annotated_ips = annotate_ips(all_ips)
    
    # 将所有提取的 IP 列表合并
    file_content = "\n".join(annotated_ips)
    upload_to_github(github_token, repo_name, file_path, file_content, commit_message)
    print("Upload completed.")

if __name__ == "__main__":
    main()
