# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import fastapi.exceptions

# Import LangGraph components
from langgraph_sdk import get_client
from agent.graph import graph

# Define the FastAPI app
app = FastAPI()

# Add CORS middleware with more permissive settings for Docker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Docker deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add health endpoint
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "deep-research-app"}

# Serve public assets like images
@app.get("/{filename}")
async def serve_public_assets(filename: str):
    """Serve public assets like images."""
    # Only serve known image extensions to avoid conflicts
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp'}
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        # Not an image file, let other routes handle it
        raise fastapi.exceptions.HTTPException(status_code=404, detail="File not found")
    
    container_public_path = pathlib.Path("/deps/frontend/public")
    if container_public_path.exists():
        file_path = container_public_path / filename
    else:
        # Development path
        dev_public_path = pathlib.Path(__file__).parent.parent.parent / "frontend/public"
        file_path = dev_public_path / filename
    
    if file_path.exists() and file_path.is_file():
        return fastapi.responses.FileResponse(file_path)
    else:
        raise fastapi.exceptions.HTTPException(status_code=404, detail="File not found")

# Redirect root to frontend
@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/app/", status_code=302)

# Add threads endpoint



def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    # Check if we're in a Docker container and use the container path
    container_build_path = pathlib.Path("/deps/frontend/dist")
    container_public_path = pathlib.Path("/deps/frontend/public")
    if container_build_path.exists():
        build_path = container_build_path
        public_path = container_public_path
    else:
        build_path = pathlib.Path(__file__).parent.parent.parent / build_dir
        public_path = pathlib.Path(__file__).parent.parent.parent / "frontend/public"
    
    static_files_path = build_path / "assets"  # Vite uses 'assets' subdir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    react = FastAPI(openapi_url="")
    
    # Mount static assets from Vite build
    react.mount(
        "/assets", StaticFiles(directory=static_files_path), name="static_assets"
    )
    
    # Mount public assets (images, etc.) at root level
    if public_path.exists():
        react.mount(
            "/", StaticFiles(directory=public_path, html=False), name="public_assets"
        )

    @react.get("/{path:path}")
    async def handle_catch_all(request: Request, path: str):
        fp = build_path / path
        if not fp.exists() or not fp.is_file():
            fp = build_path / "index.html"
        return fastapi.responses.FileResponse(fp)

    return react


# Add frontend routes directly to the main app instead of mounting
frontend_router = create_frontend_router()

# Add the frontend routes to the main app
@app.get("/app/{path:path}")
async def serve_frontend(request: Request, path: str):
    """Serve the React frontend files."""
    # Check if we're in a Docker container and use the container path
    container_build_path = pathlib.Path("/deps/frontend/dist")
    if container_build_path.exists():
        build_path = container_build_path
    else:
        build_path = pathlib.Path(__file__).parent.parent.parent / "../frontend/dist"
    
    # Handle root path
    if path == "" or path == "/":
        fp = build_path / "index.html"
    else:
        fp = build_path / path
        
    # If file doesn't exist, serve index.html for SPA routing
    if not fp.exists() or not fp.is_file():
        fp = build_path / "index.html"
        
    return fastapi.responses.FileResponse(fp)
