import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=os.getenv("POSTGRES_PORT", "5002"),
        dbname=os.getenv("POSTGRES_DB", "omniinsight_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def test_connection():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_user, version()"
            )
            return cursor.fetchone()

def save_document(
    document_id: str,
    filename: str,
    file_path: str,
    file_hash: str,
    total_pages: int,
    status: str,
):
    """Save document metadata to PostgreSQL."""

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (
                    id,
                    filename,
                    file_path,
                    file_hash,
                    total_pages,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    document_id,
                    filename,
                    file_path,
                    file_hash,
                    total_pages,
                    status,
                ),
            )

def get_all_documents():
    """Retrieve all document records from PostgreSQL."""

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    filename,
                    file_path,
                    file_hash,
                    total_pages,
                    status
                FROM documents
                ORDER BY id DESC
                """
            )

            rows = cursor.fetchall()

            return [
                {
                    "document_id": str(row[0]),
                    "filename": row[1],
                    "file_path": row[2],
                    "file_hash": row[3],
                    "total_pages": row[4],
                    "status": row[5],
                }
                for row in rows
            ]

def get_document_by_hash(file_hash: str):
    """Find an existing document using its SHA-256 hash."""

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    filename,
                    file_path,
                    file_hash,
                    total_pages,
                    status
                FROM documents
                WHERE file_hash = %s
                LIMIT 1
                """,
                (file_hash,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return {
                "document_id": str(row[0]),
                "filename": row[1],
                "file_path": row[2],
                "file_hash": row[3],
                "total_pages": row[4],
                "status": row[5],
            }
def get_document_by_id(document_id: str):
    """Retrieve a document using its unique ID."""

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    filename,
                    file_path,
                    file_hash,
                    total_pages,
                    status
                FROM documents
                WHERE id = %s
                """,
                (document_id,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return {
                "document_id": str(row[0]),
                "filename": row[1],
                "file_path": row[2],
                "file_hash": row[3],
                "total_pages": row[4],
                "status": row[5],
            }


def delete_document_record(document_id: str):
    """Delete a document's metadata record from PostgreSQL."""

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM documents
                WHERE id = %s
                RETURNING id
                """,
                (document_id,),
            )

            deleted_row = cursor.fetchone()

            return deleted_row is not None