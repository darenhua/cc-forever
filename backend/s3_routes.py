"""
S3 Proxy Routes

Provides endpoints to serve files from S3 storage, mirroring the functionality
of FastAPI's StaticFiles for local storage.

Endpoints:
    GET /s3/projects/{path} - Serve project files from S3
    GET /s3/cartridge_arts/{path} - Serve cartridge art files from S3
    GET /s3/assets/{path} - Serve asset files from S3
    POST /s3/test/upload - Upload a test file to S3
    GET /s3/test/{filename} - Retrieve a test file from S3
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pathlib import Path

from services.s3interface import get_storage, S3Storage

s3_router = APIRouter(prefix="/s3", tags=["s3"])


def get_content_type(path: str) -> str:
    """Determine content type from file extension."""
    extension = Path(path).suffix.lower()
    content_types = {
        ".html": "text/html",
        ".htm": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".json": "application/json",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
        ".ico": "image/x-icon",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".txt": "text/plain",
        ".xml": "application/xml",
        ".pdf": "application/pdf",
    }
    return content_types.get(extension, "application/octet-stream")


def serve_s3_file(prefix: str, path: str) -> Response:
    """
    Fetch a file from S3 and return it as a Response.

    Args:
        prefix: The S3 prefix/directory (e.g., "projects", "cartridge_arts")
        path: The path within the prefix

    Returns:
        Response with file content and appropriate content-type
    """
    storage = get_storage()

    if not isinstance(storage, S3Storage):
        raise HTTPException(
            status_code=404,
            detail="S3 storage not configured. Use local static file mounts instead."
        )

    full_path = f"{prefix}/{path}"
    data = storage.read_binary(full_path)

    if data is None:
        raise HTTPException(status_code=404, detail=f"File not found: {full_path}")

    content_type = get_content_type(path)
    return Response(content=data, media_type=content_type)


# =============================================================================
# S3 Proxy Endpoints (mirror StaticFiles functionality)
# =============================================================================

@s3_router.get("/projects/{path:path}")
async def get_s3_project_file(path: str):
    """
    Serve a project file from S3.

    Mirrors: app.mount("/projects", StaticFiles(directory="projects", html=True))

    Example: GET /s3/projects/20231123/1/index.html
    """
    return serve_s3_file("projects", path)


@s3_router.get("/cartridge_arts/{path:path}")
async def get_s3_cartridge_art(path: str):
    """
    Serve a cartridge art file from S3.

    Mirrors: app.mount("/cartridge_arts", StaticFiles(directory="cartridge_arts"))

    Example: GET /s3/cartridge_arts/20231123/1/cover.png
    """
    return serve_s3_file("cartridge_arts", path)


@s3_router.get("/assets/{path:path}")
async def get_s3_asset(path: str):
    """
    Serve an asset file from S3.

    Mirrors: app.mount("/assets", StaticFiles(directory="assets"))

    Example: GET /s3/assets/logo.png
    """
    return serve_s3_file("assets", path)


# =============================================================================
# Test Endpoints
# =============================================================================

@s3_router.post("/test/upload")
async def test_upload():
    """
    Upload an empty manifest.json to S3 to initialize the projects folder.

    Returns:
        URL of the uploaded file and storage info
    """
    storage = get_storage()

    if not isinstance(storage, S3Storage):
        raise HTTPException(
            status_code=400,
            detail="S3 storage not configured. Set STORAGE_BACKEND=s3 in environment."
        )

    manifest_path = "projects/manifest.json"
    content = "[]"

    url = storage.save_text(manifest_path, content)

    return {
        "success": True,
        "message": "Empty manifest.json uploaded successfully",
        "s3_path": manifest_path,
        "url": url,
        "bucket": storage.bucket_name,
        "retrieve_via": f"/s3/{manifest_path}"
    }


@s3_router.get("/test/{filename}")
async def test_retrieve(filename: str):
    """
    Retrieve a test file from S3.

    Use this after /test/upload to verify roundtrip works.
    """
    return serve_s3_file("_test", filename)


@s3_router.get("/test/check")
async def test_check():
    """
    Check S3 connectivity and configuration.

    Returns storage configuration and connection status.
    """
    storage = get_storage()

    if not isinstance(storage, S3Storage):
        return {
            "storage_type": "local",
            "s3_configured": False,
            "message": "Using local storage. Set STORAGE_BACKEND=s3 to use S3."
        }

    # Try to list files to verify connection
    try:
        files = storage.list_files("_test/")
        return {
            "storage_type": "s3",
            "s3_configured": True,
            "bucket": storage.bucket_name,
            "region": storage.region,
            "cloudfront_domain": storage.cloudfront_domain,
            "connection": "ok",
            "test_files": files[:10] if files else []
        }
    except Exception as e:
        return {
            "storage_type": "s3",
            "s3_configured": True,
            "bucket": storage.bucket_name,
            "connection": "error",
            "error": str(e)
        }
