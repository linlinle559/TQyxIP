import requests
import os
from base64 import b64encode

# GitHub 配置
github_token = os.getenv("MY_GITHUB_TOKEN")
repo_name = "jzhou9096/jilianip"  # 替换为你的 GitHub 仓库路径
file_path = "bzgj.txt"  # 存储 IP 列表的文件路径
commit_message = "Update bestcf IP list"

# 自定义前缀和后缀
custom_prefix = "可"  # 自定义前缀加在 IP# 后面
custom_suffix = "变"  # 自定义后缀加在国家代码后面

# HTML 页面链接
html_url = "https://ip.164746.xyz/ipTop10.html"  # 需要提取 IP 的 HTML 页面链接
limit_count = 10  # 限制提取前 10 个 IP

def get_html(url):
    """使用 requests 获取 HTML 页面内容"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"Downloaded HTML content from {url}")
        return response.text
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return ""

def extract_ips_from_html(html_content):
    """从 HTML 页面提取 IP 地址"""
    ips = []
    # 页面直接返回所有 IP 地址，逗号分隔
    ip_string = html_content.strip()  # 直接去掉两边空格
    ips = ip_string.split(',')  # 按逗号分割成 IP 地址
    
    # 假设 IP 地址没有端口信息，默认端口 443
    ips_with_ports = [(ip.strip(), '443') for ip in ips]
    print(f"Extracted IPs from HTML: {ips_with_ports}")
    
    return ips_with_ports

def annotate_ips(ips):
    """给 IP 地址添加注释"""
    annotated_ips = []
    for ip, port in ips:
        annotated_ips.append(f"{ip}:{port}#{custom_prefix}{custom_suffix}")
    return annotated_ips

def upload_to_github(token, repo_name, file_path, content, commit_message):
    """将结果上传到 GitHub 仓库"""
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
    
    # 获取当前文件的内容和 SHA 值（用于更新文件）
    response = requests.get(url, headers={'Authorization': f'token {token}'})
    
    if response.status_code == 200:
        file_data = response.json()
        sha = file_data['sha']
    else:
        sha = None  # 如果文件不存在，创建新文件
    
    # 用 Base64 编码内容
    encoded_content = b64encode(content.encode('utf-8')).decode('utf-8')
    
    # 构建上传请求的数据
    data = {
        "message": commit_message,
        "content": encoded_content
    }
    if sha:
        data["sha"] = sha  # 更新文件时需要传递 SHA 值
    
    # 发送请求上传文件
    response = requests.put(url, json=data, headers={'Authorization': f'token {token}'})
    
    if response.status_code == 201 or response.status_code == 200:
        print("File uploaded successfully.")
    else:
        print(f"Failed to upload file: {response.status_code} - {response.text}")

def main():
    # 获取 HTML 内容
    print(f"Downloading data from: {html_url}")
    html_content = get_html(html_url)
    if html_content:
        ip_list = extract_ips_from_html(html_content)
    
        # 标注 IP 地址并格式化
        annotated_ips = annotate_ips(ip_list)
    
        # 合并所有 IP 列表为一个字符串
        file_content = "\n".join(annotated_ips)
    
        # 上传到 GitHub
        upload_to_github(github_token, repo_name, file_path, file_content, commit_message)
        print("Upload completed.")

if __name__ == "__main__":
    main()
