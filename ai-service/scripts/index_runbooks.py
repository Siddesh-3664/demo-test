import asyncio
from app.tools.runbooks import index

if __name__ == "__main__":
    count = asyncio.run(index())
    print(f"indexed {count} chunks")
