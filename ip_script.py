import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表
urls = [
    'https://api.uouin.com/cloudflare.html',
    'https://ip.164746.xyz'
]

# 匹配IP的正则
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# 删除旧文件
for f in ['ip.txt', 'ip_area.txt']:
    if os.path.exists(f):
        os.remove(f)

# 记录国家编号
country_counter = {}

def country_to_flag(country_code):
    """ISO 两字母国家代码 转换成 国旗emoji"""
    if not country_code or len(country_code) != 2:
        return "🏳️"
    return ''.join(chr(127397 + ord(c)) for c in country_code.upper())

def get_ip_location(ip):
    """查询IP归属地（使用 ip-api 免费接口）"""
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}?lang=zh-CN", timeout=5)
        data = resp.json()
        if data['status'] == 'success':
            country = data.get('country', '未知')
            country_code = data.get('countryCode', '')
            flag = country_to_flag(country_code)
            return flag, country
    except Exception:
        pass
    return "🏳️", "未知"

with open('ip.txt', 'w', encoding='utf-8') as file_ip, \
     open('ip_area.txt', 'w', encoding='utf-8') as file_area:

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 简化选择器逻辑
            elements = soup.find_all('tr') or soup.find_all('li')

            for element in elements:
                element_text = element.get_text()
                ip_matches = re.findall(ip_pattern, element_text)

                for ip in ip_matches:
                    # 写入原始 ip.txt
                    file_ip.write(ip + '\n')

                    # 查询归属地
                    flag, country = get_ip_location(ip)

                    # 分配国家编号
                    if country not in country_counter:
                        country_counter[country] = 1
                    else:
                        country_counter[country] += 1

                    number = str(country_counter[country]).zfill(2)
                    file_area.write(f"{ip} #{flag}{country}{number}\n")

        except Exception as e:
            print(f"获取 {url} 失败: {e}")

print("已生成 ip.txt 和 ip_area.txt 文件。")
