#from Scientific.IO.NetCDF import NetCDFFile as Dataset
from netCDF4 import Dataset
import numpy
from numpy import arange, dtype
def read_model_background(nc_f):
    nc_fid = Dataset(nc_f, 'r')
    lats = nc_fid.variables['XLAT'][0,:,0]
    lons = nc_fid.variables['XLONG'][0,0,:]
    return lats, lons



def write_radar_nc(lats, lons):
    vertical_levels = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.5, 4, 4.5, 5, 
                       5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 10, 11, 12, 13, 14, 15, 16, 18]
    
    nlon = len(lons)
    nlat = len(lats)
    nvel = len(vertical_levels)
    
    ref = numpy.zeros((nlat,nlon,nvel))
    
    for i in range(0, nlat):
        for j in range(0, nlon):
            for k in range(0, nvel):
                if (i > 7 and i < 20) and (j > 5 and j < 23) and (k >= 1 and k < 30):
                    ref[i,j,k] = 60.0
                else:
                    ref[i,j,k] = -999.0

    
    rootgrp = Dataset("radar_ref.nc", "w")
    level = rootgrp.createDimension("level", nvel)
    lat = rootgrp.createDimension("lat", nlat)
    lon = rootgrp.createDimension("lon", nlon)
    
    levels = rootgrp.createVariable("level","f4",("level",))
    latitudes = rootgrp.createVariable("lat","f4",("lat",))
    longitudes = rootgrp.createVariable("lon","f4",("lon",))
    reflectivity = rootgrp.createVariable('reflectivity','f4',('lat','lon','level'))
    print 'nlon: {}'.format(nlon)
    print 'nlat: {}'.format(nlat)
    print 'nlev: {}'.format(len(vertical_levels))
    
    rootgrp.description = "radar vertical column for GSI"
    rootgrp.source = "NZ MetService"
    
    levels[:] = vertical_levels
    latitudes[:] = lats
    longitudes[:] = lons
    reflectivity[:,:,:] = ref
    
    rootgrp.close()

if __name__ == '__main__':
    background_data = '/home/jzanetti/wrf_directory/wrf_exp_20170710/wrf/wrfinput_d01'
    lats, lons = read_model_background(background_data)
    write_radar_nc(lats, lons)
    print 'done'

