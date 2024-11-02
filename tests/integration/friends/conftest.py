from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture()
def _mock_prepare_notification() -> AsyncMock:
    """Заглушка отправки push-уведомления через FireBase"""
    with patch("application.friends.router.prepare_notification") as mock:
        yield mock


@pytest.fixture(autouse=True)
async def setup_and_teardown(session: AsyncSession):
    """После каждого теста чистим таблицу User"""
    yield
    await session.execute(text('TRUNCATE TABLE "user" RESTART IDENTITY CASCADE;'))
    await session.commit()
