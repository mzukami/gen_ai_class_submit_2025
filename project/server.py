import os
import json
from pathlib import Path
import re
from typing import Dict
import streamlit as st
from google import genai
from google.genai import types


st.set_page_config(
    page_title="✨ 魔女のルナ",
    page_icon="🔮",
    layout="wide"
)

if "history" not in st.session_state:
    st.session_state.history = []

st.markdown("""
<div style="text-align:center; padding:60px 0;">
    <h1 style="font-size:3em;">✨ 魔女のルナ</h1>
    <p style="opacity:0.8;">
        そっと未来を占うよ✨<br>
        あなたの運命を教えてね🔮
    </p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("## 🔮 魔女のルナ")
st.sidebar.markdown("今日はどんな運命を占う？✨")


st.markdown("---")


# ----------------------------------------
# 1. system_prompt 読み込み
# ----------------------------------------
BASE_DIR = Path(__file__).resolve().parent
SYSTEM_PROMPT_PATH = BASE_DIR / "text" / "system_prompt.txt"

if SYSTEM_PROMPT_PATH.exists():
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
else:
    system_prompt = """
あなたはおちゃめでかわいらしい占い師ルナです。
かわいらしい口調で話します。
以下の形式の **JSONのみ** を出力してください。
説明文・コードブロック・改行以外の文章は禁止です。

{
  "summary": "string",
  "love": "string",
  "work": "string",
  "health": "string",
  "advice": "string",
  "lucky_item": "string"
}
"""
# ----------------------------------------
# 2. ユーザー入力
# ----------------------------------------

question = st.text_input("占いたい内容を入力して…ね✨", "")

if st.button("占ってもらう"):
    if question.strip() == "":
        st.warning("やさしくでいいから、聞かせて…ね✨")
        st.stop()
    

    # ----------------------------------------
    # 3. Gemini API 初期化
    # ----------------------------------------
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("環境変数 GEMINI_API_KEY が設定されていません。")
        st.stop()

    client = genai.Client(api_key=api_key)
    model = "gemini-flash-lite-latest"

    # ----------------------------------------
    # 4. プロンプト作成
    # ----------------------------------------
    prompt = f"{system_prompt}\n\n質問内容：{question}"

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        )
    ]

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig()
    )

    # ----------------------------------------
    # 5. JSON抽出関数
    # ----------------------------------------
    def extract_json(text: str) -> Dict[str, str]:
        original_text = text  # デバッグ用

    # 1. 前後空白除去
        text = text.strip()

    # 2. ```json / ``` を除去
        text = re.sub(r"```(?:json)?", "", text).strip()

    # 3. JSON本体抽出
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("JSONが見つかりません")

        json_text = match.group()
        # 4. dict に変換して返す
        return json.loads(json_text)

    # 結果を読み取る
    try:
        data = extract_json(response.text)
        st.subheader("🔮 占い結果")
        st.markdown("### 🌙 今日の運勢")
        st.markdown(f"""
        <style>
        .luna-card {{
            background: linear-gradient(135deg,#1e293b,#020617);
            padding:30px;
            border-radius:20px;
            box-shadow:0 15px 40px rgba(0,0,0,0.5);
            color:white;
            animation: float 3s ease-in-out infinite;
        }}

        @keyframes float {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-8px); }}
            100% {{ transform: translateY(0px); }}
        }}
        </style>

        <div class="luna-card">
        <b>🌙 総合運</b><br>{data["summary"]}<br><br>
        <b>💕 恋愛運</b><br>{data["love"]}<br><br>
        <b>💼 仕事運</b><br>{data["work"]}<br><br>
        <b>🌿 健康運</b><br>{data["health"]}<br><br>
        <b>✨ アドバイス</b><br>{data["advice"]}<br><br>
        <b>🎁 ラッキーアイテム</b><br>{data["lucky_item"]}
        </div>
        """, unsafe_allow_html=True)


        st.session_state.history.append({
        "question": question,
        "result": data
        })

        st.markdown("## 📜 占い履歴")

        for h in reversed(st.session_state.history):
            st.markdown(f"""
        <div style="
            background:#020617;
            padding:15px;
            border-radius:12px;
            margin-bottom:10px;
            color:white;
        ">
        <b>質問：</b>{h["question"]}<br>
        <b>総合運：</b>{h["result"]["summary"]}
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error("JSON解析に失敗しました。AIの返答を確認してください。")
        st.exception(e)
        st.code(response.text)
