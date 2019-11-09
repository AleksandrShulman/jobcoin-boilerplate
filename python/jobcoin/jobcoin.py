import json
import logging
from http import HTTPStatus

import requests

from jobcoin.config import API_COIN_URL, API_TRANSACTIONS_URL
from jobcoin.errors.BadRequestException import BadRequestException
from jobcoin.errors.IllegalArgumentException import IllegalArgumentException
from jobcoin.errors.InsufficientFundsException import \
    InsufficientFundsException
from jobcoin.errors.JobcoinException import JobcoinException


class SendRequest:
    def __init__(self, address, amount):
        self.address = address
        self.amount = amount


class Transaction:
    def __init__(self, from_address, to_address, amount):
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount


class JobcoinClient:

    DISBURSEMENT_FEE_PERCENT = 4.0

    def __init__(self, address):
        logging.info("Initializing client with address %s", address)
        self.address = address

    def generate_coins(self):
        # TODO: Finish this
        requests.post(API_COIN_URL, data={"address": self.address})
        pass

    def send_coins(self, to_addresses, amount):
        successes = list()
        failures = list()
        # TODO: A more production-ready version ought to make this atomic
        for to_address in to_addresses:
            request = SendRequest(to_address, amount)
            try:
                result = self.send_coins_to_single_address(request)
                if result:
                    successes.append(request)
                else:
                    failures.append(request)
            except JobcoinException as jce:
                logging.error("There was an issue with this operation - %s", jce)
                failures.append(request)

        return successes, failures

    def send_coins_to_single_address(self, request):
        inputs = {
            "fromAddress": self.address,
            "toAddress": request.address,
            "amount": request.amount
        }
        logging.info("About to send %s to %s", request.amount, request.address)
        response = requests.post(API_TRANSACTIONS_URL, data=inputs)
        if response.status_code == HTTPStatus.OK.value:
            if self.verify_transaction(request):
                return request.amount
            else:
                logging.error("Could not assert that the transaction was present in the chain!")

        if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value:
            raise InsufficientFundsException("Insufficient Funds: {0}".format(response.text))

        if response.status_code == HTTPStatus.BAD_GATEWAY.value:
            raise BadRequestException("Bad request - %s", response.text)

    def verify_transaction(self, request):
        transactions = self.get_transactions()
        for transaction in reversed(transactions):
            txn = Transaction(transaction['fromAddress'], transaction['toAddress'], transaction['amount'])
            # Note: One might worry that this will give a false positive for older transactions
            # that were identical, if they exist.
            # However, because of the uniqueness of the newly-generated accounts, this should not happen.
            if txn.to_address == request.address and str(txn.amount) == str(request.amount):
                return True
        return False

    def disburse_funds(self, addresses, amount, apply_fee=True):
        amount_per_client = JobcoinClient.calculate_disbursement(addresses, amount, apply_fee)
        return self.send_coins(addresses, amount_per_client)

    @staticmethod
    def calculate_disbursement(addresses, amount, apply_fee):
        try:
            float(amount)
        except Exception:
            raise IllegalArgumentException("Bad input")

        if not addresses or not amount or amount < 0:
            raise IllegalArgumentException("Bad input")
        if apply_fee:
            percentage = 100 - JobcoinClient.DISBURSEMENT_FEE_PERCENT
            amount = (percentage / 100) * amount
        result = amount / len(addresses)
        return result

    @staticmethod
    def get_transactions():
        response = requests.get(API_TRANSACTIONS_URL)

        if response.status_code == HTTPStatus.OK:
            return json.loads(response.text)

        logging.error("Unexpected status code %d with response %s", response.status_code, response.text)
