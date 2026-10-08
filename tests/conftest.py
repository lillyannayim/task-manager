import copy

import pytest

from services.tasks import TASKS


@pytest.fixture(autouse=True)
def restore_tasks():
    saved = copy.deepcopy(TASKS)
    yield
    TASKS.clear()
    TASKS.update(saved)
