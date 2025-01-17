import pytest


@pytest.fixture(autouse=True)
def a_db(db):
    pass
