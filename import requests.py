import os
from dotenv import load_dotenv
import requests
import pandas as pd
from supabase import create_client, Client

# --- 1. 보안 금고 열어서 모든 비밀정보 꺼내기 ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
EIA_API_KEY = os.getenv("EIA_API_KEY")
MY_EMAIL = os.getenv("MY_EMAIL")

# DB 연결
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. API 호출 (Extract) ---
# f-string을 써서 금고에서 꺼낸 이메일과 API 키를 안전하게 쏙쏙 집어넣습니다.
headers = {'User-Agent': f'texas_project ({MY_EMAIL})'}
nws_url = "https://api.weather.gov/gridpoints/EWX/155,90/forecast/hourly" 
eia_url = f"https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key={EIA_API_KEY}&data[]=value&facets[respondent][]=ERCO&frequency=hourly"

nws_response = requests.get(nws_url, headers=headers).json()
eia_response = requests.get(eia_url).json()

print("데이터 추출 완료! 가공(Transform)을 시작합니다...\n")

# 2. 날씨 데이터 가공 (NWS)
# 복잡한 JSON에서 'periods' 안에 있는 시간, 온도, 날씨 상태만 뽑아옵니다.
weather_list = nws_response['properties']['periods']
df_weather = pd.DataFrame(weather_list)[['startTime', 'temperature', 'shortForecast']]

# 시간 형식을 통일하기 위해 Pandas의 datetime으로 변환 (UTC 기준)
df_weather['time'] = pd.to_datetime(df_weather['startTime'], utc=True)
# 필요 없는 기존 startTime 컬럼 삭제
df_weather = df_weather.drop(columns=['startTime'])

# 3. 전력망 데이터 가공 (EIA)
# JSON에서 'response' -> 'data' 안에 있는 시간과 전력 수요량만 뽑아옵니다.
power_list = eia_response['response']['data']
df_power = pd.DataFrame(power_list)[['period', 'value']]

df_power['time'] = pd.to_datetime(df_power['period'], utc=True)
df_power = df_power.rename(columns={'value': 'electricity_demand_MWh'})
df_power = df_power.drop(columns=['period'])

# 4. 두 데이터 병합 (Merge)
# 'time'이라는 공통된 시간을 기준으로 두 표를 하나로 합칩니다.
df_merged = pd.merge(df_weather, df_power, on='time', how='inner')

# 5. 최종 데이터 정제 (중복 제거 및 텍사스 시간대로 변환)
# 중복된 시간대의 데이터가 있다면 첫 번째 것만 남기고 제거
df_merged = df_merged.drop_duplicates(subset=['time'], keep='first')

# UTC 시간을 텍사스 현지 시간(Central Time)으로 변환
df_merged['time'] = df_merged['time'].dt.tz_convert('America/Chicago')

# 결과 확인
print("성공적으로 하나로 병합된 최종 데이터프레임 (상위 5개):")
print("-" * 70)
print(df_merged.head())

#----------------------------------------------------------------------------
print("\n데이터 적재(Load)를 시작합니다...")

# 1. Supabase 연결 설정
SUPABASE_URL = "https://pkxmfcrkafyuwumlxwrn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBreG1mY3JrYWZ5dXd1bWx4d3JuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4OTI1MDA3OCwiZXhwIjoyMTA0ODI2MDc4fQ._iHcmYI78KAEJvxcXU7JfWOVpQNlDeDSg5Z-AIJ5pqc"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. DataFrame을 딕셔너리 리스트(JSON 형태)로 변환 (DB에 넣기 위해)
# UTC 기준으로 되돌려서 저장하는 것이 DB 관리의 정석입니다.
df_merged['time'] = df_merged['time'].dt.tz_convert('UTC')

# DB 컬럼명에 맞게 이름 변경
df_to_db = df_merged.rename(columns={
    'shortForecast': 'weather_condition',
    'electricity_demand_MWh': 'electricity_demand_mwh'
})
# 시간 데이터를 문자열(ISO 포맷)로 변환
df_to_db['time'] = df_to_db['time'].astype(str)

records = df_to_db.to_dict(orient='records')

# 3. Supabase에 데이터 삽입(Upsert)
try:
    # upsert: 같은 시간(time) 데이터가 이미 있으면 업데이트, 없으면 새로 삽입
    response = supabase.table('texas_forecast').upsert(records).execute()
    print("✅ 성공! Supabase 데이터베이스에 완벽하게 적재되었습니다.")
except Exception as e:
    print("❌ 에러 발생:", e)