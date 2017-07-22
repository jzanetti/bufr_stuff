!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! convert radar netcdf file into the required format by GSI
!
! Input data:
!     -- Using the gridded (3d) reflectivity data produced from python
!        Example code: /home/jzanetti/workspace/radar_bufr/write_radar_nc.py
!     -- Note that in python codes, 3d data is in (lat, lon, level), while in fortran, you have to read in inversely (e.g., (level, lon, lat))
! Compile method:
!     -- gfortran -o nc2bufr_ref.exe -I/home/jzanetti/programs/netcdf-fortran-4.4.4/include -L/home/jzanetti/programs/netcdf-fortran-4.4.4/lib -lnetcdf -lnetcdff read_ref_nc.f90
!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
program nc2bufr_ref
  use netcdf
  use kinds, only: r_kind,i_kind
  implicit none

  integer :: ncid, varid
  integer :: x, y, x_dimid, y_dimid, i, j, k
  character (len = *), parameter :: var_name = "reflectivity"
  integer, parameter :: nz = 31, nlon = 25, nlat = 30
  real :: data_in(nz, nlon, nlat)
  REAL(r_kind) :: data_out(nz+2, nlon*nlat)

  integer :: n, i_date
  character(80) :: file_in, file_out,radar_anal_time

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Reading argument
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 n = iargc()
 if (n < 3) then
   write(*,'(a)') "usage: ./*.exe YYYYMMDDHH input output"
   write(*,'(a)') "   --radar data analysis time:  YYYYMMDDHH"
   write(*,'(a)') "   --input:  obs in netcdf, e.g., test/radar_ref.nc"
   write(*,'(a)') "   --output: obs in prebufr, e.g., NSSLRefInGSI.bufr"
   stop
 else
   call getarg(1, radar_anal_time)
   call getarg(2, file_in)
   call getarg(3, file_out)
 endif

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Create the netCDF file
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  call check( nf90_open(file_in, nf90_nowrite, ncid) )
  call check( nf90_inq_varid(ncid, var_name, varid) )
  call check( nf90_get_var(ncid, varid, data_in) )

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! write the output into GSI
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  n=1
  do i=1,nlon
    do j=1,nlat
      data_out(1,n)=i
      data_out(2,n)=j
      write(*,*) data_out(1,n)
      !endif
      do k=1,nz
        data_out(k+2,n)=data_in(k,i,j)
        !write(*,*) data_in(k,i,j)
        !write(*,*) k
        !write(*,*) n
      enddo
      n=n+1
    enddo
  enddo
  
  read(radar_anal_time,'(I10)') i_date
  call write_bufr_ref(nz,nlon,nlat,n-1,data_out,file_out,i_date)

contains
  subroutine check(status)
    integer, intent ( in) :: status
    
    if(status /= nf90_noerr) then 
      print *, trim(nf90_strerror(status))
      stop "Stopped"
    end if
  end subroutine check  

end program nc2bufr_ref
