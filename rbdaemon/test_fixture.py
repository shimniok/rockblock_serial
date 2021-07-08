import os
import pytest

@pytest.fixture(scope='session')
def app():
    ''' Basic test fixture '''

    yield
