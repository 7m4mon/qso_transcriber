# QSO Transcriber
## AIによる音声認識で交信内容をテキスト化しよう！
2024 7M4MON

* 概要
  * Open AI社が提供する文字起こしAPI `Wisper` を使用して、IC-9700で受信した交信内容をテキスト化します。


  
  ![](https://github.com/7m4mon/qso_transcriber/blob/main/one_day_430_main_ch.png)  


* スケルチ検出ケーブル
  * スケルチ信号を CTS に、パワーオン信号を DSR に接続します。
  ![](https://github.com/7m4mon/qso_transcriber/blob/main/cable_sch.png)  
  ![](https://github.com/7m4mon/qso_transcriber/blob/main/cable_photo.jpg)  
  

* 前準備
  * APIキーをシステムの環境変数の `OPENAI_API_KEY` に追加します。
  * IC-9700 に、スケルチ検出ケーブルとオーディオ用のUSBケーブルを接続します。
  * オーディオデバイスのインデックスを `look_for_audio_input.py` で調べます。
  * COMポートやオーディオデバイスのインデックスなどを `settings.json` に記述します。
  * ffmpeg をインストールして、その `bin` フォルダにPATHを通しておきます。


* プログラムの流れ
  * プログラムを開始すると、設定ファイルから各設定をロードし、シリアルポートを開きます。
  * 無線機が信号を受信してスケルチが開いたら録音を開始します。スケルチが閉じたら音声ファイルを保存してmp3形式に圧縮します。
  * 圧縮した音声ファイルを Wisper API に渡して文字起こしした結果を得ます。
  * 得られた結果をGUI上に表示すると同時にテキストファイルに保存します。
  * プログラムはTKのGUIとは別スレッドで処理しています。

    ![](https://github.com/7m4mon/qso_transcriber/blob/main/qso_transcriber_flow_chart.png)  
---

* 余談  
  このようなLLMをローカルで動かす場合、10GB以上のRAMを積んだ中級以上のグラフィックボードが必要なようですが、結構なお値段なので、アマチュアが遊ぶのだったらクラウドサービスをありがたく利用させていただくのがお手軽ですね。  
  逆に外部に対する秘匿性や機密性が必要な企業は、社内に一つサーバーを用意するといろいろと捗るのではないでしょうか。
