from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
import time
import os
import glob

VIDEO_SAVE_PATH = "D:/YouTubeDownloads/outputs/"

def get_latest_video(path):
    files = glob.glob(os.path.join(path, "*.mp4"))
    if not files:
        return None
    return max(files, key=os.path.getctime)

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

print("Waiting for TikTok to load...")
time.sleep(15)

current_activity = driver.current_activity
if "aweme" not in current_activity:
    print(f"TikTok launch failed, current Activity: {current_activity}")
    driver.quit()
    exit(1)

print("TikTok launched successfully!")

def tap_bottom_center(driver):
    screen_size = driver.get_window_size()
    center_x = screen_size["width"] // 2  
    center_y = screen_size["height"] - 80  

    print(f"Tapping TikTok '+' button at coordinates: ({center_x}, {center_y})")

    driver.execute_script("mobile: clickGesture", {
        "x": center_x,
        "y": center_y
    })

    print("Successfully tapped TikTok '+' button.")

try:
    print("Tapping the '+' button...")
    tap_bottom_center(driver)
    time.sleep(10)

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    try:
        print("Waiting for 'Upload' button...")
        wait = WebDriverWait(driver, 10)
        upload_button = wait.until(EC.presence_of_element_located((By.XPATH, "//android.widget.TextView[@text='Upload']")))

        print("Clicking 'Upload' button...")
        upload_button.click()
        time.sleep(5)
    except Exception as e:
        print(f"Failed to enter upload page: {e}")
        driver.quit()
        exit(1)

except Exception as e:
    print(f"Failed to enter upload page: {e}")
    driver.quit()
    exit(1)

video_file = get_latest_video(VIDEO_SAVE_PATH)
if not video_file:
    print("No video file found for upload!")
    driver.quit()
    exit(1)

try:
    print(f"Selecting local video: {video_file}")

    video_element = None
    try:
        video_element = driver.find_element("xpath", "//android.widget.ImageView[@content-desc='Select Video']")
    except:
        pass

    if not video_element:
        try:
            video_element = driver.find_element("xpath", "//android.widget.TextView[@text='Videos']")
        except:
            pass

    if video_element:
        video_element.click()
        time.sleep(10)
    else:
        raise Exception("Unable to locate video selection panel")

    print("Confirming video selection...")
    next_button = driver.find_element("xpath", "//android.widget.TextView[@text='Next']")
    next_button.click()
    time.sleep(10)
except Exception as e:
    print(f"Video selection failed: {e}")
    driver.quit()
    exit(1)

try:
    print("Entering title...")
    title_input = driver.find_element("xpath", "//android.widget.EditText")
    title_input.send_keys("🔥 Latest trending animation! Watch now!")
    time.sleep(10)
except Exception as e:
    print(f"Failed to enter title: {e}")
    driver.quit()
    exit(1)

try:
    print("Clicking 'Post' button...")
    post_button = driver.find_element("xpath", "//android.widget.TextView[@text='Post']")
    post_button.click()
    time.sleep(10)
except Exception as e:
    print(f"Upload failed: {e}")
    driver.quit()
    exit(1)

print("Video uploaded successfully!")

driver.quit()
