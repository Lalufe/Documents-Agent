# pyright: basic

from fastapi import FastAPI


def test_create_app_returns_fastapi_application() -> None:
    from app.api.main import create_app

    app = create_app()

    assert isinstance(app, FastAPI)
    assert app.title == "文档处理办公 Agent API"
    assert app.docs_url == "/docs"
