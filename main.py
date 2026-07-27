from socket import timeout
import subprocess
import requests

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

DAEMON_TIMEOUT_SECONDS = 3
ICON = "images/icon.webp"


def notify(title: str, body: str):
    try:
        subprocess.run(
            ["notify-send", "-a", "AI Butler", "-i", ICON, title, body],
            timeout=2,
        )
    except FileNotFoundError:
        pass


class ButlerExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or ""

        if not query.strip():
            return RenderResultListAction(
                [
                    ExtensionResultItem(
                        icon=ICON,
                        name="Ask AI Butler something...",
                        description="e.g. bt sort my downloads folder",
                        on_enter=None,
                    )
                ]
            )

        return RenderResultListAction(
            [
                ExtensionResultItem(
                    icon=ICON,
                    name=f'Ask: "{query}"',
                    description="Press Enter to run",
                    on_enter=ExtensionCustomAction(query, keep_app_open=True),
                )
            ]
        )


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_data()
        port = extension.preferences.get("daemon_port", "8420")

        try:
            resp = requests.post(
                f"http://127.0.0.1:{port}/query",
                json={"text": query},
                timeout=DAEMON_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            data = resp.json()
            result_text = data.get("summary", "Done")
            description = data.get("detail", "")
        except requests.exceptions.RequestException:
            result_text = "AI Butler daemon offline"
            description = "Check systemd service: systemctl --user status ai-butler"

        notify(result_text, description)

        return RenderResultListAction(
            [
                ExtensionResultItem(
                    icon=ICON,
                    name=result_text,
                    description=description,
                    on_enter=None,
                )
            ]
        )


if __name__ == "__main__":
    ButlerExtension().run()
