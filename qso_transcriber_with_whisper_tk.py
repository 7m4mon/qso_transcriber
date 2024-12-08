'''
Title: QSO_Transcriber
Description: 
無線機のSQLが開いたときに録音し、録音したファイルを
Wisper-API に渡して交信内容を文字起こしします。
Author: 7M4MON
Date: 2024/6/11 初版
'''

import tkinter as tk
import tkinter.messagebox as messagebox
import pyaudio, wave, serial, time, json, threading, ctypes, os
from datetime import datetime
from pydub import AudioSegment
from openai import OpenAI
client = OpenAI(api_key = os.environ['OPENAI_API_KEY'])

settings_json = open('./settings.json' , 'r')
settings_dict = json.load(settings_json) 
data_path = "./data/"

# 終了時に呼ばれてスレッドをすべて終了する
def kill_all_threads():
  for thread in threading.enumerate():
    if thread != threading.main_thread():
      print(f"kill: {thread.name}")
      ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.native_id, ctypes.py_object(SystemExit))

# 音声文字起こし関数（引数：音声ファイルパス）
def speech_to_text(filepath):
    # ファイルサイズを確認 25MB以下
    if os.path.getsize(filepath) > 25000000:
        print("file size over")
        return
    audio_file= open(filepath, "rb")
    # Speech to Text変換
    response = client.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="text")
    # 変換後のテキスト出力
    return response

# データ転送量削減のため、mp3に圧縮する
def convert_mp3(wav_path):
    audio = AudioSegment.from_wav(wav_path)
    audio.export(wav_path + ".mp3", format='mp3', bitrate='64k')
    return (wav_path + ".mp3")

# 別スレッドで呼び出されて wisperで処理をする。
def transcriber(filepath):
    result = speech_to_text(convert_mp3(filepath))
    print(result)
    resultTxtFilename = filepath + ".txt"
    with open(resultTxtFilename, 'w') as f:
        f.write(result)
    #履歴フィールドにタイムスタンプと共に表示
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    received_text.insert(tk.END, '================== ' + timestamp + ' ================== \r\n' + result + '\r\n')
    received_text.yview_moveto(1)   # 下にスクロール

# ここから受信処理
def listen_radio():
    # Wavファイルのフォーマット
    chunk = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    audio = pyaudio.PyAudio()
    RATE = 24000
    try :
        # 設定値のロード
        comport = settings_dict['comport']
        record_length_max = float(settings_dict['max_rec_sec'])
        record_length_min = float(settings_dict['min_rec_sec'])
        input_device_idx = settings_dict['input_device_idx']

        ser = serial.Serial(comport, 9600, timeout=None)
        print("Initialized\r\n")
        while True:
            while(ser.cts == False or ser.dsr == False):
                time.sleep(0.01)
            print("Recording Start")
            # 音の取込開始
            stream = audio.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                frames_per_buffer = chunk,
                input_device_index = input_device_idx
                )
            frames = []
            record_length = 0
            while(ser.cts == True and ser.dsr == True and record_length < record_length_max):
                # 音データの取得
                data = stream.read(chunk)
                frames.append(data)
                time.sleep(0.01)
                record_length += 0.01

            # 録音終了処理
            print("length="+ str(record_length))
            stream.stop_stream()
            stream.close()
            
            # 十分な長さがあり、タイムアウト以外の条件で録音データをファイルに保存
            if(record_length < record_length_max and record_length > record_length_min):
                now_string = datetime.now().strftime('%Y%m%d-%H%M%S')
                wave_file_name = data_path + now_string + ".wav"
                print(wave_file_name)
                wav = wave.open(wave_file_name, 'wb')
                wav.setnchannels(CHANNELS)
                wav.setsampwidth(audio.get_sample_size(FORMAT))
                wav.setframerate(RATE)
                wav.writeframes(b''.join(frames))
                wav.close()

                # 別スレッドでwisperに渡す
                wisper_thread = threading.Thread(target = transcriber, args=(wave_file_name,))
                wisper_thread.start()


    except KeyboardInterrupt:
        pass

    except Exception as e:
        print(e)

    finally:
        audio.terminate()
        kill_all_threads()
        ser.close()
        # end of listen_radio()


# GUI 履歴をクリア
def clear_received_text():
    received_text.delete(1.0, tk.END)

# GUIのルートを作成
root = tk.Tk()
root.title("QSO Transcriber")
root.geometry(settings_dict['geometry'])

# 最下部のラベル
author_label = tk.Label(root, text=" 7M4MON, 2024")
author_label.pack(side=tk.BOTTOM, anchor=tk.E)

# クリアボタン
clear_button = tk.Button(root, text=" Clear ", command=clear_received_text)
clear_button.pack(side=tk.BOTTOM)

# 受信した内容を表示するテキストボックス
received_text = tk.Text(root)
received_text.pack(fill=tk.BOTH, expand = True, padx=5, pady=5)

# 受信スレッドを開始
read_thread = threading.Thread(target=listen_radio, daemon=True)
read_thread.start()

root.mainloop()
