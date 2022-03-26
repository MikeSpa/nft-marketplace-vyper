import pytest
from scripts.helpful_scripts import get_account, ONE, ZERO_ADDRESS
import brownie


NAME = "MyNFToken"
SYMBOL = "MNFTK"
MINT_PRICE = ONE


@pytest.fixture
def nftoken_contract(NFToken):
    account = get_account()
    yield NFToken.deploy(NAME, SYMBOL, MINT_PRICE, {"from": account})


def test_contract_name(nftoken_contract):
    assert nftoken_contract.name() == NAME


def test_contract_symbol(nftoken_contract):
    assert nftoken_contract.symbol() == SYMBOL


def test_contract_mint_price(nftoken_contract):
    assert nftoken_contract.mintPrice() == MINT_PRICE


def test_initial_totalSupply(nftoken_contract):
    assert nftoken_contract.totalSupply() == 0


def test_setMintPrice(nftoken_contract):
    assert nftoken_contract.mintPrice() == MINT_PRICE
    nftoken_contract.setMintPrice(8)
    assert nftoken_contract.mintPrice() == 8


def test_mint(nftoken_contract):
    account = get_account()
    nftoken_contract.mint({"value": ONE})
    assert nftoken_contract.balanceOf(account) == 1
    assert nftoken_contract.ownerOf(0) == account
    assert nftoken_contract.idToOwner(0) == account
    assert nftoken_contract.getApproved(0) == ZERO_ADDRESS
    assert nftoken_contract.totalSupply() == 1

    nftoken_contract.mint({"value": ONE})
    tx = nftoken_contract.mint({"value": ONE})
    assert nftoken_contract.balanceOf(account) == 3
    assert nftoken_contract.ownerOf(0) == account
    assert nftoken_contract.ownerOf(1) == account
    assert nftoken_contract.ownerOf(2) == account
    assert nftoken_contract.getApproved(1) == ZERO_ADDRESS
    assert nftoken_contract.totalSupply() == 3

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == ZERO_ADDRESS
    assert tx.events[0]["_to"] == account
    assert tx.events[0]["_tokenId"] == 2


def test_mint_revert_if_value_lower_than_price(nftoken_contract):
    account = get_account()
    # fails because you can't mint if you don't send `mintPrice`
    with brownie.reverts():
        nftoken_contract.mint({"value": ONE / 2})


def test_approve(nftoken_contract):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    nftoken_contract.mint({"value": ONE})
    nftoken_contract.mint({"value": ONE})
    nftoken_contract.mint({"value": ONE})
    assert nftoken_contract.getApproved(0) == ZERO_ADDRESS
    nftoken_contract.approve(acc1, 0)
    nftoken_contract.approve(acc1, 1)
    tx = nftoken_contract.approve(acc2, 2)
    assert nftoken_contract.getApproved(0) == acc1
    assert nftoken_contract.getApproved(1) == acc1
    assert nftoken_contract.getApproved(2) == acc2

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_owner"] == account
    assert tx.events[0]["_approved"] == acc2
    assert tx.events[0]["_tokenId"] == 2


def test_approve_revert_if_not_owner(nftoken_contract):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    nftoken_contract.mint({"value": ONE})
    assert nftoken_contract.getApproved(0) == ZERO_ADDRESS
    nftoken_contract.approve(acc1, 0)
    assert nftoken_contract.getApproved(0) == acc1

    # fails because you can't approve unminted token
    with brownie.reverts():
        nftoken_contract.approve(acc1, 1)
    assert nftoken_contract.getApproved(1) == ZERO_ADDRESS

    # fails because you can't approve unowned token
    with brownie.reverts():
        nftoken_contract.approve(account, 0, {"from": acc2})
    assert nftoken_contract.getApproved(0) == acc1


