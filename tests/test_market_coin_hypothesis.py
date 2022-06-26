from scripts.helpful_scripts import ZERO_ADDRESS, get_account, ONE, POINT_ONE, CENT
import brownie

from brownie.test import strategy
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
