// Assuming the function is part of a contract named 'YourContract'
const { expect } = require('chai');
const { ethers } = require('hardhat');

describe('DataMarket', function () {
  async function deployProLongToken() {
    const ProLongToken = await ethers.getContractFactory('ProLongToken');
    const proLongToken = await ProLongToken.deploy();
    await proLongToken.waitForDeployment();

    return proLongToken;
  }
  async function deployDataMarket(proLongToken) {
    const DataMarket = await ethers.getContractFactory('DataMarket');
    const dataMarket = await DataMarket.deploy(proLongToken.target);
    await dataMarket.waitForDeployment();

    return dataMarket;
  }

  async function runEveryTime() {
    const token = await deployProLongToken();
    const dataMarket = await deployDataMarket(token);
    const [owner, buyer] = await ethers.getSigners();
    // file info
    const cost = 100;
    const _hash = '0xa589559b0443b454b7f0dd10565a985bec8a9122d242877bcc42dad71bf8588c';

    return { token, dataMarket, owner, buyer, cost, _hash };
  }
  describe('uploadFile', function () {
    it('should upload a file', async function () {
      const { dataMarket, owner, buyer, cost, _hash } = await runEveryTime();
      const ownerAddress = await owner.getAddress();
      await dataMarket.uploadFile(cost, _hash);

      // Assert that the file was uploaded with the correct details
      const file = await dataMarket.files(_hash);
      expect(file.seller).to.equal(ownerAddress);
      expect(file.cost).to.equal(cost);
      expect(file.isAvailable).to.equal(true);

      // Assert that the auxilary mappings and arrays were updated
      expect(await dataMarket.fileIdToHash(0)).to.equal(_hash);
      expect(await dataMarket.sellerFiles(ownerAddress, 0)).to.equal(_hash);
      expect(await dataMarket.uploadedFiles(0)).to.equal(_hash);
    });
  });
  describe('buyFile', function () {
    it('should not allow a buyer to purchase an unavailable file', async function () {
      const { dataMarket, owner, buyer, cost, _hash } = await runEveryTime();

      // Call the buyFile function
      await expect(dataMarket.connect(buyer).buyFile(_hash, { from: buyer })).to.be.revertedWith('File is not available');
    });
    it('should allow a buyer to purchase an uploaded file', async function () {
      const { token, dataMarket, owner, buyer, cost, _hash } = await runEveryTime();
      buyerAddress = await buyer.getAddress();

      await dataMarket.uploadFile(cost, _hash);

      // Transfer some ProLongTokens to the buyer and approve the contract to spend on behalf of the buyer
      await token.transfer(buyer, cost * 2);
      await token.connect(buyer).approve(dataMarket.target, cost, { from: buyer });

      // Call the buyFile function
      await expect(dataMarket.connect(buyer).buyFile(_hash, { from: buyer })).to.emit(dataMarket, 'FileSold');

      // Check the state after the file purchase
      const buyerFile = await dataMarket.buyerFiles(buyer, 0);
      expect(buyerFile).to.equal(_hash);
      const isBuyer = await dataMarket.isBuyer(_hash, buyerAddress);
      expect(isBuyer).to.be.true;
    });
    it('should not allow a buyer to purchase a file twice', async function () {
      const { token, dataMarket, owner, buyer, cost, _hash } = await runEveryTime();

      await dataMarket.uploadFile(cost, _hash);

      // Transfer some ProLongTokens to the buyer and approve the contract to spend on behalf of the buyer
      await token.transfer(buyer, cost * 4);
      await token.connect(buyer).approve(dataMarket.target, cost, { from: buyer });

      await dataMarket.connect(buyer).buyFile(_hash, { from: buyer });
      await expect(dataMarket.connect(buyer).buyFile(_hash, { from: buyer })).to.be.revertedWith('You have already bought this file');

      // Check the state after the file purchase
      const buyerFile = await dataMarket.buyerFiles(buyer, 0);
      expect(buyerFile).to.equal(_hash);
      const isBuyer = await dataMarket.isBuyer(_hash, buyerAddress);
      expect(isBuyer).to.be.true;
    });
    it('should not allow a buyer to purchase a file without enough tokens', async function () {
      const { token, dataMarket, owner, buyer, cost, _hash } = await runEveryTime();
      buyerAddress = await buyer.getAddress();

      await dataMarket.uploadFile(cost, _hash);

      // do not transfer any ProLongTokens to the buyer and approve the contract to spend on behalf of the buyer
      await token.connect(buyer).approve(dataMarket.target, cost, { from: buyer });

      await expect(dataMarket.connect(buyer).buyFile(_hash, { from: buyer })).to.be.revertedWith("Insufficient balance");

      // Check the state after the file purchase
      await expect(dataMarket.buyerFiles(buyer, 0)).to.be.reverted;
      const isBuyer = await dataMarket.isBuyer(_hash, buyerAddress);
      expect(isBuyer).to.be.false;
    });
  });
});