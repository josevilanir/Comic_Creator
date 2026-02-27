"""
S3Service — wrapper boto3 para S3 e S3-compatíveis (Cloudflare R2, MinIO).

Ativado quando a variável de ambiente S3_BUCKET está definida.
Compatível com Cloudflare R2 via S3_ENDPOINT_URL.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config.settings import Config


class S3Service:
    def __init__(self, config: "Config"):
        import boto3

        self.bucket = config.S3_BUCKET
        self.presigned_expiry = config.S3_PRESIGNED_EXPIRY

        self._client = boto3.client(
            "s3",
            endpoint_url=config.S3_ENDPOINT_URL or None,
            aws_access_key_id=config.S3_ACCESS_KEY,
            aws_secret_access_key=config.S3_SECRET_KEY,
            region_name=config.S3_REGION,
        )

    # ── Upload ─────────────────────────────────────────────────────────────────

    def upload_file(self, local_path: str, key: str, content_type: str = "") -> None:
        extra = {"ContentType": content_type} if content_type else {}
        self._client.upload_file(local_path, self.bucket, key, ExtraArgs=extra)

    def upload_fileobj(self, fileobj, key: str, content_type: str = "") -> None:
        extra = {"ContentType": content_type} if content_type else {}
        self._client.upload_fileobj(fileobj, self.bucket, key, ExtraArgs=extra)

    # ── Delete ─────────────────────────────────────────────────────────────────

    def delete_object(self, key: str) -> None:
        self._client.delete_object(Bucket=self.bucket, Key=key)

    def delete_prefix(self, prefix: str) -> None:
        """Deleta todos os objetos cujo key começa com prefix."""
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            objects = [{"Key": o["Key"]} for o in page.get("Contents", [])]
            if objects:
                self._client.delete_objects(
                    Bucket=self.bucket, Delete={"Objects": objects}
                )

    # ── List ───────────────────────────────────────────────────────────────────

    def list_objects(self, prefix: str) -> list[dict]:
        """Retorna todos os objetos com o prefix dado (com paginação)."""
        paginator = self._client.get_paginator("list_objects_v2")
        result: list[dict] = []
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            result.extend(page.get("Contents", []))
        return result

    # ── Metadata ───────────────────────────────────────────────────────────────

    def object_exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    # ── URLs ───────────────────────────────────────────────────────────────────

    def get_presigned_url(self, key: str, expiry: int = 0) -> str:
        """URL assinada para GET de um objeto (usada para servir arquivos)."""
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expiry or self.presigned_expiry,
        )

    def get_object_stream(self, key: str, chunk_size: int = 65536):
        """
        Retorna um gerador que produz chunks do objeto em streaming.
        Não carrega o arquivo inteiro em memória.

        Raises:
            KeyError: se o objeto não existir (botocore.exceptions.ClientError 404)
        """
        response = self._client.get_object(Bucket=self.bucket, Key=key)
        body = response["Body"]
        content_length = response.get("ContentLength")

        def _chunks():
            while True:
                chunk = body.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        return _chunks(), content_length
