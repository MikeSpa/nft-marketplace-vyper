import pytest
from scripts.helpful_scripts import (
    get_account,
    ONE,
    ZERO_ADDRESS,
    POINT_ONE,
    CENT,
)
import brownie
from brownie import Contract, MarketCoin

NAME = "NFT1"
SYMBOL = "1"
MINT_PRICE = POINT_ONE

# TODO assert balance everywhere


@pytest.fixture
def marketplace(NFTMarketPlace, MarketCoin):
    owner = get_account(index=8)
    marketcoin = MarketCoin.deploy(owner, {"from": owner})

    marketplace = NFTMarketPlace.deploy({"from": owner})
    marketplace.setMarketCoin(marketcoin, {"from": owner})
    marketcoin.setOwner(marketplace, {"from": owner})
    return marketplace


# Deploy an NFToken "1" and mint 30 token, 10 for each account
@pytest.fixture
def NFT1(NFToken):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    nftoken = NFToken.deploy(NAME, SYMBOL, MINT_PRICE, {"from": account})
    for a in [account, acc1, acc2]:
        for i in range(10):
            nftoken.mint({"value": MINT_PRICE, "from": a})
    return nftoken


def test_initial_totalSupply(NFT1):
    assert NFT1.totalSupply() == 30


def test_set_fee(marketplace):
    owner = get_account(index=8)
    assert marketplace.postingFee() == 0
    assert marketplace.sellingFee() == 0

    marketplace.setPostingFee(POINT_ONE, {"from": owner})
    marketplace.setSellingFee(5, {"from": owner})

    assert marketplace.postingFee() == POINT_ONE
    assert marketplace.sellingFee() == 5

    assert owner.balance() == CENT


def test_set_fee_revert(marketplace):
    acc1 = get_account(index=1)
    assert marketplace.postingFee() == 0
    assert marketplace.sellingFee() == 0

    # fails because marketplace not operator
    with brownie.reverts("Only the owner can do that"):
        marketplace.setPostingFee(POINT_ONE, {"from": acc1})
    # fails because marketplace not operator
    with brownie.reverts("Only the owner can do that"):
        marketplace.setSellingFee(5, {"from": acc1})

    assert marketplace.postingFee() == 0
    assert marketplace.sellingFee() == 0


def test_set_marketcoin(marketplace):
    account = get_account()
    owner = get_account(index=8)

    marketcoin = MarketCoin.deploy(account, {"from": account})
    with brownie.reverts("Only the owner can do that"):
        marketplace.setMarketCoin(marketcoin, {"from": account})
    marketplace.setMarketCoin(marketcoin, {"from": owner})


def test_sell(marketplace, NFT1):
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
    tx = marketplace.sell(NFT1.address, 0, ONE * 42, {"from": account})

    # account remains the owner of the token
    assert NFT1.ownerOf(0) == account

    assert account.balance() == init_balance_account - marketplace.postingFee()

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_seller"] == account
    assert tx.events[0]["_price"] == ONE * 42
    assert tx.events[0]["_nft"] == NFT1
    assert tx.events[0]["_tokenId"] == 0


def test_sell_revert(marketplace, NFT1):
    account = get_account()
    owner = get_account(index=8)

    # fails because account don't own the token #10
    with brownie.reverts("Only the owner of the token can sell it"):
        marketplace.sell(NFT1.address, 10, ONE * 42, {"from": account})

    # fails because marketplace not operator
    with brownie.reverts(
        "The marketplace doesn't have authorization to sell this token for this user"
    ):
        marketplace.sell(NFT1.address, 0, ONE * 42, {"from": account})

    marketplace.setPostingFee(POINT_ONE, {"from": owner})
    # fails because amount sent is below posting fee
    with brownie.reverts("Amount sent is below postingFee"):
        marketplace.sell(NFT1, 0, ONE, {"from": account})


def test_cancelSell(marketplace, NFT1):
    account = get_account()

    # Sell
    NFT1.setApprovalForAll(marketplace, True)
    marketplace.sell(NFT1.address, 0, ONE, {"from": account, "value": 0})
    assert NFT1.ownerOf(0) == account

    # Cancel
    marketplace.cancelSell(0, {"from": account})

    assert marketplace.idToListing(0)[4] == 3


def test_cancelSell_revert(marketplace, NFT1):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    # Sell
    NFT1.setApprovalForAll(marketplace, True)
    marketplace.sell(NFT1.address, 0, ONE, {"from": account, "value": 0})
    marketplace.sell(NFT1.address, 1, ONE, {"from": account, "value": 0})

    # fails because only seller can cancel
    with brownie.reverts("Only the seller can cancel"):
        marketplace.cancelSell(0, {"from": acc1})

    marketplace.buy(0, {"from": acc2, "value": ONE})
    # fails because token already bought
    with brownie.reverts("Token already sold"):
        marketplace.cancelSell(0, {"from": account})

    marketplace.cancelSell(1, {"from": account})
    # fails because listing already cancel
    with brownie.reverts("Token not for sale (already cancel or doesn't exist)"):
        marketplace.cancelSell(1, {"from": account})


