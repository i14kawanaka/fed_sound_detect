# coding:utf-8

import os
import pandas as pd
from tqdm import tqdm
import librosa
import numpy as np
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchvision.models import resnet34
import time 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import sounddevice as sd
import wave
# 学習済みのResNetをダウンロード
resnet_model = resnet34(pretrained=True)
# ResNetの構造がわからない場合はResNetの構造を出力して確認しましょう。
# 最初の畳み込みのチャネル3をチャネル1に変更する
resnet_model.conv1 = nn.Conv2d(1, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)

# 最後の層の次元を今回のカテゴリ数に変更する
resnet_model.fc = nn.Linear(512,50)

resnet_model.load_state_dict(torch.load('./epoch50.pt'))
resnet_model.eval()

loss_function = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(resnet_model.parameters(), lr=2e-4)

cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.collection(u'users').document(u'PredResult')
doc_ref2 = db.collection(u'users2').document(u'CrowdResult')

cur = 0
prev = 0
crowd = 0

FILE_NAME = './test.wav'  # 保存するファイル名
wave_length = 5  # 録音する長さ（秒）
sample_rate = 16000  # サンプリング周波数

while True:
      start = time.time()


       # 録音開始（wave_length秒間録音。wait で録音し終わるまで待つ）
      print("Recoding Start")
      data = sd.rec(int(wave_length * sample_rate), sample_rate, channels=1)
      sd.wait()
      print("Recodeing Stop")

      # ノーマライズ。量子化ビット16bitで録音するので int16 の範囲で最大化する\
      aaa = 0
      for i in range(10):
            if(aaa < np.mean(np.abs(data[i*8000:i*8000+7999]))):
                  aaa = np.mean(np.abs(data[i*8000:i*8000+7999]))
      if(aaa < 0.02):
            crowd = 0
      elif(aaa >= 0.02 and aaa < 0.03):
            crowd = 1
      elif(aaa >= 0.03 and aaa < 0.04):
            crowd = 2
      elif(aaa >= 0.04 and aaa < 0.05):
            crowd = 3
      elif(aaa >= 0.05):
            crowd = 4

      data = data / data.max() * np.iinfo(np.int16).max

      # float -> int
      data = data.astype(np.int16)

      # ファイル保存
      with wave.open(FILE_NAME, mode='wb') as wb:
            wb.setnchannels(1)  # モノラル
            wb.setsampwidth(2)  # 16bit=2byte
            wb.setframerate(sample_rate)
            wb.writeframes(data.tobytes())  # バイト列に変換

      waveform, sr = librosa.load("./test.wav")

      feature_melspec = librosa.feature.melspectrogram(y=waveform, sr=sr)
      feature_melspec_db = librosa.power_to_db(feature_melspec, ref=np.max)
      x = torch.from_numpy(feature_melspec_db.astype(np.float32)).clone()
      x = x.unsqueeze(0)
      x = x.unsqueeze(0)

      with torch.no_grad():
            est_label = resnet_model(x) #noisyの振幅スペクトルをモデルに入れる
      _, y_pred = torch.max(est_label, 1)
      tmp = y_pred.item()
      if(tmp < 10 or tmp == 13 or tmp == 14):
            cur = 0
      elif(tmp == 15 or tmp ==10):
            cur = 1
      elif(tmp == 12):
            cur = 2
      elif(tmp == 16):
            cur = 3
      elif(tmp == 11):
            cur = 4
      elif(tmp == 19):
            cur = 5
      elif((tmp > 19 and tmp < 31) or tmp == 33 or tmp == 34 or tmp == 39 or tmp == 17 or tmp == 18):
            cur = 6
      elif(tmp == 31 or tmp == 32):
            cur = 7
      elif(tmp > 34 and tmp < 39):
            cur = 8
      else:
            cur = 9

      doc_ref2.update({u'Crowd':crowd})
      doc_ref.update({u'Cur': cur})
      doc_ref.update({u'Pre': prev})
      prev = cur
      print("Crowd Level",crowd)
      print("Recognition Result",cur)
      print("Wait Time")

      while True:
            if((time.time() - start) > 10):
                  break
            else:
                  time.sleep(0.5)
      
