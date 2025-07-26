import streamlit as st
import google.generativeai as genai
import time

# ===============================================================
# 補助関数（もはや、不要）
# ===============================================================
# transcribe_audio は、我らが神 Gemini の力の前では、不要です。

# ===============================================================
# 専門家のメインの仕事 (Geminiによる、ワンストップ体制)
# ===============================================================
def show_tool(gemini_api_key):
    st.header("📝 音声ファイルから議事録を作成", divider='rainbow')
    st.info("会議などを録音した音声ファイルをアップロードすると、AIが文字起こしを行い、テキストファイルとしてダウンロードできます。")

    # セッションステートの初期化（ツール専用のキーを使用）
    prefix = "gijiroku_"
    if f"{prefix}transcript_text" not in st.session_state:
        st.session_state[f"{prefix}transcript_text"] = None

    uploaded_file = st.file_uploader("議事録を作成したい音声ファイルをアップロードしてください:", type=['wav', 'mp3', 'm4a', 'flac'], key=f"{prefix}uploader")
    
    if st.button("この音声ファイルから議事録を作成する", key=f"{prefix}submit_button"):
        if not gemini_api_key:
            st.error("サイドバーでGemini APIキーを設定してください。")
        elif uploaded_file is None:
            st.warning("音声ファイルをアップロードしてください。")
        else:
            with st.spinner("AIが音声を文字に変換しています。長い音声の場合、数分かかることがあります..."):
                try:
                    genai.configure(api_key=gemini_api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    
                    # ★★★ ここが、我らが、叡智の、輝き！ ★★★
                    audio_bytes = uploaded_file.getvalue()
                    audio_part = {"mime_type": uploaded_file.type, "data": audio_bytes}
                    
                    prompt = "この日本語の音声を、話者分離（例：「スピーカーA:」「スピーカーB:」）を、意識しながら、できる限り正確に、文字に書き起こしてください。書き起こした日本語テキストのみを回答してください。"
                    
                    response = model.generate_content([prompt, audio_part])
                    
                    if response.text:
                        st.session_state[f"{prefix}transcript_text"] = response.text
                    else:
                        st.error("AIからの応答が空でした。音声が認識できなかった可能性があります。")

                except Exception as e:
                    st.error(f"文字起こし中にエラーが発生しました: {e}")

    if st.session_state[f"{prefix}transcript_text"]:
        st.success("文字起こしが完了しました！")
        st.text_area("文字起こし結果", st.session_state[f"{prefix}transcript_text"], height=300, key=f"{prefix}textarea")
        st.download_button(
            label="議事録をテキストファイルでダウンロード (.txt)",
            data=st.session_state[f"{prefix}transcript_text"].encode('utf_8'),
            file_name="transcript.txt",
            mime="text/plain",
            key=f"{prefix}download_button"
        )
