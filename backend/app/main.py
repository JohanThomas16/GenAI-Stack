from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from GenAI Stack!", "status": "working"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# import time

# app = FastAPI(
#     title="GenAI Stack API",
#     description="No-Code Workflow Builder API",
#     version="1.0.0",
#     docs_url="/docs",
#     redoc_url="/redoc"
# )

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, specify your frontend URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/")
# async def root():
#     return {
#         "message": "GenAI Stack API is running!",
#         "version": "1.0.0",
#         "status": "healthy",
#         "timestamp": time.time()
#     }

# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "version": "1.0.0",
#         "timestamp": time.time(),
#         "database": "connected",
#         "services": {
#             "api": "running",
#             "database": "connected",
#             "vector_store": "available"
#         }
#     }

# @app.get("/api/v1/test")
# async def test_endpoint():
#     return {"test": "API is working", "endpoint": "/api/v1/test"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