def test_transferFrom(nftoken_contract):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    nftoken_contract.mint({"value": ONE})
    nftoken_contract.mint({"value": ONE})
    nftoken_contract.mint({"value": ONE})

    nftoken_contract.transferFrom(account, acc1, 1)
    nftoken_contract.transferFrom(account, acc2, 2)
    tx = nftoken_contract.transferFrom(acc1, acc2, 1, {"from": acc1})

    assert nftoken_contract.ownerOf(0) == account
    assert nftoken_contract.ownerOf(1) == acc2
    assert nftoken_contract.ownerOf(2) == acc2

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == acc1
    assert tx.events[0]["_to"] == acc2
    assert tx.events[0]["_tokenId"] == 1


def test_transferFrom_revert_if_not_owner(nftoken_contract):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    nftoken_contract.mint({"value": ONE})
    nftoken_contract.mint({"value": ONE})
    nftoken_contract.mint({"value": ONE})

    nftoken_contract.transferFrom(account, acc1, 1)
    nftoken_contract.transferFrom(account, acc2, 2)

    # fails because you can't transfer unminted token
    with brownie.reverts():
        nftoken_contract.transferFrom(account, acc2, 42, {"from": account})

    # fails because you can't transfer unowned token
    with brownie.reverts():
        nftoken_contract.transferFrom(acc1, acc2, 1, {"from": account})

    assert nftoken_contract.ownerOf(0) == account
    assert nftoken_contract.ownerOf(1) == acc1
    assert nftoken_contract.ownerOf(2) == acc2
    assert nftoken_contract.ownerOf(42) == ZERO_ADDRESS


def test_transferFrom_revert_if_to_ZERO_ADDRESS(nftoken_contract):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    nftoken_contract.mint({"value": ONE})

    # fails because you can't transfer to ZERO_ADDRESS
    with brownie.reverts():
        nftoken_contract.transferFrom(account, ZERO_ADDRESS, 0)

    assert nftoken_contract.ownerOf(0) == account


def test_transferFrom_remove_approval(nftoken_contract):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    nftoken_contract.mint({"value": ONE})
    nftoken_contract.mint({"value": ONE})

    # approve acc1 for token 0 and 1
    nftoken_contract.approve(acc1, 0)
    nftoken_contract.approve(acc1, 1)

    # acc1 now approved for token 0
    assert nftoken_contract.getApproved(0) == acc1
    assert nftoken_contract.getApproved(1) == acc1

    nftoken_contract.transferFrom(account, acc2, 0)

    # approved for token 0 has been deleted
    assert nftoken_contract.getApproved(0) == ZERO_ADDRESS
    # approved for token 1 didn't change
    assert nftoken_contract.getApproved(1) == acc1


def test_setApprovedForAll(nftoken_contract):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    nftoken_contract.mint({"value": ONE})
    nftoken_contract.mint({"value": ONE})

    # approve acc1 for token 0 and 1
    nftoken_contract.setApprovalForAll(acc1, True)

    # acc1 now approved for all token
    assert nftoken_contract.isApprovedForAll(account, acc1) == True
    assert nftoken_contract.isApprovedForAll(account, acc2) == False

    # account stil owner of token
    assert nftoken_contract.ownerOf(0) == account

    # Approved for all can transferFrom
    nftoken_contract.transferFrom(account, acc2, 0, {"from": acc1})

    # isApprovedForAll status unchanged
    assert nftoken_contract.isApprovedForAll(account, acc1) == True
    assert nftoken_contract.isApprovedForAll(account, acc2) == False

    # remove authorization
    tx = nftoken_contract.setApprovalForAll(acc1, False)

    # isApprovedForAll status now False
    assert nftoken_contract.isApprovedForAll(account, acc1) == False

    # fails because acc1 no longer operator
    with brownie.reverts():
        nftoken_contract.transferFrom(account, acc2, 1, {"from": acc1})

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_owner"] == account
    assert tx.events[0]["_operator"] == acc1
    assert tx.events[0]["_approved"] == False
