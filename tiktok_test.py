from appium import webdriver
from appium.options.android import UiAutomator2Options
import time

caps = UiAutomator2Options()
caps.platform_name = "Android"
caps.device_name = "127.0.0.1:5555"
caps.automation_name = "UiAutomator2"
caps.app_package = "com.zhiliaoapp.musically"
caps.app_activity = "com.ss.android.ugc.aweme.splash.SplashActivity"
caps.app_wait_activity = "com.ss.android.ugc.aweme.main.MainActivity, com.ss.android.ugc.aweme.splash.SplashActivity"
caps.no_reset = True

try:
    driver = webdriver.Remote("http://127.0.0.1:4723", options=caps)
    print("Connected to Appium Server! Launching TikTok...")
except Exception as e:
    print(f"Failed to connect to Appium: {e}")
    exit(1)

time.sleep(5)

current_activity = driver.current_activity
if "aweme" not in current_activity:
    print(f"TikTok launch failed, current Activity: {current_activity}")
    driver.quit()
    exit(1)

print("TikTok launched successfully! Starting auto swipe...")

def swipe_up(driver):
    screen_size = driver.get_window_size()
    start_x = screen_size["width"] // 2
    start_y = screen_size["height"] * 3 // 4  
    end_x = start_x
    end_y = screen_size["height"] // 4  

    height = abs(end_y - start_y)

    driver.execute_script("mobile: swipeGesture", {
        "left": start_x,
        "top": min(start_y, end_y),
        "width": 1,
        "height": height, 
        "direction": "up",
        "percent": 1.0
    })

for i in range(5):
    print(f"Swiping video {i+1}...")
    swipe_up(driver)
    time.sleep(3)

print("Auto scrolling on TikTok completed!")

driver.quit()
