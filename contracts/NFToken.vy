# NFT Token
# https://eips.ethereum.org/EIPS/eip-721
# @version 0.3.1

from vyper.interfaces import ERC721
implements: ERC721

interface ERC721Receiver:
    def onERC721Received(
            _operator: address,
            _from: address,
            _tokenId: uint256,
            _data: Bytes[1024]
        ) -> bytes32: view

event Transfer:
    _from: indexed(address)
    _to: indexed(address)
    _tokenId: indexed(uint256)

event Approval:
    _owner: indexed(address)
    _approved: indexed(address)
    _tokenId: indexed(uint256)

event ApprovalForAll:
    _owner: indexed(address)
    _operator: indexed(address)
    _approved: bool 

name: public(String[100])
symbol: public(String[5])
owner: public(address)
totalSupply: public(uint256)

ownerToCount: public(HashMap[address, uint256])
idToOwner: public(HashMap[uint256, address])
idToApproved: public(HashMap[uint256, address])
ownerToApprovedForAll: public(HashMap[address, HashMap[address, bool]])

mintPrice: public(uint256)


@external
def __init__(_name: String[100], _symbol: String[5], _mintPrice: uint256):
    self.name = _name
    self.symbol = _symbol
    self.owner = msg.sender
    self.mintPrice = _mintPrice
    self.totalSupply = 0


@view
@external
def balanceOf(_owner: address) -> uint256:
    return self.ownerToCount[_owner]


@view
@external
def ownerOf(_tokenId: uint256) -> address:
    return self.idToOwner[_tokenId]


@view
@external
def getApproved(_tokenId: uint256) -> address:
    return self.idToApproved[_tokenId]


@view
@external
def isApprovedForAll(_owner: address, _operator: address) -> bool:
    return self.ownerToApprovedForAll[_owner][_operator]


@internal
def _addToken(_to: address, _tokenId: uint256):
    assert _to != ZERO_ADDRESS, "Can't transfer to null address"
    self.idToOwner[_tokenId] = _to
    self.idToApproved[_tokenId] = ZERO_ADDRESS
    self.ownerToCount[_to] += 1
    self.totalSupply += 1


@internal
def _removeToken(_from: address, _tokenId: uint256):
    assert _from == self.idToOwner[_tokenId], "Not owner of the token"
    self.idToOwner[_tokenId] = ZERO_ADDRESS
    self.ownerToCount[_from] -= 1
    self.totalSupply -= 1


@internal
def _transfer(_from: address, _to: address, _tokenId: uint256):
    assert _to != ZERO_ADDRESS, "Can't transfer to null address"
    assert _tokenId < self.totalSupply, "Token doesn't exist"
    self._removeToken(_from, _tokenId)
    self._addToken(_to, _tokenId)
    log Transfer(_from, _to, _tokenId)


@external
def transferFrom(_from: address, _to: address, _tokenId: uint256):
    
    #the sender must be the owner or approved
    assert self.idToOwner[_tokenId] == msg.sender or self.idToApproved[_tokenId] == msg.sender or self.ownerToApprovedForAll[_from][msg.sender], "Caller not approved"
    
    self._transfer(_from, _to, _tokenId)

#TODO
# implements: ERC721 throws an error if both fct are present?
# @external
# def safeTransferFrom(_from: address, _to: address, _tokenId: uint256):


@external
def safeTransferFrom(_from: address, _to: address, _tokenId: uint256, _data: Bytes[1024]):
    
    #the sender must be the owner or approved
    assert self.idToOwner[_tokenId] == msg.sender or self.idToApproved[_tokenId] == msg.sender or self.ownerToApprovedForAll[_from][msg.sender], "Caller not approved"
    
    self._transfer(_from, _to, _tokenId)

    if _to.is_contract:
        assert ERC721Receiver(_to).onERC721Received(msg.sender, _from, _tokenId, _data) == keccak256("onERC721Received(address,address,uint256,bytes)")


@external
def approve(_approved: address, _tokenId: uint256):
    assert msg.sender == self.idToOwner[_tokenId], "Only the owner can approve"
    self.idToApproved[_tokenId] = _approved
    log Approval(msg.sender, _approved, _tokenId)


@external
def setApprovalForAll(_operator: address, _approved: bool):
    self.ownerToApprovedForAll[msg.sender][_operator] = _approved
    log ApprovalForAll(msg.sender, _operator, _approved)

#TODO
@view
@external
def supportsInterface(_interfaceID: bytes32) -> bool:
    return False


@external
def setMintPrice(_newPrice: uint256):
    assert msg.sender == self.owner
    self.mintPrice = _newPrice


@payable
@external
def mint():
    assert msg.value >= self.mintPrice
    self._addToken(msg.sender, self.totalSupply)
    log Transfer(ZERO_ADDRESS, msg.sender, self.totalSupply-1)