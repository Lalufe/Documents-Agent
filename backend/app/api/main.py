from fastapi import FastAPI

from app.api.errors import install_exception_handlers
from app.api.routes.contracts import install_contract_components
from app.api.routes.health import router as health_router


def create_app() -> FastAPI:
    application = FastAPI(
        title="文档处理办公 Agent API",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/api/v1/openapi.json",
    )
    install_exception_handlers(application)
    application.include_router(health_router)
    install_contract_components(application)
    return application


app = create_app()
