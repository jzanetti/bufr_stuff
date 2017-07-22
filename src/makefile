# makefile for producing prep_bufr
#!/bin/sh -v
# write_bufr_ref.o

FC = gfortran 

INC	=	-I/home/jzanetti/programs/netcdf-fortran-4.4.4/include -I/home/jzanetti/programs/netcdf-C-4.4.4/include -I/home/jzanetti/programs/comGSIv3.5_EnKFv1.1/include
LIBS	=  	-L/home/jzanetti/programs/netcdf-fortran-4.4.4/lib -lnetcdf -lnetcdff -L/home/jzanetti/programs/comGSIv3.5_EnKFv1.1/lib -lbufr

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

clean:
	/bin/rm -f *.o *.exe
