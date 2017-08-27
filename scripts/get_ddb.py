from AMPSAws import utils, connections
from decimal import Decimal
from obs2aws import tools, dynamo_db, station_details
import Geohash
from datetime import datetime
from boto3.dynamodb.conditions import Key
from metpy.calc import get_wind_components, get_wind_speed, get_wind_dir

def get_geohashes(north, south, west, east, precision=2):
    ''' Return a list of GeoHash keys in a box such as a model domain.
        In the future we might want to call it from other packages like obs2aws etc.
    '''
    _, _, lat_incr, lon_incr = Geohash.decode_exactly(Geohash.encode(0, 0, precision=precision))

    lats = [south, north]
    lat = south + lat_incr
    while lat < north:
        lats.append(lat)
        lat += lat_incr * 2

    west_ = tools.lon_180_180(west)
    east_ = tools.lon_180_180(east)
    lons = [west_, east_]
    lon = west_ + lon_incr
    while lon < east_:
        lons.append(lon)
        lon += lon_incr * 2
    if west_ > east_:
        while lon <= 180:
            lons.append(lon)
            lon += lon_incr * 2
        lon = east_ - lon_incr
        while lon > -180:
            lons.append(lon)
            lon -= lon_incr * 2

    result = set()
    for lat in lats:
        for lon in lons:
            result.add(Geohash.encode(lat, lon, precision=precision))
    return result

def return_obsdata_from_client_query(client, FIELDS_TO_GET, data_type, table_name, start, end, cutoff_time, north, south, west, east):
    ''' Return the ddb rows in a list'''
    ghashes = get_geohashes(north,south,west,east)
    ddbrow_list = []

    def download_queue(request):
        resultset = client.query(**request)
        return resultset['Items']
    
    for geo in ghashes:
        request = {
            'ExpressionAttributeNames': {
                '#n0': 'report_type_geohash', '#n1': 'valid_time', '#n2': 'available_time'},
            'ExpressionAttributeValues': {
                        ':v0': {'S': data_type+'_'+geo},
                ':v11': {'S': start.strftime("%Y%m%d%H%M%S")},
                ':v12': {'S': end.strftime("%Y%m%d%H%M%S")},
                ':v2': {'S': cutoff_time.strftime("%Y%m%d%H%M%S")}
                },
                    'ProjectionExpression': ','.join(FIELDS_TO_GET),
            'FilterExpression': '(#n2 < :v2)',
            'KeyConditionExpression': '((#n0 = :v0) AND (#n1 BETWEEN :v11 AND :v12))',
            'IndexName': 'RecordTypeGeohashIndex',
            'TableName': table_name
                   }
        ddbrow_list.extend(download_queue(request))
    
    return ddbrow_list

def ddb_pp(ddb_row):
    new_ddb_row = {}
    for ckey in ddb_row.keys():
        if isinstance(ddb_row[ckey], Decimal):
            new_ddb_row[ckey] = float(ddb_row[ckey])
        else:
            new_ddb_row[ckey] = ddb_row[ckey]
    return new_ddb_row

def write_ascii(ddb_data):
    '''ascii format: stn_id stn_lon stn_lat stn_height obs_datetime subset 
                     obs_pressure obs_temperature obs_dewpoint obs_u obs_v 
                     metar_cloud_amount metar_cloud_base metar_weathertype metar_visibility metar_dewpoint'''

    text_file = open("Output.txt", "w")
    
    ascii_in = {'stn_id': -88888,  'stn_lon': -88888, 'stn_lat': -88888, 'stn_height': -88888, \
                'obs_datetime': -88888, 'subset': 'unknown', \
                'obs_pressure': -88888, 'obs_temperature': -88888, 'obs_dewpoint': -88888, \
                'obs_u': -88888, 'obs_v': -88888, \
                'metar_cloud_amount': -88888, 'metar_cloud_base': -88888, \
                'metar_weathertype': -88888, 'metar_visibility': -88888, 'metar_dewpoint': -88888}
    for cdata in ddb_data:
        ascii_out = ascii_in.copy()
        if set(['obs_id', 'longitude', 'latitude', 'valid_time']).issubset(cdata.keys()):
            ascii_out['stn_id'] = cdata['obs_id']
            if 'synop' in cdata['obs_id']:
                ascii_out['subset'] = 'ADPSFC'
            ascii_out['stn_lon'] = cdata['longitude']
            ascii_out['stn_lat'] = cdata['latitude']
            ascii_out['obs_datetime'] = datetime.strftime(datetime.strptime(cdata['valid_time'],'%Y%m%d%H%M%S'), '%Y%m%d%H')
        else:
            continue

        if 'elevation' in cdata.keys():
            ascii_out['stn_height'] = cdata['elevation']

        if 'pressureReducedToMeanSeaLevel' in cdata.keys():
            ascii_out['obs_pressure'] = cdata['pressureReducedToMeanSeaLevel']

        if 'airTemperature' in cdata.keys():
            ascii_out['obs_temperature'] = cdata['airTemperature']

        if 'dewpointTemperature' in cdata.keys(): 
            ascii_out['obs_dewpoint'] = cdata['dewpointTemperature']
 
        if 'windSpeed' in cdata.keys() and 'windDirection' in cdata.keys():
            obs_u, obs_v = get_wind_components(cdata['windSpeed'], cdata['windDirection'])
            ascii_out['obs_u'] = obs_u
            ascii_out['obs_v'] = obs_v
      
        text_file.write('{} {} {} {} {} {} {} {} {} {} {} {} {} {} {} {}\n'.format( \
                        ascii_out['stn_id'], ascii_out['stn_lon'], ascii_out['stn_lat'], ascii_out['stn_height'], \
                        ascii_out['obs_datetime'], ascii_out['subset'], \
                        ascii_out['obs_pressure'], ascii_out['obs_temperature'], ascii_out['obs_dewpoint'],\
                        ascii_out['obs_u'], ascii_out['obs_v'], \
                        ascii_out['metar_cloud_amount'], ascii_out['metar_cloud_base'], \
                        ascii_out['metar_weathertype'], ascii_out['metar_visibility'], ascii_out['metar_dewpoint']))

    text_file.close()

