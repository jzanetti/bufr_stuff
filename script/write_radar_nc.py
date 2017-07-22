from netCDF4 import Dataset
import numpy


lats =  numpy.arange(-90,91,2.5)
lons =  numpy.arange(-180,180,2.5)
vertical_levels = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.5, 4, 4.5, 5, 
                   5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 10, 11, 12, 13, 14, 15, 16, 18]

nlon = len(lons)
nlat = len(lats)
nvel = len(vertical_levels)

rootgrp = Dataset("radar_ref.nc", "w", format="NETCDF4")
level = rootgrp.createDimension("level", nvel)
lat = rootgrp.createDimension("lat", nlat)
lon = rootgrp.createDimension("lon", nlon)

levels = rootgrp.createVariable("level","i4",("level",))
latitudes = rootgrp.createVariable("lat","f4",("lat",))
longitudes = rootgrp.createVariable("lon","f4",("lon",))
reflectivity = rootgrp.createVariable('reflectivity','f4',('lat','lon','level'))
reflectivity[:] = -999.0
print reflectivity.shape

rootgrp.description = "radar vertical column for GSI"
rootgrp.source = "NZ MetService"

levels[:] = vertical_levels
latitudes[:] = lats
longitudes[:] = lons
reflectivity[25:70, 60:80, 3:12] = 23.5


rootgrp.close()


print 'done'

