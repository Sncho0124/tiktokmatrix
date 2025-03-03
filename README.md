# 自动批量在tiktok上传视频

### 素材视频下载
1. 通过youtube_monitor.py来监控google sheet，用户将关注的youtube频道更新到google sheet中，脚本会在循环中检索新加入的频道中的视频，对于满足播放量及点赞量的视频的url保存到名字为“Youtube”的google sheet中；
2. 通过yt-dlp.py这个脚本下载保存到“Youtube”的google sheet中的视频到本地，并自动剪切成规定长度的短视频；

### 运行Android模拟器
1. 下载模拟器：https://jp.ldplayer.net/?from=en
2. 在模拟器中从 APKPure 下载 TikTok APK
3. 在模拟器中启用开发者模式
4. 配置模拟器说明:https://docs.google.com/document/d/1P6JVwVRjpLgfG6dwtt36H9DYbmzjfOvtwKrr49CjLyA/edit?tab=t.0#heading=h.43e390xfijtn

###  配置 Appium连接模拟器
1. 确保本地的python版本为3.9+；
2.  使用以下命令安装 Appium，
```
    pip install appium
    pip install opencv-python
    pip install pyautogui
```
4.  安装 Appium Server
```
    npm install -g appium
    appium
```
6. 配置 Appium 连接模拟器
    使用该命令，链接模拟器
   ```
   adb devices
   ```   
### 使用脚本控制tiktok
    使用tiktok_test.py脚本打开 TikTok、模拟滑动刷视频
    使用tiktok_upload.py来上传视频（尚未实现）
