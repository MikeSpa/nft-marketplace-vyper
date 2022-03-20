
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
allowance_mapping: public(HashMap[address, HashMap[address, uint256]])

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


# @view
# @external
# def name() -> String[100]:
#     return "MyToken"

# @view
# @external
# def symbol() -> String[5]:
#     return "MTK"

# @view
# @external
# def decimals() -> uint8:
#     return 8

# @view
# @external
# def totalSupply() -> uint256:
#     return 10**6 * 10**8


@view
@external
def balanceOf(_owner: address) -> uint256:
    owner_balance: uint256 = self.balances[_owner]
    return owner_balance
    

@external
def transfer(_to: address, _value: uint256) -> bool:
    #may actually reverrt du to underflow if not enough balance
    # so check unnecessary? need to test TODO
    # same for transferFrom
    # if (self.balances[msg.sender] >= _value):
    self.balances[msg.sender] -= _value
    self.balances[_to] += _value
    log Transfer(msg.sender, _to, _value)
    return True
    # return False

@external 
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    # allowed: bool = True 
    # if (_value <= self.allowance_mapping[_from][msg.sender]):
    # allowed = True
    # if ( allowed and self.balances[_from] >= _value):
    self.balances[_from] -= _value
    self.allowance_mapping[_from][msg.sender] -= _value
    self.balances[_to] += _value
    log Transfer(_from, _to, _value)
    return True
    # return False


@external
def approve(_spender: address, _value: uint256) -> bool:
    self.allowance_mapping[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True

@view
@external
def allowance(_owner: address, _spender: address) -> uint256:
    return self.allowance_mapping[_owner][_spender]
