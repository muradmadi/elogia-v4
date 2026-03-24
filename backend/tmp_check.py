import asyncio
from sqlalchemy import text
from app.core.database import async_sessionmaker, engine

async def main():
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(text("SELECT job_id, email, status FROM enrichment_jobs"))
        rows = result.fetchall()
        for row in rows:
            print(dict(row._mapping))

if __name__ == "__main__":
    asyncio.run(main())
