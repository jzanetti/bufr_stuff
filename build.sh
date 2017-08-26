export INSTALL_DIR=$CONDA_PREFIX/bufr_stuff

export INTEL=/home/szhang/Programs/intel

source $INTEL/bin/compilervars.sh intel64
export CC=icc
export CXX=icpc
export CFLAGS='-O3 -xHost -ip -no-prec-div -static-intel'
export CXXFLAGS='-O3 -xHost -ip -no-prec-div -static-intel'
export F77=ifort
export FC=ifort
export F90=ifort
export FFLAGS='-O3 -xHost -ip -no-prec-div -static-intel'
export CPP='icc -E'
export CXXCPP='icpc -E'

export INSTALL_DIR=$CONDA_PREFIX/bufr_stuff
source $INTEL/bin/compilervars.sh intel64

export NETCDF_C=$CONDA_PREFIX
export NETCDF_FORTRAN=$CONDA_PREFIX
export GSI=$CONDA_PREFIX/comGSIv3.5_EnKFv1.1
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib

ln -sf $CONDA_PREFIX/comGSIv3.5_EnKFv1.1/lib/libbufr_i4r8.a $CONDA_PREFIX/comGSIv3.5_EnKFv1.1/lib/libbufr.a

./compile  

cp -rf $PWD $INSTALL_DIR

