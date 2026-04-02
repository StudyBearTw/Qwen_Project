from moviepy import VideoFileClip
import os

# 檢查生成的 MP4 檔案
mp4_path = "test_gen/scene_01_test_sound.mp4"

if not os.path.exists(mp4_path):
    print(f"❌ 找不到視頻檔案: {mp4_path}")
else:
    print(f"✅ 找到視頻檔案: {mp4_path}")
    print(f"檔案大小: {os.path.getsize(mp4_path)} bytes")
    
    try:
        video = VideoFileClip(mp4_path)
        print(f"✅ 成功讀取視頻檔案")
        print(f"   - 長度: {video.duration:.2f} 秒")
        print(f"   - 幀速率: {video.fps} fps")
        print(f"   - 解析度: {video.size}")
        
        if video.audio is None:
            print("❌ 視頻中沒有音軌！")
        else:
            print(f"✅ 視頻包含音軌")
            print(f"   - 音軌長度: {video.audio.duration:.2f} 秒")
            print(f"   - 採樣率: {video.audio.fps} Hz")
            
    except Exception as e:
        print(f"❌ 讀取視頻檔案失敗: {e}")
