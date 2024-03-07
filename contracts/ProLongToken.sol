// SPDX-License-Identifier: MIT
// Compatible with OpenZeppelin Contracts ^5.0.0

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title ProLongToken
 * @dev Implementation of the ProLongToken
 */
contract ProLongToken is ERC20 {
    /**
     * @dev Constructor
     */
    constructor() ERC20("ProLongToken", "PTK") {
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }
} // what is better: tokens or money?
