import os
import json
from pathlib import Path
import streamlit as st
from google import genai
from google.genai import types

# ----------------------------------------
# 1. system_prompt 読み込み
# ----------------------------------------
BASE_DIR = Path(__file__).resolve().parent
SYSTEM_PROMPT_PATH = BASE_DIR / "text" / "system_prompt.txt"

if SYSTEM_PROMPT_PATH.exists():
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
else:
    system_prompt = "あなたは優しい占い師ルナです。JSON形式で答えてください。"

# ----------------------------------------
# 2. Streamlit UI
# ----------------------------------------
st.set_page_config(page_title="AI占い（JSON）", page_icon="🔮")
st.title("🔮 AI占い（JSON形式）")
st.write("占いたい内容を入力すると、AIがJSON形式で占い結果を返します。")

question = st.text_input("占いたい内容", placeholder="例：今日の恋愛運を教えて")

if st.button("占う"):
    if not question:
        st.warning("内容を入力してください")
        st.stop()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("環境変数 GEMINI_API_KEY が設定されていません")
        st.stop()

    client = genai.Client(api_key=api_key)
    model = "gemini-flash-lite-latest"

    # プロンプト作成
    prompt = f"{system_prompt}\n\n質問内容：{question}\n"

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(prompt)]
        )
    ]

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(),
    )

    # JSON抽出関数
    def extract_json(text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        return json.loads(text)

    # 結果表示
    try:
        data = extract_json(response.text)
        st.success("占い結果")
        st.markdown(f"**運勢:** {data.get('summary','')}")
        st.markdown(f"**アドバイス:** {data.get('advice','')}")
        st.markdown(f"**ラッキーアイテム:** {data.get('lucky_item','')}")
    except Exception as e:
        st.error("JSONパースに失敗しました")
        st.code(response.text)
