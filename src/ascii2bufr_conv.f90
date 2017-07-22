! **********************************************************************************************
!  example of writing conventional values into a bufr file
!  Details:
!       an example for writing adpupa: GSI bufr document p36
!       prebufr observation type: http://www.emc.ncep.noaa.gov/mmb/data_processing/prepbufr.doc/table_2.htm
!       cat type: ftp://ftp.cpc.ncep.noaa.gov/wd51we/rr_tmp/sample_obs_dump/docs/LevelCat_code.txt
!       others: http://www.emc.ncep.noaa.gov/mmb/data_processing/prepbufr.doc/table_1.htm
!               http://www.dtcenter.org/com-GSI/users/docs/presentations/2015_tutorial/20150812_L09_Hu_BE_hybrid_obsE.pdf
!
!  Supported observation types:
!    -- MASS:
!        -- ADPUPA(120): Radiosonde
!        -- AIRCFT(131): Amdar
!        -- ADPSFC(181): Synop/Metar with reported station pressure
!        -- ADPSFC(187): Synop/Metar without reported station pressure
!        -- ADPSFC(183): Ship/Buoy without reported station pressure
!    -- WIND:
!        -- ADPUPA(220): Radiosonde
!        -- PROFLR(229): Wind profiler decoded from pilot
!        -- AIRCFT(231): Amdar
!        -- SATWND(240-260): Cloud drift winds from different instruments
!        -- SFCSHP(280): Ship/Buoy with reported station pressure
!        -- ADPSFC(281): Synop/Metar with reported station pressure
!        -- ADPSFC/SFCSHP(284): Ship/Buoy/Synop/Metar without reported station pressure
!
!
!  Variables:
!    -- hdstr
!       SID: station ID
!       XOB: longitude
!       YOB: latitude
!       DHR: observation time minus cycle time (in hours)
!       TYP: prebufr report type
!       ELV: station elevation (in meter)
!       SAID: satellite identifier (satellite reports only)
!       T29: data dump report type
!    -- obstr:
!       POB: pressure observation (in MB, scale=1, ref=0)
!       TDO: dewpoint observation (in degree/C, scale=1, ref=-2732) - not assimilated, used for calculating RH
!       QOB: specific humidity observation (in MG/KG, scale=0, ref=0)
!       TOB: temperature observation (in degree/C, scale=1, ref=-2732)
!       ZOB: height observation (in meter, scale=0, ref=-1000)
!       UOB: u-component wind observation (in m/s, scale=1, ref=-4096)
!       VOB: v-component wind observation (in m/s, scale=1, ref=-4096)
!       PWO: total precipitation water observation (in kg/m2, or mm, scale=1, ref=0)
!       CAT: prebufr data level category (code table, scale=0, ref=0)
!       PRSS: surface pressure observation (in Pascals, scale=-1, ref=0)
!    -- qcstr:
!       *QM: quality marker
!    -- oestr:
!       *OE: observation error
!       QOE: relative humidity observation error
!
!  Coded value:
!        Coded_value = observation_value*(10^scale) - reference
!
!  Observation error in GSI
!     -- conventional observations:
!         -- for global analysis: errors are read in from the PrepBUFR file (oberrflg=False)
!         -- for regional analysis: errors are generated based on an external observation error table (oberrflg=True)
!
!  Observation template:
!      -- adpupa: 
!            stn_id stn_lon stn_lat stn_height obs_datetime subset obs_pressure obs_temperature obs_dewpoint obs_u obs_v
!
!  Usage:
!      gfortran ascii2bufr_conv.f90 -lbufr -L/home/jzanetti/programs/comGSIv3.5_EnKFv1.1/lib -ffree-line-length-none -o ascii2bufr_conv.exe
!
! **********************************************************************************************
program ascii2bufr_conv

 implicit none
 integer :: n
 integer, parameter :: mxmn=35, mxlv=200
 character(80):: hdstr='SID XOB YOB DHR TYP ELV SAID T29'
 character(80):: obstr='POB ZOB TOB TDO UOB VOB PWO CAT PRSS'
 character(80):: qcstr='PQM QQM TQM ZQM WQM NUL PWQ'
 character(80):: oestr='POE QOE TOE NUL WOE NUL PWE'
 real(8) :: hdr(mxmn),obs(mxmn,mxlv),qcf(mxmn,mxlv),oer(mxmn,mxlv)

 character(8) subset
 integer :: unit_out=10,unit_table=20
 integer :: iret, nlvl, idate
 integer :: datetime, obs_type
 real :: station_lon, station_lat, station_ele, obs_pressure, obs_temperature, obs_dewpoint, obs_u, obs_v
 character(8) :: c_sid
 real(8) :: station_id
 character(80) :: file_in, file_out

 equivalence(station_id,c_sid)

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Reading argument
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 n = iargc()
 if (n < 2) then
   write(*,'(a)') "usage: ./*.exe input output"
   write(*,'(a)') "   --input:  obs in textfile"
   write(*,'(a)') "   --output: obs in prebufr"
   stop
 else
   call getarg(1, file_in)
   call getarg(2, file_out)
 endif

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Default values
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 hdr=10.0e10
 obs=10.0e10; qcf=10.0e10; oer=10.0e10

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Start the file: open bufr file and messagee
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 open(unit_table,file='conv_prep.bufrtable', action='read')
 open(unit_out,file=file_out,action='write',form='unformatted')
 call datelen(10)
 call openbf(unit_out,'OUT',unit_table)

 nlvl = 1 ! we encode one layer one time
 open (unit = 7, file = file_in)
 do while(.true.)
    read (7,*, end=15) c_sid, station_lon, station_lat, station_ele, datetime, subset, &
                       obs_pressure, obs_temperature, obs_dewpoint, obs_u, obs_v
    idate=datetime
    call openmb(unit_out,subset,idate)
    hdr(1)=station_id
    hdr(2)=station_lon
    hdr(3)=station_lat
    hdr(4)=0.0
    hdr(6)=station_ele

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ! For Wind observation: write dateset
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if (subset=='ADPUPA') then
        hdr(5)=220
        obs(8,1)=1.0
    elseif (subset=='ADPSFC') then
        hdr(5)=287
        obs(8,1)=6.0
    elseif (subset=='AIRCFT') then
        hdr(5)=231
        obs(8,1)=6.0
    endif
 
    if ((obs_u .ne. -88888) .and. (obs_v .ne. -88888)) then
        ! obtain wind observations
        obs(1,1)=obs_pressure; qcf(1,1)=2; oer(1,1)=10;
        obs(5,1)=obs_u; qcf(5,1)=2; oer(5,1)=0.2;
        obs(6,1)=obs_v; qcf(6,1)=2; oer(6,1)=0.2;
    endif

    ! encode dataset
    call ufbint(unit_out,hdr,mxmn,1,iret,hdstr)
    call ufbint(unit_out,obs,mxmn,nlvl,iret,obstr)
    call ufbint(unit_out,oer,mxmn,nlvl,iret,oestr)
    call ufbint(unit_out,qcf,mxmn,nlvl,iret,qcstr)
    call writsb(unit_out)

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ! For mass observation: write dateset
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if (subset=='ADPUPA') then
        hdr(5)=120
        obs(8,1)=1.0
    elseif (subset=='ADPSFC') then
        hdr(5)=187
        obs(8,1)=0.0
    elseif (subset=='AIRCFT') then
        hdr(5)=131
        obs(8,1)=6.0
    endif

    if (obs_pressure .ne. -88888)  then
        ! obtain pressure
        obs(1,1)=obs_pressure; qcf(1,1)=2; oer(1,1)=10;
    endif

    if (obs_temperature .ne. -88888)  then
        ! obtain temperature
        obs(3,1)=obs_temperature; qcf(3,1)=2; oer(3,1)=2;
    endif

    if (obs_dewpoint .ne. -88888)  then
        ! obtain dewpoint temperature
        obs(4,1)=obs_dewpoint; qcf(4,1)=2; oer(4,1)=2;
    endif

    ! encode dataset
    call ufbint(unit_out,hdr,mxmn,1,iret,hdstr)
    call ufbint(unit_out,obs,mxmn,nlvl,iret,obstr)
    call ufbint(unit_out,oer,mxmn,nlvl,iret,oestr)
    call ufbint(unit_out,qcf,mxmn,nlvl,iret,qcstr)
    call writsb(unit_out)
    call closmg(unit_out)

 enddo

 call closbf(unit_out)

 15 continue

end program
