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
    _from: address
    _to: address
    _tokenId: uint256

event Approval:
    _owner: address
    _approved: address
    _tokenId: uint256

event ApprovalForAll:
    _owner: address
    _operator: address
    _approved: bool 

name: public(String[100])
symbol: public(String[5])
owner: public(address)
supply: public(uint256)

ownerToCount: public(HashMap[address, uint256])
idToOwner: public(HashMap[uint256, address])
idToApproved: public(HashMap[uint256, address])

mintPrice: public(uint256)


@external
def __init__(_name: String[100], _symbol: String[5], _mintPrice: uint256):
    self.name = _name
    self.symbol = _symbol
    self.owner = msg.sender
    self.mintPrice = _mintPrice
    self.supply = 0


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
    return False


@internal
def _addToken(_to: address, _tokenId: uint256):
    assert _to != ZERO_ADDRESS, "Can't transfer to null address"
    self.idToOwner[_tokenId] = _to
    self.idToApproved[_tokenId] = ZERO_ADDRESS
    self.ownerToCount[_to] += 1
    self.supply += 1


@internal
def _removeToken(_from: address, _tokenId: uint256):
    assert _from == self.idToOwner[_tokenId], "Not owner of the token"
    self.idToOwner[_tokenId] = ZERO_ADDRESS
    self.ownerToCount[_from] -= 1
    self.supply -= 1


@internal
def _transfer(_from: address, _to: address, _tokenId: uint256):
    assert _to != ZERO_ADDRESS, "Can't transfer to null address"
    assert _tokenId < self.supply, "Token doesn't exist"
    self._removeToken(_from, _tokenId)
    self._addToken(_to, _tokenId)
    log Transfer(_from, _to, _tokenId)


@external
def transferFrom(_from: address, _to: address, _tokenId: uint256):
    assert msg.sender == _from and self.idToOwner[_tokenId] == msg.sender
    
    self._transfer(_from, _to, _tokenId)

    
# implements: ERC721 throws an error if both fct are present?
# @external
# def safeTransferFrom(_from: address, _to: address, _tokenId: uint256):


@external
def safeTransferFrom(_from: address, _to: address, _tokenId: uint256, _data: Bytes[1024]):
    assert msg.sender == _from and self.idToOwner[_tokenId] == msg.sender
    
    self._transfer(_from, _to, _tokenId)
    if _to.is_contract:
        assert ERC721Receiver(_to).onERC721Received(msg.sender, _from, _tokenId, _data) == keccak256("onERC721Received(address,address,uint256,bytes)")


@external
def approve(_approved: address, _tokenId: uint256):
    assert msg.sender == self.idToOwner[_tokenId]
    self.idToApproved[_tokenId] = _approved
    log Approval(msg.sender, _approved, _tokenId)


@external
def setApprovalForAll(_operator: address, _approved: bool):
    pass


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
    self._addToken(msg.sender, self.supply)
    log Transfer(ZERO_ADDRESS, msg.sender, self.supply-1)