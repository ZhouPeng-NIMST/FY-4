
# coding: utf-8

# In[ ]:


import os 
import numpy
from netCDF4 import Dataset as nc
from netCDF4 import num2date
import h5py
# import gc
# import pandas as pd
np.set_printoptions(suppress= True)


# In[ ]:


def maTch(ec_data,index_lat,index_lon,num,ispr = True):
    '''
    地面数据与大气层数据分开匹配
    '''
    if ispr:
        out = np.array([ec_data[num,:,i,j] for i,j in zip(index_lat,index_lon)])
        return out[:,::-1]
    else:
        out = np.array([ec_data[num,i,j] for i,j in zip(index_lat,index_lon)])
        return out


# In[ ]:


# 存放数据
pathout = r'D:\FY4\matched'
mons = ['07','08','09','10','11','12']
for mon in [mons[0]]:
    data = np.full((1,488),999)
    # 路径设置
    path_ec = r'F:\EC&GIIRSdata\ec_small\2018'+ mon
    path_giirs = r'F:\EC&GIIRSdata\giirs\2018'+ mon
    for file_ec in os.listdir(path_ec):
        if file_ec[-5] == 'p':
    #        print(os.path.join(path_ec,files_ec))
    #       打开文件
            fname_ec = os.path.join(path_ec,file_ec)
            f_pr = nc(fname_ec)
            f_sr = nc(fname_ec[:-5] + 'sr.nc')
    #         获取经纬度
            lon_ec = f_pr.variables['longitude'][:]
            lat_ec = f_pr.variables['latitude'][:]
            time_list = [num2date(o,f_pr.variables['time'].units).strftime('%Y%m%d') for o in f_pr.variables['time']]
            time_list_HH = [num2date(o,f_pr.variables['time'].units).strftime('%Y%m%d%H') for o in f_pr.variables['time']]
    #         遍历giirs文件
            for dirs_gr in os.listdir(path_giirs):
                for name in os.listdir(os.path.join(path_giirs,dirs_gr)):
                    if name == file_ec[6:8]:
                        dir_gr_dd = os.path.join(os.path.join(path_giirs,dirs_gr),name)
                        for file_gr in os.listdir(dir_gr_dd):
                            fname_gr = os.path.join(dir_gr_dd,file_gr)
    #                         获取giirs文件时间
                            time_gr = fname_gr.split('_')[7]
    #                         根据时间索引ec中的第几个
                            if fname_gr.split('_')[-4][8:10] == '23':
                                num = time_list.index(time_gr) + 1
                            else:
                                num = time_list.index(time_gr)
    #                         文件时间记录
                            datatime_save_ec = np.array([time_list_HH[num] for i in range(128)])
                            datatime_save_gr = np.array([fname_gr.split('_')[-4][:12]for i in range(128)])
                            print(time_list_HH[num],fname_gr.split('_')[-4][:12])
    #                       打开giirs文件
                            f_gr = h5py.File(fname_gr,'r')
    #                       读取数据
                            lon_giirs = f_gr['IRLW_Longitude'][:]
                            lat_giirs = f_gr['IRLW_Latitude'][:]
                            slaz_giirs = f_gr['IRLW_SatelliteZenith'][:]
                            saz_giirs = f_gr['IRLW_SolarZenith'][:]
                            mw = f_gr['ES_RealMW'][240:561,:].T * 100
                            lw = f_gr['ES_RealLW'][96:145,:].T
    #                       获得最近点坐标
                            index_lon = abs(lon_giirs.reshape(-1,1) - lon_ec.reshape(1,-1)).argmin(axis=1)
                            index_lat = abs(lat_giirs.reshape(-1,1) - lat_ec.reshape(1,-1)).argmin(axis=1)
                            # 匹配
                            t_ec_match = maTch(f_pr.variables['t'],index_lat,index_lon,num,ispr= True)
                            r_ec_match = maTch(f_pr.variables['r'],index_lat,index_lon,num,ispr= True)
                            o3_ec_match = maTch(f_pr.variables['o3'],index_lat,index_lon,num,ispr= True) * 1e8
                            c_ec_match = maTch(f_sr.variables['tcc'],index_lat,index_lon,num,ispr= False) * 10000
    #                         关闭文件
                            f_gr.close()
    #                       拼接
                            thisfile = np.c_[np.c_[datatime_save_ec,datatime_save_gr],np.c_[lon_giirs,lat_giirs,slaz_giirs,saz_giirs,lw,mw,t_ec_match,r_ec_match,o3_ec_match,c_ec_match].round(2)]
                            data = np.r_[data,thisfile]
                            thisfile = []
            f_pr.close()
            f_sr.close()

    # 删除第一行
    data = np.delete(data,0,axis=0)
#     np.savetxt(mon + '.txt',data,fmt='%.2s')


# In[ ]:


# # 打开文件
# f_gr = h5py.File(path1,'r')
# f_rh = nc(path2)
# f_c = nc(path2[:-5] + 'sr.nc')


# In[ ]:


# # 获取数据
# lon_ec = f_rh.variables['longitude'][:]
# lat_ec = f_rh.variables['latitude'][:]
# lon_giirs = f_gr['IRLW_Longitude'][:]
# lat_giirs = f_gr['IRLW_Latitude'][:]
# slaz_giirs = f_gr['IRLW_SatelliteZenith'][:]
# saz_giirs = f_gr['IRLW_SolarZenith'][:]
# mw = f_gr['ES_RealMW'][240:561,:].T
# lw = f_gr['ES_RealLW'][96:145,:].T


# In[ ]:


# # 获得最近点坐标
# index_lon = abs(lon_giirs.reshape(-1,1) - lon_ec.reshape(1,-1)).argmin(axis=1)
# index_lat = abs(lat_giirs.reshape(-1,1) - lat_ec.reshape(1,-1)).argmin(axis=1)


# In[ ]:


# # 匹配
# t_ec_match = maTch(f_rh.variables['t'],index_lat,index_lon,ispr= True)
# r_ec_match = maTch(f_rh.variables['r'],index_lat,index_lon,ispr= True)
# o3_ec_match = maTch(f_rh.variables['o3'],index_lat,index_lon,ispr= True)
# c_ec_match = maTch(f_c.variables['tcc'],index_lat,index_lon,ispr= False)


# In[ ]:


# # 关闭文件
# f_gr.close()
# f_ec.close()
# f_c.close()


# In[ ]:


# # 拼接
# thisfile = np.c_[lon_giirs,lat_giirs,slaz_giirs,saz_giirs,lw,mw,t_ec_match,r_ec_match,o3_ec_match,c_ec_match]
# data = np.r_[data,thisfile]

