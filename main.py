import os
from src.models.permission import populate_permissions
from src.db.database import Base, engine
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from src.api.token import router as token_router
from src.api.admins import router as admins_router
from src.api.roles import router as roles_router
from src.api.profile import router as profile_router
from src.api.permissions import router as permissions_router
from src.api.auth import router as auth_router
from src.api.api_keys import router as api_keys_router
from src.api.external_token import router as external_token_router 
from src.db.database import  get_db
from sqlalchemy.orm import Session
from src.workers.tasks import send_otp_email_task
from fastapi.middleware.cors import CORSMiddleware
from elasticapm.contrib.starlette import ElasticAPM, make_apm_client
origins = [
    os.getenv("FRONTEND_URL") if os.getenv("FRONTEND_URL") else "http://0.0.0.0:3000",
]



required_env_vars = [
    "DB_USER",
    "DB_PASS",
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "MAIL_USERNAME",
    "MAIL_PASSWORD",
    "MAIL_FROM",
    "MAIL_SERVER",
    "MAIL_PORT",
    "BASE_URL",
    "FRONTEND_URL",
    "CELERY_BROKER_URL",
]

missing = [var for var in required_env_vars if not os.getenv(var)]

if missing:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")
app = FastAPI(title="MiVerify API", redirect_slashes=False)
external_app = FastAPI(title="MiVerify External API", openapi_prefix="/external", redirect_slashes=False)

apm = make_apm_client({
    'SERVICE_NAME': os.getenv("ELASTIC_SERVICE_NAME", "FAST_API_BASE"),
    'SECRET_TOKEN': os.getenv("ELASTIC_SECRET_TOKEN", "xxxxxxxxx"),
    'SERVER_URL':   os.getenv("ELASTIC_SERVER_URL"),
})
app.add_middleware(ElasticAPM,client=apm)
external_app.add_middleware(ElasticAPM,client=apm)
app.add_middleware(
     CORSMiddleware,
    allow_origins=origins,  # OR use ["*"] for all (not recommended in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
external_app.add_middleware(
     CORSMiddleware,
    allow_origins=origins,  # OR use ["*"] for all (not recommended in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"]
)


app.include_router(token_router)
# app.include_router(accounts_router)
app.include_router(admins_router)
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(profile_router)





app.include_router(auth_router)
app.include_router(api_keys_router)
external_app.include_router(external_token_router)
app.mount("/external", external_app)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
@app.get("/")
def index():
    return {"message": "Hello World"}

@app.get("/up")
@app.get("/health")
def health_check():
    return {"status": "ok"}
Base.metadata.create_all(bind=engine)
db = next(get_db())
populate_permissions(db)

@app.on_event("startup")
async def warm_up_dependencies():

    try:
        db: Session = next(get_db())
        db.execute("SELECT 1")
    except Exception:
        pass
    try:
        send_otp_email_task.delay(admin_id=-1, otp="000000", magic_token="warmup")
    except Exception:
        pass

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=os.getenv("ENVIRONMENT") != "production")

