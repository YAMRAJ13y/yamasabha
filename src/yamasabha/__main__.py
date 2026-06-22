"""Run the Yamasabha server: ``python -m yamasabha`` or the ``yamasabha`` command."""
from __future__ import annotations

import os


def main() -> None:
    import uvicorn

    host = os.environ.get("YAMASABHA_HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", os.environ.get("YAMASABHA_PORT", "8000")))
    uvicorn.run("yamasabha.app:app", host=host, port=port)


if __name__ == "__main__":
    main()
