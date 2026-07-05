# 全自動 AI 有聲繪本Pipeline

這是一個基於 Python 開發的端到端 (End-to-End) AI 多媒體生成系統。本專案整合了擴散模型 (Diffusion Models) 與語音合成 (TTS) 技術，能將標準化的 JSON 劇本全自動轉換為高畫質、視聽同步的影音繪本。

## Key Features

本專案不僅僅是 API 串接，更專注於解決擴散模型在純文字控制下的底層物理極限：

*   **多角色特徵解耦與空間隔離**
    為了解決多角色生成時常見的「特徵污染 (Concept Bleeding)」問題，本系統引入了關聯式 JSON 架構 (`character_registry`)。透過後端 Python 動態組裝提示詞，結合數量宣告與絕對位置約束 (如 `On the left... On the right...`)，成功達到 80% 的跨物種特徵分離。
*   **微分鏡切分架構**
    將長篇旁白解構為 3~5 秒的黃金注意力區間，並強制注入漸進式鏡頭語言 (Wide -> Medium -> Close-up)，確保單張靜態圖能與語音節奏完美咬合，符合教育心理學之認知負荷理論。
*   **平行處理與硬體極限優化**
    採用 `concurrent.futures` 實作生圖與語音的雙執行緒平行運算。針對 RTX A4500 (20GB VRAM) 設備，實作極限序列卸載 (Sequential CPU Offload)，確保大型模型 (Qwen-Image-2512) 能穩定運行而不發生 OOM (Out of Memory) 崩潰。

## Tech Stack

*   **視覺生成引擎**: Qwen-Image-2512 (`diffusers`)
*   **語音合成引擎**: Qwen3-TTS (`transformers`)
*   **影音剪輯模組**: `moviepy`
*   **核心語言**: Python (PyTorch)

## Data Schema

系統採用高度模組化的 JSON 格式驅動，確保前端劇本與後端生成邏輯完美對齊：
*   `character_registry`: 支援陣列化的多配角動態載入，並鎖定角色底層屬性 (`base_clothing`) 以避免模型產生擬人化幻覺。
*   `environment`: 獨立的環境與光影控制。
*   `scenes`: 包含動態鏡頭與簡練旁白的連續分鏡陣列。

## Quick Start

### 1. 安裝環境與相依套件

請確認已安裝 Python 3.10 以上版本，並執行以下指令安裝必備套件：
```bash
pip install torch diffusers transformers soundfile moviepy accelerate

### 2. 準備劇本

請將符合本專案 Data Schema 格式的劇本儲存為 story.json，並放置於專案根目錄下。專案內已提供《青蛙王子與金球》作為預設測試範例。

### 3. 執行生成pipelne

在終端機中執行主程式：
```python main.py```

系統將自動執行以下流程：
載入生圖與語音模型至 GPU/CPU。
啟動執行緒池，平行生成各幕圖片 (.png) 與語音 (.wav)。
呼叫 MoviePy 進行影音精準對位與剪輯。
最終合成的 MP4 繪本將自動輸出於 test_gen 資料夾中。
