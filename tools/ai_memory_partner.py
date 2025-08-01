import streamlit as st
import google.generativeai as genai
import time
from google.api_core import exceptions
from streamlit_mic_recorder import mic_recorder

# === 我らが帝国の憲法：汎用型・回想対話プロンプト Ver. 3.0 (Ω.FINAL) ===
# この、魂は、Proモデルのために、作られましたが、Flashモデルにも、受け継がせます
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
# 以前の、安定した、構造に、戻します
def get_ai_response(api_key, chat_session, user_input):
    try:
        genai.configure(api_key=api_key)
        
        # セッションがなければ、ここで、新たに、魂を、吹き込む
        if chat_session is None:
            # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
            # ★★★ ここが、唯一の、変更点です ★★★
            model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", system_instruction=SYSTEM_PROMPT)
            # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
            chat_session = model.start_chat(history=[])
        
        response = chat_session.send_message(user_input)
        return response.text, chat_session

    except exceptions.ResourceExhausted as e:
        st.error("APIキーの上限に達した可能性があります。(ResourceExhausted)")
        return None, chat_session
    except Exception as e:
        error_message = str(e).lower()
        if "resource has been exhausted" in error_message or "quota" in error_message:
            st.error("APIキーの上限に達した可能性があります。(General Quota Error)")
        else:
            st.error(f"AI処理中に予期せぬエラーが発生しました: {e}")
        return None, chat_session

# === メインの仕事 (英雄の館の、表示) ===
def show_tool(gemini_api_key):
    # (表示に関する部分は、ほぼ、変更ありません)
    if st.query_params.get("unlocked") == "true":
        st.session_state.cc_usage_count = 0; st.query_params.clear()
        st.toast("おかえりなさい！"); st.balloons(); time.sleep(1.5); st.rerun()

    st.header("❤️ 認知予防ツール", divider='rainbow')
    
    if "cc_chat_session" not in st.session_state: st.session_state.cc_chat_session = None
    if "cc_chat_history" not in st.session_state: st.session_state.cc_chat_history = []
    if "cc_last_audio_id" not in st.session_state: st.session_state.cc_last_audio_id = None
    if "cc_usage_count" not in st.session_state: st.session_state.cc_usage_count = 0 

    usage_limit = 2
    is_limit_reached = st.session_state.cc_usage_count >= usage_limit
    
    with st.expander("💡 このツールについて（初めての方はお読みください）"):
        st.warning("""（内容は変更なし）""")

    if is_limit_reached:
        st.success("🎉 たくさんお話いただき、ありがとうございます！")
        st.info("このツールが、あなたの心を温める一助となれば幸いです。\n\n応援ページへ移動することで、またお話を続けることができます。")
        portal_url = "https://pray-power-is-god-and-cocoro.com/free3/continue.html"
        st.link_button("応援ページに移動して、お話を続ける", portal_url, type="primary", use_container_width=True)
    else:
        st.info("下のマイクのボタンを押して、昔の楽しかった思い出や、頑張ったお話など、なんでも自由にお話しください。")
        st.caption(f"🚀 あと {usage_limit - st.session_state.cc_usage_count} 回、お話できます。")
        audio_info = mic_recorder(start_prompt="🟢 話し始める", stop_prompt="🔴 話を聞いてもらう", key='cognitive_companion_mic', format="webm")
    
    if st.session_state.cc_chat_history:
        st.write("---")
    for message in st.session_state.cc_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 以前の、安定していた、二段階の、儀式に、戻します
    if not is_limit_reached and audio_info and audio_info['id'] != st.session_state.cc_last_audio_id:
        st.session_state.cc_last_audio_id = audio_info['id']

        if not gemini_api_key:
            st.error("サイドバーでGemini APIキーを設定してください。")
        else:
            # --- 第一の儀式：文字起こし ---
            user_text = None
            with st.spinner("（あなたの声を、言葉に、変えています...）"):
                try:
                    transcription_model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    audio_part = {"mime_type": "audio/webm", "data": audio_info['bytes']}
                    transcription_prompt = "この音声を、できる限り正確に、文字に書き起こしてください。"
                    transcription_response = transcription_model.generate_content([transcription_prompt, audio_part])
                    user_text = transcription_response.text.strip()
                except Exception as e:
                    st.error(f"音声の文字起こし中にエラーが発生しました: {e}")
            
            # --- 第二の儀式：対話 ---
            if user_text:
                st.session_state.cc_chat_history.append({"role": "user", "content": user_text})
                
                with st.spinner("（AIが、あなたのお話を、一生懸命聞いています...）"):
                    ai_response, updated_session = get_ai_response(
                        gemini_api_key, 
                        st.session_state.cc_chat_session,
                        user_text
                    )

                if ai_response:
                    st.session_state.cc_usage_count += 1
                    st.session_state.cc_chat_history.append({"role": "assistant", "content": ai_response})
                    st.session_state.cc_chat_session = updated_session # 対話の記憶を更新
                    st.rerun()

    if st.session_state.cc_chat_history and st.button("会話の履歴をリセット", key="clear_cc_history"):
        st.session_state.cc_chat_session = None
        st.session_state.cc_chat_history = []
        st.rerun()
