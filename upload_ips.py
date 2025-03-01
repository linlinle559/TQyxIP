import requests
import os
import csv
from base64 import b64encode

# GitHub 配置
github_token = os.getenv("MY_GITHUB_TOKEN")
repo_name = "jzhou9096/jilianip"  # 替换为你的 GitHub 仓库路径
file_path = "yxip.txt"  # 存储 IP 列表的文件路径
commit_message = "Update bestcf IP list"

# 自定义前缀和后缀
custom_prefix = "优"  # 自定义前缀加在 IP# 后面
custom_suffix = "选IP"  # 自定义后缀加在国家代码后面

# HTML 页面链接
html_url = "https://ip.164746.xyz/ipTop10.html"  # 需要提取 IP 的 HTML 页面链接
csv_url = ""  # 替换为实际的 CSV 文件 URL

# 限制上传的最大 IP 数量
max_ips = 20  # 设置为你想上传的最大 IP 数量

# 从 CSV URL 获取 IP 地址
def read_ips_from_csv_url(csv_url):
    """从 CSV 文件 URL 中读取 IP 地址"""
    ips = []  # 使用列表保存 IP 地址，保持顺序
    try:
        response = requests.get(csv_url)
        response.raise_for_status()
        # 解析 CSV 内容
        decoded_content = response.content.decode('utf-8')
        reader = csv.reader(decoded_content.splitlines())
        for row in reader:
            if row:
                ips.append(row[0].strip())  # 假设 IP 地址在第一列
        print(f"Read {len(ips)} IPs from CSV URL.")
    except requests.RequestException as e:
        print(f"Error downloading or reading CSV: {e}")
    return ips

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

def annotate_ips(ips, add_annotations=True):
    """给 IP 地址添加注释"""
    annotated_ips = []
    for ip in ips:
        # 如果是元组 (ip, port)，则正常处理
        if isinstance(ip, tuple) and len(ip) == 2:
            if add_annotations:
                # 返回带注释的 IP 地址
                annotated_ips.append(f"{ip[0]}:{ip[1]}#{custom_prefix}{custom_suffix}")
            else:
                # 返回只包含 IP 地址（不带端口）
                annotated_ips.append(f"{ip[0]}")
        # 如果是单一 IP 地址 (没有端口)，则默认使用端口 443
        elif isinstance(ip, str):
            if add_annotations:
                # 返回带注释的 IP 地址
                annotated_ips.append(f"{ip}:443#{custom_prefix}{custom_suffix}")
            else:
                # 返回只包含 IP 地址（不带端口）
                annotated_ips.append(f"{ip}")
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
    # 从 CSV 文件 URL 读取 IP 地址
    csv_ips = read_ips_from_csv_url(csv_url)
    
    # 获取 HTML 内容
    print(f"Downloading data from: {html_url}")
    html_content = get_html(html_url)
    
    ip_list = []  # 使用列表保存 IP 地址，保持顺序
    
    if html_content:
        html_ips = extract_ips_from_html(html_content)
        ip_list.extend(html_ips)  # 使用 extend 添加元素，保留顺序
    
    # 合并 CSV 中的 IP 地址与 HTML 提取的 IP 地址
    ip_list.extend(csv_ips)  # 使用 extend 以保留顺序
    
    # 限制上传的 IP 数量
    ip_list = ip_list[:max_ips]  # 只保留前 max_ips 个 IP
    
    # 标注 IP 地址并格式化
    add_annotations = True  # 设置为 True 或 False，控制是否带注释
    annotated_ips = annotate_ips(ip_list, add_annotations)
    
    # 合并所有 IP 列表为一个字符串
    file_content = "\n".join(annotated_ips)
    
    # 上传到 GitHub
    upload_to_github(github_token, repo_name, file_path, file_content, commit_message)
    print("Upload completed.")

if __name__ == "__main__":
    main()
