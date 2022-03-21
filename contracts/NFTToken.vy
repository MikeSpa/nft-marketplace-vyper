# NFT Token
# @version 0.3.1

from vyper.interfaces import ERC721
implements: ERC721

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


ownerToCount: public(HashMap[address, uint256])
idToOwner: public(HashMap[uint256, address])

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
    return ZERO_ADDRESS

@view
@external
def isApprovedForAll(_owner: address, _operator: address) -> bool:
    return False



@external
def transferFrom(_from: address, _to: address, _tokenId: uint256):
    assert msg.sender == _from and self.idToOwner[_tokenId] == msg.sender
    self.idToOwner[_tokenId] = _to
    log Transfer(_from, _to, _tokenId)


    

# @external
# def safeTransferFrom(_from: address, _to: address, _tokenId: uint256):
#     pass

@external
def safeTransferFrom(_from: address, _to: address, _tokenId: uint256, _data: Bytes[1024]):
    pass

@external
def approve(_approved: address, _tokenId: uint256):
    pass

@external
def setApprovalForAll(_operator: address, _approved: bool):
    pass

@view
@external
def supportsInterface(_interfaceID: bytes32) -> bool:
    return False