import json
import os
import torch
import soundfile as sf
import concurrent.futures  # 🌟 新增：Python 內建的平行處理套件
from diffusers import DiffusionPipeline 
from qwen_tts import Qwen3TTSModel
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

# 確保輸出資料夾存在
OUTPUT_DIR = "test_gen"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_models():
    print("--- [1/3] 開始載入 AI 模型 ---")
    
    # 1. 載入圖像模型 (Qwen-Image-2512)
    print("載入生圖模型 (Qwen-Image-2512) 中...")
    image_pipe = DiffusionPipeline.from_pretrained(
        "Qwen/Qwen-Image-2512", 
        torch_dtype=torch.bfloat16 
    )
    # 🌟 沿用方案 A：極限序列卸載 (這是我們能平行運作的保命符)
    image_pipe.enable_sequential_cpu_offload()
    image_pipe.vae.enable_slicing()
    image_pipe.vae.enable_tiling()

    # 2. 載入語音模型 (Qwen3-TTS)
    print("載入語音模型中...")
    tts_model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", 
        device_map="auto",
        dtype=torch.bfloat16,
        attn_implementation="sdpa"
    )
    
    print("✅ 所有模型載入完畢 (準備啟動平行運算)！\n")
    return image_pipe, tts_model

# 🌟 獨立出「畫圖」的任務函式，供執行緒呼叫
def generate_image_task(scene_id, full_prompt, image_pipe, img_path):
    print(f"  [圖-執行緒] 啟動！正在繪製第 {scene_id} 幕 (Qwen 極限運算中)...")
    image = image_pipe(
        prompt=full_prompt, 
        num_inference_steps=40, 
        guidance_scale=5.0
    ).images[0]
    full_img_path = os.path.join(OUTPUT_DIR, img_path)
    image.save(full_img_path)
    print(f"  [圖-執行緒] 第 {scene_id} 幕圖片生成完畢！")

# 🌟 獨立出「配音」的任務函式，供執行緒呼叫
def generate_audio_task(scene_id, narration, tts_model, wav_path):
    print(f"  [音-執行緒] 啟動！正在合成第 {scene_id} 幕配音...")
    wavs, sr = tts_model.generate_custom_voice(
        text=narration,
        language="Chinese",
        speaker="Vivian"
    )
    full_wav_path = os.path.join(OUTPUT_DIR, wav_path)
    sf.write(full_wav_path, wavs[0], sr)
    print(f"  [音-執行緒] 第 {scene_id} 幕配音生成完畢！")

def process_story(json_path, image_pipe, tts_model):
    print("--- [2/3] 開始解析故事並雙線平行生成素材 ---")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        story_data = json.load(f)
            
    global_style = story_data["project_metadata"]["global_style_prompt"]
    scenes = story_data["scenes"]
    
    video_clips = [] 
    
    for scene in scenes:
        scene_id = scene["scene_id"]
        print(f"\n>> 正在處理第 {scene_id} 幕...")
        
        img_path = f"test_sound_scene_{scene_id:02d}.png"
        wav_path = f"test_sound_scene_{scene_id:02d}.wav"
        full_prompt = global_style + scene["image_prompt"]
        
        # 🌟 平行處理核心：開啟一個最多容納 2 個工人的執行緒池
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # 同時把兩個任務發派給工人
            future_img = executor.submit(generate_image_task, scene_id, full_prompt, image_pipe, img_path)
            future_aud = executor.submit(generate_audio_task, scene_id, scene["narration"], tts_model, wav_path)
            
            # 程式會停在這裡，直到兩個工人都回報「做完了」才會繼續往下走
            concurrent.futures.wait([future_img, future_aud])
        
        # 兩邊都做完後，清理一下 GPU 記憶體碎片
        torch.cuda.empty_cache()

        # --- C. 合成單幕影片 ---
        print(f"  [影-主線] 正在將第 {scene_id} 幕的圖與音組合成影片...")
        audio_clip = AudioFileClip(os.path.join(OUTPUT_DIR, wav_path))
        image_clip = ImageClip(os.path.join(OUTPUT_DIR, img_path)).with_duration(audio_clip.duration)
        video_clip = image_clip.with_audio(audio_clip)
        
        video_clips.append(video_clip)
        print(f"  [影-主線] 第 {scene_id} 幕剪輯完成")

    return video_clips

def synthesize_final_video(video_clips, output_filename="testsound_final_storybook.mp4"):
    print("\n--- [3/3] 開始進行全片串接與輸出 ---")
    
    # 🌟 關鍵修復：拿掉 method="compose"，回歸最原生的串接方式
    # 這樣 MoviePy 就會乖乖保留每一幕原本已經綁定好的音軌
    final_video = concatenate_videoclips(video_clips)
    
    # 🌟 新增：提取並連接所有音軌
    audio_clips = [clip.audio for clip in video_clips if clip.audio is not None]
    if audio_clips:
        final_audio = concatenate_audioclips(audio_clips)
        final_video = final_video.with_audio(final_audio)
    
    # 計算完整的輸出路徑
    full_output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    print(f"🎬 渲染最終影片中，請稍候...")
    final_video.write_videofile(
        full_output_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="libmp3lame",
        logger=None 
    )
    print(f"\n🎉 專案大功告成！完整繪本已儲存為 {full_output_path}")

if __name__ == "__main__":
    img_pipe, tts_model = load_models()
    clips = process_story("story.json", img_pipe, tts_model)
    synthesize_final_video(clips)