def test_updateSell(marketplace, NFT1):
    account = get_account()
    acc1 = get_account(index=1)
    # Sell
    NFT1.setApprovalForAll(marketplace, True)
    marketplace.sell(NFT1.address, 0, ONE, {"from": account, "value": 0})
    marketplace.sell(NFT1.address, 1, ONE, {"from": account, "value": 0})

    tx = marketplace.updateSell(1, ONE * 2, {"from": account})

    assert marketplace.idToListing(1)[3] == ONE * 2

    # Test Event: Update Listing
    assert len(tx.events) == 1
    assert tx.events[0]["_id"] == 1
    assert tx.events[0]["_listing"][3] == ONE * 2

    # fails because value below price
    with brownie.reverts("Not enough ether sent"):
        marketplace.buy(1, {"from": acc1, "value": ONE})

    marketplace.buy(1, {"from": acc1, "value": ONE * 2})


def test_updateSell_revert(marketplace, NFT1):
    account = get_account()
    acc1 = get_account(index=1)
    # Sell
    NFT1.setApprovalForAll(marketplace, True)
    marketplace.sell(NFT1.address, 0, ONE, {"from": account, "value": ONE})
    # marketplace.sell(NFT1.address, 1, ONE, {"from": account, "value": ONE})

    # fails because same price
    with brownie.reverts("The price need to be different"):
        marketplace.updateSell(0, ONE, {"from": account})

    # fails because not seller
    with brownie.reverts("Only the seller can update"):
        marketplace.updateSell(0, ONE * 2, {"from": acc1})

    marketplace.buy(0, {"from": acc1, "value": ONE})
    # fails because not for sale
    with brownie.reverts("Token not for sale (already sold, cancel or doesn't exist)"):
        marketplace.updateSell(0, ONE * 2, {"from": account})


def test_buy(marketplace, NFT1):
    account = get_account()
    acc1 = get_account(index=1)

    init_balance_account = account.balance()
    init_balance_acc1 = acc1.balance()

    # Sell
    NFT1.setApprovalForAll(marketplace, True)
    marketplace.sell(NFT1.address, 0, ONE, {"from": account, "value": 0})
    priceNFT = marketplace.idToListing(0)[3]
    # Ownership
    assert NFT1.ownerOf(0) == account

    # Buy
    tx = marketplace.buy(0, {"from": acc1, "value": priceNFT})

    # Money
    assert account.balance() == init_balance_account + priceNFT
    assert acc1.balance() == init_balance_acc1 - priceNFT
    # Ownership
    assert NFT1.ownerOf(0) == acc1

    # Test Event
    assert len(tx.events) == 5
    ## Transfer of NFT
    assert tx.events[0]["_from"] == account
    assert tx.events[0]["_to"] == acc1
    assert tx.events[0]["_tokenId"] == 0

    ## Test Transfer Event - Mint MarketCoin to seller
    assert tx.events[1]["_from"] == ZERO_ADDRESS
    assert tx.events[1]["_to"] == account
    assert tx.events[1]["_value"] == ONE / 10

    ## Test Transfer Event - Mint MarketCoin to buyer
    assert tx.events[2]["_from"] == ZERO_ADDRESS
    assert tx.events[2]["_to"] == acc1
    assert tx.events[2]["_value"] == ONE / 10

    ## Update Listing
    assert tx.events[3]["_id"] == 0
    assert tx.events[3]["_listing"][4] == 2

    ## Sale
    assert tx.events[4]["_seller"] == account
    assert tx.events[4]["_buyer"] == acc1
    assert tx.events[4]["_price"] == ONE
    assert tx.events[4]["_nft"] == NFT1
    assert tx.events[4]["_tokenId"] == 0


def test_buy_revert(marketplace, NFT1):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    # Sell
    NFT1.setApprovalForAll(marketplace, True)
    marketplace.sell(NFT1.address, 0, ONE, {"from": account})
    marketplace.sell(NFT1.address, 1, ONE, {"from": account})
    marketplace.sell(NFT1.address, 2, ONE, {"from": account})

    # fails because value below price
    with brownie.reverts("Not enough ether sent"):
        marketplace.buy(0, {"from": acc1, "value": POINT_ONE})

    marketplace.buy(0, {"from": acc2, "value": ONE})
    # fails because token already bought
    with brownie.reverts("Token no longer for sale"):
        marketplace.buy(0, {"from": acc1, "value": ONE})

    marketplace.cancelSell(1, {"from": account})
    # fails because canceled
    with brownie.reverts("Token no longer for sale"):
        marketplace.buy(1, {"from": acc1, "value": ONE})

    # fails because listing doesn't exist
    with brownie.reverts("Listing doesn't exist"):
        marketplace.buy(3, {"from": acc1, "value": ONE})

    # should be able to buy your own stuff ERC721::transferFrom allows
    marketplace.buy(2, {"from": account, "value": ONE})


# should be possible, we still take the posting fee
def test_price_of_zero(marketplace, NFT1):
    account = get_account()
    acc1 = get_account(index=1)
    NFT1.setApprovalForAll(marketplace, True)
    marketplace.sell(NFT1.address, 0, 0, {"from": account})
    marketplace.buy(0, {"from": acc1})

    assert NFT1.ownerOf(0) == acc1


