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

name: public(String[9])
symbol: public(String[4])
owner: public(address)
totalSupply: public(uint256)

ownerToCount: public(HashMap[address, uint256])
idToOwner: public(HashMap[uint256, address])
idToApproved: public(HashMap[uint256, address])
ownerToApprovedForAll: public(HashMap[address, HashMap[address, bool]])

mintPrice: public(uint256)

#TODO add tokenURI to fully implements ERC721Metadata interface

@external
def __init__(_owner: address, _mintPrice: uint256):
    self.name = "MarketNFT"
    self.symbol = "MNFT"
    self.owner = _owner
    self.mintPrice = _mintPrice


# @notice Count all NFTs assigned to an owner
# @dev NFTs assigned to the zero address are considered invalid, and this
# function throws for queries about the zero address.
# @param _owner An address for whom to query the balance
# @return The number of NFTs owned by `_owner`, possibly zero
@view
@external
def balanceOf(_owner: address) -> uint256:
    return self.ownerToCount[_owner]


# @notice Find the owner of an NFT
# @dev NFTs assigned to zero address are considered invalid, and queries
# about them do throw.
# @param _tokenId The identifier for an NFT
# @return The address of the owner of the NFT
@view
@external
def ownerOf(_tokenId: uint256) -> address:
    return self.idToOwner[_tokenId]


# @notice Get the approved address for a single NFT
# @dev Throws if `_tokenId` is not a valid NFT.
# @param _tokenId The NFT to find the approved address for
# @return The approved address for this NFT, or the zero address if there is none
@view
@external
def getApproved(_tokenId: uint256) -> address:
    return self.idToApproved[_tokenId]


# @notice Query if an address is an authorized operator for another address
# @param _owner The address that owns the NFTs
# @param _operator The address that acts on behalf of the owner
# @return True if `_operator` is an approved operator for `_owner`, false otherwise
@view
@external
def isApprovedForAll(_owner: address, _operator: address) -> bool:
    return self.ownerToApprovedForAll[_owner][_operator]


@internal
def _addToken(_to: address, _tokenId: uint256):
    assert _to != ZERO_ADDRESS, "MarketNFT: Can't transfer to null address"
    self.idToOwner[_tokenId] = _to
    self.ownerToCount[_to] += 1
    self.totalSupply += 1


@internal
def _removeToken(_from: address, _tokenId: uint256):
    assert _from == self.idToOwner[_tokenId], "MarketNFT: Not owner of the token"
    self.idToOwner[_tokenId] = ZERO_ADDRESS
    self.idToApproved[_tokenId] = ZERO_ADDRESS
    self.ownerToCount[_from] -= 1
    self.totalSupply -= 1


@internal
def _transfer(_from: address, _to: address, _tokenId: uint256):
    assert _to != ZERO_ADDRESS, "MarketNFT: Can't transfer to null address"
    assert _tokenId < self.totalSupply, "MarketNFT: Token doesn't exist" # should never fails since we always check ownership/approval first
    self._removeToken(_from, _tokenId)
    self._addToken(_to, _tokenId)
    log Transfer(_from, _to, _tokenId)


@internal
def _isOwnerOrApproved(_address: address, _tokenId: uint256) -> bool:

    owner: address = self.idToOwner[_tokenId]
    approved: address = self.idToApproved[_tokenId]
    isApprovedForAll: bool = self.ownerToApprovedForAll[owner][_address]

    return (_address == owner or _address == approved or isApprovedForAll) 


# @notice Transfers _tokenId from address _from to address _to
# @dev Emit a Transfer Event
# @param _from The address that sends the token
# @param _to The address that should receive the token
# @param _tokenId The token to transfer

