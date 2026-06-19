import json
import os
import torch
import soundfile as sf
import concurrent.futures
from diffusers import DiffusionPipeline 
from qwen_tts import Qwen3TTSModel
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

# 確保輸出資料夾存在
OUTPUT_DIR = "test_gen"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_models():
    print("--- [1/3] 開始載入 AI 模型 ---")
    
    print("載入生圖模型 (Qwen-Image-2512) 中...")
    image_pipe = DiffusionPipeline.from_pretrained(
        "Qwen/Qwen-Image-2512", 
        torch_dtype=torch.bfloat16 
    )
    image_pipe.enable_sequential_cpu_offload()
    image_pipe.vae.enable_slicing()
    image_pipe.vae.enable_tiling()

    print("載入語音模型中...")
    tts_model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", 
        device_map="auto",
        dtype=torch.bfloat16,
        attn_implementation="sdpa"
    )
    
    print("✅ 所有模型載入完畢 (準備啟動平行運算)！\n")
    return image_pipe, tts_model

def generate_image_task(scene_id, full_prompt, image_pipe, img_path):
    print(f"  [圖-執行緒] 啟動！正在繪製第 {scene_id} 幕 (Qwen 極限運算中)...")
    
    fixed_generator = torch.Generator().manual_seed(42)
    
    image = image_pipe(
        prompt=full_prompt, 
        num_inference_steps=40, 
        guidance_scale=5.0,
        generator=fixed_generator
    ).images[0]
    
    full_img_path = os.path.join(OUTPUT_DIR, img_path)
    image.save(full_img_path)
    print(f"  [圖-執行緒] 第 {scene_id} 幕圖片生成完畢！")

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
    
    # === 1. 🌟 動態解析多角色註冊表 (Character Registry) ===
    registry = story_data["project_metadata"].get("character_registry", {})
    character_card_parts = []
    
    # 1.1 解析主角 (Protagonist)
    protagonist = registry.get("protagonist", {})
    if protagonist:
        pro_name = protagonist.get("name", "The main character")
        pro_species = protagonist.get("species", "character")
        pro_outfit = protagonist.get("outfit", "")
        pro_desc = f"The protagonist is {pro_name}, a {pro_species}."
        if pro_outfit: 
            pro_desc += f" Wearing: {pro_outfit}."
        character_card_parts.append(pro_desc)

    # 1.2 解析配角陣列 (Supporting Characters)
    supporters = registry.get("supporting_characters", [])
    for sup in supporters:
        s_name = sup.get("name", "A supporting character")
        s_species = sup.get("species", "")
        s_role = sup.get("role", "")
        s_outfit = sup.get("outfit", "")
        
        s_desc = f"Also present is {s_name}"
        if s_species: s_desc += f", a {s_species}"
        if s_role: s_desc += f" ({s_role})"
        s_desc += "."
        if s_outfit: s_desc += f" Wearing: {s_outfit}."
        character_card_parts.append(s_desc)

    # 1.3 解析角色關係 (Relationship Dynamics)
    relationship = registry.get("relationship_dynamics", "")
    if relationship:
        character_card_parts.append(f"Relationship context: {relationship}.")

    # 將所有角色資訊組合成一個巨大的提示詞區塊
    character_card = " ".join(character_card_parts)
    print(f"  [系統] 多角色設定卡已載入:\n   -> {character_card}")
    
    scenes = story_data["scenes"]
    video_clips = [] 
    
    for scene in scenes:
        scene_id = scene["scene_id"]
        print(f"\n>> 正在處理第 {scene_id} 幕...")
        
        # === 2. 動態解析單幕場景設定卡 ===
        env_data = scene.get("environment", {})
        env_parts = []
        if env_data.get("location"): 
            env_parts.append(f"Location: {env_data['location']}.")
        if env_data.get("time_and_weather"): 
            env_parts.append(f"Time and weather: {env_data['time_and_weather']}.")
        if env_data.get("key_elements"): 
            env_parts.append(f"Key elements: {env_data['key_elements']}.")
        if env_data.get("lighting_and_atmosphere"): 
            env_parts.append(f"Lighting and atmosphere: {env_data['lighting_and_atmosphere']}.")
            
        env_card = " ".join(env_parts)
        print(f"  [系統] 第 {scene_id} 幕場景卡已載入: {env_card}")
        
        img_path = f"test_sound_scene_{scene_id:02d}.png"
        wav_path = f"test_sound_scene_{scene_id:02d}.wav"
        
        # === 3. 終極 Prompt 組合方程式 ===
        # [全局畫風] + [多角色設定卡] + [單幕場景卡] + [單幕動作與鏡頭]
        full_prompt = f"{global_style} {character_card} {env_card} {scene['image_prompt']}"
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_img = executor.submit(generate_image_task, scene_id, full_prompt, image_pipe, img_path)
            future_aud = executor.submit(generate_audio_task, scene_id, scene["narration"], tts_model, wav_path)
            concurrent.futures.wait([future_img, future_aud])
        
        torch.cuda.empty_cache()

        print(f"  [影-主線] 正在將第 {scene_id} 幕的圖與音組合成影片...")
        audio_clip = AudioFileClip(os.path.join(OUTPUT_DIR, wav_path))
        image_clip = ImageClip(os.path.join(OUTPUT_DIR, img_path)).with_duration(audio_clip.duration)
        video_clip = image_clip.with_audio(audio_clip)
        
        video_clips.append(video_clip)
        print(f"  [影-主線] 第 {scene_id} 幕剪輯完成")

    return video_clips

def synthesize_final_video(video_clips, output_filename="testsound_final_storybook.mp4"):
    print("\n--- [3/3] 開始進行全片串接與輸出 ---")
    
    final_video = concatenate_videoclips(video_clips)
    
    audio_clips = [clip.audio for clip in video_clips if clip.audio is not None]
    if audio_clips:
        final_audio = concatenate_audioclips(audio_clips)
        final_video = final_video.with_audio(final_audio)
    
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