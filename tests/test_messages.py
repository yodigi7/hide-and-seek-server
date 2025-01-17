import pytest
from pydantic import ValidationError
from server.messages import JoinGameMessage, Role


def test_first_message_valid():
    # Test valid input
    valid_data = {"role": "hider"}
    message = JoinGameMessage(**valid_data)
    assert message.role == Role.HIDER


def test_first_message_invalid_role():
    # Test invalid role
    invalid_data = {"role": "invalid_role"}
    with pytest.raises(ValidationError) as excinfo:
        JoinGameMessage(**invalid_data)
    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("role",)
    assert errors[0]["msg"] == "Input should be 'hider' or 'seeker'"
