// SPDX-License-Identifier: MIT
// Compatible with OpenZeppelin Contracts ^5.0.0
pragma solidity ^0.8.20;

import "./ProLongToken.sol";

contract DataMarket {
    ProLongToken public token;

    constructor(address _tokenAddress) {
        token = ProLongToken(_tokenAddress);
    }

    struct File {
        address seller;
        uint256 cost;
        uint256 fileId;
        bool isAvailable;
    }

    uint private _fileId = 0;
    bytes32[] public uploadedFiles;

    mapping(bytes32 => File) public files;
    mapping(address => bytes32[]) public sellerFiles;
    mapping(address => bytes32[]) public buyerFiles;
    mapping(uint256 => bytes32) fileIdToHash;

    event FileUploaded(
        address indexed seller,
        bytes32 indexed hash,
        uint256 cost
    );
    event FileSold(
        address indexed seller,
        address indexed buyer,
        bytes32 indexed hash
    );
    event FileDeleted(address indexed seller, bytes32 indexed hash);

    modifier onlySeller(bytes32 _hash) {
        require(msg.sender == files[_hash].seller, "Not authorized");
        _;
    }

    function uploadFile(uint256 cost, bytes32 _hash) public {
        require(files[_hash].isAvailable == false, "File is already uploaded");
        files[_hash] = File(msg.sender, cost, _fileId, true);
        fileIdToHash[_fileId] = _hash;
        sellerFiles[msg.sender].push(_hash);
        uploadedFiles.push(_hash);
        emit FileUploaded(msg.sender, _hash, cost);

        _fileId++;
    }

    function buyFile(bytes32 _hash) public {
        // bytes32 _hash = fileIdToHash[fileId];
        require(files[_hash].isAvailable, "File not available");
        require(
            files[_hash].seller != msg.sender,
            "Seller cannot buy own file"
        );

        uint256 cost = files[_hash].cost;
        address seller = files[_hash].seller;
        address buyer = tx.origin;

        bool transferSuccess = token.transferFrom(buyer, seller, cost);

        if (transferSuccess) {
            buyerFiles[msg.sender].push(_hash);
            emit FileSold(seller, buyer, _hash); // buyer and hash is enough
        } else {
            revert("Token transfer failed");
        }
    }

    function getFileInfo(bytes32 _hash) public view returns (File memory) {
        File storage file = files[_hash];
        require(file.isAvailable, "File is not available");
        return file;
    }

    function getSellerFiles(
        address _seller
    ) public view returns (bytes32[] memory) {
        return sellerFiles[_seller];
    }

    function getBuyerFiles(
        address _buyer
    ) public view returns (bytes32[] memory) {
        return buyerFiles[_buyer];
    }

    function isBuyer(
        address _address,
        bytes32 _hash
    ) public view returns (bool) {
        bytes32[] storage boughtFiles = buyerFiles[_address];
        for (uint i = 0; i < boughtFiles.length; i++) {
            if (boughtFiles[i] == _hash) {
                return true;
            }
        }
        return false;
    }

    function deleteFile(bytes32 _hash) public onlySeller(_hash) {
        // files[_hash].isAvailable = false;
        delete files[_hash];
        delete fileIdToHash[files[_hash].fileId];
        // sellerFiles[msg.sender].pop(_hash); TODO
        emit FileDeleted(msg.sender, _hash);
    }
}
