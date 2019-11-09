import time

from jobcoin.jobcoin import SendRequest


def gen_recipient_addresses(count):
    addresses = []
    for i in range(count):
        addresses.append("recipient_" + str(int(round(time.time() * 1000))))
    return addresses


def gen_send_requests_by_count(count, amount):
    return gen_send_requests(gen_recipient_addresses(count, amount))


def gen_send_requests(addresses, amount):
    send_requests = []
    for address in addresses:
        send_requests.append(SendRequest(address, amount))
    return send_requests
