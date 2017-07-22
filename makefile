# makefile for producing prep_bufr
#!/bin/sh -v

include /home/jzanetti/programs/comGSIv3.5_EnKFv1.1/configure.gsi

FC = gfortran

INCLD=  -I/home/jzanetti/programs/netcdf-fortran-4.4.4/include -I/home/jzanetti/programs/comGSIv3.5_EnKFv1.1/include
LIBS =  -L/home/jzanetti/programs/netcdf-fortran-4.4.4/lib -lnetcdf -lnetcdff -L/home/jzanetti/programs/comGSIv3.5_EnKFv1.1/lib -lbufr

OBJS = write_bufr_ref.o nc2bufr_ref.o ascii2bufr_conv.o

all: ascii2bufr_conv nc2bufr_ref

read_nc: ${OBJS}
	${FC} -o nc2bufr_ref.exe ${FLAGS} ${OBJS} ${LIBS} 
        ${FC} -o ascii2bufr_conv.exe ${FLAGS} ${OBJS} ${LIBS}

.SUFFIXES : .f90 .o

.f90.o :
	${FC} ${FLAGS} ${INCLD} -c $<

clean:
	/bin/rm -f *.o *.exe
