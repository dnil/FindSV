# FindSV
Install
Download the pipeline using the following command:
git clone https://github.com/J35P312/FindSV.git

enter the FindSV/programFiles folder and run the downloadFindTranslocations script:
cd FindSV/programFiles
chmod +x downloadFindTranslocations
./downloadFindTranslocations

enter the FindTranslocations folder and compile:
cd FindTranslocations
mkdir build
cd build
cmake .. -DBoost_NO_BOOST_CMAKE=ON
make
make FindTranslocations executable:
cd ..
cd bin
chmod +x FindTranslocations

Running
First load python 2.7:
module load python/2.7

thereafer FindSV is started:
python FindSV --analysis projectfolders

where projectfolders is the path to a folder containing folders that contains the bam files.
to analyse only one of the folders, run the pipeline using the following arguments:

python FindSV --analysis projectfolders --project runthisproject

where runthisfolder is the project folder you wish to run.

The config file


The reference file

