from uvicorn.workers import UvicornWorker


# test comment
class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"lifespan": "off"}
