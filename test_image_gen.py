import torch
from diffusers import DiffusionPipeline

def generate_scene():
    print("--- 準備載入圖像生成模型 (Qwen-Image-2512) ---")
    
    pipe = DiffusionPipeline.from_pretrained(
        "Qwen/Qwen-Image-2512", 
        torch_dtype=torch.bfloat16
    )
    
    # 🌟 終極省 VRAM 三神技 🌟
    # 1. CPU 智慧卸載：不要用 .to("cuda")，讓套件自己決定誰該進 GPU，誰該退回 CPU
    # pipe.enable_model_cpu_offload() 
    pipe.enable_sequential_cpu_offload()
    # 2. VAE 切片解碼：將圖片切成小塊分批解碼，大幅壓低最後一步的 VRAM 峰值
    pipe.vae.enable_slicing()
    
    # 3. VAE 拼貼解碼：針對超高畫質生成的神級優化
    pipe.vae.enable_tiling()

    print("✅ 模型與 VRAM 優化設定完成！")

    #prompt = "Children's storybook illustration, watercolor style, bright and cheerful colors. Three cute little pigs standing in front of their mother pig, waving goodbye, in a sunny green meadow, wide shot."
    prompt = "童話故事書插畫，水彩風格，明亮愉快的色彩。三隻可愛的小豬站在他們的媽媽豬面前，揮手告別，在陽光明媚的綠色草地上，遠景。"
    print("開始生成圖片，請稍候...")
    
    image = pipe(
        prompt=prompt, 
        num_inference_steps=40, 
        guidance_scale=5.0
    ).images[0]
    
    output_filename = "scene_01_qwen.png"
    image.save(output_filename)
    print(f"✅ 圖片生成成功！已儲存為 {output_filename}")

if __name__ == "__main__":
    generate_scene()