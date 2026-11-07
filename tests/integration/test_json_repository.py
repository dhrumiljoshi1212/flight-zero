import json
import pytest
from flightzero.domain.errors import DataFormatError


def test_state_is_persisted(repository):
    reservation = repository.book("FLIGHT-001", "A1")
    payload = json.loads(repository.data_path.read_text())
    assert payload["reservations"][0]["reservation_id"] == reservation.reservation_id


def test_corrupt_json_is_not_reset(repository):
    repository.data_path.write_text("{broken")
    with pytest.raises(DataFormatError):
        repository.list_flights()
    assert repository.data_path.read_text() == "{broken"
