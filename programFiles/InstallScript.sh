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

#install CNVnator, the ROOTSYS path must be permanently added to path, otherwise cnvnator will not run
#how to add rootsys
#export ROOTSYS=/path/to/root/
#then add the pat to root library
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ROOTSYS/lib
#ROOTSYS could also be added via the ROOTSYS variable in the path script
#then set rootsys=/path/to/root/

#git clone http://root.cern.ch/git/root.git
#cd root
#./configure
#make
#source bin/thisroot.sh
#cd ..
#wget https://github.com/abyzovlab/CNVnator/releases/download/v0.3.2/CNVnator_v0.3.2.zip
#unzip CNVnator_v0.3.2.zip
#cd CNVnator_v0.3.2/src/samtools/
#make
#cd ..
#make
