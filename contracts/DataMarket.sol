// SPDX-License-Identifier: MIT
// Compatible with OpenZeppelin Contracts ^5.0.0
pragma solidity ^0.8.20;

import "./ProLongToken.sol";

/**
 * @title DataMarket
 * @author Vsevolod Avilkin
 * @notice DataMarket contract allows to upload files, buy them and get information about the files.
 */
contract DataMarket {
    ProLongToken public token;

    /**
     * @dev connects to ProLongToken.sol
     * @param _tokenAddress address of ProLongToken
     */
    constructor(address _tokenAddress) {
        token = ProLongToken(_tokenAddress);
    }

    /// @dev contains info about uploaded files
    struct File {
        address seller;
        uint256 cost;
        uint256 fileId;
        bool isAvailable;
    }

    /// @dev counter of uploaded files
    uint private _fileId = 0;
    /// @notice hashes of all uploaded files
    bytes32[] public uploadedFiles;

    /// @notice Maps hashes of uploaded files to their info
    mapping(bytes32 => File) public files;
    // auxilary mappings
    /// @notice Maps sellers address to their uploaded files via uploadFile function
    mapping(address => bytes32[]) public sellerFiles;
    /// @notice Maps buyers address to their bough files via buyFile function
    mapping(address => bytes32[]) public buyerFiles;
    /// @notice Maps file Id to file hash
    mapping(uint256 => bytes32) public fileIdToHash;
    mapping(bytes32 => mapping(address => bool)) public isBuyer;

    /**
     * @notice Emits event when file is uploaded
     * @param seller Seller address
     * @param hash Hash of uploaded file
     * @param cost Cost of uploaded file
     */
    event FileUploaded(
        address indexed seller,
        bytes32 indexed hash,
        uint256 cost
    );
    /**
     * @notice Emits event when file is sold
     * @param seller Seller address
     * @param buyer Buyer address
     * @param hash Hash of sold file
     */
    event FileSold(
        address indexed seller,
        address indexed buyer,
        bytes32 indexed hash,
        bytes publicKey
    );

    /**
     * @notice Emits event when file is deleted
     * @param seller Seller address
     * @param hash Hash of deleted file
     */
    event FileDeleted(address indexed seller, bytes32 indexed hash);

    /**
     * @notice only seller can work with this file
     * @param _hash Hash of uploaded file
     */
    modifier onlySeller(bytes32 _hash) {
        require(msg.sender == files[_hash].seller, "Not authorized");
        _;
    }

    /**
     * @notice uploads file to the contract
     * @dev uploads file to the contract by adding it to files mapping and other accessory mappings
     * @param cost Cost of the file in ProLongTokens
     * @param _hash Hash of the file
     */
    function uploadFile(uint256 cost, bytes32 _hash) public {
        // preconditions
        // check if file is already uploaded
        require(files[_hash].seller == address(0), "File is already uploaded");
        // main action
        files[_hash] = File(msg.sender, cost, _fileId, true);
        // auxilary mappings and arrays
        fileIdToHash[_fileId] = _hash;
        sellerFiles[msg.sender].push(_hash);
        uploadedFiles.push(_hash);

        emit FileUploaded(msg.sender, _hash, cost);

        _fileId++;
    }

    /**
     * @notice Buys file from the contract
     * @dev Buys file from the contract by transfering ProLongTokens from buyer to seller
     * @param _hash Hash of the file
     */
    function buyFile(bytes32 _hash, bytes memory _public_key) public {
        require(files[_hash].isAvailable, "File is not available");
        require(
            files[_hash].seller != msg.sender,
            "Seller cannot buy his own file"
        );
        require(
            !isBuyer[_hash][msg.sender],
            "You have already bought this file"
        );
        require(
            token.balanceOf(msg.sender) >= files[_hash].cost,
            "Insufficient balance"
        );

        uint256 cost = files[_hash].cost;
        address seller = files[_hash].seller;
        address buyer = tx.origin;
        // catch transfer failure which will revert revert ERC20InsufficientAllowance(spender, currentAllowance, value);
        bool transferSuccess = token.transferFrom(buyer, seller, cost);

        if (transferSuccess) {
            buyerFiles[msg.sender].push(_hash);
            isBuyer[_hash][msg.sender] = true;
            emit FileSold(seller, buyer, _hash, _public_key); // buyer and hash is enough
        } else {
            revert("Token transfer failed");
        }
    }

    /**
     * @notice Gets information about file
     * @dev Gets information about file by its hash
     * @param _hash Hash of the file
     * @return file Information about file
     */
    function getFileInfo(bytes32 _hash) public view returns (File memory file) {
        file = files[_hash];
        require(file.isAvailable, "File is not available");
    }

    /**
     * @notice Gets files uploaded by seller
     * @dev Gets files uploaded by seller by their address
     * @param _seller Address of seller
     * @return _files Array of file hashes uploaded by seller
     */
    function getSellerFiles(
        address _seller
    ) public view returns (bytes32[] memory _files) {
        _files = sellerFiles[_seller];
    }

    /**
     * @notice Gets files bought by buyer
     * @dev Gets files bought by buyer by their address
     * @param _buyer Address of buyer
     * @return _files Array of file hashes bought by buyer
     */
    function getBuyerFiles(
        address _buyer
    ) public view returns (bytes32[] memory _files) {
        _files = buyerFiles[_buyer];
    }

    /**
        require(
            !isBuyer(msg.sender, _hash),
            "Buyer already bought this file"
        );
     * @notice Deletes file
     * @dev Deletes file by removing it from files mapping and other accessory mappings
     * @param _hash Hash of the file
     */
    function deleteFile(bytes32 _hash) public onlySeller(_hash) {
        // check that file is not already deleted
        require(files[_hash].isAvailable, "File is already deleted");
        delete files[_hash];
        delete fileIdToHash[files[_hash].fileId];
        // deleting file from uploadedFiles
        for (uint256 i = 0; i < uploadedFiles.length; i++) {
            if (uploadedFiles[i] == _hash) {
                for (uint256 j = i; j < uploadedFiles.length - 1; j++) {
                    uploadedFiles[j] = uploadedFiles[j + 1];
                }
                uploadedFiles.pop();
                break;
            }
        }
        // deleting file from sellerFiles
        uint256 index;
        for (uint256 i = 0; i < sellerFiles[msg.sender].length; i++) {
            if (sellerFiles[msg.sender][i] == _hash) {
                index = i;
                break;
            }
        }
        require(index < sellerFiles[msg.sender].length, "File not found");
        for (uint256 i = index; i < sellerFiles[msg.sender].length - 1; i++) {
            sellerFiles[msg.sender][i] = sellerFiles[msg.sender][i + 1];
        }
        sellerFiles[msg.sender].pop();

        emit FileDeleted(msg.sender, _hash);
    }
}