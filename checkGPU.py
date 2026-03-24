import torch

def test_environment():
    print("--- 系統環境檢測 ---")
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        # 取得總 VRAM 並轉換為 GB
        total_vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        
        print(f"✅ 成功抓到 GPU: {gpu_name}")
        print(f"✅ 可用 VRAM 容量: {total_vram:.2f} GB")
        print(f"✅ PyTorch 支援的 CUDA 版本: {torch.version.cuda}")
    else:
        print("❌ 警告：沒有抓到 GPU，請檢查 PyTorch 安裝版本！")

if __name__ == "__main__":
    test_environment()

#開啟storyvenv:story_env\Scripts\activate