import streamlit as st
import os
import time
from time import sleep
from pathlib import Path
from streamlit.components.v1 import html
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from openai import OpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import functions as ft
import constants as ct


# 各種設定
load_dotenv()
st.set_page_config(
    page_title=ct.APP_NAME
)

# タイトル表示
st.markdown(f"## {ct.APP_NAME}")

# 初期処理
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.start_flg = False
    st.session_state.pre_mode = ""
    st.session_state.shadowing_flg = False
    st.session_state.shadowing_button_flg = False
    st.session_state.shadowing_count = 0
    st.session_state.shadowing_first_flg = True
    st.session_state.shadowing_audio_input_flg = False
    st.session_state.shadowing_evaluation_first_flg = True
    st.session_state.replay_problem_flg = False
    st.session_state.problem_audio_path = ""
    st.session_state.dictation_flg = False
    st.session_state.dictation_button_flg = False
    st.session_state.dictation_count = 0
    st.session_state.dictation_first_flg = True
    st.session_state.dictation_chat_message = ""
    st.session_state.dictation_evaluation_first_flg = True
    st.session_state.chat_open_flg = False
    st.session_state.problem = ""
    
    st.session_state.openai_obj = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    st.session_state.llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
    st.session_state.memory = ConversationSummaryBufferMemory(
        llm=st.session_state.llm,
        max_token_limit=1000,
        return_messages=True
    )

    # モード「日常英会話」用のChain作成
    st.session_state.chain_basic_conversation = ft.create_chain(ct.SYSTEM_TEMPLATE_BASIC_CONVERSATION)

# 初期表示
# col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
# 提出課題用
col1, col2, col3, col4 = st.columns([2, 2, 3, 3])
with col1:
    if st.session_state.start_flg:
        st.button("開始", use_container_width=True, type="primary")
    else:
        st.session_state.start_flg = st.button("開始", use_container_width=True, type="primary")
with col2:
    st.session_state.speed = st.selectbox(label="再生速度", options=ct.PLAY_SPEED_OPTION, index=3, label_visibility="collapsed")
with col3:
    st.session_state.mode = st.selectbox(label="モード", options=[ct.MODE_1, ct.MODE_2, ct.MODE_3], label_visibility="collapsed")
    # モードを変更した際の処理
    if st.session_state.mode != st.session_state.pre_mode:
        # 自動でそのモードの処理が実行されないようにする
        st.session_state.start_flg = False
        # 「日常英会話」選択時の初期化処理
        if st.session_state.mode == ct.MODE_1:
            st.session_state.dictation_flg = False
        # 「シャドーイング」選択時の初期化処理
        if st.session_state.mode == ct.MODE_2:
            st.session_state.dictation_flg = False
            st.session_state.problem = ""  # 問題文をリセット
        # 「ディクテーション」選択時の初期化処理
        if st.session_state.mode == ct.MODE_3:
            st.session_state.problem = ""  # 問題文をリセット
            st.session_state.problem_audio_path = ""
            st.session_state.dictation_evaluation_first_flg = True
        # チャット入力欄を非表示にする
        st.session_state.chat_open_flg = False
    st.session_state.pre_mode = st.session_state.mode
with col4:
    st.session_state.englv = st.selectbox(label="英語レベル", options=ct.ENGLISH_LEVEL_OPTION, label_visibility="collapsed")

with st.chat_message("assistant", avatar="images/ai_icon.jpg"):
    st.markdown("こちらは生成AIによる音声英会話の練習アプリです。何度も繰り返し練習し、英語力をアップさせましょう。")
    st.markdown("**【操作説明】**")
    st.success("""
    - モードと再生速度を選択し、「英会話開始」ボタンを押して英会話を始めましょう。
    - モードは「日常英会話」「シャドーイング」「ディクテーション」から選べます。
    - 発話後、5秒間沈黙することで音声入力が完了します。
    - 「一時中断」ボタンを押すことで、英会話を一時中断できます。
    """)
st.divider()

# メッセージリストの一覧表示
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message(message["role"], avatar="images/ai_icon.jpg"):
            st.markdown(message["content"])
    elif message["role"] == "user":
        with st.chat_message(message["role"], avatar="images/user_icon.jpg"):
            st.markdown(message["content"])
    else:
        st.divider()

