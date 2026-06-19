import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

def generate_voice():
    print("--- 準備載入 Qwen3-TTS (1.7B 高音質模型) ---")
    
    # 1. 載入模型
    # 注意：Windows 原生環境對 Flash Attention 支援較差，
    # 這裡我們明確指定使用 "sdpa" (PyTorch 內建加速) 來完美避開 Windows 報錯。
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", 
        device_map="cuda:0",
        dtype=torch.bfloat16,
        attn_implementation="sdpa" 
    )
    print("✅ 模型載入完成！")

    # 2. 設定中文文本
    text_zh = "從前從前，有三隻小豬兄弟。有一天，豬媽媽告訴他們，是時候離開家，自己去蓋房子了。"
    print(f"準備合成語音：\n「{text_zh}」\n請稍候...")

    # 3. 執行語音合成 (Qwen3-TTS 內建多種優質聲線，Vivian 是很棒的中文女聲)
    wavs, sr = model.generate_custom_voice(
        text=text_zh,
        language="Chinese",
        speaker="Vivian", 
    )
    
    # 4. 存檔
    output_filename = "scene_01.wav"
    sf.write(output_filename, wavs[0], sr)
    print(f"✅ 語音生成成功！已儲存為 {output_filename}")

if __name__ == "__main__":
    generate_voice()