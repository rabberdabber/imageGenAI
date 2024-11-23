from ...models.image import Image  # Verify this import works
from .base_class import Base

# List of all models for metadata
models = [Image]

# Re-export Base for convenience
__all__ = ["Base", "models"]
