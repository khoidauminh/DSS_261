from typing import Final, Any

Page: Final = "page"
PageSize: Final = "page_size"
PageSizeDefault: Final = 50

def validated(query: dict[str, Any]) -> dict[str, Any]:
    if Page not in query:
        query[Page] = 1

    if PageSize not in query:
        query[PageSize] = PageSizeDefault

    return query