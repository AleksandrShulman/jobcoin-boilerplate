import pytest

from jobcoin.jobcoin import JobcoinClient, JobcoinInfusion, Transaction


@pytest.fixture
def client():
    return JobcoinClient("someAddress")


def test_get_transactions(client):
    # Given a situation where we need to get transactions
    transactions = client.get_transactions()

    # Pull them down
    transaction = transactions[0]
    if 'fromAddress' not in transaction:
        txn = JobcoinInfusion(to_address=transaction['toAddress'],
                              amount=transaction['amount'])
        assert txn.from_address == JobcoinClient.JOBCOIN_GENERATOR
    else:
        txn = Transaction(transaction['fromAddress'],
                          transaction['toAddress'],
                          transaction['amount'])

    # Verify them
    assert txn.amount == transaction['amount']
    assert txn.to_address == transaction['toAddress']

# TODO: Add more test cases


if __name__ == "__main__":
    pytest.main(["./test_get_transactions.py", "-s"])