# LLMレスポンスの下部にモード実行のボタン表示
if st.session_state.mode == ct.MODE_2 and st.session_state.problem:
    col_shadowing1, col_shadowing2, col_shadowing3 = st.columns([1, 1, 1])
    with col_shadowing1:
        if st.session_state.shadowing_audio_input_flg:
            st.info("🎤 音声録音中です...")
        else:
            st.session_state.shadowing_button_flg = st.button("シャドーイング開始")
    with col_shadowing2:
        if not st.session_state.shadowing_audio_input_flg:
            st.session_state.replay_problem_flg = st.button("問題文を再生")
    with col_shadowing3:
        if not st.session_state.shadowing_audio_input_flg:
            if st.button("新しい問題"):
                st.session_state.problem = ""
                st.session_state.problem_audio_path = ""
                st.session_state.shadowing_evaluation_first_flg = True
                st.rerun()
elif st.session_state.mode == ct.MODE_2:
    if not st.session_state.problem:
        st.info("「開始」ボタンを押して問題文を生成してください。")

if st.session_state.dictation_flg:
    col_dictation1, col_dictation2, col_dictation3 = st.columns([1, 1, 1])
    with col_dictation1:
        st.session_state.dictation_button_flg = st.button("ディクテーション開始")
    with col_dictation2:
        if st.session_state.problem and st.session_state.problem_audio_path:
            st.session_state.replay_problem_flg = st.button("問題文を再生")
    with col_dictation3:
        if st.button("新しい問題"):
            st.session_state.problem = ""
            st.session_state.problem_audio_path = ""
            st.session_state.dictation_evaluation_first_flg = True
            st.session_state.chat_open_flg = False
            st.rerun()

# 「ディクテーション」モードのチャット入力受付時に実行
if st.session_state.chat_open_flg:
    st.info("AIが読み上げた音声を、画面下部のチャット欄からそのまま入力・送信してください。")

st.session_state.dictation_chat_message = st.chat_input("※「ディクテーション」選択時以外は送信不可")

if st.session_state.dictation_chat_message and not st.session_state.chat_open_flg:
    st.stop()

# シャドーイング開始ボタンの処理（start_flgに関係なく実行）

# 「シャドーイング開始」ボタンが押された時の処理
if st.session_state.mode == ct.MODE_2 and st.session_state.shadowing_button_flg:
    # 問題文の存在確認
    if not st.session_state.problem:
        st.error("問題文が生成されていません。「開始」ボタンを押してください。")
        st.session_state.shadowing_button_flg = False
        st.rerun()
    
    # 音声録音UIを表示状態にする
    st.session_state.shadowing_audio_input_flg = True
    st.session_state.shadowing_button_flg = False
    st.rerun()

# 音声録音処理（shadowing_audio_input_flgがTrueの時）
if st.session_state.mode == ct.MODE_2 and st.session_state.shadowing_audio_input_flg:
    st.info("🎤 問題文を聞いて、同じように発話してください：")
    
    # 音声録音UIを表示
    audio_input_file_path = f"{ct.AUDIO_INPUT_DIR}/audio_input_{int(time.time())}.wav"
    audio_recorded, cleaned_audio_path = ft.record_audio(audio_input_file_path)
    
    # 音声が録音された場合の処理
    if audio_recorded:
        st.session_state.shadowing_audio_input_flg = False

        with st.spinner('音声入力をテキストに変換中...'):
            # ノイズ除去済みの音声ファイルから文字起こしテキストを取得
            transcript = ft.transcribe_audio(cleaned_audio_path)
            audio_input_text = transcript.text

        # AIメッセージとユーザーメッセージの画面表示
        with st.chat_message("assistant", avatar=ct.AI_ICON_PATH):
            st.markdown(st.session_state.problem)
        with st.chat_message("user", avatar=ct.USER_ICON_PATH):
            st.markdown(audio_input_text)
        
        # LLMが生成した問題文と音声入力値をメッセージリストに追加
        st.session_state.messages.append({"role": "assistant", "content": st.session_state.problem})
        st.session_state.messages.append({"role": "user", "content": audio_input_text})

        with st.spinner('評価結果の生成中...'):
            try:
                if st.session_state.shadowing_evaluation_first_flg:
                    system_template = ct.SYSTEM_TEMPLATE_EVALUATION.format(
                        llm_text=st.session_state.problem,
                        user_text=audio_input_text
                    )
                    st.session_state.chain_evaluation = ft.create_chain(system_template)
                    st.session_state.shadowing_evaluation_first_flg = False
                
                # 問題文と回答を比較し、評価結果の生成を指示するプロンプトを作成
                llm_response_evaluation = ft.create_evaluation()
                
                if not llm_response_evaluation:
                    llm_response_evaluation = "評価の生成に失敗しました。もう一度お試しください。"
                    
            except Exception as e:
                st.error(f"評価生成中にエラーが発生しました: {str(e)}")
                llm_response_evaluation = f"評価処理中にエラーが発生しました。問題文: '{st.session_state.problem}', 音声入力: '{audio_input_text}'"
        
        # 評価結果のメッセージリストへの追加と表示
        with st.chat_message("assistant", avatar=ct.AI_ICON_PATH):
            st.markdown(llm_response_evaluation)
        st.session_state.messages.append({"role": "assistant", "content": llm_response_evaluation})
        st.session_state.messages.append({"role": "other"})
        
        # 各種フラグの更新とリセット
        st.session_state.shadowing_count += 1

        # 「シャドーイング」ボタンを表示するために再描画
        st.rerun()

