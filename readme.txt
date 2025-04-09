
# 1.Configure CORS in FastAPI (for development):
Add CORS middleware in your main.py to allow Vue dev server communication:
"""
    from fastapi.middleware.cors import CORSMiddleware
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8080"],  # Vue's default port
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
"""

# 2.Vue Project Structure:
Create a separate directory for your Vue project at the same level as your FastAPI project:
"""
    project-root/
    ├── frontend/      # Vue project
    │   ├── src/
    │   ├── public/
    │   └── ...
    ├── api/
    ├── main.py
    └── ...
"""

