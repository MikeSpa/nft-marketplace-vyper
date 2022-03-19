
# Token
# Implementation of https://eips.ethereum.org/EIPS/eip-20

# @version 0.3.1


balances: HashMap[address, uint256]
allowance_mapping: HashMap[address, HashMap[address, uint256]]

@external
def name() -> String[100]:
    return "MyToken"

@external
def symbol() -> String[5]:
    return "MTK"


@external
def decimals() -> uint8:
    return 8

@external
def totalSupply() -> uint256:
    return 10**6 * 10**8


@external
def balanceOf(_owner: address) -> uint256:
    owner_balance: uint256 = self.balances[_owner]
    return owner_balance
    

@external
def transfer(_to: address, _value: uint256) -> bool:
    if (self.balances[msg.sender] >= _value):
        self.balances[msg.sender] -= _value
        self.balances[_to] += _value
        return True
    return False

@external 
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    allowed: bool = True 
    if (_value <= self.allowance_mapping[_from][msg.sender]):
        allowed = True
    if ( allowed and self.balances[_from] >= _value):
        self.balances[_from] -= _value
        self.balances[_to] += _value
        return True
    return False


@external
def approve(_spender: address, _value: uint256) -> bool:
    self.allowance_mapping[msg.sender][_spender] = _value
    return True

@external
def allowance(_owner: address, _spender: address) -> uint256:
    return self.allowance_mapping[_owner][_spender]
