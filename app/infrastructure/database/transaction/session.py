from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.transaction import ITransactionalSession


class TransactionalSession(AsyncSession, ITransactionalSession): ...


TransactionalSessionFactory = async_sessionmaker[TransactionalSession]
