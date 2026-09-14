import os
from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import create_client, Client

# --- 보안 금고 열기 ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 금고에서 꺼낸 정보로 연결!
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()
#------------------------------------------------------------------------
# 기본 환영 주소
@app.get("/")
def read_root():
    return {"message": "텍사스 기상 및 전력 API 서버입니다."}

# 2. 진짜 데이터를 내어주는 새로운 창구 만들기!
@app.get("/api/forecast")
def get_texas_forecast():
    # Supabase의 'texas_forecast' 테이블에서 모든 데이터(*)를 시간순으로 가져오기
    # 실무 팁: 데이터가 너무 많을 수 있으니 최신 100개만(limit) 가져오도록 안전장치 설정
    response = supabase.table('texas_forecast').select("*").order('time').limit(100).execute()
    
    # DB에서 꺼낸 데이터를 바로 손님(브라우저)에게 던져줍니다.
    return {"data": response.data}