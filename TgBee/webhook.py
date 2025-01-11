from fastapi import FastAPI, Request
from .bot import Bot
from .types import Update

app = FastAPI()
bot = Bot()

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    update = Update.from_dict(data)
    await bot.process_update(update)
    return {"ok": True}

def run_webhook(token: str, webhook_url: str, host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    bot.set_token(token)
    bot.set_webhook(url=webhook_url)
    uvicorn.run(app, host=host, port=port)

