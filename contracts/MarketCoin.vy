# Token
# Implementation of https://eips.ethereum.org/EIPS/eip-20

# @version 0.3.1

from vyper.interfaces import ERC20
implements: ERC20

event Transfer:
    _from: indexed(address)
    _to: indexed(address)
    _value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    _value: uint256

balanceOf: public(HashMap[address, uint256])  # balance of an account
allowance: public(HashMap[address, HashMap[address, uint256]])

name: public(String[10])  # "MarketCoin"
symbol: public(String[2])  # "MC"
decimals: public(uint8)  # 18
totalSupply: public(uint256)  # Total supply of coin that has been minted
owner: public(address)  # Marketplace


@external
def __init__(_owner: address):
    self.name = "MarketCoin"
    self.symbol = "MC"
    self.decimals = 18
    self.owner = _owner


@external
def setOwner(_newOwner: address):
    assert msg.sender == self.owner
    self.owner = _newOwner


@external
def transfer(_to: address, _value: uint256) -> bool:
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    log Transfer(msg.sender, _to, _value)
    return True


@external 
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    self.balanceOf[_from] -= _value
    self.allowance[_from][msg.sender] -= _value
    self.balanceOf[_to] += _value
    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender: address, _value: uint256) -> bool:
    self.allowance[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True
