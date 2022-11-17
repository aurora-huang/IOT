from machine import Pin, I2C, PWM
from hcsr04 import HCSR04
import bh1750fvi, network, urequests, utime

'''
雲端智慧小夜燈
用超音波模組及亮度感測模組打造能在太暗或有人靠近的時候就亮起小夜燈
- D1 mini
- RGB LED
- 220 歐姆電阻x2
- 亮度感測模組
- 超音波模組
'''
ssid = "你的WiFi名稱"
pw =   "你的WiFi密碼"
key =  "你的金鑰"
# thingspeak API
url = "https://api.thingspeak.com/update?api_key="+ key

print("連接 WiFi: " + ssid + "...")
wifi = network.WLAN(network.STA_IF)
wifi.active(True) # 啟用WiFi物件
wifi.connect(ssid, pw) # 開始連接到指定WiFi
# 檢查連線狀態，還沒連接上就繼續跑迴圈
while not wifi.isconnected():
    pass
print("已連上")

print("智慧小夜燈已啟動")

# 建立超音波模組物件
# 指定trigger在0號腳位(D3)，指定echo在16號腳位(D0)
sonar = HCSR04(trigger_pin=0, echo_pin=16)

# r = PWM(Pin(14, Pin.OUT), freq=1000, duty=0)
g = PWM(Pin(12, Pin.OUT), freq=1000, duty=0)
b = PWM(Pin(13, Pin.OUT), freq=1000, duty=0)
# 是否有人過來 0 沒有 1 有
go_by = 0

'''
Field 1 light_level     亮度等級
Field 2 led_light_value LED亮度
Field 3 distance        距離
Field 4 go_by           是否有人過來
'''
while True:
    go_by = 0
    led_light_value = 0
    distance = sonar.distance_cm()  # 讀取超音波模組偵測到的障礙物距離(公分)
    # 讀取亮度感測器的亮度，使用i2c物件指定scl在5號腳位(D1)，指定sda在4號腳位(D2)
    light_level = bh1750fvi.sample(I2C(scl=Pin(5), sda=Pin(4)), mode=0x23) 
    
    if 2 <= distance <= 30: # 如果距離在2~30公分
        print("有人經過")
        led_light_value = 1023        
        go_by = 1        
    else: # 判斷亮度是否小於256
        if light_level > 256:
            light_level = 256
        if light_level < 256:
            print("亮度太暗")
            led_light_value = (256 - light_level) * 4 - 1
        if led_light_value < 1:
            led_light_value = 0
    
    # led_light_value改變LED工作週期
    g.duty(led_light_value) 
    b.duty(led_light_value)
    
    if led_light_value:# 如果亮了，傳送資料到 thingspeak
        if wifi.isconnected():
            response = urequests.get(url+ "&field1=" + str(light_level)
                                         + "&field2=" + str(led_light_value)
                                         + "&field3=" + str(distance)
                                         + "&field4=" + str(go_by))
            if response.status_code == 200:
                print("thingspeak 呼叫成功: 傳送資料", light_level, led_light_value, distance, go_by)
            else:
                print("thingspeak 呼叫失敗", light_level, led_light_value, distance, go_by)
        else:
            print('網路斷線')    
    utime.sleep(10)

'''  
# 超音波腳位  意義     D1 MINI對應腳位
# VCC         電源     3V3
# Gnd         接地     G
# Trig        觸發角   D3(0號腳位)
# Echo        接收角   D0(16號腳位)

# 亮度模組腳位    意義         D1 MINI對應腳位
# Vcc             電源         3V3
# GND             接地         G
# SCL             串列時脈線   D1(5號腳位)
# SDA             串列資料線   D2(4號腳位)
# ADDR            位址切換     不接線

# RGB LED腳位   D1 MINI對應腳位
# R             不接線
# G             D6(12號腳位)
# B             D7(13號腳位)
# 接地          G
'''
