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

#wget http://sourceforge.net/projects/snpeff/files/snpEff_latest_core.zip
#unzip snpEff_latest_core.zip
#rm snpEff_latest_core.zip

#install RTG
wget https://github.com/RealTimeGenomics/rtg-tools/releases/download/3.5.1/rtg-tools-3.5.1-linux-x64.zip
unzip rtg-tools-3.5.1-linux-x64.zip
rm rtg-tools-3.5.1-linux-x64.zip
mv rtg-tools-3.5.1 RTG
cd RTG
yes n | ./rtg
cd ..

#install VEP
curl -LO "https://github.com/Ensembl/ensembl-tools/archive/release/81.zip"
unzip 81.zip
rm 81.zip
cd ensembl-tools-release-81/scripts/variant_effect_predictor/
perl INSTALL.pl --AUTO ac --s homo_sapiens --ASSEMBLY GRCh37
