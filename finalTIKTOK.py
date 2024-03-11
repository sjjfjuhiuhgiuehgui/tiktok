import os
import sys
import time
import requests
import random
import base64
import pyautogui
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
def PIL_base64_outer(img_url_outer):
    with Image.open(img_url_outer) as img:
        img_format = img.format or 'JPEG'
        format_str = 'PNG' if img.mode == "RGBA" else img_format

        output_buffer = BytesIO()
        img.save(output_buffer, format=format_str, quality=100)
        byte_data = output_buffer.getvalue()
        base64_str = 'data:image/' + img_format.lower() + ';base64,' + base64.b64encode(byte_data).decode('utf-8')

        return base64_str

def PIL_base64_inner(img_url_inner):
    with Image.open(img_url_inner) as img:
        img_format = img.format or 'JPEG'
        format_str = 'PNG' if img.mode == "RGBA" else img_format

        output_buffer = BytesIO()
        img.save(output_buffer, format=format_str, quality=100)
        byte_data = output_buffer.getvalue()
        base64_str = 'data:image/' + img_format.lower() + ';base64,' + base64.b64encode(byte_data).decode('utf-8')

        return base64_str

# 验证码识别接口
def shibie(img_url_outer, img_url_inner):
    # 将URL下载的图片转换为base64
    img1_base64 = PIL_base64_outer(img_url_outer)
    img2_base64 = PIL_base64_inner(img_url_inner)

    # 调用API
    url = "http://www.detayun.cn/openapi/verify_code_identify/"
    data = {
        "key": "yZeSZxzlVK2OV3grzJ5R",
        "verify_idf_id": "37",
        "img1": img1_base64,
        "img2": img2_base64,
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    print(response_data)
    # 處理響應
    if response_data["code"] == 200 and "data" in response_data:
        angle = response_data["data"].get("angle")  # 使用返回的角度值
        if angle is not None:
            return int(angle), int(angle)  # 假設外圈和內圈的旋轉角度相同
    print("Failed to recognize captcha or invalid response.")
    return None, None
    
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# 加载防检测js
absolute_path = 'C:/Users/teter/Desktop/KaiPython/抖音/stealth.min.js-main/stealth.min.js'
with open(absolute_path) as f:
    js = f.read()
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": js
})
driver.get('https://www.tiktok.com')
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": js
})

driver.maximize_window()
time.sleep(5)

# 點擊帳號 (確保這個元素是可見的並且可以被點擊)
driver.find_element(By.XPATH,'/html/body/div[5]/div[3]/div/div/div/div[1]/div/div/div[1]/div[2]/div[2]/div[2]').click() 
time.sleep(2)  # 等待登入彈窗打開
driver.find_element(By.XPATH,'/html/body/div[5]/div[3]/div/div/div/div[1]/div/form/a').click()  #點擊使用密碼
account = driver.find_element(By.XPATH,'//*[@id="loginContainer"]/div/form/div[2]/div/div[2]/input')
account.clear()
account.send_keys('989101823')
password = driver.find_element(By.XPATH,'//*[@id="loginContainer"]/div/form/div[3]/div/input')
password.clear()
password.send_keys('@stup1236')
driver.find_element(By.XPATH,'/html/body/div[5]/div[3]/div/div/div/div[1]/div/form/button').click() #點擊登入按鈕
time.sleep(1)

max_retries = 10
retry_interval = 5


for _ in range(max_retries):
    try:
        # 等待並獲取第一張【旋轉圖像】元素
        tag1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//img[@data-testid='whirl-outer-img']")))
        img_url_outer = tag1.get_attribute('src')

        # 下載第一張圖片
        response_outer = requests.get(img_url_outer)
        if response_outer.status_code == 200 and 'image' in response_outer.headers['Content-Type']:
            img_outer = Image.open(BytesIO(response_outer.content))
            img_outer_rgb = img_outer.convert('RGB')
            temp_img_path_outer = 'train_img/outer_{}.jpg'.format(int(time.time() * 1000))
            img_outer_rgb.save(temp_img_path_outer)
            print("第一張圖片下載成功，路徑：" + temp_img_path_outer)
        
        # 等待並獲取第二張【旋轉圖像】元素
        tag2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//img[@data-testid='whirl-inner-img']")))
        img_url_inner = tag2.get_attribute('src')

        # 下載第二張圖片
        response_inner = requests.get(img_url_inner)
        if response_inner.status_code == 200 and 'image' in response_inner.headers['Content-Type']:
            img_inner = Image.open(BytesIO(response_inner.content))
            img_inner_rgb = img_inner.convert('RGB')
            temp_img_path_inner = 'train_img/inner_{}.jpg'.format(int(time.time() * 1000))
            img_inner_rgb.save(temp_img_path_inner)
            print("第二張圖片下載成功，路徑：" + temp_img_path_inner)
        else:
            print("第二張圖片下載失敗")

        # 處理這兩張圖片並獲取旋轉角度，此部分需要你根據實際情況完成
        # 以下為示例
        raw_angle = shibie(temp_img_path_outer, temp_img_path_inner)
        if raw_angle is not None:
            angle = raw_angle[0]
            angle = int(angle)
            print(f"识别到的旋转角度为：{angle}度")
            move_x = int(angle * 1.535)  # 示例计算公式，可能需要调整
            overshoot = 5  # 超过目标位置的偏移量

            # 定位到滑块元素
            slider = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "secsdk-captcha-drag-icon")]')))
            ActionChains(driver).click_and_hold(slider).perform()

            # 先将滑块移动到111度向右5PX的位置
            ActionChains(driver).move_by_offset(move_x + overshoot, 0).perform()
            time.sleep(0.5)  # 暂停模拟人类操作

            # 获取当前鼠标位置
            current_mouse_x, current_mouse_y = pyautogui.position()

            # 使用"pyautogui"的方式在屏幕上方左右滑动5PX
            pyautogui.moveRel(5, 0, duration=0.25)  # 向右移动5PX
            pyautogui.moveRel(-10, 0, duration=0.5)  # 向左移动5PX
            pyautogui.moveRel(5, 0, duration=0.25)  # 再次向右移动5PX

            # 将鼠标移回到滑块操作的初始位置，准备进行最后的滑动操作
            pyautogui.moveTo(current_mouse_x, current_mouse_y)

            # 继续使用ActionChains将滑块拖曳回最初设置的角度
            ActionChains(driver).move_by_offset(-overshoot, 0).perform()  # 移回计算的位置

            # 释放滑块
            ActionChains(driver).release().perform()

            print("模拟人类滑动操作执行完毕")
        else:
            print("无法成功识别两张图片的旋转角度")

    except Exception as e:
        print(f"出現異常: {e}")
        time.sleep(retry_interval)

input("Press Enter to exit...")  # 程序会在这里暂停，等待用户按Enter键退出
driver.quit()