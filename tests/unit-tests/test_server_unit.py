import json
import pytest
from unittest.mock import mock_open
import server


@pytest.mark.usefixtures("test_data", "app", "mock_db")
class TestServerUnit:

    def test_loadClubs(self, test_data, mocker):
        fake_content = json.dumps({"clubs": test_data['clubs']})
        mocker.patch("builtins.open", mock_open(read_data=fake_content))
        result = server.loadClubs()

        assert result == test_data['clubs']

    def test_loadCompetitions(self, test_data, mocker):
        fake_content = json.dumps({"competitions": test_data["competitions"]})
        mocker.patch("builtins.open", mock_open(read_data=fake_content))
        result = server.loadCompetitions()

        assert result == test_data['competitions']
