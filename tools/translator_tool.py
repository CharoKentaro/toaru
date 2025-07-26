import streamlit as st
import google.generativeai as genai
import time
from google.api_core import exceptions
import json 
from streamlit_mic_recorder import mic_recorder # ★★★ 痛恨の極み。追放してしまっていた、音声の専門家を、再度、招聘いたします。 ★★★

# ===============================================================
# 補助関数 (成功確率99%の『JSON構造化契約』対応バージョン)
# ===============================================================
def translate_with_gemini(content_to_process, api_key):
    # --- 関数呼び出しの、入り口での、基本的な、門番チェック (変更なし) ---
    if not content_to_process or not api_key:
        return None, None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # ★★★ ここが、我々の、新たなる、魂の、契約書です ★★★
        system_prompt = """
        # 命令書: 実践的シーン別・言語コンサルタントとしての、あなたの、絶対的、責務

        あなたは、単なる、翻訳機では、断じて、ない。
        あなたは、ユーザーの、言葉の、裏にある、意図を、深く、読み取り、それが、どのような「場面（シチュエーション）」で使われるかを、鋭く、洞察する、プロフェッショナルな、実践的、言語コンサルタントである。

        ## あなたの、唯一無二の、任務：
        ユーザーから渡された日本語の言葉（単語、または、文章）を、深く、解釈せよ。
        そして、その言葉が、実際に、使われるであろう、最も、典型的で、かつ、重要な、3つの、ビジネスシーンを、想定せよ。
        最後に、それぞれの、シーンに、最も、適した、英語表現と、その、具体的な、使用例を、以下の、JSON形式に、寸分違わず、落とし込んで、提出すること。

        ## JSON出力に関する、絶対的な、契約条件：
        あなたの回答は、必ず、以下のJSON構造に、厳密に、従うこと。
        このJSONオブジェクト以外の、いかなるテキスト（挨拶、前置き、後書き、Markdownの`json`タグなど）も、絶対に、絶対に、含めてはならない。

        ```json
        {
          "proposals": [
            {
              "situation": "ここに、想定される1つ目の具体的なビジネスシーンを記述します。（例：親しい同僚への、カジュアルな朝の挨拶）",
              "phrase": "ここに、そのシーンに最適な、中心となる英語表現（フレーズ）を記述します。",
              "example_sentence": "ここに、上記のフレーズを使った、そのまま使える、具体的な英語の例文を記述します。",
              "explanation": "なぜ、このフレーズが、このシーンに、最適なのか。その文化的背景や、相手に与える印象を、簡潔に、しかし、深く、解説します。"
            },
            {
              "situation": "ここに、想定される2つ目の、異なるビジネスシーンを記述します。（例：顧客や上司への、フォーマルなメールの書き出し）",
              "phrase": "ここに、そのシーンに最適な、中心となる英語表現（フレーズ）を記述します。",
              "example_sentence": "ここに、上記のフレーズを使った、そのまま使える、具体的な英語の例文を記述します。",
              "explanation": "1つ目の候補との、明確な違いや、この表現を選ぶことの、戦略的な、メリットを、解説します。"
            },
            {
              "situation": "ここに、想定される3つ目の、さらに異なるビジネスシーンを記述します。（例：会議やプレゼンテーションの、冒頭での、大勢への挨拶）",
              "phrase": "ここに、そのシーンに最適な、中心となる英語表現（フレーズ）を記述します。",
              "example_sentence": "ここに、上記のフレーズを使った、そのまま使える、具体的な英語の例文を記述します。",
              "explanation": "この表現が、持つ、特殊な、ニュアンスや、プロフェッショナルな、印象を、与えるための、ヒントを、解説します。"
            }
          ]
        }
        ```
        """

        # --- AIへの、リクエスト部分の、進化 (音声とテキストで共通化) ---
        if isinstance(content_to_process, str):
            original_text = content_to_process
            request_contents = [system_prompt, original_text]
        elif isinstance(content_to_process, bytes):
            original_text = "(音声入力)"
            audio_part = {"mime_type": "audio/webm", "data": content_to_process}
            request_contents = [system_prompt, "この日本語の音声を解釈し、提案してください:", audio_part]
        else:
            return None, None

        # --- AIからの、応答を、待つ (変更なし) ---
        response = model.generate_content(request_contents)
        
        # ★★★ ここが、AIとの、契約が、守られたかを、確認する、最重要の、関所です ★★★
        try:
            # AIからの回答（response.text）を、厳格に、JSONとして、解析する
            translated_proposals = json.loads(response.text)
            return original_text, translated_proposals
        except (json.JSONDecodeError, TypeError):
            # AIが、万が一、契約を、破り、JSON以外の、テキストを、返してきた場合の、防衛ライン
            st.error("AIからの応答を解析できませんでした。AIが予期せぬ形式で回答した可能性があります。もう一度お試しください。")
            # デバッグのために、AIの生の回答を、コンソールに、こっそり、表示しておく
            print("AI Non-JSON Response:", response.text) 
            return None, None

    # --- 我らが誇る、『二段構え』迎撃システム (変更なし、しかし、常に、我々の、背後を、守り続ける) ---
    except exceptions.ResourceExhausted as e:
        st.error("APIキーの上限に達した可能性があります。少し時間をあけるか、明日以降に再試行してください。")
        return None, None
    except Exception as e:
        error_message = str(e).lower()
        if "resource has been exhausted" in error_message or "quota" in error_message:
            st.error("APIキーの上限に達した可能性があります。少し時間をあけるか、明日以降に再試行してください。")
        else:
            st.error(f"AI処理中に予期せぬエラーが発生しました: {e}")
        return None, None

