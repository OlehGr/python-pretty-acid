import asyncio

import pytest
from dishka import make_container

from app.infrastructure.database.transaction import (
    TransactionalSession,
    TransactionalSessionFactory,
    TransactionManager,
)
from app.models import User
from app.providers import DatabaseProvider

pytestmark = pytest.mark.asyncio


@pytest.fixture
def di_container():
    di_container = make_container(DatabaseProvider())
    yield di_container
    di_container.close()


@pytest.fixture
def tm(di_container):
    return TransactionManager(di_container.get(TransactionalSessionFactory))


@pytest.fixture
def session_factory(di_container):
    return di_container.get(TransactionalSessionFactory)


class TestTransactionManagerUnit:
    async def test_nested_session_shares_same_instance(self, tm: TransactionManager):
        """
        Вложенные контексты tm.session() при открытие не должны создавать новые сессии,
        а должны использовать ту же сессию, которую создал корневой (родительский) контекст
        при этом не открывая транзакцию:
        s1 = s2 = s3 = s4
        .in_transaction() -> False
        """
        async with tm.session() as s1:
            async with tm.session() as s2:
                async with tm.session() as s3:
                    assert s1 is s2
                    assert s2 is s3

            async with tm.session() as s4:
                assert s1 is s4
                assert s4.in_transaction() is False

    async def test_nested_transaction_shares_same_instance(
        self, tm: TransactionManager
    ):
        """
        Вложенные контексты tm.transaction() при открытие не должны создавать новые сессии
        и открывать транзакцию, а должны использовать ту же сессию, которую создал корневой (родительский) контекст
        при этом транзакция открыта
        t1 = t2 = t3 = t4
        .in_transaction() -> True
        """
        async with tm.transaction() as t1:
            async with tm.transaction() as t2:
                async with tm.transaction() as t3:
                    assert t1 is t2
                    assert t2 is t3

            async with tm.transaction() as t4:
                assert t1 is t4
                assert t4.in_transaction()

    async def test_nested_transaction_sharing_in_separate_func_calls(
        self, tm: TransactionManager
    ):
        """
        Вложенные контексты при вызове внутри других функций должны использовать
        сессию контекста, открытого в коде, который вызвал эти функции.
        """

        async def sub_method_with_transaction(
            manager: TransactionManager, parent_session: TransactionalSession
        ):
            async with manager.transaction() as tx:
                assert tx is parent_session

        async def sub_method_with_session(
            manager: TransactionManager, parent_session: TransactionalSession
        ):
            async with manager.session() as s:
                assert s is parent_session

        async def super_parent_method(
            manager: TransactionManager, parent_session: TransactionalSession
        ):
            await sub_method_with_transaction(manager, parent_session)
            await sub_method_with_session(manager, parent_session)

        async with tm.transaction() as tx:
            await super_parent_method(tm, tx)

    async def test_root_transaction_commit_persists(self, tm: TransactionManager):
        """
        При завернении контекста транзакции выполняется коммит и даанные сохраняються в базе
        """

        user = User.create(name="Bob")

        async with tm.transaction() as tx:
            await tx.merge(user)

        async with tm.session() as s:
            exits_user = await s.get(User, user.id)
            assert exits_user is not None
            assert exits_user.name == "Bob"

    async def test_root_transaction_rollback_on_exception(self, tm: TransactionManager):
        """
        При исключении в контексте транзакции, должен произойти .rollback(),
        а данные не должны быть сохранены
        """

        tx_which_wiil_be_closed = None

        user = User.create(name="Bob")

        with pytest.raises(RuntimeError):
            async with tm.transaction() as tx:
                tx_which_wiil_be_closed = tx
                await tx.merge(user)
                raise RuntimeError("BOOM!")

        assert tx_which_wiil_be_closed
        assert tx_which_wiil_be_closed.get_transaction() is None

        async with tm.session() as s:
            unexist_user = await s.get(User, user.id)
            assert unexist_user is None

    async def test_root_transaction_rollback_on_exception_in_subcontext(
        self, tm: TransactionManager
    ):
        """
        При исключении в дочернем контексте транзакции, должен произойти .rollback(),
        а данные не должны быть сохранены, в том числе те которые были записаны в соседних
        успешных контекстах
        """

        tx_which_wiil_be_closed = None

        good_user = User.create(name="Good Bob")
        bad_user = User.create(name="Bad Bob")

        with pytest.raises(RuntimeError):
            async with tm.transaction() as tx1:
                tx_which_wiil_be_closed = tx1

                async with tm.transaction() as tx2:
                    good_user = User.create(name="Bob")
                    await tx2.merge(good_user)

                async with tm.transaction() as tx3:
                    bad_user = User.create(name="Bob")
                    await tx3.merge(bad_user)
                    raise RuntimeError("BOOM!")

        assert tx_which_wiil_be_closed
        assert tx_which_wiil_be_closed.get_transaction() is None

        async with tm.session() as s:
            assert await s.get(User, good_user.id) is None
            assert await s.get(User, bad_user.id) is None

    async def test_nested_transaction_calls_flush_on_success(
        self, tm: TransactionManager, monkeypatch
    ):
        """
        При завершении дочернии контексты вызывают .flush()
        для промежуточного сохранения данных в случае чтения незакомиченных данных в рамках активной транзакции
        """

        fantom_user = User.create(name="Fantom Bob")

        calls = {"flush": 0}

        async with tm.transaction() as root_tx:
            real_flush = root_tx.flush

            async def fake_flush(*args, **kwargs):
                calls["flush"] += 1
                return await real_flush(*args, **kwargs)

            monkeypatch.setattr(root_tx, "flush", fake_flush)

            async with tm.transaction() as tx:
                await tx.merge(fantom_user)

            async with tm.session() as s:
                saved_user = await s.get(User, fantom_user.id)
                assert saved_user is not None
                assert saved_user.name == "Fantom Bob"

            async with tm.transaction():
                pass

        assert calls["flush"] == 2

    async def test_nested_transaction_does_not_flush_on_exception(
        self, tm, monkeypatch
    ):
        """
        При возникновении исключения дочерний контексттранзакции не дожен вызвать .flush()
        """
        calls = {"flush": 0}

        with pytest.raises(RuntimeError):
            async with tm.transaction() as root_tx:
                real_flush = root_tx.flush

                async def fake_flush(*args, **kwargs):
                    calls["flush"] += 1
                    return await real_flush(*args, **kwargs)

                monkeypatch.setattr(root_tx, "flush", fake_flush)

                async with tm.transaction():
                    raise RuntimeError()

        assert calls["flush"] == 0

    async def test_session_context_does_not_commit(self, tm: TransactionManager):
        """
        Контекст сессии НЕ должен начинать / завершать транзакцию ( .begin() / .commit() )
        """

        user = User.create(name="no-commit")

        async with tm.session() as s:
            await s.merge(user)

        async with tm.session() as s:
            assert await s.get(User, user.id) is None

    async def test_concurrent_tasks_do_not_share_session(self, tm: TransactionManager):
        """
        Паралельные асинхронные операции, работая с одним и тем же экземпляром TransactionManager,
        не должны шарить между собой сессии
        """
        sessions = []

        async def worker():
            async with tm.transaction() as s:
                async with tm.transaction() as s:
                    sessions.append(s)
                    await asyncio.sleep(1)

        await asyncio.gather(worker(), worker())
        assert sessions[0] is not sessions[1]
