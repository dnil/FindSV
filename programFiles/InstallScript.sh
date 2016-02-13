#install findTranslocations
# wget https://cmake.org/files/v3.4/cmake-3.4.1-Linux-x86_64.tar.gz

git clone https://github.com/J35P312/FindTranslocations.git

cd FindTranslocations
mkdir build
cd build

cmake .. -DBoost_NO_BOOST_CMAKE=ON
make

cd ../bin
chmod a+x FindTranslocations
cd ../..

# perl modules for VEP
# cpanm Archive::Extract Archive::Zip DBI DBD::mysql CGI LWP::Simple LWP::Protocol::https

#install VEP
curl -LO "https://github.com/Ensembl/ensembl-tools/archive/release/81.zip"
unzip 81.zip
rm 81.zip
cd ensembl-tools-release-81/scripts/variant_effect_predictor/
perl INSTALL.pl --AUTO ac --s homo_sapiens --ASSEMBLY GRCh37

#install genmod
pip install genmod

#install CNVnator

# wget http://sv.gersteinlab.org/cnvnator/CNVnator_v0.3.zip
# unzip CNVnator_v0.3.zip
#cd CNVnator_v0.3
#wget https://root.cern.ch/download/root_v5.34.34.Linux-slc6-x86_64-gcc4.4.tar.gz
#tar xvf root_v5.34.34.Linux-slc6-x86_64-gcc4.4.tar.gz
#cd root
#export ROOTSYS=`pwd`
#export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ROOTSYS}/lib
#cd ../src/samtools/
#make
#cd ..
#make
