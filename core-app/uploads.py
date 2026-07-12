from pathlib import Path

from werkzeug.utils import secure_filename

UPLOAD_DIR = Path(__file__).parent / "uploads"


def task_upload_dir(task_id: int) -> Path:
    return UPLOAD_DIR / str(task_id)


def list_attachments(task_id: int) -> list[str]:
    task_dir = task_upload_dir(task_id)
    if not task_dir.exists():
        return []
    return sorted(f.name for f in task_dir.iterdir() if f.is_file())


def save_attachment(task_id: int, file_storage) -> str:
    task_dir = task_upload_dir(task_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    filename = secure_filename(file_storage.filename)
    file_storage.save(task_dir / filename)
    return filename


def delete_attachment(task_id: int, filename: str) -> bool:
    file_path = task_upload_dir(task_id) / secure_filename(filename)
    if file_path.exists():
        file_path.unlink()
        return True
    return False
