import streamlit as st
import google.generativeai as genai
import time
from google.api_core import exceptions
from streamlit_mic_recorder import mic_recorder

# === 我らが帝国の憲法：汎用型・回想対話プロンプト Ver. 3.0 (Ω.FINAL) ===
SYSTEM_PROMPT = """
# 指示

あなたは、カール・ロジャーズの心理学と解決志向アプローチを統合した、究極の『思い出の聞き手』です。
あなたの目的は、相手が人生の素晴らしい経験や、困難を乗り越えた強さを語る手助けをし、脳と心を活性化させ、自己肯定感を最大化することです。

# 守るべきルール

1.  **役割:** あなたは共感的な聞き役であり、決して教えたり、評価・判断したりしないでください。相手の全ての言葉を無条件に肯定し、聖なる空間のような安心感を提供してください。
2.  **開始:** 初回の応答では、まず自己紹介とツールの簡単な説明をした上で、相手が話しやすいように、ポジティブな記憶に繋がりやすい、具体的で簡単な質問を一つだけしてください。（例：「こんにちは。私は、あなたの人生の素敵な思い出をお聞きする、AIパートナーです。昔、時間を忘れるほど夢中になったことは何でしたか？」）
3.  **深掘り:** 相手がポジティブな体験を語っている間は、遮らずに深く頷き、共感してください。そして、「その時、どんな気持ちでしたか？」「周りの景色を覚えていますか？」など、感情や五感に焦点を当てた質問で、さらに記憶を引き出す手助けをしてください。

4.  **【最重要】『聖なる分岐点』- ネガティブな記憶への究極の対処法:**
    もし相手が辛い体験を語り始めたら、以下のステップを厳密に実行してください。
    *   **ステップ1 (深い共感):** まず、「それは、本当にお辛かったですね」と、その感情に全身全霊で共感し、相手が安心して気持ちを吐き出せる場を作ります。
    *   **ステップ2 (分岐点の提示):** 次に、無理に励ますのではなく、相手に選択肢を委ねる、魔法の質問を投げかけてください。
        *   「もしよろしければ、その時のお気持ちを、もう少しだけ聞かせていただけますか？ あるいは、そんな大変な状況を乗り越えられた、あなたの『お力』について、お聞かせ願えますか？」
    *   **ステップ3 (相手の選択への追従):**
        *   もし相手が「気持ち」について話し続けたなら、あなたはただひたすら聞き役に徹し、共感を深めてください。
        *   もし相手が「どう乗り越えたか」について話し始めたなら、その強さや工夫を具体的に賞賛し、自己肯定感を高める手助けをしてください。

5.  **肯定:** 会話の締めくくりや適切なタイミングで、語られたエピソード全体を包み込むように肯定します。楽しかった経験、乗り越えた強さ、そして語ってくれたその勇気、その全てが、その人の人生の豊かさの証であることを、心からの言葉で伝えてください。
6.  **簡潔さ:** あなたの発言は常に短く、穏やかで、最大限の敬意に満ちたものにしてください。
"""

# === AIとの対話を行う、聖なる儀式 ===
def talk_with_ai(api_key, chat_session, user_input):
    try:
        genai.configure(api_key=api_key)
        response = chat_session.send_message(user_input)
        return response.text
    # --- 『二段構えの迎撃システム』も、健在 ---
    except exceptions.ResourceExhausted as e:
        st.error("APIキーの上限に達した可能性があります。少し時間をあけるか、明日以降に再試行してください。")
        return None
    except Exception as e:
        error_message = str(e).lower()
        if "resource has been exhausted" in error_message or "quota" in error_message:
            st.error("APIキーの上限に達した可能性があります。少し時間をあけるか、明日以降に再試行してください。")
        else:
            st.error(f"AI処理中に予期せぬエラーが発生しました: {e}")
        return None

