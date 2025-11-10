% function dbase2station
% Seperate data to each station,
%        ! Calculate extreme indices from station data in a single format
% ! Format is:
%
% !      lat,long  (-ve latitude for southern hemisphere, longitude format not important)
% ! yr,mth,day,tmin,tmax,tmean,precip
% !      ...
% !      ...
% !      ...
% ! yr,mth,day,tmin,tmax,tmean,precip
%
% ! fields need to be separated by a comma or space
% Data source: China Meteorological Information Sharing System (CIMISS£©
%      PRCP = Precipitation (mm)
%      TMAX = Maximum temperature (degrees C)
%      TMIN = Minimum temperature (degrees C)
%      RHU  = Rative humidity (%)
%      SSD  = Sunlit hour (hour)
%      WIN  = Average daily wind speed (meters per second)
%_________________By:jbwang@igsnrr.ac.cn,On Dec.30, 2016___________________
close all; clear all; clc;
vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
vad_value = [-60 60; 0 1000; -60 60; -60 60; 0 100; 0 18; 0 20]*10;
yr1 = 1960; yr2 = 2015;
load sta_info;

s0 = char(sta_info{1,1});
x0 = sta_info{1,3};
y0 = sta_info{1,2};
sid = [];
for i = 1 : length(s0), sid{i,1} = s0(i,:);end
ns = length(s0);
nt = datenum(yr2+1,1,1)-datenum(yr1,1,1);

tic;
v = 1;
fcsv = ['E:\MeteoGRid\Stations\' vname{v} '_' num2str(yr1) '-' num2str(yr2) '.csv'];
TAVG = load(fcsv);
v = 2;
fcsv = ['E:\MeteoGRid\Stations\' vname{v} '_' num2str(yr1) '-' num2str(yr2) '.csv'];
PRCP = load(fcsv);
v = 3;
fcsv = ['E:\MeteoGRid\Stations\' vname{v} '_' num2str(yr1) '-' num2str(yr2) '.csv'];
TMIN = load(fcsv);
v = 4;
fcsv = ['E:\MeteoGRid\Stations\' vname{v} '_' num2str(yr1) '-' num2str(yr2) '.csv'];
TMAX = load(fcsv);
j = 1;

xs = find(~isnan(TAVG(:,1)));
ns = length(xs);

t1 = datenum(yr1,1,1);
t2 = datenum(yr2,12,31);
tz = t1:t2;
yr = year(tz);
mo = month(tz);
dy = day(tz);

sta = sid(xs);
lon = x0(xs);
lat = y0(xs);
for i = 1 : ns
    id = xs(i);
    ff = ['E:\MeteoGRid\Stations\' sta{i} '.csv'];
    fp = fopen(ff, 'w');
    fprintf(fp, '%.4f,%.4f\n', lat(i), lon(i));
    fclose(fp);
    
    ti = TMIN(id,:)/10; tx = TMAX(id,:)/10; tm = TAVG(id,:)/10;
    js = find(~isnan(ti) & ~isnan(tx) & isnan(tm));
    tm(js) = (ti(js) + tx(js))/2;
    
    XD = [yr;mo;dy;ti; tx; tm; PRCP(id,:)/10];
    
    dlmwrite(ff,XD','delimiter',',','-append');
end

