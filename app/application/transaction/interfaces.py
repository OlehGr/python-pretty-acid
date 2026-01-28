from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

TransactionalSession = AsyncSession

TransactionalSessionFactory = async_sessionmaker[AsyncSession]
