"""
デバイス上でのオーディオ系の機器情報を表示する
出典 https://qiita.com/KENTAROSZK/items/8d82a495b7cffec69862
"""

import pyaudio

pa = pyaudio.PyAudio()
for i in range(pa.get_device_count()):
    print(pa.get_device_info_by_index(i))
    print()
pa.terminate()
