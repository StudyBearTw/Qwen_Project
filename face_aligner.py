import cv2
import os
import insightface
from insightface.app import FaceAnalysis

class FaceAligner:
    def __init__(self, model_dir="./models"):
        print("\n--- [Stage 2] 初始化臉部對齊引擎 (InsightFace) ---")
        
        # 1. 載入人臉偵測與特徵提取模型 (buffalo_l 是官方推薦的強大模型)
        self.app = FaceAnalysis(name='buffalo_l', root=model_dir)
        # ctx_id=0 代表強制使用第一張 GPU，det_size 設為 640 提高小臉偵測率
        self.app.prepare(ctx_id=0, det_size=(640, 640)) 
        
        # 2. 載入換臉核心模型 (Inswapper)
        swapper_path = os.path.join(model_dir, 'inswapper_128.onnx')
        if not os.path.exists(swapper_path):
            raise FileNotFoundError(f"❌ 找不到換臉模型：{swapper_path}。請確認已下載並放置於正確位置！")
            
        self.swapper = insightface.model_zoo.get_model(swapper_path, download=False, download_zip=False)
        print("✅ 臉部對齊引擎載入完成！")

    def align_faces(self, image_paths):
        """
        傳入包含圖片路徑的 List。
        預設第一張圖 image_paths[0] 為基準臉 (Source)，後續圖片為目標圖 (Target)。
        """
        if not image_paths or len(image_paths) < 2:
            print("  [Stage 2] 圖片數量不足，略過臉部對齊。")
            return

        # --- A. 提取第一幕基準臉 (Source Face) ---
        ref_path = image_paths[0]
        ref_img = cv2.imread(ref_path)
        ref_faces = self.app.get(ref_img)

        if not ref_faces:
            print(f"  [警告] 在第一幕 {ref_path} 中找不到臉部，放棄對齊。")
            return

        # 假設畫面中最大的臉就是主角
        source_face = ref_faces[0] 
        print(f"  [系統] 成功鎖定基準臉部特徵 (來源: {ref_path})")

        # --- B. 替換後續幕的臉部 (Target Faces) ---
        for target_path in image_paths[1:]:
            target_img = cv2.imread(target_path)
            target_faces = self.app.get(target_img)

            if not target_faces:
                print(f"  [警告] 在 {target_path} 中找不到臉部，跳過對齊。")
                continue

            target_face = target_faces[0]
            
            # 執行換臉魔法
            result_img = self.swapper.get(target_img, target_face, source_face, paste_back=True)
            
            # 覆寫原本略有漂移的圖片
            cv2.imwrite(target_path, result_img)
            print(f"  [系統] 🪄 已成功對齊並修復五官：{target_path}")