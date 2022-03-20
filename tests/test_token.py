import pytest
from scripts.helpful_scripts import get_account
import brownie


NAME = "MyToken"
SYMBOL = "MTK"
DECIMALS = 8
SUPPLY = 10 ** 6
TOTAL_SUPPLY = 10 ** 6 * 10 ** 8


@pytest.fixture
def token_contract(Token):
    account = get_account()
    yield Token.deploy(NAME, SYMBOL, DECIMALS, SUPPLY, {"from": account})


def test_contract_name(token_contract):
    assert token_contract.name() == NAME


def test_contract_symbol(token_contract):
    assert token_contract.symbol() == SYMBOL


def test_contract_decimals(token_contract):
    assert token_contract.decimals() == DECIMALS


def test_total_supply(token_contract):
    assert token_contract.totalSupply() == TOTAL_SUPPLY


def test_initial_balance(token_contract):
    account = get_account()
    assert token_contract.balanceOf(account) == TOTAL_SUPPLY


def test_transfer(token_contract, _value=100):
    account = get_account()
    acc2 = get_account(index=1)
    acc3 = get_account(index=2)
    token_contract.transfer(acc2, _value, {"from": account})
    assert token_contract.balanceOf(account) == TOTAL_SUPPLY - _value
    assert token_contract.balanceOf(acc2) == _value

    token_contract.transfer(acc3, _value, {"from": acc2})
    assert token_contract.balanceOf(account) == TOTAL_SUPPLY - _value
    assert token_contract.balanceOf(acc2) == 0
    assert token_contract.balanceOf(acc3) == _value


def test_transfer_revert_if_insufficient_supply(token_contract, _value=100):
    account = get_account()
    acc2 = get_account(index=1)
    acc3 = get_account(index=2)
    token_contract.transfer(acc2, _value, {"from": account})
    assert token_contract.balanceOf(account) == TOTAL_SUPPLY - _value
    assert token_contract.balanceOf(acc2) == _value

    with brownie.reverts():
        token_contract.transfer(acc3, _value * 2, {"from": acc2})


def test_approve(token_contract, _value=100):
    account = get_account()
    acc2 = get_account(index=1)

    assert token_contract.approve(acc2, _value, {"from": account})
    assert token_contract.allowance(account, acc2) == _value


def test_allowance(token_contract, _value=100):
    account = get_account()
    acc2 = get_account(index=1)
    acc3 = get_account(index=3)

    assert token_contract.approve(acc2, _value, {"from": account})
    assert token_contract.allowance(account, acc2) == _value
    assert token_contract.allowance(account, acc3) == 0


def test_transferFrom(token_contract, _value=100):
    account = get_account()
    acc2 = get_account(index=1)
    acc3 = get_account(index=2)

    # approve
    token_contract.approve(acc2, _value, {"from": account})
    token_contract.transferFrom(account, acc2, _value, {"from": acc2})

    assert token_contract.balanceOf(acc2) == _value


def test_transferFrom_revert_if_not_enough_allowance(token_contract, _value=100):
    account = get_account()
    acc2 = get_account(index=1)
    acc3 = get_account(index=2)

    # approve
    token_contract.approve(acc2, _value / 2, {"from": account})

    with brownie.reverts():
        token_contract.transferFrom(account, acc2, _value, {"from": acc2})


def test_transferFrom_revert_if_not_enough_balance(token_contract, _value=100):
    account = get_account()
    acc2 = get_account(index=1)
    acc3 = get_account(index=2)

    token_contract.transfer(acc2, _value, {"from": account})
    # approve
    token_contract.approve(account, 2 * _value, {"from": acc2})

    token_contract.transferFrom(acc2, account, _value, {"from": account})

    with brownie.reverts():
        token_contract.transferFrom(acc2, account, _value, {"from": account})


def test_event_transfer(token_contract, _value=100):
    account = get_account()
    acc2 = get_account(index=1)
    tx = token_contract.transfer(acc2, _value, {"from": account})

    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == account
    assert tx.events[0]["_to"] == acc2
    assert tx.events[0]["_value"] == _value


def test_event_transferFrom(token_contract, _value=100):
    account = get_account()
    acc2 = get_account(index=1)
    token_contract.approve(acc2, _value, {"from": account})
    tx = token_contract.transferFrom(account, acc2, _value, {"from": acc2})

    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == account
    assert tx.events[0]["_to"] == acc2
    assert tx.events[0]["_value"] == _value


# def test_


# def test_events(adv_storage_contract, accounts):
#     tx1 = adv_storage_contract.set(10, {'from': accounts[0])
#     tx2 = adv_storage_contract.set(20, {'from': accounts[1])
#     tx3 = adv_storage_contract.reset({'from': accounts[0])

#     # Check log contents
#     assert len(tx1.events) == 1
#     assert tx1.events[0]['value'] == 10

#     assert len(tx2.events) == 1
#     assert tx2.events[0]['setter'] == accounts[1]

#     assert not tx3.events
