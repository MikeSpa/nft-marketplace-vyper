import pytest
from scripts.helpful_scripts import get_account, ONE, ZERO_ADDRESS
import brownie


NAME = "MarketNFT"
SYMBOL = "MNFT"
MINT_PRICE = ONE


@pytest.fixture
def marketNFT(MarketNFT):
    owner = get_account(index=8)
    yield MarketNFT.deploy(owner, MINT_PRICE, {"from": owner})


def test_contract_mint_price(marketNFT):
    assert marketNFT.mintPrice() == MINT_PRICE


def test_initial_totalSupply(marketNFT):
    assert marketNFT.totalSupply() == 0


def test_setMintPrice(marketNFT):
    assert marketNFT.mintPrice() == MINT_PRICE
    marketNFT.setMintPrice(8)
    assert marketNFT.mintPrice() == 8


def test_mint(marketNFT):
    account = get_account()
    marketNFT.mint({"from": account, "value": MINT_PRICE})
    assert marketNFT.balanceOf(account) == 1
    assert marketNFT.ownerOf(0) == account
    assert marketNFT.idToOwner(0) == account
    assert marketNFT.getApproved(0) == ZERO_ADDRESS
    assert marketNFT.totalSupply() == 1

    marketNFT.mint({"from": account, "value": MINT_PRICE})
    tx = marketNFT.mint({"from": account, "value": MINT_PRICE})
    assert marketNFT.balanceOf(account) == 3
    assert marketNFT.ownerOf(0) == account
    assert marketNFT.ownerOf(1) == account
    assert marketNFT.ownerOf(2) == account
    assert marketNFT.getApproved(1) == ZERO_ADDRESS
    assert marketNFT.totalSupply() == 3

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == ZERO_ADDRESS
    assert tx.events[0]["_to"] == account
    assert tx.events[0]["_tokenId"] == 2


def test_mint_revert_if_value_lower_than_price(marketNFT):
    account = get_account()
    # fails because you can't mint if you don't send `mintPrice`
    with brownie.reverts():
        marketNFT.mint({"value": MINT_PRICE / 2})


