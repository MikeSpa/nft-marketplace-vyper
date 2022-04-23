import pytest
from scripts.helpful_scripts import ZERO_ADDRESS, get_account, ONE, POINT_ONE, CENT
import brownie


NAME = "MarketCoin"
SYMBOL = "MC"
DECIMALS = 18
# SUPPLY = 10 ** 6
# TOTAL_SUPPLY = 10 ** 6 * 10 ** 8


@pytest.fixture
def marketCoin(MarketCoin):
    owner = get_account(index=8)
    yield MarketCoin.deploy(owner, {"from": owner})


def test_contract_name(marketCoin):
    assert marketCoin.name() == NAME


def test_contract_symbol(marketCoin):
    assert marketCoin.symbol() == SYMBOL


def test_contract_decimals(marketCoin):
    assert marketCoin.decimals() == DECIMALS


def test_initial_total_supply(marketCoin):
    assert marketCoin.totalSupply() == 0


def test_setOwner(marketCoin):
    owner = get_account(index=8)
    acc1 = get_account(index=1)

    marketCoin.setOwner(acc1, {"from": owner})
    assert marketCoin.owner() == acc1

    marketCoin.setOwner(owner, {"from": acc1})
    assert marketCoin.owner() == owner


def test_setOwner_revert(marketCoin):
    owner = get_account(index=8)
    acc1 = get_account(index=1)

    with brownie.reverts("MarketCoin: Only the owner can set a new owner"):
        marketCoin.setOwner(acc1, {"from": acc1})

    assert marketCoin.owner() == owner


def test_mint(marketCoin):
    owner = get_account(index=8)
    acc1 = get_account(index=1)
    marketCoin.mint(owner, CENT, {"from": owner})

    assert marketCoin.balanceOf(owner) == CENT
    assert marketCoin.balanceOf(acc1) == 0
    assert marketCoin.totalSupply() == CENT

    tx = marketCoin.mint(acc1, ONE, {"from": owner})

    assert marketCoin.balanceOf(owner) == CENT
    assert marketCoin.balanceOf(acc1) == ONE
    assert marketCoin.totalSupply() == CENT + ONE

    # Test Transfer Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == ZERO_ADDRESS
    assert tx.events[0]["_to"] == acc1
    assert tx.events[0]["_value"] == ONE


def test_mint_revert(marketCoin):
    owner = get_account(index=8)
    acc1 = get_account(index=1)

    with brownie.reverts("MarketCoin: Only owner can mint token"):
        marketCoin.mint(ZERO_ADDRESS, CENT, {"from": acc1})

    with brownie.reverts("MarketCoin: Can't mint to ZERO_ADDRESS"):
        marketCoin.mint(ZERO_ADDRESS, CENT, {"from": owner})

    assert marketCoin.totalSupply() == 0


def test_burn(marketCoin):
    owner = get_account(index=8)
    marketCoin.mint(owner, CENT)

    assert marketCoin.balanceOf(owner) == CENT
    assert marketCoin.totalSupply() == CENT

    tx = marketCoin.burn(CENT / 2, {"from": owner})

    assert marketCoin.balanceOf(owner) == CENT / 2
    assert marketCoin.totalSupply() == CENT / 2

    # Test Transfer Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == owner
    assert tx.events[0]["_to"] == ZERO_ADDRESS
    assert tx.events[0]["_value"] == CENT / 2


def test_burn_revert(marketCoin):
    owner = get_account(index=8)

    assert marketCoin.balanceOf(owner) == 0

    # fails because balance too low: underflow
    with brownie.reverts():
        marketCoin.burn(CENT, {"from": owner})


############## TRANSFER #######################


