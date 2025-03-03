# tiktokmatrix

自动批量在tiktok上传视频

素材视频下载
通过youtube_monitor.py来监控google sheet，用户将关注的youtube频道更新到google sheet中，脚本会在循环中检索新加入的频道中的视频，对于满足播放量及点赞量的视频的url保存到名字为“Youtube”的google sheet中；
通过yt-dlp.py这个脚本下载保存到“Youtube”的google sheet中的视频到本地，并自动剪切成规定长度的短视频；
运行Android模拟器
下载模拟器：https://jp.ldplayer.net/?from=en
在模拟器中从 APKPure 下载 TikTok APK
在模拟器中启用开发者模式
配置模拟器说明
配置 Appium连接模拟器
确保本地的python版本为3.9+；
使用以下命令安装 Appium，
pip install appium
pip install opencv-python
pip install pyautogui
安装 Appium Server
npm install -g appium
appium
配置 Appium 连接模拟器
使用该命令，链接模拟器：bash：adb devices
使用tiktok_test.py脚本打开 TikTok、模拟滑动刷视频
使用tiktok_upload.py来上传视频（尚未实现）
