import re

class QueryPreprocessor:
    def __init__(self):
        # Bảng từ đồng nghĩa và viết tắt thông dụng trong lĩnh vực lao động
        self.synonyms = {
            "hdld": "hợp đồng lao động",
            "hđlđ": "hợp đồng lao động",
            "nlđ": "người lao động",
            "nsdlđ": "người sử dụng lao động",
            "bhxh": "bảo hiểm xã hội",
            "bhyt": "bảo hiểm y tế",
            "bhtn": "bảo hiểm thất nghiệp",
            "ot": "làm thêm giờ",
            "bầu bí": "thai sản",
            "nghỉ đẻ": "nghỉ thai sản",
            "đẻ": "sinh con",
            "đuổi việc": "sa thải",
            "chấm dứt hợp đồng": "chấm dứt hợp đồng lao động",
            "lương cơ bản": "mức lương tối thiểu",
            "thưởng tết": "tiền thưởng",
            "tai nạn lđ": "tai nạn lao động",
            "bệnh nn": "bệnh nghề nghiệp",
            "nghỉ đẻ xong": "sau khi sinh con",
            "phạt tiền": "xử lý kỷ luật",
            "trừ lương": "khấu trừ tiền lương",
            "kí hợp đồng": "giao kết hợp đồng",
            "bỏ việc": "đơn phương chấm dứt hợp đồng",
            "nghỉ việc": "thôi việc",
            "đền bù": "bồi thường",
            "công ty": "người sử dụng lao động",
            "nhân viên": "người lao động",
            "sếp": "người sử dụng lao động",
            "vợ đẻ": "vợ sinh con",
            "cưới": "kết hôn",
            "lễ tết": "nghỉ lễ",
            "tăng ca": "làm thêm giờ"
        }

        # Biên dịch regex để thay thế từ nguyên vẹn (word boundaries)
        # Vì tiếng Việt có dấu, \b có thể không hoàn hảo nhưng vẫn dùng tốt cho các từ tiếng Việt chuẩn.
        # Một cách an toàn hơn cho tiếng Việt là dùng regex thay thế với r'(?<!\w)word(?!\w)'
        self.patterns = []
        for key, value in self.synonyms.items():
            pattern = r"(?<!\S)" + re.escape(key) + r"(?!\S)"
            self.patterns.append((re.compile(pattern), value))

    def preprocess(self, text: str) -> str:
        if not text:
            return text
            
        # 1. Lowercase
        text = text.lower()
        
        # 2. Xóa các ký tự đặc biệt không cần thiết (chỉ giữ lại chữ cái, số, khoảng trắng và các dấu câu cơ bản)
        text = re.sub(r'[^\w\s\.,\?]', ' ', text)
        
        # 3. Thay thế từ đồng nghĩa / viết tắt
        for pattern, replacement in self.patterns:
            text = pattern.sub(replacement, text)
            
        # 4. Chuẩn hóa khoảng trắng (loại bỏ khoảng trắng thừa)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
