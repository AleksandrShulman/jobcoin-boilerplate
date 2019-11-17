import mock
import pytest

from jobcoin.errors import IllegalArgumentException
from jobcoin.jobcoin import JobcoinClient
from tests.utils.generator import gen_recipient_addresses

DEFAULT_INPUT_ADDRESS = "inputAddress"
FULL_TRANSFER_AMOUNT = float(750.25)
DEFAULT_SINGLE_TRANSFER_AMOUNT = 42.42


@pytest.fixture()
def user_address():
    return DEFAULT_INPUT_ADDRESS


@pytest.fixture()
def client(user_address):
    jobclient = JobcoinClient(user_address)

    # Adjust the client to not actually do anything; we can't just be sending
    # coins willy-nilly! These things are valuable, after all!
    jobclient.send_coins_to_single_address = mock.MagicMock(
        return_value=DEFAULT_SINGLE_TRANSFER_AMOUNT)
    return jobclient


@pytest.fixture()
def txn_verification_failing_client(user_address):
    jobclient = JobcoinClient(user_address)
    jobclient.verify_transaction = mock.MagicMock(return_value=False)

    return jobclient


@pytest.mark.parametrize("recipient_addresses, apply_fee, expected_result", [
    (gen_recipient_addresses(1), True,
     FULL_TRANSFER_AMOUNT *
     (100 - JobcoinClient.DISBURSEMENT_FEE_PERCENT) / 100),
    (gen_recipient_addresses(1), False,
     FULL_TRANSFER_AMOUNT),
    (gen_recipient_addresses(3), True,
     FULL_TRANSFER_AMOUNT *
     (100 - JobcoinClient.DISBURSEMENT_FEE_PERCENT) / (3 * 100)),
    (gen_recipient_addresses(3), False,
     FULL_TRANSFER_AMOUNT / 3),
    (gen_recipient_addresses(20), True,
     FULL_TRANSFER_AMOUNT *
     (100 - JobcoinClient.DISBURSEMENT_FEE_PERCENT) / (20 * 100)),
    (gen_recipient_addresses(20), False,
     FULL_TRANSFER_AMOUNT / 20)
])
def test_percentage_deduction(recipient_addresses, apply_fee, expected_result):
    assert JobcoinClient.calculate_disbursement(
        recipient_addresses,
        FULL_TRANSFER_AMOUNT,
        apply_fee) == expected_result


@pytest.mark.parametrize("recipient_addresses, apply_fee, input_amount", [
    (list(), True, FULL_TRANSFER_AMOUNT *
     (100 - JobcoinClient.DISBURSEMENT_FEE_PERCENT) / 100),
    (gen_recipient_addresses(1), False, None),
    (gen_recipient_addresses(3), True, -5),
    (gen_recipient_addresses(3), False, "abc123"),
    (gen_recipient_addresses(3), True, "")
])
def test_invalid_deduction_inputs(recipient_addresses,
                                  apply_fee, input_amount):
    with pytest.raises(IllegalArgumentException.IllegalArgumentException):
        JobcoinClient.calculate_disbursement(
            recipient_addresses, input_amount, apply_fee)


def test_correct_transactions(client):
    # Given a valid set of inputs
    num_addresses = 5
    successes, failures = client.send_coins(
        gen_recipient_addresses(num_addresses),
        DEFAULT_SINGLE_TRANSFER_AMOUNT)
    assert len(successes) == num_addresses
    assert not failures


def test_send_coin_cannot_verify_transaction(txn_verification_failing_client):
    num_addresses = 5
    successes, failures = txn_verification_failing_client.send_coins(
        gen_recipient_addresses(num_addresses), DEFAULT_SINGLE_TRANSFER_AMOUNT)
    assert not successes
    assert len(failures) == num_addresses


# TODO:
# Test out other failure modes such as:
# 1. Exceptions occurring during either the transfer or the verification
# 2. Partial success or partial failure


if __name__ == "__main__":
    pytest.main(["./test_rest_client.py", "-s"])
