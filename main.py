import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from database import engine, Base
from routers import orders, work_results
from routers import data_summary
from routers.weather import router as weather_router
from middlewares.logging_middleware import LoggingMiddleware
from middlewares.jwt_middleware import JWTMiddleware
import os

# 로깅 설정 (환경변수 DEBUG가 '1'일 때 디버그 레벨로 동작)
log_level = logging.DEBUG if os.getenv("DEBUG", "0") == "1" else logging.INFO
logging.basicConfig(
    level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def debug_if_enabled(msg: str, *args, **kwargs) -> None:
    """
    logger.debug 호출을 더 효율적으로 하기 위한 헬퍼.
    - 문자열 포매팅은 logger.debug("... %s", value) 형태로 전달하면
      로그 레벨이 debug가 아닐 때 불필요한 포맷 연산을 피할 수 있다.
    - 무거운 연산이 필요한 경우 이 헬퍼를 사용하거나 직접
      logger.isEnabledFor(logging.DEBUG)로 감싸서 연산을 지연시킨다.
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(msg, *args, **kwargs)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="MES Copilot Demo")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],  # 허용할 도메인
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)

# Add JWT middleware
# app.add_middleware(JWTMiddleware)


app.include_router(orders.router)
app.include_router(work_results.router)
# include data router
app.include_router(data_summary.router)
app.include_router(weather_router)


@app.get("/")
def read_root():
    # 예시: logger.debug 호출을 더 효율적으로 변경
    # 잘못된 예: f-string 또는 .format을 사용하면 항상 문자열이 계산됨
    # logger.debug(f"Root called, unused_var={unused_var}")  # 비효율적
    #
    # 권장 예1 (지연 포매팅 — 더 효율적):
    # logger.debug("Root called, unused_var=%s", unused_var)
    #
    # 권장 예2 (무거운 연산이 있을 때):
    # if logger.isEnabledFor(logging.DEBUG):
    #     heavy = expensive_computation()
    #     logger.debug("Computed heavy=%s", heavy)
    #
    # 또는 위 헬퍼 사용:
    debug_if_enabled("Root called, unused_var=%s", unused_var)

    return {"message": "MES Copilot API is running"}


unused_var = 10
