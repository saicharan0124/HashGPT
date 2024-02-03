from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.routes import user, core
from app.database import db_config

# Create a FastAPI app instance
app = FastAPI()

# Include routers for notes and authentication
app.include_router(core.router, prefix="/api/core", tags=["core"])
app.include_router(user.router, prefix="/api/auth", tags=["user"])

# Call the 'init' function on application startup
@app.on_event("startup")
async def startup_event():
    print("Initializing database")
    posts_collection, users_collection = db_config.init_db()

# Redirect '/' to '/docs'
@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse("/docs")

# Allow all origins with CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, replace with specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
