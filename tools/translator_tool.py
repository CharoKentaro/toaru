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
    # session_stateの初期化（最小限に）
    if "translator_results" not in st.session_state: 
        st.session_state.translator_results = []
    if "translator_usage_count" not in st.session_state: 
        st.session_state.translator_usage_count = 0

    # アンロック処理（シンプル化）
    unlocked = st.query_params.get("unlocked")
    if unlocked == "true":
        st.session_state.translator_usage_count = 0
        st.query_params.clear()
        st.success("✅ おかえりなさい！利用回数がリセットされました。")
        st.balloons()

    st.header("🤝 フレンドリー翻訳ツール", divider='rainbow')

    # 制限回数の設定
    usage_limit = 2  # テスト用に2回
    remaining_count = usage_limit - st.session_state.translator_usage_count
    is_limit_reached = remaining_count <= 0

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
        
        # 制限時でも履歴は表示
        if st.session_state.translator_results:
            st.write("---")
            st.subheader("📝 翻訳履歴")
            for i, result in enumerate(st.session_state.translator_results):
                with st.container(border=True):
                    st.caption(f"翻訳履歴 No.{len(st.session_state.translator_results) - i}")
                    st.markdown(f"**🇯🇵 あなたの入力:**\n> {result['original']}")
                    st.markdown(f"**🇺🇸 AIの翻訳:**\n> {result['translated']}")
        return

    # 通常時の表示
    st.info("マイクで日本語を話すか、テキストボックスに入力してください。自然な英語に翻訳します。")
    st.caption(f"🚀 あと {remaining_count} 回、翻訳できます")
    
    # 入力方法選択
    input_method = st.radio(
        "入力方法を選択してください：",
        ["テキスト入力", "音声入力"],
        horizontal=True,
        key="input_method"
    )
    
    japanese_text = None
    
    if input_method == "テキスト入力":
        # テキスト入力
        japanese_text = st.text_input(
            "日本語を入力してください：",
            key="text_input"
        )
        
        if japanese_text:
            translate_button = st.button("🔄 翻訳する", type="primary")
            if translate_button:
                if not gemini_api_key:
                    st.error("❌ サイドバーでGemini APIキーを設定してください。")
                else:
                    with st.spinner("AIが最適な英語を考えています..."):
                        translated_text = translate_text_with_gemini(japanese_text, gemini_api_key)
                    
                    if translated_text:
                        # 使用回数を増やす
                        st.session_state.translator_usage_count += 1
                        
                        # 結果を追加
                        st.session_state.translator_results.insert(0, {
                            "original": japanese_text, 
                            "translated": translated_text
                        })
                        
                        # 結果表示
                        st.success("✅ 翻訳が完了しました！")
                        with st.container(border=True):
                            st.markdown(f"**🇯🇵 あなたの入力:**\n> {japanese_text}")
                            st.markdown(f"**🇺🇸 AIの翻訳:**\n> {translated_text}")
                        
                        # 入力をクリア（次の翻訳のため）
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ 翻訳に失敗しました。もう一度お試しください。")
    
    else:  # 音声入力
        st.info("📢 下のボタンを押して音声で日本語を話してください")
        
        # マイクレコーダー（キーを動的に変更してDOM衝突を回避）
        mic_key = f"mic_{st.session_state.translator_usage_count}_{int(time.time() % 1000)}"
        audio_data = mic_recorder(
            start_prompt="🎤 録音開始", 
            stop_prompt="⏹️ 録音停止",
            key=mic_key
        )
        
        if audio_data and audio_data.get('bytes'):
            with st.spinner("🎧 音声を日本語に変換中..."):
                japanese_text = transcribe_audio(audio_data['bytes'], speech_api_key)
            
            if japanese_text:
                st.success(f"🎯 認識結果: {japanese_text}")
                
                if not gemini_api_key:
                    st.error("❌ サイドバーでGemini APIキーを設定してください。")
                else:
                    with st.spinner("AIが最適な英語を考えています..."):
                        translated_text = translate_text_with_gemini(japanese_text, gemini_api_key)
                    
                    if translated_text:
                        # 使用回数を増やす
                        st.session_state.translator_usage_count += 2
                        
                        # 結果を追加
                        st.session_state.translator_results.insert(0, {
                            "original": japanese_text, 
                            "translated": translated_text
                        })
                        
                        # 結果表示
                        st.success("✅ 翻訳が完了しました！")
                        with st.container(border=True):
                            st.markdown(f"**🇯🇵 あなたの入力:**\n> {japanese_text}")
                            st.markdown(f"**🇺🇸 AIの翻訳:**\n> {translated_text}")
                        
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ 翻訳に失敗しました。もう一度お試しください。")
            else:
                st.warning("⚠️ 音声を認識できませんでした。もう一度お試しください。")

    # 翻訳履歴表示
    if st.session_state.translator_results:
        st.write("---")
        st.subheader("📝 翻訳履歴")
        
        for i, result in enumerate(st.session_state.translator_results):
            with st.container(border=True):
                st.caption(f"翻訳履歴 No.{len(st.session_state.translator_results) - i}")
                st.markdown(f"**🇯🇵 あなたの入力:**\n> {result['original']}")
                st.markdown(f"**🇺🇸 AIの翻訳:**\n> {result['translated']}")
        
        # 履歴クリアボタン
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🗑️ 翻訳履歴をクリア", key="clear_history"):
                st.session_state.translator_results = []
                st.success("✅ 翻訳履歴をクリアしました。")
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("🔄 使用回数をリセット（デバッグ用）", key="reset_count"):
                st.session_state.translator_usage_count = 0
                st.success("✅ 使用回数をリセットしました。")
                time.sleep(1)
                st.rerun()
