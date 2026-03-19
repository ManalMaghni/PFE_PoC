import httpx
import asyncio
from shared.config import GROQ_API_KEY, GROQ_MODEL, GROQ_URL

async def call_groq(messages: list, tools: list = None, retries: int = 3) -> dict:
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": 2048,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    for attempt in range(retries):
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(GROQ_URL, json=payload, headers=headers)

            if response.status_code == 429:
                wait = 15 * (attempt + 1)
                print(f"⏳ Rate limit — attente {wait}s (tentative {attempt+1}/{retries})")
                await asyncio.sleep(wait)
                continue

            if response.status_code == 400:
                print(f"❌ 400 Bad Request — body: {response.text[:500]}")
                raise Exception(f"400 Bad Request: {response.text[:200]}")

            response.raise_for_status()
            return response.json()["choices"][0]["message"]

    raise Exception("❌ Rate limit dépassé après plusieurs tentatives")