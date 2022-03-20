
# Token
# Implementation of https://eips.ethereum.org/EIPS/eip-20

# @version 0.3.1


event Transfer:
    _from: indexed(address)
    _to: indexed(address)
    _value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    _value: uint256

balances: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])

name: public(String[100])
symbol: public(String[5])
decimals: public(uint8)
totalSupply: public(uint256)

@external
def __init__(_name: String[100], _symbol: String[5], _decimals: uint8, _totalSupply: uint256):
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.totalSupply = _totalSupply * 10** convert(_decimals, uint256)
    self.balances[msg.sender] = self.totalSupply
    log Transfer(ZERO_ADDRESS, msg.sender, self.totalSupply)




@view
@external
def balanceOf(_owner: address) -> uint256:
    owner_balance: uint256 = self.balances[_owner]
    return owner_balance
    

@external
def transfer(_to: address, _value: uint256) -> bool:
    self.balances[msg.sender] -= _value
    self.balances[_to] += _value
    log Transfer(msg.sender, _to, _value)
    return True

@external 
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    self.balances[_from] -= _value
    self.allowance[_from][msg.sender] -= _value
    self.balances[_to] += _value
    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender: address, _value: uint256) -> bool:
    self.allowance[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True

