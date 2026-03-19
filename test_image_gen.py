import torch
from diffusers import AutoPipelineForText2Image

def generate_scene():
    print("--- 準備載入圖像生成模型 ---")
    
    # 1. 載入模型
    # 這裡我們使用 SDXL Turbo 作為測試，它速度極快且支援高畫質
    # (第一次執行時會自動從網路下載模型權重檔，約需幾 GB 的空間)
    pipe = AutoPipelineForText2Image.from_pretrained(
        "stabilityai/sdxl-turbo", 
        torch_dtype=torch.float16, 
        variant="fp16"
    )
    
    # 將模型推送到你的 RTX A4500 GPU 上
    pipe.to("cuda")
    print("✅ 模型載入完成！")

    # 2. 設定提示詞 (這就是未來從 Gemini JSON 解析出來的內容)
    # 我們把 global_style (水彩繪本風) 與 image_prompt (三隻小豬道別) 結合
    prompt = "Children's storybook illustration, watercolor style, bright and cheerful colors. Three cute little pigs standing in front of their mother pig, waving goodbye, in a sunny green meadow, wide shot."
    
    print("開始生成圖片，請稍候...")
    
    # 3. 執行推論生成 (Turbo 模型只需要 4 步就能生圖)
    image = pipe(prompt=prompt, num_inference_steps=4, guidance_scale=0.0).images[0]
    
    # 4. 存檔
    output_filename = "scene_01.png"
    image.save(output_filename)
    print(f"✅ 圖片生成成功！已儲存為 {output_filename}")

if __name__ == "__main__":
    generate_scene()