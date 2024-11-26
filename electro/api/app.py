"""The API server that works as an endpoint for all the Electro Interfaces."""

from fastapi import FastAPI

from api.schemas import DiscordMessage

app = FastAPI(
    title="Electro API",
    description="The API server that works as an endpoint for all the Electro Interfaces.",
    version="0.1.0",
    # docs_url="/",
    # redoc_url=None,
)


@app.post("/message")
async def process_message(message: DiscordMessage) -> list[DiscordMessage] | None:
    """Process the message."""

    # TODO: [2024-11-26 by Mykola] Actually process the message, not just echo it back
    return [
        DiscordMessage(
            id=message.id,
            content=message.content,
            author=message.author,
            channel=message.channel,
            created_at=message.created_at,
            edited_at=message.edited_at,
        )
    ]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
