import FinanceDataReader as fdr
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from datetime import datetime, timedelta

# 주식 데이터 불러오기 (예시로 삼성전자 주가)
stock_code = '005930'  # 삼성전자
start_date = '2020-01-01'

# 현재 날짜 가져오기
current_date = datetime.now().strftime('%Y-%m-%d')

# end_date 설정 (현재 날짜로 설정)
end_date = current_date

df = fdr.DataReader(stock_code, start_date, end_date)

# 종가 데이터만 사용
data = df['Close'].values.reshape(-1, 1)

# 다음날 상승 여부 레이블 생성
df['Next_Day_Close'] = df['Close'].shift(-1)
df['Price_Up'] = np.where(df['Close'] < df['Next_Day_Close'], 1, 0)

# 데이터 전처리
scaler = MinMaxScaler(feature_range=(0, 1))
data_scaled = scaler.fit_transform(data)

# 학습 데이터 생성
look_back = 10  # 몇일 전 데이터를 기반으로 예측할 것인지
X, y = [], []

for i in range(len(data_scaled) - look_back):
    X.append(data_scaled[i:(i + look_back), 0])
    y.append(df['Price_Up'].iloc[i + look_back])

X, y = np.array(X), np.array(y)
X = np.reshape(X, (X.shape[0], X.shape[1], 1))

# 데이터를 학습 세트와 테스트 세트로 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# LSTM 모델 생성
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)))
model.add(LSTM(units=50))
model.add(Dense(units=1, activation='sigmoid'))  # 시그모이드 활성화 함수 사용

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 모델 학습
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

# 모델 평가
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Loss: {loss}, Test Accuracy: {accuracy}")

# 현재까지의 데이터로 다음날 종가 상승 여부 예측
last_data = data_scaled[-look_back:].reshape(1, -1, 1)
prediction = model.predict(last_data)

# 예측 결과 출력
if prediction[0, 0] > 0.5:
    print("다음날 종가가 상승할 것으로 예측됩니다.")
else:
    print("다음날 종가가 하락할 것으로 예측됩니다.")