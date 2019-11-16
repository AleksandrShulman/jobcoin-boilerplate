#!/usr/local/bin/python3
import re

import pytest
from click.testing import CliRunner

import cli


@pytest.fixture
def response():
    import requests
    return requests.get('https://jobcoin.gemini.com/')


def test_content(response):
    assert 'Hello!' in response.text


def test_cli_basic():
    input_address = "client_addr"
    runner = CliRunner()
    result = runner.invoke(cli.main, args=[input_address])
    assert result.exit_code == 0
    assert 'Welcome, {0} to the Jobcoin mixer'.format(
        input_address) in result.output


def test_cli_requires_input_address():
    runner = CliRunner()
    address_create_output = runner.invoke(cli.main).output
    assert "Missing argument" in address_create_output


def test_cli_creates_address():
    runner = CliRunner()
    address_create_output = runner.invoke(
        cli.main, args=["inputAddress"]).output
    output_re = re.compile(
        r'You may now send Jobcoins to address [0-9a-zA-Z]{32}. '
        'They will be mixed and sent to your destination addresses.'
    )
    assert output_re.search(address_create_output) is not None


def test_cli_end_to_end():
    ### TODO: Finish this
    runner = CliRunner()
    address_create_output = runner.invoke(
        cli.main, args=["inputAddress"]).output
    output_re = re.compile(
        r'You may now send Jobcoins to address [0-9a-zA-Z]{32}. '
        'They will be mixed and sent to your destination addresses.'
    )
    assert output_re.search(address_create_output) is not None


def test_cli_at_start_quit():
    runner = CliRunner()
    result = runner.invoke(cli.main, args=["inputAddress"], input="quit()")

    assert "Thank you" in result.output
    assert result.exit_code == 0


def test_cli_quit_at_amount():
    runner = CliRunner()
    result = runner.invoke(cli.main, args=["inputAddress"],
                           input="abc234\nquit()")

    assert "Have a good day" in result.output
    assert result.exit_code == 0


# TODO: Need a way to test this w/o actually sending any coins!
# This will need to somehow dependency-inject a mock client
# whose behavior we control.
# For now this is okay b/c it's going from known addresses to other known
# addresses, but then it can no longer be run as a unit test

def test_cli_quit_at_end():
    runner = CliRunner()
    result = runner.invoke(cli.main, args=["inputAddress"],
                           input="abc234\n2\nquit()")

    assert "Thank you for using Jobcoin" in result.output
    assert result.exit_code == 0


if __name__ == "__main__":
    pytest.main(["./test_cli.py", "-s"])
