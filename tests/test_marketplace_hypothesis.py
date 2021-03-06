from scripts.helpful_scripts import ZERO_ADDRESS, get_account, ONE, POINT_ONE, CENT
import brownie
from brownie import Contract, MarketCoin, MarketNFT
import numpy as np
from decimal import *
import pytest
from brownie.test import given, strategy
from hypothesis import settings

NAME = "NFT1"
SYMBOL = "1"
MINT_PRICE = POINT_ONE
MARKETNFT_MINT_PRICE = POINT_ONE

ACCOUNT = "0x66aB6D9362d4F35596279692F0251Db635165871"
ACCOUNT1 = "0x33A4622B82D4c04a53e170c638B944ce27cffce3"
OWNER = "0xA868bC7c1AF08B8831795FAC946025557369F69C"


@pytest.fixture(scope="module", autouse=True)
def marketplace(NFTMarketPlace, MarketCoin):
    owner = get_account(index=8)
    marketcoin = MarketCoin.deploy(owner, {"from": owner})

    marketplace = NFTMarketPlace.deploy({"from": owner})
    marketnft = MarketNFT.deploy(marketplace, MARKETNFT_MINT_PRICE, {"from": owner})
    marketplace.setMarketCoin(marketcoin, {"from": owner})
    marketplace.setMarketNFT(marketnft, {"from": owner})
    marketcoin.setOwner(marketplace, {"from": owner})
    return marketplace


# Deploy an NFToken "1" and mint 30 token, 10 for each account
@pytest.fixture(scope="module", autouse=True)
def NFT1(NFToken):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    nftoken = NFToken.deploy(NAME, SYMBOL, MINT_PRICE, {"from": account})
    for a in [account, acc1, acc2]:
        for i in range(10):
            nftoken.mint({"value": MINT_PRICE, "from": a})
    return nftoken


@brownie.test.given(
    _value=strategy("uint256"),
    _tokenId=strategy("uint256", max_value=9),
)
def test_sell(NFT1, marketplace, _value, _tokenId):

    account = get_account()

    init_balance_account = account.balance()
    # first tx approve the marketplace as operator
    tx = NFT1.setApprovalForAll(marketplace, True)
    assert account.balance() == init_balance_account

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_owner"] == account
    assert tx.events[0]["_operator"] == marketplace
    assert tx.events[0]["_approved"] == True

    # second tx list the token
    tx = marketplace.sell(NFT1.address, _tokenId, _value, {"from": account})

    # account remains the owner of the token
    assert NFT1.ownerOf(_tokenId) == account

    assert account.balance() == init_balance_account - marketplace.postingFee()

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_seller"] == account
    assert tx.events[0]["_price"] == _value
    assert tx.events[0]["_nft"] == NFT1
    assert tx.events[0]["_tokenId"] == _tokenId


@brownie.test.given(
    _value=strategy("uint256", max_value=99000000000000000000),
    _tokenId=strategy("uint256", max_value=9),
    _buyer=strategy("address", exclude=ACCOUNT),
)
def test_buy(NFT1, marketplace, _value, _tokenId, _buyer):
    account = get_account()

    init_balance_account = account.balance()
    init_balance_buyer = _buyer.balance()

    # Sell
    NFT1.setApprovalForAll(marketplace, True)
    id = marketplace.sell(
        NFT1.address, _tokenId, _value, {"from": account}
    ).return_value
    priceNFT = marketplace.idToListing(id)[3]
    assert priceNFT == _value
    # Ownership
    assert NFT1.ownerOf(_tokenId) == account
    # Buy
    tx = marketplace.buy(id, {"from": _buyer, "value": priceNFT})

    # Money
    assert (
        account.balance() == init_balance_account + priceNFT - marketplace.postingFee()
    )
    assert _buyer.balance() == init_balance_buyer - priceNFT
    # Ownership
    assert NFT1.ownerOf(_tokenId) == _buyer

    # Test Event
    assert len(tx.events) == 5
    ## Transfer of NFT
    assert tx.events[0]["_from"] == account
    assert tx.events[0]["_to"] == _buyer
    assert tx.events[0]["_tokenId"] == _tokenId

    ## Test Transfer Event - Mint MarketCoin to seller
    assert tx.events[1]["_from"] == ZERO_ADDRESS
    assert tx.events[1]["_to"] == account
    assert tx.events[1]["_value"] == np.floor(Decimal(_value) / 10)

    ## Test Transfer Event - Mint MarketCoin to buyer
    assert tx.events[2]["_from"] == ZERO_ADDRESS
    assert tx.events[2]["_to"] == _buyer
    assert tx.events[2]["_value"] == np.floor(Decimal(_value) / 10)

    ## Update Listing
    assert tx.events[3]["_id"] == id
    assert tx.events[3]["_listing"][4] == 2

    ## Sale
    assert tx.events[4]["_seller"] == account
    assert tx.events[4]["_buyer"] == _buyer
    assert tx.events[4]["_price"] == _value
    assert tx.events[4]["_nft"] == NFT1
    assert tx.events[4]["_tokenId"] == _tokenId