# === メインの仕事 (英雄の館の、表示) ===
def show_tool(gemini_api_key):
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    # ★★★ 『帰還者の祝福』モデル、新たなる英雄への、完全なる、継承 ★★★
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    
    # --- 帰還者の検知 ---
    if st.query_params.get("unlocked") == "true":
        # 『聖なる炎』による、記憶の浄化
        st.session_state.cc_usage_count = 0
        st.query_params.clear()
        st.toast("おかえりなさい！またお話できることを、楽しみにしておりました。")
        st.balloons()
        time.sleep(1.5) # 少し長めに余韻を
        st.rerun()

    st.header("❤️ 認知予防ツール", divider='rainbow')
    
    # --- セッション管理 (英雄ごとの、記憶領域) ---
    if "cc_chat_session" not in st.session_state: st.session_state.cc_chat_session = None
    if "cc_chat_history" not in st.session_state: st.session_state.cc_chat_history = []
    if "cc_last_audio_id" not in st.session_state: st.session_state.cc_last_audio_id = None
    # ★ 変更点：利用回数の記憶領域を追加
    if "cc_usage_count" not in st.session_state: st.session_state.cc_usage_count = 0 

    # ★ 変更点：利用制限の定義
    usage_limit = 2
    is_limit_reached = st.session_state.cc_usage_count >= usage_limit
    
    # --- 倫理的・運用上の最終防衛線 ---
    with st.expander("💡 このツールについて（初めての方はお読みください）"):
        st.warning("""
        - このツールは、AIと昔の思い出をお話することで、楽しく認知機能の健康を維持することを目的としています。医療行為や診断、治療を行うものではありません。
        - 対話相手はAIであり、人間の専門家ではありません。専門的なカウンセリングや、緊急の対応は行えません。
        - 心配なことや、専門的な助けが必要だと感じた場合は、ご家族や、かかりつけのお医者様にご相談ください。
        """)

    # --- 利用回数に応じた、画面の分岐 ---
    if is_limit_reached:
        st.success("🎉 たくさんお話いただき、ありがとうございます！")
        st.info("このツールが、あなたの心を温める一助となれば幸いです。\n\n応援ページへ移動することで、またお話を続けることができます。")
        # ★ 変更点：応援ページのURL
        portal_url = "https://example.com/your-support-page" # ← ちゃろ様の応援ページのURLに変更してください
        st.link_button("応援ページに移動して、お話を続ける", portal_url, type="primary", use_container_width=True)
    else:
        st.info("下のマイクのボタンを押して、昔の楽しかった思い出や、頑張ったお話など、なんでも自由にお話しください。")
        # ★ 変更点：残り回数の表示
        st.caption(f"🚀 あと {usage_limit - st.session_state.cc_usage_count} 回、お話できます。")

        # --- 対話インターフェース ---
        audio_info = mic_recorder(
            start_prompt="🟢 話し始める (クリックして録音開始)",
            stop_prompt="🔴 話を聞いてもらう (クリックして録音停止)",
            key='cognitive_companion_mic',
            format="webm"
        )
    
    # チャット履歴の表示
    if st.session_state.cc_chat_history:
        st.write("---")
    for message in st.session_state.cc_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- 処理の実行 (『最強の門番』ロジックは不変) ---
    if not is_limit_reached and audio_info and audio_info['id'] != st.session_state.cc_last_audio_id:
        st.session_state.cc_last_audio_id = audio_info['id']

        if not gemini_api_key:
            st.error("サイドバーでGemini APIキーを設定してください。")
        else:
            with st.spinner("（あなたの声を、言葉に、変えています...）"):
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                audio_part = {"mime_type": "audio/webm", "data": audio_info['bytes']}
                transcription_prompt = "この音声を、できる限り正確に、文字に書き起こしてください。"
                try:
                    transcription_response = model.generate_content([transcription_prompt, audio_part])
                    user_text = transcription_response.text.strip()
                except Exception as e:
                    st.error(f"音声の文字起こし中にエラーが発生しました: {e}")
                    user_text = None

            if user_text:
                st.session_state.cc_chat_history.append({"role": "user", "content": user_text})

                if st.session_state.cc_chat_session is None:
                    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest", system_instruction=SYSTEM_PROMPT)
                    st.session_state.cc_chat_session = model.start_chat(history=[])

                with st.spinner("（AIが、あなたのお話を、一生懸命聞いています...）"):
                    ai_response = talk_with_ai(gemini_api_key, st.session_state.cc_chat_session, user_text)

                if ai_response:
                    # ★ 変更点：AIの応答があった時点で、カウンターを1増やす
                    st.session_state.cc_usage_count += 1
                    st.session_state.cc_chat_history.append({"role": "assistant", "content": ai_response})
                    st.rerun()

    if st.session_state.cc_chat_history and st.button("会話の履歴をリセット", key="clear_cc_history"):
        st.session_state.cc_chat_session = None
        st.session_state.cc_chat_history = []
        # ★ 変更点：履歴リセット時に、回数もリセットする（お好みで）
        # st.session_state.cc_usage_count = 0 
        st.rerun()
