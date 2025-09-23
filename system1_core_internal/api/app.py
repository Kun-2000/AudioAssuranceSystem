"""
AudioAssuranceSystem - 主 FastAPI 應用程式檔案
負責創建應用、掛載路由、設定中介軟體和服務靜態檔案
"""

import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings

from api import routes as http_routes
from api import websocket as websocket_routes

# --- 應用程式初始化 ---

app = FastAPI(
    title="Audio Assurance System",
    description="即時音訊品質保障與監控系統",
    version="1.0.0",
    debug=settings.DEBUG,
)

# --- 中介軟體 (Middleware) 設定 ---

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 路由 (Router) 掛載 ---

app.include_router(http_routes.router)
app.include_router(websocket_routes.router)


# --- 靜態檔案 (Static Files) 服務設定 ---

try:
    app.mount("/storage", StaticFiles(directory=settings.STORAGE_PATH), name="storage")
except RuntimeError:
    logging.warning("儲存目錄 %s 不存在，暫不掛載。", settings.STORAGE_PATH)

try:
    app.mount(
        "/call",
        StaticFiles(directory=settings.BASE_DIR / "web/call_app"),
        name="call_app",
    )
except RuntimeError:
    logging.warning("通話前端目錄 'web/call_app' 不存在，暫不掛載。")

try:
    app.mount(
        "/dashboard",
        StaticFiles(directory=settings.BASE_DIR / "web/dashboard_app"),
        name="dashboard_app",
    )
except RuntimeError:
    logging.warning("儀表板前端目錄 'web/dashboard_app' 不存在，暫不掛載。")


# --- 根目錄與健康檢查路由 ---


@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def root():
    """
    根目錄，提供一個簡單的導覽頁面，方便開發時切換不同的前端應用。
    """
    html_content = """
    <html>
        <head>
            <title>AudioAssuranceSystem</title>
            <style>
                body {
                    font-family: sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #f0f2f5;
                }
                .container { text-align: center; }
                .link-card {
                    background-color: white; padding: 2rem;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    margin: 1rem; text-decoration: none;
                    color: black; display: block;
                }
                .link-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 8px 12px rgba(0,0,0,0.15);
                    transition: all 0.2s ease-in-out;
                }
                h1 { margin-bottom: 2rem; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Welcome to AudioAssuranceSystem</h1>
                <div>
                    <a href="/call/index.html" class="link-card">
                        <h2>📞 Go to Call App</h2>
                    </a>
                    <a href="/dashboard/index.html" class="link-card">
                        <h2>📊 Go to Dashboard App</h2>
                    </a>
                </div>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health", tags=["System"])
async def health_check():
    """
    系統健康檢查端點，用於監控服務是否正常運行。
    """
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
