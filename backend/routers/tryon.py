import os
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

router = APIRouter(prefix="/api/tryon", tags=["tryon"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "tryon")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Store task results in memory (for demo; use DB/Redis in production)
_tasks: dict = {}


@router.post("")
async def create_tryon(
    person_image: UploadFile = File(...),
    clothing_image_url: str = Form(...),
):
    """
    Submit a virtual try-on request.
    - person_image: user's photo
    - clothing_image_url: URL/path of the clothing item to try on

    TODO: Integrate with actual AI try-on API (e.g., Alibaba Cloud, Baidu, etc.)
    Currently returns a placeholder response.
    """
    # Save person image
    ext = os.path.splitext(person_image.filename)[1]
    person_filename = f"{uuid.uuid4().hex}{ext}"
    person_path = os.path.join(UPLOAD_DIR, person_filename)
    with open(person_path, "wb") as f:
        f.write(await person_image.read())

    task_id = uuid.uuid4().hex

    # TODO: Call external AI API here
    # For now, store as pending
    _tasks[task_id] = {
        "status": "pending",
        "person_image": f"/uploads/tryon/{person_filename}",
        "clothing_image": clothing_image_url,
        "result_image": None,
        "message": "AI换装功能即将接入，敬请期待！",
    }

    return {"task_id": task_id, "status": "pending", "message": "AI换装功能即将接入，敬请期待！"}


@router.get("/{task_id}")
def get_tryon_result(task_id: str):
    """Get the result of a try-on task."""
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    return task
