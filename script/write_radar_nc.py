#from Scientific.IO.NetCDF import NetCDFFile as Dataset
from netCDF4 import Dataset
import numpy
from numpy import arange, dtype
from scipy.ndimage import map_coordinates
from scipy.interpolate import RegularGridInterpolator as rgi

gsi_vertical_levels = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.5, 4, 4.5, 5, 
                       5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 10, 11, 12, 13, 14, 15, 16, 18]

def mock_ref(radar_north=-39.0, radar_south=-40.0, radar_west=173.5, radar_east=174.0, radar_bottom=0.5, radar_top=20.0,
             ref_north=None, ref_south=None, ref_west=None, ref_east=None, ref_bottom=None, ref_top=None):
    radar_coverage_lat = numpy.arange(radar_south, radar_north, 0.01)
    radar_coverage_lon = numpy.arange(radar_west, radar_east, 0.01)
    radar_coverage_height = numpy.arange(radar_bottom, radar_top, 0.25)
    
    mock_ref_value = 23.5
    radar_map = numpy.zeros((len(radar_coverage_lat),len(radar_coverage_lon),len(radar_coverage_height)))
    for ilat, lat in enumerate(radar_coverage_lat):
        for ilon, lon in enumerate(radar_coverage_lon):
            for iheight, height in enumerate(radar_coverage_height):
                if ref_north != None:
                    if (lat > ref_south and lat < ref_north) and ((lon > ref_west) and (lon < ref_east)) and ((height > ref_bottom and height < ref_top)):
                        radar_map[ilat, ilon, iheight] = mock_ref_value
                    else:
                        radar_map[ilat, ilon, iheight] = 0.0
    
    return radar_map, radar_coverage_lat, radar_coverage_lon, radar_coverage_height


def radar2model_grid(radar_map, radar_lat, radar_lon, radar_height,
                     model_lats, model_lons, vertical_levels):
    
    my_interpolating_function = rgi((radar_lat,radar_lon,radar_height), radar_map, fill_value=-999.0)

    radar_at_model_space = numpy.empty((len(model_lats), len(model_lons), len(vertical_levels)))
    for i, cmlats in enumerate(model_lats):
        for j, cmlons in enumerate(model_lons):
            for k, cl in enumerate(vertical_levels):
                if cmlats < radar_lat.max() and cmlats > radar_lat.min() and cmlons < radar_lon.max() and cmlons > radar_lon.min():
                    pts = numpy.array([[cmlats, cmlons, cl]])
                    vi = my_interpolating_function(pts)
                else:
                    vi = -999.0
                
                radar_at_model_space[i,j,k] = vi
                
    return radar_at_model_space

def interp3(x, y, z, v, xi, yi, zi, **kwargs):
    """Sample a 3D array "v" with pixel corner locations at "x","y","z" at the
    points in "xi", "yi", "zi" using linear interpolation. Additional kwargs
    are passed on to ``scipy.ndimage.map_coordinates``."""
    def index_coords(corner_locs, interp_locs):
        index = numpy.arange(len(corner_locs))
        if numpy.all(numpy.diff(corner_locs) < 0):
            corner_locs, index = corner_locs[::-1], index[::-1]
        return numpy.interp(interp_locs, corner_locs, index)

    orig_shape = numpy.asarray(xi).shape
    xi, yi, zi = numpy.atleast_1d(xi, yi, zi)
    for arr in [xi, yi, zi]:
        arr.shape = -1

    output = numpy.empty(xi.shape, dtype=float)
    coords = [index_coords(*item) for item in zip([x, y, z], [xi, yi, zi])]

    map_coordinates(v, coords, order=1, output=output, **kwargs)

    return output.reshape(orig_shape)

def read_model_background(nc_f):
    nc_fid = Dataset(nc_f, 'r')
    lats = nc_fid.variables['XLAT'][0,:,0]
    lons = nc_fid.variables['XLONG'][0,0,:]
    return lats, lons



def write_radar_nc(lats, lons, vertical_levels, radar):
    
    nlat = radar.shape[0]
    nlon = radar.shape[1]
    nvel = radar.shape[2]
    
    rootgrp = Dataset("radar_ref.nc", "w")
    level = rootgrp.createDimension("level", nvel)
    lat = rootgrp.createDimension("lat", nlat)
    lon = rootgrp.createDimension("lon", nlon)
    
    levels = rootgrp.createVariable("level","f4",("level",))
    latitudes = rootgrp.createVariable("lat","f4",("lat",))
    longitudes = rootgrp.createVariable("lon","f4",("lon",))
    reflectivity = rootgrp.createVariable('reflectivity','f4',('lat','lon','level'))
    print 'nlat: {}'.format(nlat)
    print 'nlon: {}'.format(nlon)
    print 'nlev: {}'.format(nvel)
    
    rootgrp.description = "radar vertical column for GSI"
    rootgrp.source = "NZ MetService"
    
    levels[:] = vertical_levels
    latitudes[:] = lats
    longitudes[:] = lons
    reflectivity[:,:,:] = radar
    rootgrp.close()

if __name__ == '__main__':
    background_data = '/home/jzanetti/wrf_directory/wrf_exp_20170710/wrf/wrfinput_d01'
    model_lats, model_lons = read_model_background(background_data)
    #radar_map, radar_lat, radar_lon, radar_height = \
    #        mock_ref(radar_north=-39.0, radar_south=-40.0, radar_west=173.5, radar_east=174.0, radar_bottom=0.5, radar_top=20.0,
    #                 ref_north=-39.5, ref_south=-39.75, ref_west=173.6, ref_east=173.75, ref_bottom=0.02, ref_top=15.0)
    radar_map, radar_lat, radar_lon, radar_height = \
            mock_ref(radar_north=-39.0, radar_south=-40.0, radar_west=173.5, radar_east=174.0, radar_bottom=0.5, radar_top=20.0,
                     ref_north=-39.5, ref_south=-39.6, ref_west=173.6, ref_east=173.65, ref_bottom=0.75, ref_top=1.5)
    radar_map = radar2model_grid(radar_map, radar_lat, radar_lon, radar_height,
                     model_lats, model_lons, gsi_vertical_levels)
    write_radar_nc(model_lats, model_lons, gsi_vertical_levels, radar_map)
    print 'done'

