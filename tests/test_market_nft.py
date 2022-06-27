import pytest
from scripts.helpful_scripts import get_account, ONE, ZERO_ADDRESS
import brownie


NAME = "MarketNFT"
SYMBOL = "MNFT"
MINT_PRICE = ONE


@pytest.fixture
def marketNFT(MarketNFT):
    owner = get_account(index=8)
    account = get_account()
    yield MarketNFT.deploy(account, MINT_PRICE, {"from": owner})


def test_contract_name(marketNFT):
    assert marketNFT.name() == NAME


def test_contract_symbol(marketNFT):
    assert marketNFT.symbol() == SYMBOL


def test_contract_mint_price(marketNFT):
    assert marketNFT.mintPrice() == MINT_PRICE


def test_initial_totalSupply(marketNFT):
    assert marketNFT.totalSupply() == 0


def test_balanceOf(marketNFT):
    account = get_account()
    assert marketNFT.balanceOf(account) == 0
    marketNFT.mint(account, {"from": account})
    assert marketNFT.balanceOf(account) == 1
    # fails because address is 0x00
    with brownie.reverts("MarketNFT: ZERO_ADDRESS cannot own NFTs"):
        marketNFT.balanceOf(ZERO_ADDRESS)


def test_ownerOf(marketNFT):
    account = get_account()
    with brownie.reverts("MarketNFT: Token doesn't exist"):
        marketNFT.ownerOf(0) == ZERO_ADDRESS

    marketNFT.mint(account, {"from": account})
    marketNFT.ownerOf(0) == account