def test_transfer(marketCoin, _value=ONE):
    owner = get_account(index=8)
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    acc3 = get_account(index=3)
    marketCoin.mint(acc1, CENT, {"from": owner})

    assert marketCoin.totalSupply() == CENT

    acc1_init_balance = marketCoin.balanceOf(acc1)

    marketCoin.transfer(acc2, _value, {"from": acc1})

    assert marketCoin.balanceOf(acc1) == acc1_init_balance - _value
    assert marketCoin.balanceOf(acc2) == _value
    assert marketCoin.balanceOf(acc3) == 0

    # self transfer shouldn't change anyting
    marketCoin.transfer(acc1, _value, {"from": acc1})
    assert marketCoin.balanceOf(acc1) == acc1_init_balance - _value
    assert marketCoin.balanceOf(acc2) == _value
    assert marketCoin.balanceOf(acc3) == 0

    marketCoin.transfer(acc3, _value, {"from": acc1})
    tx = marketCoin.transfer(acc3, _value, {"from": acc2})

    assert marketCoin.balanceOf(acc1) == acc1_init_balance - 2 * _value
    assert marketCoin.balanceOf(acc2) == 0
    assert marketCoin.balanceOf(acc3) == 2 * _value

    # Test Transfer Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == acc2
    assert tx.events[0]["_to"] == acc3
    assert tx.events[0]["_value"] == _value

    assert marketCoin.totalSupply() == CENT


def test_transfer_revert(marketCoin, _value=ONE):
    owner = get_account(index=8)
    acc1 = get_account(index=1)
    acc2 = get_account(index=1)
    marketCoin.mint(acc1, ONE, {"from": owner})
    assert marketCoin.balanceOf(acc1) == ONE == _value

    # fails because undeflow
    with brownie.reverts():
        marketCoin.transfer(acc2, _value * 2, {"from": acc1})

    # fails because _to == ZERO
    with brownie.reverts("MarketCoin: Can't transfer to ZERO_ADDRESS"):
        marketCoin.transfer(ZERO_ADDRESS, _value, {"from": acc1})


def test_approve(marketCoin, _value=ONE):
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)

    tx = marketCoin.approve(acc2, _value, {"from": acc1})
    assert marketCoin.allowance(acc1, acc2) == _value

    # Test Approval Event
    assert len(tx.events) == 1
    assert tx.events[0]["_owner"] == acc1
    assert tx.events[0]["_spender"] == acc2
    assert tx.events[0]["_value"] == _value


def test_allowance(marketCoin, _value=ONE):
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    acc3 = get_account(index=3)

    assert marketCoin.approve(acc2, _value, {"from": acc1})
    assert marketCoin.allowance(acc1, acc2) == _value
    assert marketCoin.allowance(acc1, acc3) == 0


def test_transferFrom(marketCoin, _value=ONE):
    owner = get_account(index=8)
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketCoin.mint(acc1, CENT, {"from": owner})

    init_acc1_balance = marketCoin.balanceOf(acc1)
    init_acc2_balance = marketCoin.balanceOf(acc2)

    # approve
    marketCoin.approve(acc2, _value, {"from": acc1})
    tx = marketCoin.transferFrom(acc1, acc2, _value, {"from": acc2})

    assert marketCoin.balanceOf(acc1) == init_acc1_balance - _value
    assert marketCoin.balanceOf(acc2) == init_acc2_balance + _value

    # Test Transfer Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == acc1
    assert tx.events[0]["_to"] == acc2
    assert tx.events[0]["_value"] == _value


def test_transferFrom_revert(marketCoin, _value=ONE):
    owner = get_account(index=8)
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketCoin.mint(acc1, ONE, {"from": owner})

    # fails because no approval
    with brownie.reverts():
        marketCoin.transferFrom(acc1, acc2, _value, {"from": acc2})

    # approve
    marketCoin.approve(acc2, _value / 2, {"from": acc1})

    # fails because approval smaller than _value
    with brownie.reverts():
        marketCoin.transferFrom(acc1, acc2, _value, {"from": acc2})

    assert marketCoin.balanceOf(acc1) == ONE
    assert marketCoin.balanceOf(acc2) == 0

    # success
    tx = marketCoin.transferFrom(acc1, acc2, _value / 2, {"from": acc2})
    assert marketCoin.balanceOf(acc1) == ONE - _value / 2
    assert marketCoin.balanceOf(acc2) == _value / 2

    # approve
    marketCoin.approve(acc2, _value, {"from": acc1})

    # fails because approval smaller than _value
    with brownie.reverts():
        marketCoin.transferFrom(acc1, acc2, _value, {"from": acc2})

    assert marketCoin.balanceOf(acc1) == ONE - _value / 2
    assert marketCoin.balanceOf(acc2) == _value / 2
