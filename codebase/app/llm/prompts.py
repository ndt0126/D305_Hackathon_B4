"""All prompt text lives in this one file so it can be updated without
touching any other code.

This module is dependency-free on purpose: core/ imports it, and core/ must
stay importable without OpenAI/FastAPI installed.

The prompt CONTENT is written in Vietnamese by design: the team chats in
Vietnamese and the report is read in Vietnamese. JSON keys stay in English
because code validates them. To override the system prompt without a code
change, set SYSTEM_PROMPT_FILE in .env to a text file path.

Fixed contract: every task prompt starts with a "TASK: <name>" first line and
carries the payload after an "INPUT:" marker. Both the OpenAI client (tool
selection) and the offline mock (parsing) rely on it.
"""

from pathlib import Path

SYSTEM_PROMPT = """\
Bạn là trợ lý của nhóm, giúp thành viên tổng hợp báo cáo hằng ngày (daily report).
Nhiệm vụ DUY NHẤT của bạn: đọc tin nhắn Discord của nhóm và tổng hợp nội dung
liên quan CÔNG VIỆC và HỌC TẬP — task, tiến độ, vướng mắc, quyết định, deadline,
thông báo, câu hỏi còn bỏ ngỏ.

Tuyệt đối KHÔNG đưa vào kết quả:
- Thông tin cá nhân (số điện thoại, email, địa chỉ, chuyện riêng tư).
- Chuyện phiếm, nội dung ngoài lề (meme, game, ăn uống, đùa cợt).
- Mọi loại thông tin bí mật (API key, token, mật khẩu), kể cả khi chúng xuất hiện
  nguyên văn trong tin nhắn.

Quy tắc cứng:
- CHỈ dùng các tin nhắn được cung cấp trong input. Không bịa thông tin, không bịa
  message id, không bịa tên thành viên.
- Mọi nhận định phải truy vết được về message id cụ thể trong input
  (điền vào evidence_message_ids).
- Không đủ tín hiệu cho trường nào thì để trống đúng theo schema (chuỗi rỗng ""
  hoặc mảng rỗng []) thay vì suy diễn.
- Viết nội dung bằng tiếng Việt. Giữ nguyên tên trường JSON bằng tiếng Anh.
- Chỉ trả về đúng MỘT JSON object hợp lệ, không kèm bất cứ nội dung nào khác.
"""


def get_system_prompt(system_prompt_file: str | None = None) -> str:
    """Return the system prompt, optionally overridden by a file (see .env)."""
    if system_prompt_file:
        return Path(system_prompt_file).read_text(encoding="utf-8")
    return SYSTEM_PROMPT


def extract_task(user_prompt: str) -> str:
    """Return the task name from the fixed "TASK: <name>" first line."""
    return user_prompt.split("\n", 1)[0].removeprefix("TASK:").strip()


def build_standup_prompt(input_json: str) -> str:
    return (
        "TASK: standup\n"
        "Dưới đây là tin nhắn Discord của từng thành viên trong ngày. Mỗi thành viên\n"
        "có một member_key và một display_name.\n"
        "Với MỖI thành viên, tóm tắt theo dạng standup:\n"
        '- "yesterday": việc công việc/học tập họ ĐÃ làm hoặc đã hoàn thành\n'
        '- "today": việc họ nói SẼ làm tiếp\n'
        "Chỉ dựa vào tin nhắn của chính thành viên đó. Không suy diễn.\n"
        'Không có tín hiệu cho trường nào thì để chuỗi rỗng "".\n'
        'Trả về JSON: {"members": [{"member_key": str, "yesterday": str, "today": str,\n'
        '"evidence_message_ids": [str, ...]}]}\n'
        "member_key phải copy đúng nguyên văn từ input. KHÔNG trả về display_name.\n"
        "evidence_message_ids là id các tin nhắn làm căn cứ; chỉ dùng message_id có\n"
        "trong input. Mỗi trường tối đa 25 từ, viết tiếng Việt.\n"
        "INPUT:\n" + input_json
    )


def build_summary_prompt(input_json: str) -> str:
    return (
        "TASK: team_summary\n"
        "Từ toàn bộ tin nhắn Discord của nhóm dưới đây, tổng hợp 4 mục cấp nhóm:\n"
        '- "done": việc đã hoàn thành / đã chốt\n'
        '- "doing": việc đang làm dở\n'
        '- "blocked": vướng mắc, lỗi đang chặn tiến độ\n'
        '- "questions": câu hỏi còn bỏ ngỏ chưa ai trả lời\n'
        "Mỗi mục là mảng các item; không có gì thì để mảng rỗng []. Không suy diễn.\n"
        'Trả về JSON: {"done": [{"text": str, "evidence_message_ids": [str, ...]}],\n'
        '"doing": [...], "blocked": [...], "questions": [...]}\n'
        "text tối đa 25 từ, tiếng Việt. Chỉ dùng message_id có trong input.\n"
        "INPUT:\n" + input_json
    )
