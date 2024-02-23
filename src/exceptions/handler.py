from fastapi.responses import JSONResponse

from src.exceptions.exc_types import LamodaCategoriesNotFoundException
from src.main import app


@app.exception_handler(LamodaCategoriesNotFoundException)
async def lamoda_exception_handler(request, exc: LamodaCategoriesNotFoundException):
    """
    Custom exception handler for lamoda categories.

    Args:
    - request - incoming FastAPI request.
    - exc - exception raised during handling request.

    Returns:
    - JSONResponse - response with error message and details
        which represents existing categories/subcategories.
    """
    return JSONResponse({"error": exc.message, "details": exc.details})
