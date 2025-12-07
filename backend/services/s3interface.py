"""
S3 Storage Interface

Provides an abstraction layer for file storage operations that supports
both local filesystem and AWS S3 storage backends.

Usage:
    from services.s3interface import get_storage

    storage = get_storage()  # Returns S3Storage or LocalStorage based on env

    # Save files
    url = storage.save_binary("path/to/file.png", binary_data)
    url = storage.save_text("path/to/file.html", html_content)

    # Get URLs for serving
    url = storage.get_url("path/to/file.png")
"""

import os
import io
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

load_dotenv()

class StorageInterface(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def save_binary(self, path: str, data: bytes, content_type: Optional[str] = None) -> str:
        """
        Save binary data to storage.

        Args:
            path: Relative path for the file (e.g., "projects/20231123/1/assets/image.png")
            data: Binary data to save
            content_type: Optional MIME type (e.g., "image/png")

        Returns:
            URL or path to access the saved file
        """
        pass

    @abstractmethod
    def save_text(self, path: str, content: str, content_type: Optional[str] = None) -> str:
        """
        Save text content to storage.

        Args:
            path: Relative path for the file (e.g., "projects/20231123/1/index.html")
            content: Text content to save
            content_type: Optional MIME type (e.g., "text/html")

        Returns:
            URL or path to access the saved file
        """
        pass

    @abstractmethod
    def get_url(self, path: str) -> str:
        """
        Get the public URL for a stored file.

        Args:
            path: Relative path to the file

        Returns:
            Public URL to access the file
        """
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            path: Relative path to check

        Returns:
            True if the file exists, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, path: str) -> bool:
        """
        Delete a file from storage.

        Args:
            path: Relative path to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    def list_files(self, prefix: str) -> list[str]:
        """
        List all files under a given prefix/directory.

        Args:
            prefix: Path prefix to list (e.g., "projects/20231123/1/")

        Returns:
            List of file paths
        """
        pass

    @abstractmethod
    def copy(self, source_path: str, dest_path: str) -> str:
        """
        Copy a file within storage.

        Args:
            source_path: Source file path
            dest_path: Destination file path

        Returns:
            URL or path to the copied file
        """
        pass

    @abstractmethod
    def read_binary(self, path: str) -> Optional[bytes]:
        """
        Read binary data from storage.

        Args:
            path: Relative path to the file

        Returns:
            Binary data or None if not found
        """
        pass

    @abstractmethod
    def read_text(self, path: str) -> Optional[str]:
        """
        Read text content from storage.

        Args:
            path: Relative path to the file

        Returns:
            Text content or None if not found
        """
        pass


class S3Storage(StorageInterface):
    """AWS S3 storage backend."""

    def __init__(
        self,
        bucket_name: str,
        region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        custom_endpoint: Optional[str] = None,
        cloudfront_domain: Optional[str] = None,
    ):
        """
        Initialize S3 storage.

        Args:
            bucket_name: S3 bucket name
            region: AWS region (default: us-east-1)
            aws_access_key_id: AWS access key (uses env/IAM if not provided)
            aws_secret_access_key: AWS secret key (uses env/IAM if not provided)
            custom_endpoint: Custom S3-compatible endpoint (for MinIO, R2, etc.)
            cloudfront_domain: Optional CloudFront domain for serving files
        """
        self.bucket_name = bucket_name
        self.region = region
        self.cloudfront_domain = cloudfront_domain

        # Configure boto3 client
        client_kwargs = {
            "service_name": "s3",
            "region_name": region,
        }

        if aws_access_key_id and aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = aws_access_key_id
            client_kwargs["aws_secret_access_key"] = aws_secret_access_key

        if custom_endpoint:
            client_kwargs["endpoint_url"] = custom_endpoint

        self.client = boto3.client(**client_kwargs)
        self.bucket_name = bucket_name

    def _get_content_type(self, path: str, provided_type: Optional[str] = None) -> str:
        """Determine content type from file extension or provided type."""
        if provided_type:
            return provided_type

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
            ".mp4": "video/mp4",
            ".webm": "video/webm",
        }
        return content_types.get(extension, "application/octet-stream")

    def save_binary(self, path: str, data: bytes, content_type: Optional[str] = None) -> str:
        """Save binary data to S3."""
        content_type = self._get_content_type(path, content_type)

        self.client.put_object(
            Bucket=self.bucket_name,
            Key=path,
            Body=data,
            ContentType=content_type,
        )

        return self.get_url(path)

    def save_text(self, path: str, content: str, content_type: Optional[str] = None) -> str:
        """Save text content to S3."""
        content_type = self._get_content_type(path, content_type)

        self.client.put_object(
            Bucket=self.bucket_name,
            Key=path,
            Body=content.encode("utf-8"),
            ContentType=content_type,
        )

        return self.get_url(path)

    def get_url(self, path: str) -> str:
        """Get the public URL for an S3 object."""
        if self.cloudfront_domain:
            return f"https://{self.cloudfront_domain}/{path}"
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{path}"

    def exists(self, path: str) -> bool:
        """Check if an object exists in S3."""
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=path)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def delete(self, path: str) -> bool:
        """Delete an object from S3."""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=path)
            return True
        except ClientError:
            return False

    def list_files(self, prefix: str) -> list[str]:
        """List all objects under a prefix in S3."""
        files = []
        paginator = self.client.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
            if "Contents" in page:
                files.extend([obj["Key"] for obj in page["Contents"]])

        return files

    def copy(self, source_path: str, dest_path: str) -> str:
        """Copy an object within S3."""
        self.client.copy_object(
            Bucket=self.bucket_name,
            CopySource={"Bucket": self.bucket_name, "Key": source_path},
            Key=dest_path,
        )
        return self.get_url(dest_path)

    def read_binary(self, path: str) -> Optional[bytes]:
        """Read binary data from S3."""
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=path)
            return response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise

    def read_text(self, path: str) -> Optional[str]:
        """Read text content from S3."""
        data = self.read_binary(path)
        if data is None:
            return None
        return data.decode("utf-8")

    def upload_directory(self, local_dir: str, s3_prefix: str) -> list[str]:
        """
        Upload an entire local directory to S3.

        Args:
            local_dir: Local directory path
            s3_prefix: S3 prefix/path for the uploaded files

        Returns:
            List of uploaded file URLs
        """
        uploaded = []
        local_path = Path(local_dir)

        for file_path in local_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(local_path)
                s3_path = f"{s3_prefix}/{relative_path}".replace("\\", "/")

                with open(file_path, "rb") as f:
                    url = self.save_binary(s3_path, f.read())
                    uploaded.append(url)

        return uploaded


class LocalStorage(StorageInterface):
    """Local filesystem storage backend (for development/backwards compatibility)."""

    def __init__(self, base_path: str = ".", base_url: str = ""):
        """
        Initialize local storage.

        Args:
            base_path: Base directory for storing files
            base_url: Base URL for serving files (e.g., "http://localhost:8001")
        """
        self.base_path = Path(base_path)
        self.base_url = base_url.rstrip("/")

    def _full_path(self, path: str) -> Path:
        """Get full filesystem path."""
        return self.base_path / path

    def save_binary(self, path: str, data: bytes, content_type: Optional[str] = None) -> str:
        """Save binary data to local filesystem."""
        full_path = self._full_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(data)

        print(f"File saved to: {full_path}")
        return self.get_url(path)

    def save_text(self, path: str, content: str, content_type: Optional[str] = None) -> str:
        """Save text content to local filesystem."""
        full_path = self._full_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"File saved to: {full_path}")
        return self.get_url(path)

    def get_url(self, path: str) -> str:
        """Get URL for a local file."""
        if self.base_url:
            return f"{self.base_url}/{path}"
        return f"/{path}"

    def exists(self, path: str) -> bool:
        """Check if a file exists locally."""
        return self._full_path(path).exists()

    def delete(self, path: str) -> bool:
        """Delete a local file."""
        try:
            self._full_path(path).unlink()
            return True
        except FileNotFoundError:
            return False

    def list_files(self, prefix: str) -> list[str]:
        """List all files under a directory."""
        full_path = self._full_path(prefix)
        if not full_path.exists():
            return []

        files = []
        for file_path in full_path.rglob("*"):
            if file_path.is_file():
                relative = file_path.relative_to(self.base_path)
                files.append(str(relative).replace("\\", "/"))

        return files

    def copy(self, source_path: str, dest_path: str) -> str:
        """Copy a local file."""
        import shutil

        source = self._full_path(source_path)
        dest = self._full_path(dest_path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source, dest)
        return self.get_url(dest_path)

    def read_binary(self, path: str) -> Optional[bytes]:
        """Read binary data from local filesystem."""
        try:
            with open(self._full_path(path), "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def read_text(self, path: str) -> Optional[str]:
        """Read text content from local filesystem."""
        try:
            with open(self._full_path(path), "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def copy_directory(self, source_dir: str, dest_dir: str) -> bool:
        """
        Copy an entire directory locally.

        Args:
            source_dir: Source directory path (can be absolute or relative)
            dest_dir: Destination directory path relative to base_path

        Returns:
            True if successful
        """
        import shutil
        import errno

        dest = self._full_path(dest_dir)
        dest.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copytree(source_dir, dest)
            return True
        except OSError as err:
            if err.errno == errno.ENOTDIR:
                shutil.copy2(source_dir, dest)
                return True
            raise


# Storage instance singleton
_storage_instance: Optional[StorageInterface] = None


def get_storage() -> StorageInterface:
    """
    Get the configured storage backend.

    Uses environment variables to determine which backend to use:
    - STORAGE_BACKEND: "s3" or "local" (default: "local")
    - S3_BUCKET_NAME: Required for S3
    - S3_REGION: AWS region (default: "us-east-1")
    - AWS_ACCESS_KEY_ID: AWS access key
    - AWS_SECRET_ACCESS_KEY: AWS secret key
    - S3_ENDPOINT: Custom endpoint for S3-compatible services
    - CLOUDFRONT_DOMAIN: Optional CloudFront distribution domain
    - LOCAL_STORAGE_PATH: Base path for local storage (default: ".")
    - LOCAL_STORAGE_URL: Base URL for local file serving

    Returns:
        Configured StorageInterface instance
    """
    global _storage_instance

    if _storage_instance is not None:
        return _storage_instance

    backend = os.getenv("STORAGE_BACKEND", "local").lower()

    if backend == "s3":
        bucket_name = os.getenv("S3_BUCKET_NAME")
        if not bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is required for S3 storage")

        _storage_instance = S3Storage(
            bucket_name=bucket_name,
            region=os.getenv("S3_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            custom_endpoint=os.getenv("S3_ENDPOINT"),
            cloudfront_domain=os.getenv("CLOUDFRONT_DOMAIN"),
        )
    else:
        _storage_instance = LocalStorage(
            base_path=os.getenv("LOCAL_STORAGE_PATH", "."),
            base_url=os.getenv("LOCAL_STORAGE_URL", ""),
        )

    return _storage_instance


def reset_storage():
    """Reset the storage singleton (useful for testing)."""
    global _storage_instance
    _storage_instance = None
