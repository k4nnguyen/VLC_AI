import sys
import subprocess
import os

def run_script(script_path):
    print(f"\n{'='*60}")
    print(f"Đang chạy: {script_path}")
    print(f"{'='*60}")
    # Đảm bảo PYTHONPATH trỏ về thư mục gốc để không bị lỗi import
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    # Chạy script bằng subprocess
    try:
        subprocess.run([sys.executable, script_path], env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[LỖI] Quá trình chạy {script_path} thất bại với mã lỗi {e.returncode}")
    except KeyboardInterrupt:
        print(f"\n[DỪNG] Người dùng đã dừng chạy {script_path}")
    print(f"{'='*60}\n")

def main():
    while True:
        print("HỆ THỐNG ĐÁNH GIÁ (EVALUATION SYSTEM)")
        print("1. Đánh giá Khả năng truy xuất (evaluate.py)")
        print("2. Đánh giá Khả năng tạo câu trả lời (evaluate_generation.py)")
        print("3. Đánh giá Khả năng viết lại câu hỏi (evaluate_query_rewrite.py)")
        print("4. Tạo tập dữ liệu đánh giá mới (generate_evaluation.py)")
        print("5. Thoát")
        
        choice = input("Nhập lựa chọn của bạn (1-5): ").strip()
        
        if choice == '1':
            run_script("evaluations/evaluate.py")
        elif choice == '2':
            run_script("evaluations/evaluate_generation.py")
        elif choice == '3':
            run_script("evaluations/evaluate_query_rewrite.py")
        elif choice == '4':
            run_script("evaluations/generate_evaluation.py")
        elif choice == '5':
            print("Đã thoát chương trình.")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng nhập số từ 1 đến 5.\n")

if __name__ == "__main__":
    # Sửa lỗi hiển thị tiếng Việt trên Terminal Windows
    sys.stdout.reconfigure(encoding='utf-8')
    main()
