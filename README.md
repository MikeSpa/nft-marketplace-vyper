# NFT Marketplace in Vyper


Marketplace for NFT where users can sell and buy any ERC721 NFTs. The more a user buy/sell NFTs on the marketplace, the more MarketCoin token he will receive. He can then use those coins to mint MarketNFTs.

All contracts have a full suite of tests.
All contracts are written in Vyper.


## Contracts

### MarketPlace
Main contract 

### Token
Generic ERC-20 token

### NFToken
Generic ERC-721 token

### MarketCoin
Custom  ERC-20 token for the marketplace. User buying and selling NFT on the marketplace are rewarded with MarketCoin token. Can be use to mint MarketNFT.

### MarketNFT
Custom ERC-721 token for the marketplace, user can mint it on the marketplace with Marketcoin instead of ETH. Once minted, can also be buy/sell on any marketplace like a regular ERC-721 token.

## Test
Every contract has unit tests written in python with pytest and property-based test with hypothesis.


## TODO
- [x]: add comment to MarketNFT
- [ ] add Bid functionality + test
- [x]: add MarketCoin in MarketPlace
- [ ]: ERC721Metadata for MarketNFT
- [x]: improve test coverage for marketplace
- [x]: MarketNFT::safeTransferFrom()
- [x]: coverage for MarketNFT