import os
from pathlib import Path

import pytest

test_path = Path("test_data")
if not test_path.exists():
    test_path.mkdir(parents=True)
os.chdir(test_path.absolute())


@pytest.fixture(scope="module", autouse=True)
def test_print_new_line():
    print("\n")
    yield
    print("\n")
