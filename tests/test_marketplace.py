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
    for i in range(10):
        nftoken.mint({"value": ONE})
        nftoken.mint({"from": acc1, "value": ONE})
        nftoken.mint({"from": acc2, "value": ONE + ONE})
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
    print("GO")
    print(NFT1.address)
    print(marketplace.address)
    print(account.address)
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