# @notice Transfer ownership of an NFT -- THE CALLER IS RESPONSIBLE
# TO CONFIRM THAT `_to` IS CAPABLE OF RECEIVING NFTS OR ELSE
# THEY MAY BE PERMANENTLY LOST
# @dev Throws unless `msg.sender` is the current owner, an authorized
# operator, or the approved address for this NFT. Throws if `_from` is
# not the current owner. Throws if `_to` is the zero address. Throws if
# `_tokenId` is not a valid NFT.
# @param _from The current owner of the NFT
# @param _to The new owner
# @param _tokenId The NFT to transfer
@external
def transferFrom(_from: address, _to: address, _tokenId: uint256):
    
    #the sender must be the owner or approved
    assert self._isOwnerOrApproved(msg.sender, _tokenId), "MarketNFT: Caller not approved"
    
    self._transfer(_from, _to, _tokenId)

# @notice Transfers the ownership of an NFT from one address to another address
# @dev Throws unless `msg.sender` is the current owner, an authorized
# operator, or the approved address for this NFT. Throws if `_from` is
# not the current owner. Throws if `_to` is the zero address. Throws if
# `_tokenId` is not a valid NFT. When transfer is complete, this function
# checks if `_to` is a smart contract (code size > 0). If so, it calls
# `onERC721Received` on `_to` and throws if the return value is not
# `bytes4(keccak256("onERC721Received(address,address,uint256,bytes)"))`.
# @param _from The current owner of the NFT
# @param _to The new owner
# @param _tokenId The NFT to transfer
# @param data Additional data with no specified format, sent in call to `_to`
@external
def safeTransferFrom(_from: address, _to: address, _tokenId: uint256, _data: Bytes[1024]=b''):
    
    #the sender must be the owner or approved
    assert self._isOwnerOrApproved(msg.sender, _tokenId), "MarketNFT: Caller not approved"

    self._transfer(_from, _to, _tokenId)

    if _to.is_contract:
        assert ERC721Receiver(_to).onERC721Received(msg.sender, _from, _tokenId, _data) == keccak256("onERC721Received(address,address,uint256,bytes)")


# @notice Change or reaffirm the approved address for an NFT
# @dev The zero address indicates there is no approved address.
# Throws unless `msg.sender` is the current NFT owner, or an authorized
# operator of the current owner.
# @param _approved The new approved NFT controller
# @param _tokenId The NFT to approve
@external
def approve(_approved: address, _tokenId: uint256):
    assert self._isOwnerOrApproved(msg.sender, _tokenId), "MarketNFT: Caller not approved"
    self.idToApproved[_tokenId] = _approved
    log Approval(msg.sender, _approved, _tokenId)


# @notice Enable or disable approval for a third party ("operator") to manage
# all of `msg.sender`'s assets
# @dev Emits the ApprovalForAll event. Multiple operators per owner are allowed
# @param _operator Address to add to the set of authorized operators
# @param _approved True if the operator is approved, false to revoke approval
@external
def setApprovalForAll(_operator: address, _approved: bool):
    self.ownerToApprovedForAll[msg.sender][_operator] = _approved
    log ApprovalForAll(msg.sender, _operator, _approved)


# @notice Query if a contract implements an interface
# @param _interfaceID The interface identifier, as specified in ERC-165
# @dev Interface identification is specified in ERC-165. This function
#  uses less than 30,000 gas.
# @return `true` if the contract implements `_interfaceID` and
#  `_interfaceID` is not 0xffffffff, `false` otherwise
#TODO
@view
@external
def supportsInterface(_interfaceID: bytes32) -> bool:
    return False

# @notice Set a mint price
# @param _newPrice The new mint price
@external
def setMintPrice(_newPrice: uint256):
    assert msg.sender == self.owner, "MarketNFT: Only owner can do that"
    self.mintPrice = _newPrice

# @notice Mint an NFT
# @param _to The address that will receive the NFT
# @dev An NFT can only be mint by the owner, e.g. a marketplace. Necessary checks need to be done there
@external
def mint(_to: address):
    assert msg.sender == self.owner, "MarketNFT: Only owner can mint"
    self._addToken(msg.sender, self.totalSupply)
    log Transfer(ZERO_ADDRESS, msg.sender, self.totalSupply-1)
