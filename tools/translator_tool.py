import streamlit as st
import google.generativeai as genai
from google.cloud import speech
from google.api_core.client_options import ClientOptions
from streamlit_mic_recorder import mic_recorder
import time
import json
import base64

# ページ設定
st.set_page_config(
    page_title="フレンドリー翻訳ツール",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #4A90E2;
        margin-bottom: 30px;
    }
    .usage-counter {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 10px 0;
    }
    .result-container {
        background: #f8f9fa;
        border-left: 5px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .input-container {
        background: #f1f3f4;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# 補助関数
def transcribe_audio(audio_bytes, api_key):
    """音声をテキストに変換する関数"""
    if not audio_bytes or not api_key: 
        return None
    
    try:
        # Google Cloud Speech-to-Text クライアント設定
        client_options = ClientOptions(api_key=api_key)
        client = speech.SpeechClient(client_options=client_options)
        
        # 音声データを設定
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="ja-JP",
            model="latest_long",
            enable_automatic_punctuation=True,
        )
        
        # 音声認識実行
        response = client.recognize(config=config, audio=audio)
        
        if response.results and len(response.results) > 0:
            return response.results[0].alternatives[0].transcript
        else:
            return None
            
    except Exception as e: 
        st.error(f"音声認識エラー: {str(e)}")
        return None

def translate_text_with_gemini(text_to_translate, api_key):
    """Gemini AIを使って日本語を英語に翻訳する関数"""
    if not text_to_translate or not api_key: 
        return None
    
    try:
        # Gemini AI設定
        genai.configure(api_key=api_key)
        
        # システムプロンプト
        system_prompt = """あなたは、言語の壁を乗り越える手助けをする、非常に優秀な翻訳アシスタントです。

ユーザーから渡された日本語のテキストを、海外の親しい友人との会話で使われるような、自然で、カジュアルでありながら礼儀正しく、そしてフレンドリーな英語に翻訳してください。

重要な注意事項：
- 非常に硬い表現や、ビジネス文書のような翻訳は避けてください
- 自然で流暢な英語表現を心がけてください
- 文脈に応じて適切な敬語レベルを選択してください
- 翻訳後の英語テキストのみを回答してください
- 他の説明や言葉は一切含めないでください"""

        # Geminiモデル初期化
        model = genai.GenerativeModel(
            'gemini-1.5-flash-latest', 
            system_instruction=system_prompt
        )
        
        # 翻訳実行
        response = model.generate_content(text_to_translate)
        
        if response and response.text:
            return response.text.strip()
        else:
            return None
            
    except Exception as e: 
        st.error(f"翻訳エラー: {str(e)}")
        return None

def initialize_session_state():
    """セッション状態を初期化する関数"""
    if "translator_results" not in st.session_state: 
        st.session_state.translator_results = []
    if "translator_usage_count" not in st.session_state: 
        st.session_state.translator_usage_count = 0
    if "translator_last_input" not in st.session_state:
        st.session_state.translator_last_input = ""
    if "translator_initialized" not in st.session_state:
        st.session_state.translator_initialized = True

def handle_unlock_process():
    """アンロック処理を行う関数"""
    unlocked = st.query_params.get("unlocked")
    if unlocked == "true":
        st.session_state.translator_usage_count = 0
        st.query_params.clear()
        st.success("✅ おかえりなさい！利用回数がリセットされました。")
        st.balloons()
        time.sleep(2)
        st.rerun()

def display_usage_counter(remaining_count, usage_limit):
    """使用回数カウンターを表示する関数"""
    progress = (usage_limit - remaining_count) / usage_limit
    
    st.markdown(f"""
    <div class="usage-counter">
        🚀 残り使用回数: {remaining_count} / {usage_limit}
    </div>
    """, unsafe_allow_html=True)
    
    st.progress(progress)

def display_translation_result(original_text, translated_text):
    """翻訳結果を表示する関数"""
    st.markdown("""
    <div class="result-container">
        <h4>✅ 翻訳完了！</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🇯🇵 あなたの入力:**")
        st.info(original_text)
    
    with col2:
        st.markdown("**🇺🇸 AIの翻訳:**")
        st.success(translated_text)

def display_translation_history():
    """翻訳履歴を表示する関数"""
    if not st.session_state.translator_results:
        return
    
    st.markdown("---")
    st.subheader("📝 翻訳履歴")
    
    for i, result in enumerate(st.session_state.translator_results):
        with st.expander(f"翻訳 #{len(st.session_state.translator_results) - i}: {result['original'][:30]}..."):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🇯🇵 日本語:**")
                st.write(result['original'])
            
            with col2:
                st.markdown("**🇺🇸 英語:**")
                st.write(result['translated'])
            
            st.caption(f"翻訳日時: {result.get('timestamp', '不明')}")

def process_translation(japanese_text, gemini_api_key):
    """翻訳処理を実行する関数"""
    if not gemini_api_key:
        st.error("❌ サイドバーでGemini APIキーを設定してください。")
        return False
    
    if not japanese_text.strip():
        st.warning("⚠️ 翻訳するテキストを入力してください。")
        return False
    
    # 翻訳実行
    with st.spinner("🤖 AIが最適な英語を考えています..."):
        translated_text = translate_text_with_gemini(japanese_text, gemini_api_key)
    
    if translated_text:
        # 使用回数を増やす
        st.session_state.translator_usage_count += 1
        
        # 結果を履歴に追加
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.translator_results.insert(0, {
            "original": japanese_text, 
            "translated": translated_text,
            "timestamp": current_time
        })
        
        # 結果表示
        display_translation_result(japanese_text, translated_text)
        
        return True
    else:
        st.error("❌ 翻訳に失敗しました。もう一度お試しください。")
        return False

def show_limit_reached_screen(usage_limit):
    """制限到達時の画面を表示する関数"""
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h2>🎉 たくさんのご利用、ありがとうございます！</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.info(
        f"""
        このツールが、あなたの世界を広げる一助となれば幸いです。

        下のボタンから応援ページに移動することで、
        **さらに{usage_limit}回**、翻訳を続けることができます。
        """
    )
    
    portal_url = "https://experiment-site.pray-power-is-god-and-cocoro.com/continue.html" 
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.link_button(
            "🌟 応援ページに移動して、翻訳を続ける", 
            portal_url, 
            type="primary",
            use_container_width=True
        )

def main():
    """メイン関数"""
    # セッション状態初期化
    initialize_session_state()
    
    # アンロック処理
    handle_unlock_process()
    
    # サイドバー設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # APIキー設定
        gemini_api_key = st.text_input(
            "Gemini API Key", 
            type="password",
            help="Google AI StudioでGemini APIキーを取得してください"
        )
        
        speech_api_key = st.text_input(
            "Google Cloud Speech API Key", 
            type="password",
            help="Google Cloud Consoleで音声認識APIキーを取得してください"
        )
        
        st.markdown("---")
        
        # デバッグ情報
        if st.checkbox("デバッグ情報を表示"):
            st.write("**セッション状態:**")
            st.json({
                "使用回数": st.session_state.translator_usage_count,
                "履歴数": len(st.session_state.translator_results),
                "最後の入力": st.session_state.translator_last_input[:50] + "..." if len(st.session_state.translator_last_input) > 50 else st.session_state.translator_last_input
            })
            
            if st.button("🔄 使用回数リセット（テスト用）"):
                st.session_state.translator_usage_count = 0
                st.success("リセットしました")
                st.rerun()
    
    # メインヘッダー
    st.markdown('<h1 class="main-header">🤝 フレンドリー翻訳ツール</h1>', unsafe_allow_html=True)
    
    # 制限設定
    usage_limit = 2  # テスト用: 本番では10に変更
    remaining_count = usage_limit - st.session_state.translator_usage_count
    is_limit_reached = remaining_count <= 0
    
    # 制限到達時の表示
    if is_limit_reached:
        show_limit_reached_screen(usage_limit)
        display_translation_history()
        return
    
    # 使用回数表示
    display_usage_counter(remaining_count, usage_limit)
    
    # 説明
    st.info("🎯 マイクで日本語を話すか、テキストボックスに入力してください。自然でフレンドリーな英語に翻訳します。")
    
    # 入力方法選択
    input_method = st.radio(
        "📝 入力方法を選択:",
        ["💬 テキスト入力", "🎤 音声入力"],
        horizontal=True,
        help="お好みの方法で日本語を入力してください"
    )
    
    # 入力処理
    if input_method == "💬 テキスト入力":
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        
        # テキスト入力
        japanese_text = st.text_area(
            "日本語を入力してください:",
            height=100,
            placeholder="例: こんにちは、元気ですか？",
            help="翻訳したい日本語のテキストを入力してください"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            translate_button = st.button(
                "🔄 翻訳実行", 
                type="primary",
                use_container_width=True,
                disabled=not japanese_text.strip()
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 翻訳実行
        if translate_button and japanese_text:
            if process_translation(japanese_text, gemini_api_key):
                time.sleep(2)
                st.rerun()
    
    else:  # 音声入力
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        st.markdown("🎙️ **音声で日本語を話してください**")
        
        if not speech_api_key:
            st.warning("⚠️ 音声入力を使用するには、サイドバーでGoogle Cloud Speech APIキーを設定してください。")
        else:
            # マイクレコーダー
            mic_key = f"mic_{st.session_state.translator_usage_count}_{int(time.time() % 10000)}"
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                audio_data = mic_recorder(
                    start_prompt="🎤 録音開始", 
                    stop_prompt="⏹️ 録音停止",
                    key=mic_key,
                    format="webm"
                )
            
            if audio_data and audio_data.get('bytes'):
                st.success("🎧 音声を受信しました。処理中...")
                
                # 音声をテキストに変換
                with st.spinner("🎯 音声を日本語に変換中..."):
                    japanese_text = transcribe_audio(audio_data['bytes'], speech_api_key)
                
                if japanese_text:
                    st.success(f"✅ 認識結果: **{japanese_text}**")
                    
                    # 翻訳実行
                    if process_translation(japanese_text, gemini_api_key):
                        time.sleep(3)
                        st.rerun()
                else:
                    st.error("❌ 音声を認識できませんでした。もう一度お試しください。")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 翻訳履歴表示
    display_translation_history()
    
    # 履歴管理ボタン
    if st.session_state.translator_results:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ 履歴をクリア"):
                st.session_state.translator_results = []
                st.success("✅ 履歴をクリアしました")
                time.sleep(1)
                st.rerun()
        
        with col2:
            # 履歴をJSONでダウンロード
            history_json = json.dumps(
                st.session_state.translator_results, 
                ensure_ascii=False, 
                indent=2
            )
            st.download_button(
                "📥 履歴をダウンロード",
                data=history_json,
                file_name=f"translation_history_{time.strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# メイン実行
if __name__ == "__main__":
    main()
