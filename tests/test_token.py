import pytest
from scripts.helpful_scripts import get_account


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
