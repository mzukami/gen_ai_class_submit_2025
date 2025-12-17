import os
import json
from pathlib import Path
from google import genai
from google.genai import types

# ----------------------------------------
# 1. system_prompt を読み込み
# ----------------------------------------
BASE_DIR = Path(__file__).resolve().parent
SYSTEM_PROMPT_PATH = BASE_DIR / "text" / "system_prompt.txt"

if SYSTEM_PROMPT_PATH.exists():
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
else:
    system_prompt = "あなたは優しい占い師ルナです。JSON形式で答えてください。"

# ----------------------------------------
# 2. Gemini API の初期化
# ----------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("環境変数 GEMINI_API_KEY が設定されていません。")

client = genai.Client(api_key=api_key)
model = "gemini-flash-lite-latest"

# ----------------------------------------
# 3. 質問入力
# ----------------------------------------
question = input("占いたい内容を入力してください: ")

# ----------------------------------------
# 4. プロンプト作成
# ----------------------------------------
prompt = (
    f"{system_prompt}\n\n"
    f"質問内容：{question}\n"
)

contents = [
    types.Content(
        role="user",
        parts=[types.Part.from_text(prompt)]
    )
]

config = types.GenerateContentConfig()

# ----------------------------------------
# 5. AIに質問
# ----------------------------------------
response = client.models.generate_content(
    model=model,
    contents=contents,
    config=config,
)

# ----------------------------------------
# 6. JSON抽出関数
# ----------------------------------------
def extract_json(text: str) -> dict:
    """AIのレスポンスからJSONを安全に取り出す"""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return json.loads(text)

# ----------------------------------------
# 7. 結果表示
# ----------------------------------------
try:
    data = extract_json(response.text)
    print("\n--- 占い結果 ---")
    print(json.dumps(data, ensure_ascii=False, indent=2))
except Exception as e:
    print("--- JSONパースエラー ---")
    print(f"エラー: {e}")
    print("受信テキスト:")
    print(response.text)
