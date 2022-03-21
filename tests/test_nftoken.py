import pytest
from scripts.helpful_scripts import get_account, ONE
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


def test_initial_supply(nftoken_contract):
    assert nftoken_contract.supply() == 0


def test_setMintPrice(nftoken_contract):
    assert nftoken_contract.mintPrice() == MINT_PRICE
    nftoken_contract.setMintPrice(8)
    assert nftoken_contract.mintPrice() == 8
