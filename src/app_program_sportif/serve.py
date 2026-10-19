"""Lance l'application web en local et ouvre le navigateur."""

import threading
import webbrowser

import uvicorn

URL = "http://127.0.0.1:8000"


def main() -> None:
    threading.Timer(1.0, lambda: webbrowser.open(URL)).start()
    uvicorn.run("app_program_sportif.api.app:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