# 問題文を再生ボタンの処理（start_flgに関係なく実行）
if (st.session_state.mode == ct.MODE_2 or st.session_state.mode == ct.MODE_3) and st.session_state.replay_problem_flg and st.session_state.problem_audio_path:
    with st.spinner('問題文を再生中...'):
        # ファイルの存在確認
        import os
        if os.path.exists(st.session_state.problem_audio_path):
            # 保存された音声ファイルを再生
            ft.play_wav(st.session_state.problem_audio_path, speed=st.session_state.speed)
        else:
            # ファイルが見つからない場合は問題文を再生成
            st.error("音声ファイルが見つかりません。問題文を再生成します。")
            problem_audio = st.session_state.openai_obj.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=st.session_state.problem
            )
            ft.save_to_wav(problem_audio.content, st.session_state.problem_audio_path)
            ft.play_wav(st.session_state.problem_audio_path, speed=st.session_state.speed)
    # フラグをリセット
    st.session_state.replay_problem_flg = False

# 「英会話開始」ボタンが押された場合の処理
if st.session_state.start_flg:

    # モード：「ディクテーション」
    # 「ディクテーション」ボタン押下時か、「英会話開始」ボタン押下時か、チャット送信時
    if st.session_state.mode == ct.MODE_3 and (st.session_state.dictation_button_flg or st.session_state.dictation_count == 0 or st.session_state.dictation_chat_message):
        if st.session_state.dictation_first_flg:
            # 英語レベルを反映したテンプレートでChainを作成
            template_with_level = ct.SYSTEM_TEMPLATE_CREATE_PROBLEM.format(englv=st.session_state.englv)
            st.session_state.chain_create_problem = ft.create_chain(template_with_level)
            st.session_state.dictation_first_flg = False
        # チャット入力以外
        if not st.session_state.chat_open_flg:
            with st.spinner('問題文生成中...'):
                st.session_state.problem, llm_response_audio = ft.create_problem_and_play_audio()

            # 問題文の音声ファイルを保存して再利用できるようにする
            st.session_state.problem_audio_path = f"{ct.AUDIO_OUTPUT_DIR}/problem_{int(time.time())}.wav"
            # ft.create_problem_and_play_audio()で既に再生用音声が生成されているので
            # 同じ問題文で改めて音声を生成して保存
            problem_audio = st.session_state.openai_obj.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=st.session_state.problem
            )
            # 音声ファイルを確実に保存
            ft.save_to_wav(problem_audio.content, st.session_state.problem_audio_path)

            st.session_state.chat_open_flg = True
            st.session_state.dictation_flg = True  # ボタンを表示するためTrueに設定
            st.rerun()
        # チャット入力時の処理
        else:
            # チャット欄から入力された場合にのみ評価処理が実行されるようにする
            if not st.session_state.dictation_chat_message:
                st.stop()
            
            # AIメッセージとユーザーメッセージの画面表示
            with st.chat_message("assistant", avatar=ct.AI_ICON_PATH):
                st.markdown(st.session_state.problem)
            with st.chat_message("user", avatar=ct.USER_ICON_PATH):
                st.markdown(st.session_state.dictation_chat_message)

            # LLMが生成した問題文とチャット入力値をメッセージリストに追加
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.problem})
            st.session_state.messages.append({"role": "user", "content": st.session_state.dictation_chat_message})
            
            with st.spinner('評価結果の生成中...'):
                system_template = ct.SYSTEM_TEMPLATE_EVALUATION.format(
                    llm_text=st.session_state.problem,
                    user_text=st.session_state.dictation_chat_message
                )
                st.session_state.chain_evaluation = ft.create_chain(system_template)
                # 問題文と回答を比較し、評価結果の生成を指示するプロンプトを作成
                llm_response_evaluation = ft.create_evaluation()
            
            # 評価結果のメッセージリストへの追加と表示
            with st.chat_message("assistant", avatar=ct.AI_ICON_PATH):
                st.markdown(llm_response_evaluation)
            st.session_state.messages.append({"role": "assistant", "content": llm_response_evaluation})
            st.session_state.messages.append({"role": "other"})
            
            # 各種フラグの更新
            st.session_state.dictation_flg = True
            st.session_state.dictation_chat_message = ""
            st.session_state.dictation_count += 1
            st.session_state.chat_open_flg = False

            st.rerun()

    
    # モード：「日常英会話」
    if st.session_state.mode == ct.MODE_1:
        # 音声入力を受け取って音声ファイルを作成
        audio_input_file_path = f"{ct.AUDIO_INPUT_DIR}/audio_input_{int(time.time())}.wav"
        audio_recorded = ft.record_audio(audio_input_file_path)
        
        if not audio_recorded:
            st.error("音声録音に失敗しました。再度お試しください。")
            st.stop()

        # 音声入力ファイルから文字起こしテキストを取得
        with st.spinner('音声入力をテキストに変換中...'):
            transcript = ft.transcribe_audio(audio_input_file_path)
            audio_input_text = transcript.text

        # 音声入力テキストの画面表示
        with st.chat_message("user", avatar=ct.USER_ICON_PATH):
            st.markdown(audio_input_text)

        with st.spinner("回答の音声読み上げ準備中..."):
            # ユーザー入力値をLLMに渡して回答取得
            llm_response = st.session_state.chain_basic_conversation.predict(input=audio_input_text)
            
            # LLMからの回答を音声データに変換
            llm_response_audio = st.session_state.openai_obj.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=llm_response
            )

            # 一旦mp3形式で音声ファイル作成後、wav形式に変換
            audio_output_file_path = f"{ct.AUDIO_OUTPUT_DIR}/audio_output_{int(time.time())}.wav"
            ft.save_to_wav(llm_response_audio.content, audio_output_file_path)

        # 音声ファイルの読み上げ
        ft.play_wav(audio_output_file_path, speed=st.session_state.speed)

        # AIメッセージの画面表示とリストへの追加
        with st.chat_message("assistant", avatar=ct.AI_ICON_PATH):
            st.markdown(llm_response)

        # ユーザー入力値とLLMからの回答をメッセージ一覧に追加
        st.session_state.messages.append({"role": "user", "content": audio_input_text})
        st.session_state.messages.append({"role": "assistant", "content": llm_response})


    # モード：「シャドーイング」
    if st.session_state.mode == ct.MODE_2:
        # 初期化処理
        if st.session_state.shadowing_first_flg:
            # 英語レベルを反映したテンプレートでChainを作成
            template_with_level = ct.SYSTEM_TEMPLATE_CREATE_PROBLEM.format(englv=st.session_state.englv)
            st.session_state.chain_create_problem = ft.create_chain(template_with_level)
            st.session_state.shadowing_first_flg = False
        
        # 問題文生成処理（初回のみ）
        if not st.session_state.problem:
            with st.spinner('問題文生成中...'):
                st.session_state.problem, llm_response_audio = ft.create_problem_and_play_audio()
            
            # 問題文の音声ファイルを保存して再利用できるようにする
            st.session_state.problem_audio_path = f"{ct.AUDIO_OUTPUT_DIR}/problem_{int(time.time())}.wav"
            # ft.create_problem_and_play_audio()で既に再生用音声が生成されているので
            # 同じ問題文で改めて音声を生成して保存
            problem_audio = st.session_state.openai_obj.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=st.session_state.problem
            )
            # 音声ファイルを確実に保存
            ft.save_to_wav(problem_audio.content, st.session_state.problem_audio_path)
            
            st.rerun()