import asyncio
import os
from enum import StrEnum
from typing import Optional
from uuid import UUID

import httpx

# Add these imports to existing ones
from fastapi import APIRouter, Depends, File, HTTPException, Path, UploadFile
from fastapi.responses import Response
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.db.database import get_db
from ...models.image import Image

router = APIRouter(tags=["images"])

API_BASE_URL = "https://api.bfl.ml/v1"

class ImageGenerationResultStatus(StrEnum):
    TASK_NOT_FOUND = "Task not found"
    PENDING = "Pending"
    REQUEST_MODERATED = "Request Moderated"
    CONTENT_MODERATED = "Content Moderated"
    READY = "Ready"
    ERROR = "Error"


class FluxModel(StrEnum):
    FLUX_PRO_1_1 = "flux-pro-1.1"
    FLUX_PRO = "flux-pro"
    FLUX_DEV = "flux-dev"
    FLUX_PRO_1_1_ULTRA = "flux-pro-1.1-ultra"
    FLUX_PRO_1_0_FILL = "flux-pro-1.0-fill"
    FLUX_PRO_1_0_CANYON = "flux-pro-1.0-canny"
    FLUX_PRO_1_0_DEPTH = "flux-pro-1.0-depth"


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to generate the image from")
    width: int = Field(default=1024, ge=64, le=2048, description="Image width in pixels")
    height: int = Field(default=768, ge=64, le=2048, description="Image height in pixels")
    prompt_upsampling: bool = Field(default=False, description="Whether to use prompt upsampling")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducible generations")
    safety_tolerance: int = Field(
        default=2,
        ge=0,
        le=3,
        description="Safety filter tolerance level (0-3)"
    )
    output_format: str = Field(
        default="jpeg",
        pattern="^(jpeg|png)$",
        description="Output format of the generated image"
    )

@router.post("/generate-image")
async def generate_image(
    request: ImageGenerationRequest,
    model: FluxModel = FluxModel.FLUX_PRO_1_1
) -> Response:
    """Generate an image using the model."""
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Start the image generation
            generation_response = await client.post(
                f"{API_BASE_URL}/{model.value}",
                json=request.model_dump(),  # Convert Pydantic model to dict
                headers={
                    "Content-Type": "application/json",
                    "X-Key": settings.FLUX_API_KEY
                }
            )
            generation_data = generation_response.json()
            task_id = generation_data.get("id")

            if not task_id:
                raise HTTPException(status_code=500, detail=f"Failed to start image generation: {generation_data}")

            # Step 2: Poll for results
            max_attempts = 15  # Maximum number of attempts
            attempt = 0
            while attempt < max_attempts:
                result_response = await client.get(
                    f"{API_BASE_URL}/get_result?id={task_id}"
                )
                result_data = result_response.json()
                status = result_data.get("status")

                if status == ImageGenerationResultStatus.READY:
                    # Get the image data
                    image_url = result_data.get("result").get("sample")
                    image_response = await client.get(image_url)
                    return Response(
                        content=image_response.content,
                        media_type="image/png"
                    )
                elif status == ImageGenerationResultStatus.ERROR:
                    return Response(
                        content="Image generation failed",
                        status_code=500,
                        media_type="text/plain"
                    )
                elif status == ImageGenerationResultStatus.TASK_NOT_FOUND:
                    return Response(
                        content="Task not found",
                        status_code=404,
                        media_type="text/plain"
                    )
                elif status == ImageGenerationResultStatus.REQUEST_MODERATED:
                    return Response(
                        content="Request was moderated due to content policy",
                        status_code=400,
                        media_type="text/plain"
                    )
                elif status == ImageGenerationResultStatus.CONTENT_MODERATED:
                    return Response(
                        content="Generated content was moderated due to content policy",
                        status_code=400,
                        media_type="text/plain"
                    )
                elif status == ImageGenerationResultStatus.PENDING:
                    # Continue polling
                    await asyncio.sleep(0.3)
                    attempt += 1
                    logger.info(f"Image generation status: {status}")
                    logger.info(f"Attempt: {attempt}")
                    continue

            return Response(
                content="Timeout waiting for image generation",
                status_code=408,
                media_type="text/plain"
            )

    except Exception as e:
        return Response(
            content=f"Error generating image: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )



# Add this function to handle file uploads
def is_valid_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS

@router.post("/upload/{image_id}")
async def upload_image(
    image_id: UUID = Path(..., description="The UUID for the image"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Upload an image with a specific UUID and return its URL."""
    image_id_str = str(image_id)
    try:
        if not is_valid_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail="File type not allowed"
            )

        # Create uploads directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        # Generate unique filename using the provided UUID
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{image_id_str}.{ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

        # Check if UUID already exists
        result = await db.execute(select(Image).where(Image.id == image_id_str))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"Image with ID {image_id_str} already exists"
            )

        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Create URL
        url = f"{settings.BASE_URL}/uploads/{unique_filename}"

        # Create new image record with specified UUID
        db_image = Image(
            id=image_id_str,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            url=url,
            content_type=file.content_type
        )

        # Add and commit to database
        db.add(db_image)
        await db.commit()
        await db.refresh(db_image)

        return {
            "id": str(db_image.id),  # Convert UUID to string for JSON response
            "url": db_image.url,
            "filename": db_image.filename
        }

    except Exception as e:
        # Clean up file if database operation fails
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )
