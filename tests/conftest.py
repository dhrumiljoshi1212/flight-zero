import pytest
from flightzero.infrastructure.json_repository import JsonReservationRepository


@pytest.fixture
def repository(tmp_path):
    repo = JsonReservationRepository(tmp_path / "reservations.json")
    repo.initialize()
    return repo
