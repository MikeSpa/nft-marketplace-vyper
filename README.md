# NFT Marketplace in Vyper


Marketplace for NFT where users can sell and buy any ERC721 NFTs. The more a user buy/sell NFT the more MarketCoin token he will receive. All contracts are written in Vyper.


# Contract

## MarketPlace
Main contract 

## Token
Generic ERC-20 token

## NFToken
Generic ERC-721 token

## MarketCoin
ERC-20 token for the marketplace. User buying and selling NFT on the marketplace are rewarded with MarketCoin token.

## MarketNFT
Custom ERC-721 token for the marketplace, user can buy it on the marketplace with Marketcoin instead of ETH. Can also be buy/sell like a regular ERC-721 token.

# Test
All contract have tests written in python with pytest.


## TODO
- [ ]: add comment to MarketNFT
- [ ]: add Bid functionality + test
- [x]: add MarketCoin in MarketPlace
- [ ]: add autho for approved address