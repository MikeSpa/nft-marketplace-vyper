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

event ListingUpdated:
    _id: uint256
    _listing: Listing

event Sale:
    _seller: address
    _buyer: address
    _price: uint256
    _nft: address
    _tokenId: uint256

event BidEvent:
    _listing: uint256
    _bidder: address
    _bid: uint256

struct Bid:
    _bidder: address
    _bid: uint256
    
struct Listing:
    _seller: address
    _nft: address
    _tokenId: uint256
    _price: uint256
    _status: uint8 # 0-DONT EXIST, 1-OPEN, 2-SOLD, 3-CANCELED


currentId: public(uint256)
idToListing: public(HashMap[uint256, Listing])
idToBid: public(HashMap[uint256, HashMap[uint256, Bid]])  # listing Id -> bid # -> Bid
listingToBidNumber: public(HashMap[uint256, uint256])  # listing Id -> highest current Bid Id in self.idToBid
postingFee: public(uint256) # in wei
sellingFee: public(uint256) # in %
owner: public(address)
marketplace: public(address)


@external
def __init__():
    self.owner = msg.sender
    self.marketplace = self
    self.currentId = 0
    # self.postingFee = 0
    # self.sellingFee = 0

@external
def setPostingFee(_newFee: uint256):
    assert msg.sender == self.owner, "Only the owner can do that"
    self.postingFee = _newFee

@external
def setSellingFee(_newFee: uint256):
    assert msg.sender == self.owner, "Only the owner can do that"
    self.sellingFee = _newFee

@internal
def _addListing(_seller: address, _nft: address, _tokenId: uint256, _price: uint256):
    listing: Listing = Listing({_seller: _seller, _nft: _nft, _tokenId: _tokenId, _price: _price, _status: 1})
    id: uint256 = self.currentId
    self.idToListing[id] = listing
    self.currentId += 1


@internal
def _updateListing(_listingId: uint256, _listing: Listing):
    # listing: Listing = _listing
    self.idToListing[_listingId] = _listing
    log ListingUpdated(_listingId, _listing)


@payable
@external
def sell(_nft: address, _tokenId: uint256, _price: uint256):
    assert msg.value >= self.postingFee, "Amount sent is below postingFee"
    # check that msg.sender is owner
    assert msg.sender == NFToken(_nft).ownerOf(_tokenId), "Only the owner of the token can sell it"#TODO approved also

    # Check that we are operator for the seller nft
    assert NFToken(_nft).isApprovedForAll(msg.sender, self), "The marketplace doesn't have authorization to sell this token for this user"

    self._addListing(msg.sender, _nft, _tokenId, _price)
    log Posting(msg.sender, _price, _nft, _tokenId)

@payable
@external
def cancelSell(_id: uint256):
    # assert msg.value >= self.postingFee, "Amount sent is below cancellingFee"
    listing: Listing = self.idToListing[_id]
    assert msg.sender == listing._seller, "Only the seller can cancel"
    assert listing._status != 2, "Token already sold"
    assert listing._status == 1, "Token not for sale (already cancel or doesn't exist)"
    listing._status = 3  # cancel listing
    self.idToListing[_id] = listing #TODO test
    log ListingUpdated(_id, listing)

@payable
@external
def updateSell(_id: uint256, _newPrice: uint256):
    listing: Listing = self.idToListing[_id]
    assert listing._status == 1, "Token not for sale (already sold, cancel or doesn't exist)"
    assert listing._seller == msg.sender, "Only the seller can update"
    assert listing._price != _newPrice, "The price need to be different"

    listing._price = _newPrice
    self._updateListing(_id, listing)


@payable
@external
def buy(_id: uint256):
    listing: Listing = self.idToListing[_id]
    assert listing._status != 0, "Listing doesn't exist"
    assert listing._status == 1, "Token no longer for sale"

    price: uint256 = listing._price
    # enough ether is sent
    assert msg.value >= price, "Not enough ether sent"

    #Pay the seller
    seller: address = listing._seller
    fee: uint256 = price*self.sellingFee/100
    send(seller, price - fee)
    #Transfer the nft
    nft: address = listing._nft
    tokenId: uint256 = listing._tokenId
    NFToken(nft).transferFrom(seller, msg.sender, tokenId)

    #update Listing
    newStatus: uint8 = 2
    listing._status = newStatus
    self._updateListing(_id, listing)

    log Sale(seller, msg.sender, price, nft, listing._tokenId)


# maybe try to play with Dynamic Arrays for once-> need to wait for 0.3.2
# fucking ugly
@payable
@external
def bid(_id: uint256, _bid: uint256):
    listing: Listing = self.idToListing[_id]

    #assert ether.allowance > _bid, need to check for all listing: mapping address -> totalBidValue

    assert listing._status == 1, "Token not for sale"
    assert _bid > 0, "Bid can't be 0"

    highestBidId: uint256 = self.listingToBidNumber[_id]
    if highestBidId == 0:  # first bid
        new_bid: Bid = Bid({_bidder: msg.sender, _bid:_bid})
        self.idToBid[_id][1] = new_bid
        self.listingToBidNumber[_id] = 1 # start at one

    else:
        previous_bid: Bid = self.idToBid[_id][highestBidId]

        assert previous_bid._bid < _bid, "Bid too low"

        new_bid: Bid = Bid({_bidder: msg.sender, _bid:_bid})
        self.idToBid[_id][highestBidId + 1] = new_bid
        self.listingToBidNumber[_id] = highestBidId + 1

    log BidEvent(_id, msg.sender, _bid)

    
# @payable
# @external
# def cancelBid(_listingId: uint256, _bidId: uint256):
#     bid: Bid = self.idToBid[_listingId][_bidId]
#     assert bid._bidder == msg.sender

#     bid._bid = 0

#     self.idToBid[_listingId][_bidId] = bid

#     # bidId: uint256 = 

#     for bidId in range(_bidId, 0, -1):
#         if (self.listingToBidNumber[_listingId] == _bidId): # was highest bid
#             self.listingToBidNumber[_listingId] = bidId -1
#         if (self.idToBid[_listingId][self.listingToBidNumber[_listingId]]._bid) > 0:
#             break

#     #TODO

# g

# @payable
# @external
# def acceptBid(_id: uint256, _bidId: uint256):
#     pass

#BID
#Accept BID

@external
def withdraw(_amount: uint256):
    assert msg.sender == self.owner, "Only the owner can withdraw"
    send(self.owner, _amount)

#TODO handle if seller transfer nft



