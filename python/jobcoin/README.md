# Jobcoin CLI and Library

## Purpose
The purpose of this mixer is to disguise the source of funds into 
an account when paying from that account.

Just enter the accounts from which you'd like to eventually withdraw money.

The mixer will create a dummy account to which to send the funds.
It will send the funds there. From there, the funds are later 
(at some random point in the future to avoid being conspicuous),
sent to the provided accounts and are usable.

Please note that there is a fee (default 4%), to any money transferred.

### Usage
$> cli.py [user_address]

### Example
Sample input:
>$> cli.py abc

Sample output:
>Welcome, abc to the Jobcoin mixer!
>
>Please enter a comma-separated list of new, unused Jobcoin
>addresses where your mixed Jobcoins will be sent.
>
>[quit() to exit] > abc123, zyx23, lkjd992
>
>You may now send Jobcoins to address e191d29dd4db4ac6b1acf15c800abff6. They will be mixed and sent to your destination addresses.
>
>Please enter the total amount of Jobcoins to mix
>[quit() to exit] > 3.4
>
>Just sent 3.4 jobcoins to e191d29dd4db4ac6b1acf15c800abff6. Please standby for disbursement.....
>There will be a standard 4.0 percent fee.
>
>Please expect 3.2639999999999993 jobcoins to be available across accounts abc123, zyx23, lkjd992.
>Thank you for using Jobcoin!
>
>
>
>Please enter a comma-separated list of new, unused Jobcoin
>addresses where your mixed Jobcoins will be sent.
>
>[quit() to exit] > 


## Failure Modes
### Insufficient Funds
There will be an error indicating that there are not enough
funds. Right now we can potentially find out mid-transaction
that there are not enough coins. Ideally, we'd do a check beforehand,
and/or implement atomicity.
#### Example
>[quit() to exit] > abc123, zyx23, lkjd992
>
>You may now send Jobcoins to address 58dcbead4fc54489a5f201fa03eb9d15. They will be mixed and sent to your destination addresses.
>
>Please enter the total amount of Jobcoins to mix
>[quit() to exit] > 3.4
>Failed to send 3.4 coins to 58dcbead4fc54489a5f201fa03eb9d15. Please try again.
>ERROR:root:There was an issue with this operation - Insufficient Funds: {"error":"abc only has 0.6 jobcoins!"}

### Partial Transactions
It's possible that not all the provided accounts will receive money.
In that case, the CLI provides info about which funds failed to be distributed.

Still, it would be much better if the client had retry semantics. This would be a great feature for follow-on work.

## Testing
### Prerequesites
Please make sure install all the necessary libraries by using requirements.txt
before running, or make sure the requirements are otherwise met.
> pip install -r tests/requirements.txt

You can run all tests using:
> python -m pytest tests/

There are two categories of tests:
- Unit: Work only on the local code and have no need for a network connection. They should give a 
quick reading as to the general health of the code.

> python -m pytest tests/unit

- Integration: These tests can be run anywhere, as long as they have access to the hosts
specified in the configuration file. They work on live data and are generally written in such a way
as to minimize the amount of data actually written to the blockchain.

> python -m pytest tests/integration

Your results should look similar to this:
>Aleksandrs-MacBook-Pro:python aleksandrshulman$ python3 -m pytest ./tests/

>===================== test session starts ==============================

>platform darwin -- Python 3.7.4, pytest-5.2.1, py-1.8.0, pluggy-0.13.0

>rootdir: /Users/aleksandrshulman/development/jobcoin-boilerplate/python

>collected 22 items                                                                                                                    

>tests/integration/test_cli.py ........                          [ 36%]

>tests/integration/test_get_transactions.py .                    [ 40%]

>tests/unit/test_rest_client.py .............                    [100%]

>======================== 22 passed in 3.47s =================


You are also welcome to add other parameters to pytest, for performance and/or verbosity tuning. For example, -n will allow for parallelized test execution.

# Future Work

## Make jobcoin transfer atomic. This may require some work in the webapp to properly
implement. For now, all the client can do is triage/retry when something
abnormal happens in one or more of the transactions.

## Automate Jobcoin creation
This will require finding out the exact API call that adds jobcoins to an account
and automating that.

## More testing
### More functional testing where indicated.
### Rounding errors
In particular these can be tricky and
the various string<->float conversions that take place
need to be vetted for all types of inputs.

### Input Vetting
Not all edge cases have been tested, and in particular, malicious input
needs to be examined.

### Multiple Jobcoin Clients Running In Parallel
Although the random account creation is supposed to provide isolation in some respects, 
if more than one client is operating on a shared account, there may be some race conditions.
This is more a problem for the webapp than the client, but there may be lurking
interesting race conditions that may be hard to predict apriori.

## Error handling semantics
Should give more thought into how errors in the REST client
will map into the CLI layer without leaking implementation details.

In particular, separating out the behavior in the case of a 5xx (as opposed to a 4xx like is defined in the API spec.)
This kind of touches on the core web service itself which we don't have access to, but
we should still do the best we can.

## Test runner
Create a more sophisticated test runner that will run the unit
and integration tests separately.


## Linter
Add a linter so that code checkins keep code quality high.
They will keep the code conformant to pep8.
For log imports, isort will be used to detect improperly formatted imports.

## Code Coverage
Add codecov or cobertura to the build process in order to verify that newly-added
features are well tested.
