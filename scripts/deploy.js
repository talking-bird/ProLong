const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();

  console.log("Deploying contracts with the account:", deployer.address);

  const ProLongToken = await hre.ethers.getContractFactory("ProLongToken");
  const proLongToken = await ProLongToken.deploy();

  await proLongToken.waitForDeployment();

  console.log("ProLongToken deployed to:", proLongToken.target);

  const DataMarket = await hre.ethers.getContractFactory("DataMarket");
  const dataMarket = await DataMarket.deploy(proLongToken.target);

  await dataMarket.waitForDeployment();

  console.log("DataMarket deployed to:", dataMarket.target);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