def test_withdraw(marketplace, NFT1):
    owner = get_account(index=8)
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    acc3 = get_account(index=3)
    acc4 = get_account(index=4)

    init_balance_owner = owner.balance()
    init_balance_account = account.balance()
    init_balance_acc1 = acc1.balance()
    init_balance_acc2 = acc2.balance()
    init_balance_acc3 = acc3.balance()
    init_balance_acc4 = acc4.balance()

    init_total_balance = (
        init_balance_owner
        + init_balance_account
        + init_balance_acc1
        + init_balance_acc2
        + init_balance_acc3
        + init_balance_acc4
        + marketplace.balance()
    )

    # Sell
    marketplace.setSellingFee(1, {"from": owner})
    assert marketplace.sellingFee() == 1

    NFT1.setApprovalForAll(marketplace, True, {"from": account})
    NFT1.setApprovalForAll(marketplace, True, {"from": acc1})
    NFT1.setApprovalForAll(marketplace, True, {"from": acc2})

    marketplace.sell(NFT1.address, 0, ONE, {"from": account, "value": 0})
    marketplace.sell(NFT1.address, 1, ONE, {"from": account, "value": 0})
    marketplace.sell(NFT1.address, 2, ONE, {"from": account, "value": 0})
    marketplace.sell(NFT1.address, 3, ONE, {"from": account, "value": 0})
    marketplace.sell(NFT1.address, 4, ONE, {"from": account, "value": 0})
    marketplace.sell(NFT1.address, 10, ONE, {"from": acc1, "value": 0})
    marketplace.sell(NFT1.address, 11, ONE, {"from": acc1, "value": 0})
    marketplace.sell(NFT1.address, 20, ONE, {"from": acc2, "value": 0})
    priceNFT = ONE
    # How much a seeler receive after the selling tax
    seller_get = priceNFT - priceNFT * 1 / 100

    # Buy
    marketplace.buy(0, {"from": acc1, "value": priceNFT})
    marketplace.buy(1, {"from": acc4, "value": priceNFT})
    marketplace.buy(2, {"from": acc4, "value": priceNFT})
    marketplace.buy(3, {"from": acc3, "value": priceNFT})
    marketplace.buy(4, {"from": acc3, "value": priceNFT})
    marketplace.buy(5, {"from": acc4, "value": priceNFT})
    marketplace.buy(6, {"from": acc1, "value": priceNFT})
    marketplace.buy(7, {"from": account, "value": priceNFT})

    # 8 Buy at price of ONE and 1% of fee
    total_fee = 8 * ONE * 1 / 100

    assert marketplace.balance() == total_fee

    # Withdraw
    marketplace.withdraw(total_fee, {"from": owner})

    # Money
    assert account.balance() == init_balance_account + 5 * seller_get - priceNFT
    assert acc1.balance() == init_balance_acc1 + 2 * seller_get - 2 * priceNFT
    assert acc2.balance() == init_balance_acc2 + seller_get
    assert acc3.balance() == init_balance_acc3 - 2 * priceNFT
    assert acc4.balance() == init_balance_acc4 - 3 * priceNFT

    assert owner.balance() == init_balance_owner + total_fee
    assert marketplace.balance() == 0

    assert (
        init_total_balance
        == owner.balance()
        + account.balance()
        + acc1.balance()
        + acc2.balance()
        + acc3.balance()
        + acc4.balance()
        + marketplace.balance()
    )

    with brownie.reverts("Only the owner can withdraw"):
        marketplace.withdraw(0, {"from": account})


def test_marketcoin_balance(marketplace, NFT1):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)

    marketCoin_address = marketplace.marketCoin()
    marketCoin = Contract.from_abi(MarketCoin._name, marketCoin_address, MarketCoin.abi)
    init_balance_account = marketCoin.balanceOf(account)
    init_balance_acc1 = marketCoin.balanceOf(acc1)
    init_balance_acc2 = marketCoin.balanceOf(acc2)

    # Sell
    NFT1.setApprovalForAll(marketplace, True)
    priceNFT = ONE
    marketplace.sell(NFT1.address, 0, priceNFT, {"from": account, "value": 0})
    marketplace.sell(NFT1.address, 1, priceNFT, {"from": account, "value": 0})
    marketplace.sell(NFT1.address, 2, priceNFT, {"from": account, "value": 0})
    marketplace.sell(NFT1.address, 3, priceNFT, {"from": account, "value": 0})

    # Buy
    tx = marketplace.buy(0, {"from": acc1, "value": priceNFT})
    marketplace.buy(1, {"from": acc1, "value": priceNFT})
    marketplace.buy(2, {"from": acc2, "value": priceNFT})
    marketplace.buy(3, {"from": account, "value": priceNFT})

    # Money
    assert marketCoin.balanceOf(account) == init_balance_account + 5 * priceNFT / 10
    assert marketCoin.balanceOf(acc1) == init_balance_acc1 + 2 * priceNFT / 10
    assert marketCoin.balanceOf(acc2) == init_balance_acc2 + priceNFT / 10
