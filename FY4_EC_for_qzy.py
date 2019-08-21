# coding: utf-8


from netCDF4 import Dataset as nc
from netCDF4 import num2date
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
np.set_printoptions(suppress=True)


def fidx(data_ec, index_lon, index_lat, time):
    '''
    return matched arr
    '''
    arr = np.zeros((37,index_lon.shape[0],index_lon.shape[1]))
    for i in range(index_lon.shape[0]):
        for j in range(index_lon.shape[1]):
            arr[:,i,j] = data_ec.variables['t'][time,:,index_lat[i,j],index_lon[i,j]].data
    return arr

def getTime(data_ec, time):
    '''
    return str of time[i]
    '''
    return num2date(data_ec['time'][time],data_ec['time'].units).strftime('%Y%m%d%H')

def getLonlat(data_f4, flag=1):
    '''
    data_f4: dataset of fy-4
    flag: 1:T/0:H
    '''
    lon = data_f4.variables['LW_Longitude'][:] if flag else data_f4.variables['MW_Longitude'][:]
    lat = data_f4.variables['LW_Latitude'][:] if flag else data_f4.variables['MW_Latitude'][:]
    return lon.data, lat.data    

def getGoodTH(data_f4, flag = 1, allbest = 1):
    '''
    data_f4: dataset of fy-4
    flag: 1:T/0:H
    '''
    QF = data_f4.variables['AT_Prof_QFlag'][:] if flag else data_f4.variables['AH_Prof_QFlag'][:]
    mask = np.where(QF < 1, False, True) if allbest else np.where(QF < 2, False, True)
    return mask

def match_f4_ec(data_f4, data_ec, time):
    '''
    return data_ec & data_f4 matched
    '''
    lon_f4, lat_f4 = getLonlat(data_f4, 1)
    lon_ec = data_ec.variables['longitude'][:].data
    lat_ec = data_ec.variables['latitude'][:].data 
    index_lon = np.argmin(np.abs(lon_f4.reshape(-1,1) - lon_ec.reshape(1,-1)), axis=1)
    index_lat = np.argmin(np.abs(lat_f4.reshape(-1,1) - lat_ec.reshape(1,-1)), axis=1)
    index_lon = index_lon.reshape(lon_f4.shape)
    index_lat = index_lat.reshape(lat_f4.shape)
    arr = fidx(data_ec, index_lon, index_lat, time)
    return arr

def dataInterp(matched_ec, p_f4, p_ec):
    '''
    return interped matched data_f4
    '''
    matched_ec_interp = interpolate.interp1d(p_ec, matched_ec, axis=0, bounds_error= False, fill_value= 'extrapolate')(p_f4)
    return matched_ec_interp


def run():
    path_f4 = r'F:/FY-4-EC/FY4/FY4A-_GIIRS-_N_REGX_1047E_L2-_AVP-_MULT_NUL_20180710060000_20180710060929_016KM_V0001.NC'
    path_ec = r'F:/FY-4-EC/071011tqnewpl'
    data_f4 = nc(path_f4)
    data_ec = nc(path_ec)
    p_f4 = data_f4.variables['Pressure'][:].data
    p_ec = data_ec.variables['level'][:].data
    matched_ec = match_f4_ec(data_f4, data_ec, time= 1)
    mask = getGoodTH(data_f4, flag = 1, allbest = 1)
    matched_ec_interp = dataInterp(matched_ec, p_f4, p_ec)
    f4_t = data_f4.variables['AT_Prof'][:]
    f4_t.mask = mask
    arr = abs(matched_ec_interp - f4_t)
    arr.mask = np.where(arr > 10, True, arr.mask)
    mean_err = [arr[i,:,:].mean() for i in range(101)]
    rms_err = [(arr[i,:,:]**2).mean()**0.5 for i in range(101)]
    return mean_err, rms_err, p_f4

if __name__ == '__main__':
    mean_err,rms_err,p_f4 = run()
    plt.plot(rms_err[30:],p_f4[30:])
    ax = plt.gca()
    ax.invert_yaxis()
    plt.xlabel('RMSE/K',fontsize = 15)
    plt.ylabel('Pre/hPa',fontsize = 15)
    # plt.savefig('')
