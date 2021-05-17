import uvicorn  # type: ignore

from src.application import create_app
from src.utils.logging_setup import setup_logging

app = create_app()

@app.on_event("startup")
async def startup_event():
    setup_logging()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
