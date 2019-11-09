#!/usr/bin/env python
import logging
import sys
import uuid

import click

from jobcoin.jobcoin import JobcoinClient


@click.command()
@click.argument('address')
def main(address):
    click.echo('Welcome, {0} to the Jobcoin mixer!\n'.format(address))
    while True:
        # TODO: Fill out more of this
        addresses = click.prompt(
            'Please enter a comma-separated list of new, unused Jobcoin\n'
            'addresses where your mixed Jobcoins will be sent.\n',
            prompt_suffix='\n[quit() to exit] > ',
            default='',
            show_default=False)
        if addresses.strip().lower() == 'quit()':
            click.echo("Thank you for using Jobcoin!\n\n\n")
            sys.exit(0)
        addresses = addresses.split(',')
        deposit_address = uuid.uuid4().hex
        click.echo(
            '\nYou may now send Jobcoins to address {deposit_address}. They '
            'will be mixed and sent to your destination addresses.\n'.format(
                deposit_address=deposit_address))
        amount = click.prompt('Please enter the total amount of Jobcoins to mix',
                              prompt_suffix='\n[quit() to exit] > ',
                              default='',
                              show_default=False)
        if not amount or amount.strip().lower() == 'quit()':
            click.echo("Have a good day!")
            sys.exit(0)

        # Ok send them from the current user's account (which is?) to the newly-creatd account
        jobcoin_client = JobcoinClient(address)

        successes, failures = jobcoin_client.send_coins([deposit_address], amount)
        if failures:
            failure = failures[0]
            click.echo("Failed to send {0} coins to {1}. Please try again.\n\n".format(
                failure.amount, failure.address))
            continue
        click.echo(
            '\nJust sent {amount} jobcoins to {deposit_address}. Please standby for disbursement.'
            '\nThere will be a standard {disbursement_fee_percent} percent fee.\n'.format(
                amount=amount, deposit_address=deposit_address,
                disbursement_fee_percent=JobcoinClient.DISBURSEMENT_FEE_PERCENT))

        # Then do the transfer from the parent account to the supplied accounts (w/a little randomization)
        disbursement_client = JobcoinClient(deposit_address)

        successes, failures = disbursement_client.disburse_funds(addresses, amount)
        if len(failures):
            click.echo("Did not distribute all of the funds! Please retry the following transactions:")
            for txn in failures:
                print(txn)
            continue

        total_new_funds_available = sum([x.amount for x in successes])
        click.echo("Please expect {0} jobcoins to be available across accounts {1}.".format(
            total_new_funds_available, ",".join(addresses)))
        click.echo("Thank you for using Jobcoin!\n\n\n")


if __name__ == '__main__':
    sys.exit(main())
