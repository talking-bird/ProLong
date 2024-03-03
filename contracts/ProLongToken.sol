// SPDX-License-Identifier: MIT
// Compatible with OpenZeppelin Contracts ^5.0.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract ProLongToken is ERC20 {
    constructor()
        ERC20("ProLongToken", "PTK"){
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }
}// как соотносятся токены и деньги?