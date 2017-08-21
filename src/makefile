# makefile for producing prep_bufr
#!/bin/sh -v
# write_bufr_ref.o

FC		=	gfortran 
NETCDF_C	=	/home/jzanetti/programs/netcdf-C-4.4.1.1
NETCDF_FORTRAN	=	/home/jzanetti/programs/netcdf-fortran-4.4.4
GSI		=	/home/jzanetti/programs/comGSIv3.5_EnKFv1.1

INC	=	-I$(NETCDF_FORTRAN)/include -I$(NETCDF_C)/include -I$(GSI)/include
LIBS	=  	-L$(NETCDF_FORTRAN)/lib -L$(NETCDF_C)/lib -lnetcdf -lnetcdff -L$(GSI)/lib -lbufr

OBJS_nc2bufr_ref	=	nc2bufr_ref.o write_bufr_ref.o
OBJS_ascii2bufr_conv	=	ascii2bufr_conv.o

all: 			nc2bufr_ref ascii2bufr_conv

nc2bufr_ref:	 	$(OBJS_nc2bufr_ref)
	         	$(FC) -o nc2bufr_ref.exe $(FLAGS) $(OBJS_nc2bufr_ref) $(INC) $(LIBS) 

ascii2bufr_conv: 	$(OBJS_ascii2bufr_conv) 
			$(FC) -o ascii2bufr_conv.exe $(INC) $(OBJS_ascii2bufr_conv) $(LIBS)

.SUFFIXES : .f90 .o

.f90.o :
	$(FC) $(FLAGS) $(INC) -c $<

%.o : %.mod

clean:
	/bin/rm -f *.o *.exe
