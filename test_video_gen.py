from moviepy import ImageClip, AudioFileClip

def create_video_scene():
    print("--- 啟動自動化剪輯台 ---")
    
    # 1. 設定素材路徑
    image_path = "scene_01.png"
    audio_path = "scene_01.wav"
    output_path = "scene_01.mp4"

    # 2. 載入音檔，獲取精準的語音長度
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration
    print(f"🎵 讀取到語音長度: {audio_duration:.2f} 秒")

    # 3. 載入圖片 (注意：2.x 版本改用 with_duration)
    image_clip = ImageClip(image_path).with_duration(audio_duration)

    # 4. 把語音軌道合併到圖片軌道上 (注意：2.x 版本改用 with_audio)
    video_clip = image_clip.with_audio(audio_clip)

    # 5. 輸出成 MP4 影片
    print("🎬 開始渲染影片，請稍候...")
    video_clip.write_videofile(
        output_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac"
    )

    print(f"✅ 第一幕影音合成成功！已儲存為 {output_path}")

if __name__ == "__main__":
    create_video_scene()