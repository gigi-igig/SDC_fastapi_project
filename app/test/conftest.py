import pytest
from fastapi.testclient import TestClient
from configs.config import settings

from main import app
from dependencies.DBSession import get_session, init_db
from sqlmodel import Session,  create_engine

# scope = session: this fixture only runs once per test session (clear after all tests)
# scope = function(default): this fixture runs once per test function (clear after each test function)
@pytest.fixture(name="session", scope="session")
def session_fixture():
    TEST_DATABASE_URL = (
        f"postgresql://{settings.test_postgres_user}:{settings.test_postgres_password}"
        f"@{settings.test_postgres_host}:{settings.test_postgres_port}/{settings.test_postgres_db}"
    )
    test_engine = create_engine(TEST_DATABASE_URL)
    init_db(custom_engine=test_engine, dropFirst=True)
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)

    yield client
    app.dependency_overrides.clear()