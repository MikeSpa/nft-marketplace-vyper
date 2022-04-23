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
    _owner: indexed(address)
    _spender: indexed(address)
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


# @notice Change the owner of the contract
# @dev onlyOwner
# @param _newOwner The new owner
@external
def setOwner(_newOwner: address):
    assert msg.sender == self.owner, "MarketCoin: Only the owner can set a new owner"
    self.owner = _newOwner


# @notice Transfers _value amount of tokens to address _to
# @dev Emit a Transfer Event
# @param _to The address that should receive the token
# @param _value The amount of token to transfer
# @return True if transaction successful.
@external
def transfer(_to: address, _value: uint256) -> bool:
    assert _to != ZERO_ADDRESS, "MarketCoin: Can't transfer to ZERO_ADDRESS"
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    log Transfer(msg.sender, _to, _value)
    return True


# @notice Transfers _value amount of tokens from address _from to address _to
# @dev Emit a Transfer Event
# @param _from The address that sends the token
# @param _to The address that should receive the token
# @param _value The amount of token to transfer
# @return True if transaction successful.
@external 
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    self.balanceOf[_from] -= _value
    self.allowance[_from][msg.sender] -= _value
    self.balanceOf[_to] += _value
    log Transfer(_from, _to, _value)
    return True


# @notice Allows _spender to withdraw from the caller account multiple times, up to the _value amount
# @dev Emit a Approval Event
# @dev If this function is called again it overwrites the current allowance with _value
# @param _spender The address that can withdraw from the caller account
# @param _value The maximum amount of token that can then be transfer
# @return True if transaction successful.
@external
def approve(_spender: address, _value: uint256) -> bool:
    self.allowance[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True


# @notice Mint _amount of token to _to
# @dev Emit a Transfer Event
# @dev onlyOwner
# @param _to The address to which the token should be minted
# @param _amount The amount of token to be minted
@external
def mint(_to: address, _amount: uint256):

    assert msg.sender == self.owner, "MarketCoin: Only owner can mint token"
    assert _to != ZERO_ADDRESS, "MarketCoin: Can't mint to ZERO_ADDRESS"
    
    self.balanceOf[_to] += _amount
    
    self.totalSupply += _amount
    
    log Transfer(ZERO_ADDRESS, _to, _amount)


# @notice Burn _amount of token
# @dev Emit a Transfer Event
# @param _amount The amount of token to be burned
@external
def burn(_amount: uint256):
    self.balanceOf[msg.sender] -= _amount
    self.totalSupply -= _amount
    log Transfer(msg.sender, ZERO_ADDRESS, _amount)