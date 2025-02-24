import requests
import csv
import os
from github import Github

# GitHub 配置
github_token = os.getenv("MY_GITHUB_TOKEN")
repo_name = "jzhou9096/jilianip"  # 替换为你的 GitHub 仓库路径
file_path = "bzgj.txt"  # 存储 IP 列表的文件路径
commit_message = "Update bestcf IP list"

# IP地理位置API配置
ipinfo_token = "80a32dbe4fc97e"  # 替换为你的ipinfo.io API密钥
ipinfo_base_url = "https://ipinfo.io/"

# 自定义前缀和后缀
custom_prefix = "可"  # 自定义前缀加在 # 后面
custom_suffix = "变"  # 自定义后缀加在国家代码前面

# 多个 API 地址
csv_urls = [
    "https://ipdb.030101.xyz/api/bestcf.csv",  # 第一个链接
    # 可以添加更多链接
]
limit_count = 10  # 限制提取前 5 个 IP，改成 10 以提取 10 个

def download_csv(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_ips(csv_content):
    ips = []
    reader = csv.reader(csv_content.splitlines())
    for row in reader:
        if row and row[0].count('.') == 3:  # 简单检查 IPv4 地址格式
            ips.append(row[0])
        if len(ips) >= limit_count:  # 达到限制数量后停止
            break
    return ips

def get_ip_location(ip):
    response = requests.get(f"{ipinfo_base_url}{ip}/json", headers={"Authorization": f"Bearer {ipinfo_token}"})
    if response.status_code == 200:
        data = response.json()
        country = data.get("country", "Unknown")
        return f"{ip}#{custom_prefix}{custom_suffix}{country}"
    else:
        return f"{ip}#{custom_prefix}Unknown{custom_suffix}"

def annotate_ips(ips):
    annotated_ips = []
    for ip in ips:
        annotated_ips.append(get_ip_location(ip))
    return annotated_ips

def upload_to_github(token, repo_name, file_path, content, commit_message):
    g = Github(token)
    repo = g.get_repo(repo_name)
    try:
        file = repo.get_contents(file_path)
        repo.update_file(file.path, commit_message, content, file.sha)
    except:
        repo.create_file(file_path, commit_message, content)

def main():
    all_ips = []
    for url in csv_urls:
        print(f"Downloading data from: {url}")
        csv_content = download_csv(url)
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
