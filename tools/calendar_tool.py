import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime
import urllib.parse
import pytz
from streamlit_mic_recorder import mic_recorder

# ===============================================================
# 補助関数（シンプル化）
# ===============================================================
def create_google_calendar_url(details):
    try:
        jst = pytz.timezone('Asia/Tokyo')
        start_time_jst = jst.localize(datetime.fromisoformat(details['start_time']))
        end_time_jst = jst.localize(datetime.fromisoformat(details['end_time']))
        start_time_utc = start_time_jst.astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')
        end_time_utc = end_time_jst.astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')
        dates = f"{start_time_utc}/{end_time_utc}"
    except (ValueError, KeyError):
        dates = ""
    base_url = "https://www.google.com/calendar/render?action=TEMPLATE"
    params = {
        "text": details.get('title', ''),
        "dates": dates,
        "location": details.get('location', ''),
        "details": details.get('details', '')
    }
    return f"{base_url}&{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"

# ===============================================================
# 専門家のメインの仕事（Geminiによる、完全、ワンストップ体制）
# ===============================================================
def show_tool(gemini_api_key):
    st.header("📅 あなただけのAI秘書", divider='rainbow')

    # --- 状態管理の初期化 ---
    if "cal_messages" not in st.session_state:
        st.session_state.cal_messages = [{"role": "assistant", "content": "こんにちは！ご予定を、下の方法でお伝えください。"}]
    if "cal_last_mic_id" not in st.session_state: st.session_state.cal_last_mic_id = None
    if "cal_last_file_name" not in st.session_state: st.session_state.cal_last_file_name = None

    # --- 音声処理とAI処理を、一つに、統合 ---
    def process_input(user_input):
        with st.chat_message("assistant"):
            if not gemini_api_key:
                st.error("サイドバーでGemini APIキーを設定してください。")
                return

            try:
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')

                # --- ★★★ ここが、我らが、叡智『二段階認証プロセス』の、輝きです ★★★ ---
                with st.spinner("（あなたの、言葉を、解読しています...）"):
                    if isinstance(user_input, bytes):
                        audio_part = {"mime_type": "audio/webm", "data": user_input}
                        transcription_prompt = "この日本語の音声を、できる限り正確に、文字に書き起こしてください。書き起こした日本語テキストのみを回答してください。"
                        transcription_response = model.generate_content([transcription_prompt, audio_part])
                        prompt_text = transcription_response.text.strip()
                        if not prompt_text:
                            st.warning("音声を認識できませんでした。もう一度お試しください。")
                            return
                    else:
                        prompt_text = user_input
                
                st.session_state.cal_messages.append({"role": "user", "content": prompt_text})
                
                with st.spinner("AIが予定を組み立てています..."):
                    jst = pytz.timezone('Asia/Tokyo')
                    current_time_jst = datetime.now(jst).isoformat()
                    system_prompt = f"""
                    あなたは予定を解釈する優秀なアシスタントです。ユーザーのテキストから「title」「start_time」「end_time」「location」「details」を抽出してください。
                    - 現在の日時は `{current_time_jst}` (JST)です。これを基準に日時を解釈してください。
                    - 日時は `YYYY-MM-DDTHH:MM:SS` 形式で出力してください。
                    - `end_time` が不明な場合は、`start_time` の1時間後を自動設定してください。
                    - 必ず以下のJSON形式のみで回答してください。他の言葉は一切含めないでください。
                    ```json
                    {{ "title": "（件名）", "start_time": "YYYY-MM-DDTHH:MM:SS", "end_time": "YYYY-MM-DDTHH:MM:SS", "location": "（場所）", "details": "（詳細）" }}
                    ```
                    """
                    schedule_model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=system_prompt)
                    response = schedule_model.generate_content(prompt_text)
                    json_text = response.text.strip().lstrip("```json").rstrip("```").strip()
                    schedule_details = json.loads(json_text)
                    calendar_url = create_google_calendar_url(schedule_details)
                    display_start_time = "未設定"
                    if schedule_details.get('start_time'):
                        try: display_start_time = datetime.fromisoformat(schedule_details['start_time']).strftime('%Y年%m月%d日 %H:%M')
                        except: display_start_time = "AIが日付の解析に失敗"
                    ai_response = f"""以下の内容で承りました。よろしければリンクをクリックしてカレンダーに登録してください。\n\n- **件名:** {schedule_details.get('title', '未設定')}\n- **日時:** {display_start_time}\n- **場所:** {schedule_details.get('location', '未設定')}\n- **詳細:** {schedule_details.get('details', '未設定')}\n\n[📅 Googleカレンダーにこの予定を追加する]({calendar_url})"""
                    st.session_state.cal_messages.append({"role": "assistant", "content": ai_response})

            except Exception as e:
                error_message = f"AIとの通信中にエラーが発生しました: {e}"
                st.session_state.cal_messages.append({"role": "assistant", "content": f"申し訳ありません、エラーが発生しました。({e})"})

    # --- UIウィジェットの表示 ---
    for message in st.session_state.cal_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        audio_info = mic_recorder(start_prompt="🎤 マイクで録音", stop_prompt="⏹️ 停止", key='cal_mic_recorder')
    with col2:
        uploaded_file = st.file_uploader("📁 音声ファイルをアップロード", type=['wav', 'mp3', 'm4a', 'flac'], key="cal_uploader")
    text_prompt = st.chat_input("キーボードで予定を入力...", key="cal_text_input")

    # --- 入力があった場合の、一度きりの、処理 ---
    user_input_data = None
    if text_prompt:
        user_input_data = text_prompt
    elif audio_info and audio_info['id'] != st.session_state.cal_last_mic_id:
        st.session_state.cal_last_mic_id = audio_info['id']
        user_input_data = audio_info['bytes']
    elif uploaded_file and uploaded_file.name != st.session_state.cal_last_file_name:
        st.session_state.cal_last_file_name = uploaded_file.name
        user_input_data = uploaded_file.getvalue()

    if user_input_data:
        process_input(user_input_data)
        st.rerun()
