from moviepy import ImageClip, AudioFileClip
import os

def create_video_scene():
    print("--- 啟動自動化剪輯台 ---")
    
    # 1. 設定素材路徑
    image_path = "test_gen/scene_01.png"
    audio_path = "test_gen/scene_01.wav"
    output_path = "test_gen/scene_01_test_sound.mp4"

    # 檢查檔案是否存在
    if not os.path.exists(image_path):
        print(f"❌ 錯誤：找不到圖片檔案 {image_path}")
        return
    if not os.path.exists(audio_path):
        print(f"❌ 錯誤：找不到音檔 {audio_path}")
        return

    # 2. 載入音檔，獲取精準的語音長度
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration
    print(f"🎵 讀取到語音長度: {audio_duration:.2f} 秒")
    print(f"🎵 音頻詳情 - 採樣率: {audio_clip.fps} Hz")

    # 3. 載入圖片 (注意：2.x 版本改用 with_duration)
    image_clip = ImageClip(image_path).with_duration(audio_duration)

    # 4. 把語音軌道合併到圖片軌道上 (注意：2.x 版本改用 with_audio)
    video_clip = image_clip.with_audio(audio_clip)
    
    # 檢查音頻是否正確附加
    if video_clip.audio is None:
        print("⚠️ 警告：音頻附加失败")
    else:
        print(f"✅ 音頻已成功附加，長度: {video_clip.audio.duration:.2f} 秒")

    # 5. 輸出成 MP4 影片 - 嘗試不同的編碼參數
    print("🎬 開始渲染影片，請稍候...")
    video_clip.write_videofile(
        output_path, 
        fps=24,
        codec="libx264",
        audio_codec="libmp3lame"  # 改用 MP3 編碼，相容性更好
    )

    print(f"✅ 第一幕影音合成成功！已儲存為 {output_path}")

if __name__ == "__main__":
    create_video_scene()

if __name__ == "__main__":
    create_video_scene()