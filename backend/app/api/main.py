from fastapi import FastAPI


def create_app() -> FastAPI:
    return FastAPI(
        title="文档处理办公 Agent API",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/api/v1/openapi.json",
    )


app = create_app()
