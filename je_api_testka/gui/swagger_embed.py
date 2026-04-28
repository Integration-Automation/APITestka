"""
Swagger UI embed helpers.

* :func:`build_swagger_html` returns an HTML string that loads Swagger UI from
  a CDN against a given OpenAPI spec URL.
* :func:`build_swagger_widget` returns a ``QWebEngineView`` rendering the same
  HTML inside the existing PySide6 GUI. Both PySide6 and the WebEngine module
  are optional - they only have to be present when calling this function.
"""
from __future__ import annotations

from je_api_testka.utils.exception.exceptions import APITesterException

DEFAULT_SWAGGER_VERSION: str = "5.17.14"
DEFAULT_SWAGGER_CSS: str = (
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@{version}/swagger-ui.css"
)
DEFAULT_SWAGGER_BUNDLE: str = (
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@{version}/swagger-ui-bundle.js"
)
PYSIDE_QTWEBENGINE_NOT_INSTALLED: str = (
    "PySide6 QtWebEngineWidgets is required. Install with `pip install PySide6 PySide6-Addons`."
)


def build_swagger_html(spec_url: str, version: str = DEFAULT_SWAGGER_VERSION) -> str:
    """Return an HTML page that boots Swagger UI against ``spec_url``."""
    css_url = DEFAULT_SWAGGER_CSS.format(version=version)
    bundle_url = DEFAULT_SWAGGER_BUNDLE.format(version=version)
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\" />
<title>APITestka Swagger</title>
<link rel=\"stylesheet\" href=\"{css_url}\" />
</head>
<body>
<div id=\"swagger-ui\"></div>
<script src=\"{bundle_url}\"></script>
<script>
window.onload = function () {{
    window.ui = SwaggerUIBundle({{
        url: \"{spec_url}\",
        dom_id: \"#swagger-ui\"
    }});
}};
</script>
</body>
</html>
"""


def build_swagger_widget(spec_url: str, version: str = DEFAULT_SWAGGER_VERSION):
    """Return a ``QWebEngineView`` ready to embed into the GUI."""
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore
    except ImportError as error:
        raise APITesterException(PYSIDE_QTWEBENGINE_NOT_INSTALLED) from error
    view = QWebEngineView()
    view.setHtml(build_swagger_html(spec_url, version=version))
    return view