def return_obsdata_from_resource_query(client, FIELDS_TO_GET, data_type, table_name, start, end, cutoff_time, north, south, west, east):
    ''' Return the ddb rows in a list'''
    ghashes = get_geohashes(north,south,west,east)
    ddbrow_list = []

    def download_queue(request):
        resultset = client.query(**request)
        return resultset['Items']
    
    for geo in ghashes:
        request = {
            'ExpressionAttributeNames': {
                '#n0': 'report_type_geohash', '#n1': 'valid_time', '#n2': 'available_time'},
            'ExpressionAttributeValues': {
                        ':v0': {'S': data_type+'_'+geo},
                ':v11': {'S': start.strftime("%Y%m%d%H%M%S")},
                ':v12': {'S': end.strftime("%Y%m%d%H%M%S")},
                ':v2': {'S': cutoff_time.strftime("%Y%m%d%H%M%S")}
                },
                    'ProjectionExpression': ','.join(FIELDS_TO_GET),
            'FilterExpression': '(#n2 < :v2)',
            'KeyConditionExpression': '((#n0 = :v0) AND (#n1 BETWEEN :v11 AND :v12))',
            'IndexName': 'RecordTypeGeohashIndex',
            'TableName': table_name
                   }
        ddbrow_list.extend(download_queue(request))
    
    return ddbrow_list

if __name__ == '__main__':
    ddb_status = 'prod'
    ddb_region = 'us-west-2'
    DDB_OBS = ['synop']
    valid_from = '201708210000'
    valid_to = '201708220000'
    cutoff_time = '201708230000'
    north = -30.5372929888
    south = -50.3248894675
    west = 150.911072332
    east = 180.96116602
    query_method = 'resource' # client or resource
    
    hostlocation = 'kelburn'
    table_name = '{}_observations_archive_2017'.format(ddb_status)
    
    conv = tools.byteify(utils.get_conventions(ddb_status))
    keys_path = conv[ddb_status][hostlocation]['path_to_iam_keys']

    valid_from = datetime.strptime(valid_from, '%Y%m%d%H%M')
    valid_to = datetime.strptime(valid_to, '%Y%m%d%H%M')
    cutoff_time = datetime.strptime(cutoff_time, '%Y%m%d%H%M')
    
    
    resource = connections.get_resource('dynamodb', region_name = ddb_region, 
                                                        status = ddb_status,
                                                        role_name='amps-{}-gp'.format(ddb_status),
                                                        keys_path=keys_path)

    ddb_fields = 'pressureReducedToMeanSeaLevel, elevation, dewpointTemperature, longitude, obs_id, valid_time, windSpeed, latitude, airTemperature, windDirection'
    ddb_data = []
    for data_type in DDB_OBS:
        request = Key('report_type_geohash').eq('{}_rb'.format(data_type)) & Key('valid_time').between(valid_from.strftime('%Y%m%d%H%M'), valid_to.strftime('%Y%m%d%H%M'))
            
        response = resource.Table(name=table_name).query(IndexName='RecordTypeGeohashIndex',
                                                             ProjectionExpression=ddb_fields,
                                                             KeyConditionExpression=request)
        for cddb_row in response['Items']:
            ddb_data.append(ddb_pp(cddb_row))

    write_ascii(ddb_data)
    print 'done'
        
