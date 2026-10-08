import streamlit as st
import os
import time
from pathlib import Path
import wave
import pyaudio
from pydub import AudioSegment
from audiorecorder import audiorecorder
import numpy as np
from scipy.io.wavfile import write
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
import constants as ct

def record_audio(audio_input_file_path):
    """
    音声入力を受け取って音声ファイルを作成
    """
    import streamlit as st

    audio = audiorecorder(
        start_prompt="発話開始",
        pause_prompt="やり直す",
        stop_prompt="発話終了",
        start_style={"color":"white", "background-color":"black"},
        pause_style={"color":"gray", "background-color":"white"},
        stop_style={"color":"white", "background-color":"black"}
    )
    
    if len(audio) > 0:
        audio.export(audio_input_file_path, format="wav")
        # ノイズ除去処理を適用
        cleaned_audio_path = reduce_audio_noise(audio_input_file_path)
        return True, cleaned_audio_path
    else:
        return False, None

def reduce_audio_noise(audio_file_path):
    """
    音声ファイルのノイズを除去する
    """
    try:
        import noisereduce as nr
        import librosa
        import soundfile as sf
        import os
        
        # 音声ファイルを読み込み
        y, sr = librosa.load(audio_file_path, sr=None)
        
        # ノイズ除去（背景ノイズを自動検出して除去）
        reduced_noise = nr.reduce_noise(y=y, sr=sr, stationary=True)
        
        # ノイズ除去後のファイルを保存
        cleaned_file_path = audio_file_path.replace(".wav", "_cleaned.wav")
        sf.write(cleaned_file_path, reduced_noise, sr)
        
        return cleaned_file_path
    except Exception as e:
        # ノイズ除去に失敗した場合は元のファイルを返す
        print(f"ノイズ除去処理でエラーが発生しました: {e}")
        return audio_file_path

def transcribe_audio(audio_input_file_path):
    """
    音声入力ファイルから文字起こしテキストを取得
    Args:
        audio_input_file_path: 音声入力ファイルのパス
    """

    with open(audio_input_file_path, 'rb') as audio_input_file:
        transcript = st.session_state.openai_obj.audio.transcriptions.create(
            model="whisper-1",
            file=audio_input_file,
            language="en"
        )
    
    # 音声入力ファイルを削除
    os.remove(audio_input_file_path)

    return transcript

def save_to_wav(llm_response_audio, audio_output_file_path):
    """
    一旦mp3形式で音声ファイル作成後、wav形式に変換
    Args:
        llm_response_audio: LLMからの回答の音声データ
        audio_output_file_path: 出力先のファイルパス
    """

    temp_audio_output_filename = f"{ct.AUDIO_OUTPUT_DIR}/temp_audio_output_{int(time.time())}.mp3"
    with open(temp_audio_output_filename, "wb") as temp_audio_output_file:
        temp_audio_output_file.write(llm_response_audio)
    
    audio_mp3 = AudioSegment.from_file(temp_audio_output_filename, format="mp3")
    audio_mp3.export(audio_output_file_path, format="wav")

    # 音声出力用に一時的に作ったmp3ファイルを削除
    os.remove(temp_audio_output_filename)

def play_wav(audio_output_file_path, speed=1.0):
    """
    音声ファイルの読み上げ
    Args:
        audio_output_file_path: 音声ファイルのパス
        speed: 再生速度（1.0が通常速度、0.5で半分の速さ、2.0で倍速など）
    """

    # 音声ファイルの読み込み
    audio = AudioSegment.from_wav(audio_output_file_path)
    
    # 速度を変更
    if speed != 1.0:
        # frame_rateを変更することで速度を調整
        modified_audio = audio._spawn(
            audio.raw_data, 
            overrides={"frame_rate": int(audio.frame_rate * speed)}
        )
        # 元のframe_rateに戻すことで正常再生させる（ピッチを保持したまま速度だけ変更）
        modified_audio = modified_audio.set_frame_rate(audio.frame_rate)

        modified_audio.export(audio_output_file_path, format="wav")

    # PyAudioで再生
    with wave.open(audio_output_file_path, 'rb') as play_target_file:
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(play_target_file.getsampwidth()),
            channels=play_target_file.getnchannels(),
            rate=play_target_file.getframerate(),
            output=True
        )

        data = play_target_file.readframes(1024)
        while data:
            stream.write(data)
            data = play_target_file.readframes(1024)

        stream.stop_stream()
        stream.close()
        p.terminate()
    
    # LLMからの回答の音声ファイルを削除
    os.remove(audio_output_file_path)

def create_chain(system_template):
    """
    LLMによる回答生成用のChain作成
    """

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_template),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    chain = ConversationChain(
        llm=st.session_state.llm,
        memory=st.session_state.memory,
        prompt=prompt
    )

    return chain

def create_problem_and_play_audio():
    """
    問題生成と音声ファイルの再生
    Args:
        chain: 問題文生成用のChain
        speed: 再生速度（1.0が通常速度、0.5で半分の速さ、2.0で倍速など）
        openai_obj: OpenAIのオブジェクト
    """

    # 英語レベルを含むプロンプトで問題文を生成
    input_text = f"English Level: {st.session_state.englv}"
    problem = st.session_state.chain_create_problem.predict(input=input_text)

    # LLMからの回答を音声データに変換
    llm_response_audio = st.session_state.openai_obj.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=problem
    )

    # 音声ファイルの作成
    audio_output_file_path = f"{ct.AUDIO_OUTPUT_DIR}/audio_output_{int(time.time())}.wav"
    save_to_wav(llm_response_audio.content, audio_output_file_path)

    # 音声ファイルの読み上げ
    play_wav(audio_output_file_path, st.session_state.speed)

    return problem, llm_response_audio

def create_evaluation():
    """
    ユーザー入力値の評価生成
    """
    import streamlit as st
    
    try:
        st.info("デバッグ: create_evaluation 関数内部開始")
        if not hasattr(st.session_state, 'chain_evaluation'):
            st.error("デバッグ: chain_evaluation が存在しません")
            return "chain_evaluationが初期化されていません"
        
        st.info("デバッグ: chain_evaluation.predict 呼び出し開始")
        llm_response_evaluation = st.session_state.chain_evaluation.predict(input="上記の問題文と回答文を分析し、詳細な評価とフィードバックを提供してください。")
        st.info(f"デバッグ: LLM応答受信: {len(llm_response_evaluation) if llm_response_evaluation else 0}文字")
        
        return llm_response_evaluation
    except Exception as e:
        st.error(f"デバッグ: create_evaluation でエラー: {str(e)}")
        import traceback
        st.error(f"デバッグ: トレースバック: {traceback.format_exc()}")
        return f"評価生成エラー: {str(e)}"