from moviepy import AudioFileClip
import os

# 檢查音檔是否有效
audio_path = "test_gen/scene_01.wav"

if not os.path.exists(audio_path):
    print(f"❌ 找不到檔案: {audio_path}")
else:
    print(f"✅ 找到檔案: {audio_path}")
    print(f"檔案大小: {os.path.getsize(audio_path)} bytes")
    
    try:
        audio = AudioFileClip(audio_path)
        print(f"✅ 成功讀取音檔")
        print(f"   - 長度: {audio.duration:.2f} 秒")
        print(f"   - 採樣率: {audio.fps} Hz")
        print(f"   - 音頻陣列形狀: {audio.to_soundarray().shape}")
        print(f"   - 音頻數據範圍: 最小={audio.to_soundarray().min()}, 最大={audio.to_soundarray().max()}")
        
        # 檢查是否全是靜音（全是0）
        sound_array = audio.to_soundarray()
        if (sound_array == 0).all():
            print("⚠️ 警告：音檔全是靜音！")
        else:
            print("✅ 音檔包含音頻數據")
            
    except Exception as e:
        print(f"❌ 讀取音檔失敗: {e}")
