import streamlit as st
from tools import translator_tool

# 1. アプリの基本設定
st.set_page_config(page_title="フレンドリー翻訳ツール", page_icon="🤝", layout="wide")

# 2. UI描画 + ツール起動ロジック
with st.sidebar:
    st.title("🤝 フレンドリー翻訳")
    st.info("このツールは、あなたの言葉を、海外の親しい友人との会話で使われるような、自然でフレンドリーな英語に翻訳します。")
    st.divider()
    if 'gemini_api_key' not in st.session_state: st.session_state.gemini_api_key = ""
    if 'speech_api_key' not in st.session_state: st.session_state.speech_api_key = ""
    with st.expander("⚙️ APIキーの設定", expanded=not(st.session_state.gemini_api_key)):
        st.session_state.gemini_api_key = st.text_input("Gemini APIキー", type="password", value=st.session_state.gemini_api_key, help="翻訳機能に必要です。")
        st.session_state.speech_api_key = st.text_input("Speech-to-Text APIキー", type="password", value=st.session_state.speech_api_key, help="音声入力機能には現在対応していません。")
    st.markdown("""<div style="font-size: 0.9em; text-align: center;"><a href="https://aistudio.google.com/app/apikey" target="_blank">Gemini APIキーの取得はこちら</a><br><a href="https://console.cloud.google.com/apis/credentials" target="_blank">Speech-to-Text APIキーの取得はこちら</a></div>""", unsafe_allow_html=True)

# --- メインコンテンツ ---
st.title("AIアシスタント・ポータル")
translator_tool.show_tool(
    gemini_api_key=st.session_state.get('gemini_api_key', ''),
    speech_api_key=st.session_state.get('speech_api_key', '')
)```

#### **3. `tools/__init__.py`**
これは空のファイルのままです。

#### **4. `tools/translator_tool.py`**
これが今回の修正の核心です。API通信のプロセスを詳細に表示するように`translate_text_with_gemini`関数と`show_tool`関数内の呼び出し部分を修正します。

```python
import streamlit as st
import google.generativeai as genai
from google.cloud import speech
from google.api_core.client_options import ClientOptions
import time
import traceback

# 補助関数 (translate_text_with_geminiを修正)
def transcribe_audio(audio_bytes, api_key):
    if not audio_bytes or not api_key: return None, "音声データまたはAPIキーがありません。"
    try:
        client_options = ClientOptions(api_key=api_key)
        client = speech.SpeechClient(client_options=client_options)
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(language_code="ja-JP")
        response = client.recognize(config=config, audio=audio)
        if response.results:
            return response.results[0].alternatives[0].transcript, None
        return None, "音声認識結果が空です。"
    except Exception as e:
        return None, f"音声認識中にエラーが発生しました: {e}\n{traceback.format_exc()}"

def translate_text_with_gemini(text_to_translate, api_key):
    if not text_to_translate or not api_key:
        return None, "翻訳するテキストまたはAPIキーがありません。"
    
    try:
        st.write("1. Gemini APIキーを設定しています...")
        genai.configure(api_key=api_key)
        
        st.write("2. 翻訳モデル（gemini-1.5-flash-latest）を準備しています...")
        model = genai.GenerativeModel(
            'gemini-1.5-flash-latest',
            system_instruction="あなたは、言語の壁を乗り越える手助けをする、非常に優秀な翻訳アシスタントです。ユーザーから渡された日本語のテキストを、海外の親しい友人との会話で使われるような、自然で、カジュアルでありながら礼儀正しく、そしてフレンドリーな英語に翻訳してください。- 非常に硬い表現や、ビジネス文書のような翻訳は避けてください。- 翻訳後の英語テキストのみを回答してください。他の言葉は一切含めないでください。"
        )
        
        st.write("3. AIに翻訳を依頼しています...（この処理には時間がかかる場合があります）")
        response = model.generate_content(text_to_translate)
        
        st.write("4. AIから翻訳結果を受け取りました。")
        return response.text.strip(), None
    except Exception as e:
        error_details = traceback.format_exc()
        st.write("エラーが発生しました。")
        return None, f"翻訳中にエラーが発生しました: {e}\n\n**詳細:**\n```\n{error_details}\n```"

# ===============================================================
# 専門家のメインの仕事 (最終安定バージョン)
# ===============================================================
def show_tool(gemini_api_key, speech_api_key):

    if st.query_params.get("unlocked") == "true":
        st.session_state.translator_usage_count = 0
        st.query_params.clear()
        st.toast("おかえりなさい！利用回数がリセットされました。")
        st.balloons()
        time.sleep(1)
        st.rerun()

    st.header("🤝 フレンドリー翻訳ツール", divider='rainbow')

    if "translator_results" not in st.session_state: st.session_state.translator_results = []
    if "translator_last_text" not in st.session_state: st.session_state.translator_last_text = ""
    if "translator_usage_count" not in st.session_state: st.session_state.translator_usage_count = 0

    usage_limit = 2
    is_limit_reached = st.session_state.translator_usage_count >= usage_limit

    if is_limit_reached:
        st.success("🎉 たくさんのご利用、ありがとうございます！")
        st.info(
            "このツールが、あなたの世界を広げる一助となれば幸いです。\n\n"
            "下のボタンから応援ページに移動することで、"
            f"**さらに{usage_limit}回**、翻訳を続けることができます。"
        )
        portal_url = "https://experiment-site.pray-power-is-god-and-cocoro.com/continue.html" 
        st.link_button("応援ページに移動して、翻訳を続ける", portal_url, type="primary")
        
    else:
        st.info("テキストボックスに日本語を入力して、Enterキーを押してください。")
        st.caption(f"🚀 あと {usage_limit - st.session_state.translator_usage_count} 回、翻訳できます")
        
        text_prompt = st.text_input("ここに日本語を入力してください...", key="translator_text")

        if st.session_state.translator_results:
            st.write("---")
            for i, result in enumerate(st.session_state.translator_results):
                with st.container(border=True):
                    st.caption(f"翻訳履歴 No.{len(st.session_state.translator_results) - i}")
                    st.markdown(f"**🇯🇵 あなたの入力:**\n> {result['original']}")
                    st.markdown(f"**🇺🇸 AIの翻訳:**\n> {result['translated']}")
            if st.button("翻訳履歴をクリア", key="clear_translator_history"):
                st.session_state.translator_results = []
                st.session_state.translator_last_text = ""
                st.session_state.translator_usage_count = 0 
                st.rerun()

        japanese_text_to_process = None
        if text_prompt and text_prompt != st.session_state.translator_last_text:
            japanese_text_to_process = text_prompt
            st.session_state.translator_last_text = text_prompt

        if japanese_text_to_process:
            if not gemini_api_key:
                st.error("サイドバーでGemini APIキーを設定してください。")
            else:
                with st.status("AIとの通信を開始します...", expanded=True) as status:
                    translated_text, error_message = translate_text_with_gemini(japanese_text_to_process, gemini_api_key)
                    
                    if error_message:
                        status.update(label="翻訳エラー", state="error", expanded=True)
                        st.error(error_message)
                        st.session_state.translator_last_text = ""
                    else:
                        status.update(label="翻訳完了！", state="complete", expanded=False)
                        st.session_state.translator_usage_count += 1
                        st.session_state.translator_results.insert(0, {"original": japanese_text_to_process, "translated": translated_text})
                        time.sleep(0.5)
                        st.rerun()