def test_approve(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketNFT.mint({"from": account, "value": MINT_PRICE})
    marketNFT.mint({"from": account, "value": MINT_PRICE})
    marketNFT.mint({"from": account, "value": MINT_PRICE})
    assert marketNFT.getApproved(0) == ZERO_ADDRESS
    marketNFT.approve(acc1, 0, {"from": account})
    marketNFT.approve(acc1, 1, {"from": account})
    tx = marketNFT.approve(acc2, 2, {"from": account})
    assert marketNFT.getApproved(0) == acc1
    assert marketNFT.getApproved(1) == acc1
    assert marketNFT.getApproved(2) == acc2

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_owner"] == account
    assert tx.events[0]["_approved"] == acc2
    assert tx.events[0]["_tokenId"] == 2


def test_approve_revert_if_not_owner(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketNFT.mint({"from": account, "value": MINT_PRICE})
    assert marketNFT.getApproved(0) == ZERO_ADDRESS
    marketNFT.approve(acc1, 0, {"from": account})
    assert marketNFT.getApproved(0) == acc1

    # fails because you can't approve unminted token
    with brownie.reverts():
        marketNFT.approve(acc1, 1, {"from": account})
    assert marketNFT.getApproved(1) == ZERO_ADDRESS

    # fails because you can't approve unowned token
    with brownie.reverts():
        marketNFT.approve(account, 0, {"from": acc2})
    assert marketNFT.getApproved(0) == acc1


def test_transferFrom(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketNFT.mint({"from": account, "value": MINT_PRICE})
    marketNFT.mint({"from": account, "value": MINT_PRICE})
    marketNFT.mint({"from": account, "value": MINT_PRICE})

    marketNFT.transferFrom(account, acc1, 1, {"from": account})
    marketNFT.transferFrom(account, acc2, 2, {"from": account})
    tx = marketNFT.transferFrom(acc1, acc2, 1, {"from": acc1})

    assert marketNFT.ownerOf(0) == account
    assert marketNFT.ownerOf(1) == acc2
    assert marketNFT.ownerOf(2) == acc2

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == acc1
    assert tx.events[0]["_to"] == acc2
    assert tx.events[0]["_tokenId"] == 1


def test_transferFrom_revert_if_not_owner(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketNFT.mint({"from": account, "value": MINT_PRICE})
    marketNFT.mint({"from": account, "value": MINT_PRICE})
    marketNFT.mint({"from": account, "value": MINT_PRICE})

    marketNFT.transferFrom(account, acc1, 1, {"from": account})
    marketNFT.transferFrom(account, acc2, 2, {"from": account})

    # fails because you can't transfer unminted token
    with brownie.reverts():
        marketNFT.transferFrom(account, acc2, 42, {"from": account})

    # fails because you can't transfer unowned token
    with brownie.reverts():
        marketNFT.transferFrom(acc1, acc2, 1, {"from": account})

    assert marketNFT.ownerOf(0) == account
    assert marketNFT.ownerOf(1) == acc1
    assert marketNFT.ownerOf(2) == acc2
    assert marketNFT.ownerOf(42) == ZERO_ADDRESS


def test_transferFrom_revert_if_to_ZERO_ADDRESS(marketNFT):
    account = get_account()
    marketNFT.mint({"from": account, "value": MINT_PRICE})

    # fails because you can't transfer to ZERO_ADDRESS
    with brownie.reverts():
        marketNFT.transferFrom(account, ZERO_ADDRESS, 0, {"from": account})

    assert marketNFT.ownerOf(0) == account


def test_transferFrom_remove_approval(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketNFT.mint({"from": account, "value": MINT_PRICE})
    marketNFT.mint({"from": account, "value": MINT_PRICE})

    # approve acc1 for token 0 and 1
    marketNFT.approve(acc1, 0, {"from": account})
    marketNFT.approve(acc1, 1, {"from": account})

    # acc1 now approved for token 0
    assert marketNFT.getApproved(0) == acc1
    assert marketNFT.getApproved(1) == acc1

    marketNFT.transferFrom(account, acc2, 0, {"from": account})

    # approved for token 0 has been deleted
    assert marketNFT.getApproved(0) == ZERO_ADDRESS
    # approved for token 1 didn't change
    assert marketNFT.getApproved(1) == acc1


def test_setApprovedForAll(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketNFT.mint({"from": account, "value": MINT_PRICE})
    marketNFT.mint({"from": account, "value": MINT_PRICE})

    # approve acc1 for token 0 and 1
    marketNFT.setApprovalForAll(acc1, True, {"from": account})

    # acc1 now approved for all token
    assert marketNFT.isApprovedForAll(account, acc1) == True
    assert marketNFT.isApprovedForAll(account, acc2) == False

    # account stil owner of token
    assert marketNFT.ownerOf(0) == account

    # Approved for all can transferFrom
    marketNFT.transferFrom(account, acc2, 0, {"from": acc1})

    # isApprovedForAll status unchanged
    assert marketNFT.isApprovedForAll(account, acc1) == True
    assert marketNFT.isApprovedForAll(account, acc2) == False

    # remove authorization
    tx = marketNFT.setApprovalForAll(acc1, False, {"from": account})

    # isApprovedForAll status now False
    assert marketNFT.isApprovedForAll(account, acc1) == False

    # fails because acc1 no longer operator
    with brownie.reverts():
        marketNFT.transferFrom(account, acc2, 1, {"from": acc1})

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_owner"] == account
    assert tx.events[0]["_operator"] == acc1
    assert tx.events[0]["_approved"] == False


def test_transfer_revert_if_token_doesnt_exist(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    marketNFT.mint({"from": account, "value": MINT_PRICE})

    # fails because account can't transfer token since neither owner nor approved
    with brownie.reverts():
        marketNFT.transferFrom(account, acc1, 1, {"from": account})
