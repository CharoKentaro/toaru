import streamlit as st
import google.generativeai as genai
from google.cloud import speech
from google.api_core.client_options import ClientOptions
from streamlit_mic_recorder import mic_recorder
import time

# 補助関数（変更なし）
def transcribe_audio(audio_bytes, api_key):
    if not audio_bytes or not api_key: 
        return None
    try:
        client_options = ClientOptions(api_key=api_key)
        client = speech.SpeechClient(client_options=client_options)
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(language_code="ja-JP")
        response = client.recognize(config=config, audio=audio)
        if response.results: 
            return response.results[0].alternatives[0].transcript
    except Exception as e: 
        st.error(f"音声認識エラー: {e}")
    return None

def translate_text_with_gemini(text_to_translate, api_key):
    if not text_to_translate or not api_key: 
        return None
    try:
        genai.configure(api_key=api_key)
        system_prompt = "あなたは、言語の壁を乗り越える手助けをする、非常に優秀な翻訳アシスタントです。ユーザーから渡された日本語のテキストを、海外の親しい友人との会話で使われるような、自然で、カジュアルでありながら礼儀正しく、そしてフレンドリーな英語に翻訳してください。- 非常に硬い表現や、ビジネス文書のような翻訳は避けてください。- 翻訳後の英語テキストのみを回答してください。他の言葉は一切含めないでください。"
        model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=system_prompt)
        response = model.generate_content(text_to_translate)
        return response.text.strip()
    except Exception as e: 
        st.error(f"翻訳エラー: {e}")
    return None

def show_tool(gemini_api_key, speech_api_key):
    # session_stateの初期化
    if "translator_results" not in st.session_state: 
        st.session_state.translator_results = []
    if "translator_last_mic_id" not in st.session_state: 
        st.session_state.translator_last_mic_id = None
    if "translator_last_text" not in st.session_state: 
        st.session_state.translator_last_text = ""
    if "translator_usage_count" not in st.session_state: 
        st.session_state.translator_usage_count = 0
    if "translator_processing" not in st.session_state:
        st.session_state.translator_processing = False

    # アンロック処理（ページ読み込み時のみ実行）
    if st.query_params.get("unlocked") == "true" and not st.session_state.get("translator_unlocked_processed", False):
        st.session_state.translator_usage_count = 0
        st.session_state.translator_unlocked_processed = True
        st.query_params.clear()
        st.toast("おかえりなさい！利用回数がリセットされました。")
        st.balloons()
        # rerunを使わずに状態をクリア
        st.session_state.translator_last_text = ""
        st.session_state.translator_last_mic_id = None

    st.header("🤝 フレンドリー翻訳ツール", divider='rainbow')

    # 制限回数の設定
    usage_limit = 2  # テスト用に2回に設定
    is_limit_reached = st.session_state.translator_usage_count >= usage_limit

    # 制限時の表示
    if is_limit_reached:
        st.success("🎉 たくさんのご利用、ありがとうございます！")
        st.info(
            "このツールが、あなたの世界を広げる一助となれば幸いです。\n\n"
            "下のボタンから応援ページに移動することで、"
            f"**さらに{usage_limit}回**、翻訳を続けることができます。"
        )
        portal_url = "https://experiment-site.pray-power-is-god-and-cocoro.com/continue.html" 
        st.link_button("応援ページに移動して、翻訳を続ける", portal_url, type="primary")
        return  # ここで関数を終了して、以下の処理を実行しない

    # 通常時の表示
    st.info("マイクで日本語を話すか、テキストボックスに入力してください。自然な英語に翻訳します。")
    remaining_count = usage_limit - st.session_state.translator_usage_count
    st.caption(f"🚀 あと {remaining_count} 回、翻訳できます")
    
    # 入力エリア
    col1, col2 = st.columns([1, 2])
    with col1:
        audio_info = mic_recorder(
            start_prompt="🎤 話し始める", 
            stop_prompt="⏹️ 翻訳する", 
            key='translator_mic'
        )
    with col2:
        text_prompt = st.text_input(
            "または、ここに日本語を入力してEnterキーを押してください...", 
            key="translator_text",
            disabled=st.session_state.translator_processing
        )

    # 翻訳処理中の表示
    if st.session_state.translator_processing:
        st.info("🔄 翻訳処理中です。しばらくお待ちください...")

    # 入力検知と翻訳処理
    japanese_text_to_process = None
    
    # 音声入力の検知
    if (audio_info and 
        audio_info.get('id') and
        audio_info['id'] != st.session_state.translator_last_mic_id and
        not st.session_state.translator_processing):
        
        st.session_state.translator_processing = True
        with st.spinner("音声を日本語に変換中..."):
            text_from_mic = transcribe_audio(audio_info['bytes'], speech_api_key)
        
        if text_from_mic:
            japanese_text_to_process = text_from_mic
            st.session_state.translator_last_mic_id = audio_info['id']
            st.session_state.translator_last_text = text_from_mic
    
    # テキスト入力の検知
    elif (text_prompt and 
          text_prompt != st.session_state.translator_last_text and
          not st.session_state.translator_processing):
        
        japanese_text_to_process = text_prompt
        st.session_state.translator_last_text = text_prompt

    # 翻訳実行
    if japanese_text_to_process and not st.session_state.translator_processing:
        if not gemini_api_key:
            st.error("サイドバーでGemini APIキーを設定してください。")
        else:
            st.session_state.translator_processing = True
            
            with st.spinner("AIが最適な英語を考えています..."):
                translated_text = translate_text_with_gemini(japanese_text_to_process, gemini_api_key)
            
            if translated_text:
                # 使用回数を増やす
                st.session_state.translator_usage_count += 2
                
                # 結果を追加
                st.session_state.translator_results.insert(0, {
                    "original": japanese_text_to_process, 
                    "translated": translated_text
                })
                
                # 成功メッセージを表示
                st.success("✅ 翻訳が完了しました！")
                
            else:
                st.warning("翻訳に失敗しました。もう一度お試しください。")
                st.session_state.translator_last_text = ""
            
            # 処理フラグをリセット
            st.session_state.translator_processing = False

    # 結果表示エリア
    if st.session_state.translator_results:
        st.write("---")
        st.subheader("📝 翻訳履歴")
        
        for i, result in enumerate(st.session_state.translator_results):
            with st.container(border=True):
                st.caption(f"翻訳履歴 No.{len(st.session_state.translator_results) - i}")
                st.markdown(f"**🇯🇵 あなたの入力:**\n> {result['original']}")
                st.markdown(f"**🇺🇸 AIの翻訳:**\n> {result['translated']}")
        
        # 履歴クリアボタン
        if st.button("翻訳履歴をクリア", key="clear_translator_history"):
            st.session_state.translator_results = []
            st.session_state.translator_last_text = ""
            st.session_state.translator_last_mic_id = None
            st.session_state.translator_processing = False
            # 使用回数はリセットしない（意図的な仕様として）
            st.success("翻訳履歴をクリアしました。")
            time.sleep(1)
            st.rerun()
