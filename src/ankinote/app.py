from ankinote.utils.httpcli import close_session, init_session


class Application:
    def __init__(self):
        init_session()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Do not inspect or cancel global tasks here: when this runs inside a
        # server's event loop, those tasks include the server's own.
        await close_session()
