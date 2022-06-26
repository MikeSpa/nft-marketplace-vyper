from scripts.helpful_scripts import ZERO_ADDRESS, get_account, ONE, POINT_ONE, CENT
import brownie

import pytest
from brownie.test import given, strategy
from hypothesis import settings

ACCOUNT1 = "0x33A4622B82D4c04a53e170c638B944ce27cffce3"
OWNER = "0xA868bC7c1AF08B8831795FAC946025557369F69C"


@brownie.test.given(
    _value=strategy("uint256"),
    _to=strategy("address", exclude=[ACCOUNT1, ZERO_ADDRESS]),
)
@settings(max_examples=50)
def test_mint(MarketCoin, _value, _to):
    owner = get_account(index=8)
    marketCoin = MarketCoin.deploy(owner, {"from": owner})

    tx = marketCoin.mint(_to, _value, {"from": owner})

    assert marketCoin.balanceOf(_to) == _value
    assert marketCoin.totalSupply() == _value

    # Test Transfer Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == ZERO_ADDRESS
    assert tx.events[0]["_to"] == _to
    assert tx.events[0]["_value"] == _value


@brownie.test.given(
    _value=strategy("uint256", max_value=CENT),
)
@settings(max_examples=50)
def test_burn(MarketCoin, _value):
    owner = get_account(index=8)
    marketCoin = MarketCoin.deploy(owner, {"from": owner})
    marketCoin.mint(owner, CENT)

    assert marketCoin.balanceOf(owner) == CENT
    assert marketCoin.totalSupply() == CENT

    tx = marketCoin.burn(_value, {"from": owner})

    assert marketCoin.balanceOf(owner) == CENT - _value
    assert marketCoin.totalSupply() == CENT - _value

    # Test Transfer Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == owner
    assert tx.events[0]["_to"] == ZERO_ADDRESS
    assert tx.events[0]["_value"] == _value


@brownie.test.given(
    _value=strategy("uint256"),
    _to=strategy("address", exclude=[ACCOUNT1, ZERO_ADDRESS]),
)
@settings(max_examples=50)
def test_transfer(MarketCoin, _value, _to):

    owner = get_account(index=8)
    marketCoin = MarketCoin.deploy(owner, {"from": owner})
    acc1 = get_account(index=1)

    marketCoin.mint(acc1, _value, {"from": owner})

    assert marketCoin.totalSupply() == _value

    acc1_init_balance = marketCoin.balanceOf(acc1)
    tx = marketCoin.transfer(_to, _value, {"from": acc1})

    assert marketCoin.balanceOf(acc1) == 0
    assert marketCoin.balanceOf(acc1) == acc1_init_balance - _value
    assert marketCoin.balanceOf(_to) == _value

    # Test Transfer Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == acc1
    assert tx.events[0]["_to"] == _to
    assert tx.events[0]["_value"] == _value


@brownie.test.given(
    _value=strategy("uint256"),
    _to=strategy("address", exclude=[OWNER, ZERO_ADDRESS]),
)
@settings(max_examples=50)
def test_transferFrom(MarketCoin, _value, _to):
    owner = get_account(index=8)
    print(owner)
    marketCoin = MarketCoin.deploy(owner, {"from": owner})
    marketCoin.mint(owner, _value, {"from": owner})

    init_owner_balance = marketCoin.balanceOf(owner)
    init_to_balance = marketCoin.balanceOf(_to)

    # approve
    marketCoin.approve(_to, _value, {"from": owner})
    tx = marketCoin.transferFrom(owner, _to, _value, {"from": _to})

    assert marketCoin.balanceOf(owner) == init_owner_balance - _value
    assert marketCoin.balanceOf(_to) == init_to_balance + _value

    # Test Transfer Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == owner
    assert tx.events[0]["_to"] == _to
    assert tx.events[0]["_value"] == _value
