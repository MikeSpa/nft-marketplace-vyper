import pytest
from scripts.helpful_scripts import get_account, ONE, ZERO_ADDRESS, POINT_ONE
import brownie

NAME = "NFT1"
SYMBOL = "1"
MINT_PRICE = ONE


@pytest.fixture
def marketplace(NFTMarketPlace):
    account = get_account()
    yield NFTMarketPlace.deploy({"from": account})


# Deploy an NFToken "1" and mint 30 token, 10 for each account
@pytest.fixture
def NFT1(NFToken):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    nftoken = NFToken.deploy(NAME, SYMBOL, MINT_PRICE, {"from": account})
    for a in [account, acc1, acc2]:
        for i in range(10):
            nftoken.mint({"value": ONE, "from": a})
    return nftoken


def test_initial_totalSupply(NFT1):
    assert NFT1.totalSupply() == 30


def test_set_fee(marketplace):
    assert marketplace.postingFee() == 0
    assert marketplace.sellingFee() == 0

    marketplace.setPostingFee(POINT_ONE)
    marketplace.setSellingFee(5)

    assert marketplace.postingFee() == POINT_ONE
    assert marketplace.sellingFee() == 5


def test_sell(marketplace, NFT1):
    account = get_account()
    # first tx approve the marketplace as operator
    tx = NFT1.setApprovalForAll(marketplace, True)

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_owner"] == account
    assert tx.events[0]["_operator"] == marketplace
    assert tx.events[0]["_approved"] == True

    # second tx list the token
    tx = marketplace.sell(
        NFT1.address, 0, ONE * 42, {"from": account, "value": ONE / 10}
    )

    # account remains the owner of the token
    assert NFT1.ownerOf(0) == account

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_seller"] == account
    assert tx.events[0]["_price"] == ONE * 42
    assert tx.events[0]["_nft"] == NFT1
    assert tx.events[0]["_tokenId"] == 0


def test_sell_revert(marketplace, NFT1):
    account = get_account()

    # fails because account don't own the token #10
    with brownie.reverts("Only the owner of the token can sell it"):
        tx = marketplace.sell(NFT1.address, 10, ONE * 42, {"from": account})

    # fails because marketplace not operator
    with brownie.reverts(
        "The marketplace doesn't have authorization to sell this token for this user"
    ):
        tx = marketplace.sell(NFT1.address, 0, ONE * 42, {"from": account})


def test_cancelSell(marketplace, NFT1):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    # Sell
    NFT1.setApprovalForAll(marketplace, True)
    marketplace.sell(NFT1.address, 0, ONE, {"from": account, "value": ONE})
    assert NFT1.ownerOf(0) == account

    # Cancel
    marketplace.cancelSell(0)

    assert marketplace.idToListing(0)[4] == 3


def test_cancelSell_revert(marketplace, NFT1):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    # Sell
    NFT1.setApprovalForAll(marketplace, True)
    # print(account)
    # print(acc1)
    # print(acc2)
    # for i in range(30):
    #     print(f"{i}: {NFT1.ownerOf(i)}")
    marketplace.sell(NFT1.address, 0, ONE, {"from": account, "value": ONE})
    marketplace.sell(NFT1.address, 1, ONE, {"from": account, "value": ONE})

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


def test_buy(marketplace, NFT1):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    # Sell
    NFT1.setApprovalForAll(marketplace, True)
    marketplace.sell(NFT1.address, 0, ONE, {"from": account, "value": ONE})
    assert NFT1.ownerOf(0) == account
    # Buy

    tx = marketplace.buy(0, {"from": acc1, "value": ONE})

    assert NFT1.ownerOf(0) == acc1

    # Test Event
    assert len(tx.events) == 2
    ## Transfer of NFT
    assert tx.events[0]["_from"] == account
    assert tx.events[0]["_to"] == acc1
    assert tx.events[0]["_tokenId"] == 0

    ## Sale
    assert tx.events[1]["_seller"] == account
    assert tx.events[1]["_buyer"] == acc1
    assert tx.events[1]["_price"] == ONE
    assert tx.events[1]["_nft"] == NFT1
    assert tx.events[1]["_tokenId"] == 0


##test buy revert if value too small, buying own stuff, already bought
