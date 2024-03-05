import os
import sys
import time
import requests
import random
import base64
from io import BytesIO
from PIL import Image
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 添加当前脚本目录的父目录到系统路径
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
# PIL图片保存为base64编码
def PIL_base64(img, coding='utf-8'):
    img_format = img.format
    if img_format == None:
        img_format = 'JPEG'
    format_str = 'JPEG'
    if 'png' == img_format.lower():
        format_str = 'PNG'
    if 'gif' == img_format.lower():
        format_str = 'gif'
    if img.mode == "P":
        img = img.convert('RGB')
    if img.mode == "RGBA":
        format_str = 'PNG'
        img_format = 'PNG'
    output_buffer = BytesIO()
    # img.save(output_buffer, format=format_str)
    img.save(output_buffer, quality=100, format=format_str)
    byte_data = output_buffer.getvalue()
    base64_str = 'data:image/' + img_format.lower() + ';base64,' + base64.b64encode(byte_data).decode(coding)
    return base64_str
# 验证码识别接口
def shibie(img):
    url = "http://www.detayun.cn/openapi/verify_code_identify/"
    data = {
        # 用户的key
        "key":"yZeSZxzlVK2OV3grzJ5R",
        # 验证码类型
        "verify_idf_id":"24",
        # 样例图片
        "img_base64":PIL_base64(img),
        "img_byte": None,
        # 中文点选，空间语义类型验证码的文本描述（这里缺省为空字符串）
        "words":""
    }
    header = {"Content-Type": "application/json"}
    # 发送请求调用接口
    response = requests.post(url=url, json=data, headers=header)
    print(response.text)
    return response.json()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# 加载防检测js
absolute_path = 'C:/Users/teter/Desktop/KaiPython/抖音/stealth.min.js-main/stealth.min.js'
with open(absolute_path) as f:
    js = f.read()
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": js
})
driver.get('https://www.xiaohongshu.com/website-login/captcha?redirectPath=https%3A%2F%2Fwww.xiaohongshu.com%2Fexplore&verifyUuid=shield-4f9bcc31-0bc0-462a-843a-e60239713e46&verifyType=101&verifyBiz=461')
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": js
})
driver.maximize_window()
time.sleep(5)
for i in range(1):
    # 等待【旋转图像】元素出现
    WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, '//div[@id="red-captcha-rotate"]/img'))
)
    # 找到【旋转图像】元素
    tag1 = driver.find_element(By.XPATH, '//div[@id="red-captcha-rotate"]/img')
    # 获取图像链接
    img_url = tag1.get_attribute('src')
    print(img_url)
    header = {
        "Host": "picasso-static.xiaohongshu.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cookie": "xsecappid=login; a1=1896916369fehn0yq7nomanvre3fghfkj0zubt7zx50000120287; webId=75af27905db67b6fcb29a4899d200062; web_session=030037a385d8a837e5e590cace234a6e266fd5; gid=yYjKjyK484VKyYjKjyKqK89WjidxI8vAWIl6uuC0IhFdq728ikxiTD888yJ8JYW84DySKW0Y; webBuild=2.17.8; websectiga=634d3ad75ffb42a2ade2c5e1705a73c845837578aeb31ba0e442d75c648da36a; sec_poison_id=41187a04-9f82-4fbc-8b98-d530606b7696",
        "Upgrade-Insecure-Requests": "1",
        "If-Modified-Since": "Thu, 06 Jul 2023 11:42:07 GMT",
        "If-None-Match": '"7e53c313a9f321775e8f5e190de21081"',
        "TE": "Trailers",
    }
    # 下载图片
    response = requests.get(url=img_url, headers=header)
    img = Image.open(BytesIO(response.content))
    img.convert('RGB').save('train_img/{}.jpg'.format(int(time.time() * 1000)))
    res = shibie(img)
    # 检查res['data']是否为字典且包含'res_str'键
if isinstance(res.get('data'), dict) and 'res_str' in res['data']:
    angle_str = res['data']['res_str']
    angle = int(angle_str.replace('顺时针旋转', '').replace('度', ''))
    # 找到【旋转图像】元素
    tag2 = driver.find_element(By.XPATH, '//div[@class="red-captcha-slider-icon"]')
    # 滑动滑块
    action = ActionChains(driver)
    action.click_and_hold(tag2).perform()
    time.sleep(1)
    # 计算实际滑动距离 = 像素距离 + 前面空白距离
    move_x = angle * 0.765
    # 滑动1：直接滑动
    action.move_by_offset(move_x, 5)
    # 滑动2：分段滑动
    #n = (random.randint(3, 5))
    #move_x = move_x / n
    #for i in range(n):
    # action.move_by_offset(move_x, 5)
    time.sleep(0.01)
    time.sleep(1)
    action.release().perform()
    time.sleep(2)

else:
    print("无法识别的响应格式或缺少所需的数据")
    # 根据需要处理错误或设置默认值
    angle = 0  # 示例：设置一个默认角度
    print(angle)
    img = img.rotate(360 - angle, fillcolor=(0, 0, 0))
    img.show()
    # 等待【旋转图像】元素出现
    WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, '//div[@class="red-captcha-slider-icon"]')))
    # 找到【旋转图像】元素
    tag2 = driver.find_element(By.XPATH, '//div[@class="red-captcha-slider-icon"]')
    # 滑动滑块
    action = ActionChains(driver)
    action.click_and_hold(tag2).perform()
    time.sleep(1)
    # 计算实际滑动距离 = 像素距离 + 前面空白距离
    move_x = angle * 0.79
    # 滑动1：直接滑动
    action.move_by_offset(move_x, 5)
    # 滑动2：分段滑动
    n = (random.randint(3, 5))
    move_x = move_x / n
    for i in range(n):
     action.move_by_offset(move_x, 5)
    time.sleep(0.01)
    time.sleep(1)
    action.release().perform()
    time.sleep(2)
 


input("Press Enter to exit...")  # 程序会在这里暂停，等待用户按Enter键
driver.quit()  # 最后关闭浏览器
