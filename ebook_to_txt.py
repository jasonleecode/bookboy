import pyautogui
from pynput import mouse
import time
# 引入 macOS 原生 OCR 库
from ocrmac import ocrmac 

# ================= 配置区域 =================
# 翻页后的等待时间（秒）
PAGE_TURN_WAIT = 1.5 

# 输出文件名
OUTPUT_FILE = 'ebook_mac_content.txt'
# ===========================================

class EbookRipper:
    def __init__(self):
        self.coords = []

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.coords.append((x, y))
            step = len(self.coords)
            
            if step == 1:
                print(f"✅ 已记录文字区域【左上角】: ({x}, {y})")
                print("👉 请点击文字区域的【右下角】...")
            elif step == 2:
                print(f"✅ 已记录文字区域【右下角】: ({x}, {y})")
                print("👉 请点击电子书的【下一页按钮】...")
            elif step == 3:
                print(f"✅ 已记录【翻页按钮】位置: ({x}, {y})")
                print("\n🎉 校准完成！程序将在 3 秒后开始自动运行。")
                return False # 停止监听

    def calibrate(self):
        print("="*40)
        print("   Mac 原生 OCR 电子书转换工具 (校准模式)")
        print("="*40)
        print("请依次点击：1.左上角  2.右下角  3.翻页按钮")
        
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()
        
        return self.coords

    def run(self):
        coords = self.calibrate()
        top_left = coords[0]
        bottom_right = coords[1]
        next_btn = coords[2]

        # 计算截图区域
        region = (
            int(top_left[0]),
            int(top_left[1]),
            int(bottom_right[0] - top_left[0]),
            int(bottom_right[1] - top_left[1])
        )

        time.sleep(3)

        page_count = 1
        
        try:
            with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                while True:
                    print(f"正在处理第 {page_count} 页...", end="", flush=True)
                    
                    # 1. 截图并保存为临时文件 (ocrmac 需要文件路径或PIL image)
                    # 为了最佳兼容性，我们将截图保存到内存中的PIL对象，然后传给ocrmac
                    screenshot = pyautogui.screenshot(region=region)
                    
                    # 2. 使用 Mac 原生 OCR 识别
                    # ocrmac 支持直接传入 PIL Image 对象
                    # annotations = ocrmac.OCR(screenshot).recognize()
                    # 'zh-Hans' 代表简体中文，强制系统优先匹配中文
                    annotations = ocrmac.OCR(screenshot, language_preference=['zh-Hans']).recognize()
                    
                    # 3. 处理识别结果
                    # annotations 返回的是一个列表，每一项包含 (text, confidence, bbox)
                    # 我们只需要把 text 拼接起来
                    page_text = []
                    for item in annotations:
                        text_content = item[0] # 获取文字
                        page_text.append(text_content)
                    
                    final_text = "\n".join(page_text)

                    # 4. 写入文件
                    f.write(f"\n\n--- Page {page_count} ---\n\n")
                    f.write(final_text)
                    
                    print(f" 识别到 {len(page_text)} 行文字。翻页中...")

                    # 5. 点击下一页
                    pyautogui.click(x=next_btn[0], y=next_btn[1])
                    
                    page_count += 1
                    time.sleep(PAGE_TURN_WAIT)

        except KeyboardInterrupt:
            print("\n🛑 程序已停止。")
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    ripper = EbookRipper()
    ripper.run()