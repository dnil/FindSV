#install findTranslocations
git clone https://github.com/J35P312/FindTranslocations.git

cd FindTranslocations
mkdir build
cd build
cmake .. -DBoost_NO_BOOST_CMAKE=ON
make

cd ../bin
chmod a+x FindTranslocations
cd ../..

#install VEP
curl -LO "https://github.com/Ensembl/ensembl-tools/archive/release/81.zip"
unzip 81.zip
rm 81.zip
cd ensembl-tools-release-81/scripts/variant_effect_predictor/
perl INSTALL.pl --AUTO ac --s homo_sapiens --ASSEMBLY GRCh37
