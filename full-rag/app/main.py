# Current package(app) ke server.py file se FastAPI app object import kar raha hai
from .server import app

# on deploy we will run server from this file


def main():
    import uvicorn

    # Python script ke through uvicorn sa server start kar raha hai
    uvicorn.run(app="app.server:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()