# ===============================================================
# 専門家のメインの仕事 (新たなる、価値を、表示するために、進化)
# ===============================================================
def show_tool(gemini_api_key):
    # --- 応援者、帰還システム (変更なし) ---
    if st.query_params.get("unlocked") == "true":
        st.session_state.translator_usage_count = 0
        st.query_params.clear()
        st.toast("おかえりなさい！利用回数がリセットされました。")
        st.balloons()
        time.sleep(1)
        st.rerun()

    st.header("🤝 プロフェッショナル翻訳ツール", divider='rainbow')

    # --- セッション管理 (変更なし) ---
    if "translator_results" not in st.session_state: st.session_state.translator_results = []
    if "translator_last_mic_id" not in st.session_state: st.session_state.translator_last_mic_id = None
    if "text_to_process" not in st.session_state: st.session_state.text_to_process = None
    if "translator_last_input" not in st.session_state: st.session_state.translator_last_input = ""
    if "translator_usage_count" not in st.session_state: st.session_state.translator_usage_count = 0

    # --- 制限と、応援への、誘導 (変更なし) ---
    usage_limit = 10
    is_limit_reached = st.session_state.translator_usage_count >= usage_limit

    if is_limit_reached:
        st.success("🎉 たくさんのご利用、ありがとうございます！")
        st.info("このツールが、あなたの世界を広げる一助となれば幸いです。\n\n下のボタンから応援ページに移動することで、翻訳を続けることができます。")
        portal_url = "https://experiment-site.pray-power-is-god-and-cocoro.com/continue.html"
        st.link_button("応援ページに移動して、翻訳を続ける", portal_url, type="primary")
    else:
        st.info("マイクで日本語を話すか、テキストボックスに入力してください。シーン別のプロフェッショナルな英語表現を3つ提案します。")
        st.caption(f"🚀 あと {usage_limit - st.session_state.translator_usage_count} 回、提案を受けられます。応援後、リセットされます。")
        with st.expander("💡 このツールのAIについて"):
            st.markdown("""
            このツールは、Googleの**Gemini 1.5 Flash**というAIモデルを使用しています。
            現在、このモデルには**1分あたり15回、1日あたり1,500回まで**の無料利用枠が設定されています。
            心ゆくまで、言語の壁を越える旅をお楽しみください！
            """, unsafe_allow_html=True)
        def handle_text_input():
            st.session_state.text_to_process = st.session_state.translator_text
        col1, col2 = st.columns([1, 2])
        with col1:
            audio_info = mic_recorder(start_prompt="🎤 話し始める", stop_prompt="⏹️ 提案を受ける", key='translator_mic', format="webm")
        with col2:
            st.text_input("または、ここに日本語を入力してEnter...", key="translator_text", on_change=handle_text_input)

    # --- 入力検知と、処理実行の、分離 (我らが『最強の門番』ロジック、変更なし) ---
    content_to_process = None
    if audio_info and audio_info['id'] != st.session_state.translator_last_mic_id:
        content_to_process = audio_info['bytes']
        st.session_state.translator_last_mic_id = audio_info['id']
    elif st.session_state.text_to_process:
        content_to_process = st.session_state.text_to_process
        st.session_state.text_to_process = None

    if content_to_process and content_to_process != st.session_state.translator_last_input:
        st.session_state.translator_last_input = content_to_process
        if not gemini_api_key:
            st.error("サイドバーでGemini APIキーを設定してください。")
        else:
            with st.spinner("AIが様々なビジネスシーンを想定し、最適な表現を考えています..."):
                original, proposals_data = translate_with_gemini(content_to_process, gemini_api_key)
            
            if proposals_data and "proposals" in proposals_data:
                st.session_state.translator_usage_count += 1
                st.session_state.translator_results.insert(0, {"original": original, "proposals": proposals_data["proposals"]})
                st.rerun()
            else:
                st.session_state.translator_last_input = ""

    # ★★★ ここからが、我々の、新たなる、価値を、ユーザーに、届ける、神聖なる、陳列棚です ★★★
    if st.session_state.translator_results:
        st.write("---")
        for i, result in enumerate(st.session_state.translator_results):
            with st.container(border=True):
                st.markdown(f"#### 履歴 No.{len(st.session_state.translator_results) - i}")
                st.markdown(f"**🇯🇵 あなたの入力:** {result['original']}")
                st.write("---")
                
                if "proposals" in result and isinstance(result["proposals"], list):
                    for proposal_index, proposal in enumerate(result["proposals"]):
                        with st.expander(f"**提案 {proposal_index + 1}: {proposal.get('situation', 'N/A')}**", expanded=(proposal_index == 0)):
                            st.markdown(f"##### 🗣️ このフレーズが最適です")
                            st.code(f"{proposal.get('phrase', 'N/A')}", language="markdown")
                            st.markdown(f"##### ✍️ このように使います（例文）")
                            st.success(f"{proposal.get('example_sentence', 'N/A')}")
                            st.markdown(f"##### 💡 なぜなら... (解説)")
                            st.info(f"{proposal.get('explanation', 'N/A')}")

        if st.button("提案履歴をクリア", key="clear_translator_history"):
            st.session_state.translator_results = []
            st.session_state.translator_last_input = ""
            st.rerun()
