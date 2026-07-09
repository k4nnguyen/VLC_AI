import json
from pathlib import Path

def sort_json_cache(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"File {file_path} không tồn tại!")
        return

    # Đọc dữ liệu JSON hiện tại
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Hàm lấy số Điều để sắp xếp (ví dụ: "article_10" -> 10)
    # Tránh việc "article_10" đứng trước "article_2" theo bảng chữ cái
    def sort_key(item):
        key = item[0]
        try:
            return int(key.split("_")[1])
        except (IndexError, ValueError):
            return 999999 # Đẩy các key bị lỗi/lạ xuống cuối cùng

    # Sắp xếp dict theo số Điều luật
    sorted_data = dict(sorted(data.items(), key=sort_key))

    # Ghi đè lại vào file
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)

    print(f"Đã sắp xếp gọn gàng {len(sorted_data)} điều luật trong file {path.name}!")

if __name__ == "__main__":
    sort_json_cache("data/processed/concepts_cache.json")
