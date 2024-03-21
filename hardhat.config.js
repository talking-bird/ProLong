/** @type import('hardhat/config').HardhatUserConfig */

// hardhat.config.js
require("@nomicfoundation/hardhat-ethers");
require("@nomicfoundation/hardhat-chai-matchers")
require("@nomicfoundation/hardhat-toolbox")

require('dotenv').config();


// Go to https://infura.io, sign up, create a new API key
// in its dashboard, and replace "KEY" with it
const INFURA_API_KEY = "ca745db3f9cf4dcdbc16110c9c83c55c";

module.exports = {
  solidity: "0.8.24",
//  networks: {
//    sepolia: {
//      url: `https://sepolia.infura.io/v3/${INFURA_API_KEY}`,
//      accounts: [process.env.SEPOLIA_PRIVATE_KEY]
//    }
//  }
};
