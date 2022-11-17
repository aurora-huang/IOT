import network, urequests, utime, bh1750fvi
from machine import Pin, I2C

'''
雲端亮度紀錄
讀取亮度感測模組的值，並透過IFTTT上傳到GOOGLE試算表
- D1 mini
- 亮度感測模組
'''

ssid = "你的WiFi名稱"
pw =   "你的WiFi密碼"
key =  "你的金鑰"
# Webhooks觸發網址
url = "https://maker.ifttt.com/trigger/light_level/with/key/" + key
# 建立WiFi物件，設為工作站(station)模式
print("連接 WiFi...")
wifi = network.WLAN(network.STA_IF)
wifi.active(True) # 啟用WiFi物件
wifi.connect(ssid, pw) # 開始連接到指定WiFi
# 檢查連線狀態，還沒連接上就繼續跑迴圈
while not wifi.isconnected():
    pass
# 執行到此處，就代表控制板已連上WiFi
print("已連上")

print("亮度記錄器已啟動")

while True:
    
    light_level = bh1750fvi.sample(I2C(scl=Pin(5), sda=Pin(4)), mode=0x23)
    # 觸發IFTTT Webhooks服務
    # 網址加上要傳送的資料
    response = urequests.get(url + "?value1=" + str(light_level))
    # IFTTT狀態碼傳回200,觸發成功    
    if response.status_code == 200:
        print("IFTTT 呼叫成功: 傳送亮度 " + str(light_level) + " lux")

    else:
        print("IFTTT 呼叫失敗")
        
    utime.sleep(5)
