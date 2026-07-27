import requests

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction

DAEMON_TIMEOUT_SECONDS = 3


class ButlerExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or ""
        port = extension.preferences.get("daemon_port", "8420")

        if not query.strip():
            return RenderResultListAction([
                ExtensionResultItem(
                    icon="images/icon.webp",
                    name="Ask AI Butler something...",
                    description="e.g. bt sort my downloads folder",
                    on_enter=None,
                )
            ])

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

        return RenderResultListAction([
            ExtensionResultItem(
                icon="images/icon.png",
                name=result_text,
                description=description,
                on_enter=None,
            )
        ])


if __name__ == "__main__":
    ButlerExtension().run()
