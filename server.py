import asyncio
from main import app, PORT

async def main():
    await app.run_async(transport="http", host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Exiting.")
