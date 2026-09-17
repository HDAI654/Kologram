from fastapi import Request


def build_graphql_context(request: Request) -> dict:
    return {
        "request": request,
        "uow_factory": request.app.state.uow,
        "event_publisher": request.app.state.event_publisher,
    }