def test_setMintPrice(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    assert marketNFT.mintPrice() == MINT_PRICE
    marketNFT.setMintPrice(8, {"from": account})
    assert marketNFT.mintPrice() == 8

    with brownie.reverts("MarketNFT: Only owner can do that"):
        marketNFT.setMintPrice(42, {"from": acc1})


def test_mint(marketNFT):
    account = get_account()
    marketNFT.mint(account, {"from": account})
    assert marketNFT.balanceOf(account) == 1
    assert marketNFT.ownerOf(0) == account
    assert marketNFT.idToOwner(0) == account
    assert marketNFT.getApproved(0) == ZERO_ADDRESS
    assert marketNFT.totalSupply() == 1

    marketNFT.mint(account, {"from": account})
    tx = marketNFT.mint(account, {"from": account})
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


def test_mint_argument_to(marketNFT):
    # test that mint send the NFT to the _to address and not the minter
    account = get_account()
    acc1 = get_account(index=1)
    marketNFT.mint(acc1, {"from": account})
    assert marketNFT.balanceOf(acc1) == 1
    assert marketNFT.ownerOf(0) == acc1
    assert marketNFT.idToOwner(0) == acc1
    assert marketNFT.getApproved(0) == ZERO_ADDRESS
    assert marketNFT.totalSupply() == 1

    marketNFT.mint(acc1, {"from": account})
    tx = marketNFT.mint(acc1, {"from": account})
    assert marketNFT.balanceOf(acc1) == 3
    assert marketNFT.ownerOf(0) == acc1
    assert marketNFT.ownerOf(1) == acc1
    assert marketNFT.ownerOf(2) == acc1
    assert marketNFT.getApproved(1) == ZERO_ADDRESS
    assert marketNFT.totalSupply() == 3

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == ZERO_ADDRESS
    assert tx.events[0]["_to"] == acc1
    assert tx.events[0]["_tokenId"] == 2


def test_mint_revert(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)

    with brownie.reverts("MarketNFT: Only owner of MarketNFT can mint"):
        marketNFT.mint(acc1, {"from": acc1})

    marketNFT.mint(account, {"from": account})


def test_burn(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    marketNFT.mint(acc1, {"from": account})
    marketNFT.mint(acc1, {"from": account})
    marketNFT.mint(acc1, {"from": account})

    assert marketNFT.balanceOf(acc1) == 3
    assert marketNFT.ownerOf(0) == marketNFT.ownerOf(1) == marketNFT.ownerOf(2) == acc1
    assert marketNFT.totalSupply() == 3
    assert marketNFT.nextTokenId() == 3

    tx = marketNFT.burn(1, {"from": account})

    assert marketNFT.balanceOf(acc1) == 2
    assert marketNFT.ownerOf(0) == marketNFT.ownerOf(2) == acc1
    # fails because tokenId 1 doesn't exist anymore
    with brownie.reverts("MarketNFT: Token doesn't exist"):
        marketNFT.ownerOf(1)
    assert marketNFT.totalSupply() == 2
    assert marketNFT.nextTokenId() == 3

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == acc1
    assert tx.events[0]["_to"] == ZERO_ADDRESS
    assert tx.events[0]["_tokenId"] == 1

    # mint continue at token 3
    tx = marketNFT.mint(acc1, {"from": account})

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == ZERO_ADDRESS
    assert tx.events[0]["_to"] == acc1
    assert tx.events[0]["_tokenId"] == 3
    assert marketNFT.balanceOf(acc1) == 3


def test_burn_revert(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    marketNFT.mint(acc1, {"from": account})
    marketNFT.mint(acc1, {"from": account})
    marketNFT.mint(acc1, {"from": account})

    assert marketNFT.balanceOf(acc1) == 3
    assert marketNFT.ownerOf(0) == marketNFT.ownerOf(1) == marketNFT.ownerOf(2) == acc1
    assert marketNFT.totalSupply() == 3
    assert marketNFT.nextTokenId() == 3

    # fails because tokenId 3 doesn't exist
    with brownie.reverts():
        marketNFT.burn(3, {"from": account})
    # fails because acc1 not owner of MarketNFT
    with brownie.reverts("MarketNFT: Only owner of MarketNFT can burn"):
        marketNFT.burn(0, {"from": acc1})

    marketNFT.burn(0, {"from": account})
    # fails because tokenId 0 doesn't exist anymore (already burnt)
    with brownie.reverts():
        marketNFT.burn(0, {"from": account})


def test_approve(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketNFT.mint(account, {"from": account})
    marketNFT.mint(account, {"from": account})
    marketNFT.mint(account, {"from": account})
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
    marketNFT.mint(account, {"from": account})
    assert marketNFT.getApproved(0) == ZERO_ADDRESS
    marketNFT.approve(acc1, 0, {"from": account})
    assert marketNFT.getApproved(0) == acc1

    # fails because you can't approve unminted token
    with brownie.reverts("MarketNFT: Caller not approved"):
        marketNFT.approve(acc1, 1, {"from": account})
    assert marketNFT.getApproved(1) == ZERO_ADDRESS

    # fails because you can't approve unowned token
    with brownie.reverts("MarketNFT: Caller not approved"):
        marketNFT.approve(account, 0, {"from": acc2})
    assert marketNFT.getApproved(0) == acc1


def test_transferFrom(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketNFT.mint(account, {"from": account})
    marketNFT.mint(account, {"from": account})
    marketNFT.mint(account, {"from": account})

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
    marketNFT.mint(account, {"from": account})
    marketNFT.mint(account, {"from": account})
    marketNFT.mint(account, {"from": account})

    marketNFT.transferFrom(account, acc1, 1, {"from": account})
    marketNFT.transferFrom(account, acc2, 2, {"from": account})

    # fails because you can't transfer unminted token
    with brownie.reverts("MarketNFT: Caller not approved"):
        marketNFT.transferFrom(account, acc2, 42, {"from": account})

    # fails because you can't transfer unowned token
    with brownie.reverts("MarketNFT: Caller not approved"):
        marketNFT.transferFrom(acc1, acc2, 1, {"from": account})

    assert marketNFT.ownerOf(0) == account
    assert marketNFT.ownerOf(1) == acc1
    assert marketNFT.ownerOf(2) == acc2
    with brownie.reverts("MarketNFT: Token doesn't exist"):
        marketNFT.ownerOf(42)


def test_transferFrom_revert_if_to_ZERO_ADDRESS(marketNFT):
    account = get_account()
    marketNFT.mint(account, {"from": account})

    # fails because you can't transfer to ZERO_ADDRESS
    with brownie.reverts("MarketNFT: Can't transfer to null address"):
        marketNFT.transferFrom(account, ZERO_ADDRESS, 0, {"from": account})

    assert marketNFT.ownerOf(0) == account


def test_transferFrom_remove_approval(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketNFT.mint(account, {"from": account})
    marketNFT.mint(account, {"from": account})

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


def test_safeTransferFrom(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketNFT.mint(account, {"from": account})
    marketNFT.mint(account, {"from": account})
    marketNFT.mint(account, {"from": account})

    # regular safeTransferFrom to an EOA with no data
    marketNFT.safeTransferFrom(account, acc1, 1, {"from": account})
    # regular safeTransferFrom to an EOA with data
    marketNFT.safeTransferFrom(account, acc2, 2, 0x6E7370616872, {"from": account})
    tx = marketNFT.safeTransferFrom(acc1, acc2, 1, 0x766972676F72756661, {"from": acc1})

    assert marketNFT.ownerOf(0) == account
    assert marketNFT.ownerOf(1) == acc2
    assert marketNFT.ownerOf(2) == acc2

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_from"] == acc1
    assert tx.events[0]["_to"] == acc2
    assert tx.events[0]["_tokenId"] == 1

    # fails because caller not approved
    with brownie.reverts("MarketNFT: Caller not approved"):
        marketNFT.safeTransferFrom(account, acc2, 1, {"from": acc1})


def test_safeTransferFrom_to_contract(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketNFT.mint(account, {"from": account})
    marketNFT.mint(account, {"from": account})
    marketNFT.mint(account, {"from": account})

    # fails because contract not ERC721Receiver
    with brownie.reverts():
        marketNFT.safeTransferFrom(account, marketNFT, 1, {"from": account})


def test_setApprovedForAll(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketNFT.mint(account, {"from": account})
    marketNFT.mint(account, {"from": account})

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
    with brownie.reverts("MarketNFT: Caller not approved"):
        marketNFT.transferFrom(account, acc2, 1, {"from": acc1})

    # Test Event
    assert len(tx.events) == 1
    assert tx.events[0]["_owner"] == account
    assert tx.events[0]["_operator"] == acc1
    assert tx.events[0]["_approved"] == False


def test_transfer_revert_if_token_doesnt_exist(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    marketNFT.mint(account, {"from": account})

    # fails because account can't transfer token since neither owner nor approved
    with brownie.reverts("MarketNFT: Caller not approved"):
        marketNFT.transferFrom(account, acc1, 1, {"from": account})


def test_remove_token_revert(marketNFT):
    account = get_account()
    acc1 = get_account(index=1)
    acc2 = get_account(index=2)
    marketNFT.mint(account, {"from": account})
    marketNFT.mint(acc1, {"from": account})

    # acc1 give approval to account
    assert marketNFT.ownerOf(1) == acc1
    marketNFT.approve(account, 1, {"from": acc1})

    # fails because account doesn't own token 1
    with brownie.reverts("MarketNFT: Not owner of the token"):
        marketNFT.transferFrom(account, acc2, 1, {"from": account})


def test_add_token_revert(marketNFT):
    account = get_account()
    marketNFT.mint(account, {"from": account})

    # fails because ZERO_ADDRESS can't receive NFT
    with brownie.reverts("MarketNFT: Can't transfer to null address"):
        marketNFT.mint(ZERO_ADDRESS, {"from": account})


def test_supportsInterface(marketNFT):

    assert marketNFT.supportsInterface(0x80AC58CD)  # ERC721
    assert marketNFT.supportsInterface(0x5B5E139F) == False  # ERC721Metadata
    assert marketNFT.supportsInterface(0x780E9D63) == False  # ERC721Enumerable
    assert marketNFT.supportsInterface(0xFFFFFFFF) == False
