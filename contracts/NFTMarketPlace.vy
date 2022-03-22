#NFT MarketPlace
# @version 0.3.1


interface NFToken:
    def onERC721Received(
            _operator: address,
            _from: address,
            _tokenId: uint256,
            _data: Bytes[1024]
        ) -> bytes32: view
    def balanceOf(_owner: address) -> uint256: view
    def ownerOf(_tokenId: uint256) -> address: view
    def getApproved(_tokenId: uint256) -> address: view
    def isApprovedForAll(_owner: address, _operator: address) -> bool: nonpayable
    def transferFrom(_from: address, _to: address, _tokenId: uint256): nonpayable
    def safeTransferFrom(_from: address, _to: address, _tokenId: uint256, _data: Bytes[1024]): nonpayable
    def approve(_approved: address, _tokenId: uint256): nonpayable
    def setApprovalForAll(_operator: address, _approved: bool): nonpayable
    def setMintPrice(_newPrice: uint256): nonpayable
    def mint(): payable

event Posting:
    _seller: address
    _price: uint256
    _nft: address
    _tokenId: uint256

event Sale:
    _seller: address
    _buyer: address
    _price: uint256
    _nft: address
    _tokenId: uint256

    
postingFee: public(uint256)
sellingFee: public(uint256)
owner: public(address)
marketplace: public(address)
# nft -> tokenid -> price
forSale: public(HashMap[address, HashMap[uint256, uint256]])
@external
def __init__():
    self.owner = msg.sender
    self.marketplace = self

@external
def setPostingFee(_newFee: uint256):
    self.postingFee = _newFee

@external
def setSellingFee(_newFee: uint256):
    self.sellingFee = _newFee

@payable
@external
def sell(_nft: address, _tokenId: uint256, _price: uint256):
    assert msg.value >= self.postingFee
    # check that msg.sender is owner
    assert msg.sender == NFToken(_nft).ownerOf(_tokenId)
    NFToken(_nft).approve(self.marketplace, _tokenId)
    self.forSale[_nft][_tokenId] = _price
    log Posting(msg.sender, _price, _nft, _tokenId)

@payable
@external
def buy(_nft: address, _tokenId: uint256):
    price: uint256 = self.forSale[_nft][_tokenId]
    # token is for sale and money is send
    assert price > 0 and msg.value >= price

    # seller: address # yep need that general ID

    #transfer nft
    # NFToken(_nft).transferFrom(seller, msg.sender, _tokenId)

    log Sale(self.marketplace, msg.sender, price, _nft, _tokenId)#TODO seller, probably need general itemID and mapping ID->seller

#Need structure for a posting with seller, nft, token, price and mapping GID -> struct