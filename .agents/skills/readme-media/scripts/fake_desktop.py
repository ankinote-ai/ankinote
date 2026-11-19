"""Answer as Anki Desktop with AnkiConnect on 127.0.0.1:8765, for the wizard shot.

Backed by a throwaway collection in DIR, through the test suite's
AnkiConnect fake (real ``anki`` library, real HTTP). Runs until stopped.

    uv run python .agents/skills/readme-media/scripts/fake_desktop.py DIR
"""

import asyncio
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests" / "services"))

import fake_anki_connect_server as fake

from ankinote.services.collection_runtime import CollectionRuntime

PORT = 8765


class _Server(fake._Server):
    def __init__(self, runtime, loop):
        fake.ThreadingHTTPServer.__init__(self, ("127.0.0.1", PORT), fake._Handler)
        self.runtime = runtime
        self.loop = loop


async def main(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    runtime = CollectionRuntime(str(directory / "collection.anki2"))
    await runtime.open()
    server = _Server(runtime, asyncio.get_running_loop())
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"AnkiConnect fake on http://127.0.0.1:{PORT}", flush=True)
    try:
        await asyncio.Event().wait()
    finally:
        server.shutdown()
        await runtime.close()


asyncio.run(main(Path(sys.argv[1])))
