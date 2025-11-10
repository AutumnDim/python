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


tic;
parfor v = 3 : 4
    s0 = char(sta_info{1,1});
    x0 = char(sta_info{1,3});
    y0 = char(sta_info{1,2});
    sid = [];
    for i = 1 : length(s0), sid{i,1} = s0(i,:);end
    ns = length(s0);
    nt = datenum(yr2+1,1,1)-datenum(yr1,1,1);
    XS = ones([ns,nt])*NaN;
    vr = vname{v};
    for yr = yr1:yr2
        days = datenum(yr+1,1,1)-datenum(yr,1,1);
        t1 = datenum(yr,1,1)-datenum(yr1,1,1)+1;
        t2 = datenum(yr+1,1,1)-datenum(yr1,1,1);
        tz = t1:t2;
        % READ GHCN-CIMISS
        if yr < 1980
            if v == 1
                vr = 'TMEAN';
            end
            headerline = 0;
            delim_str = '\t';
            field_num = days;
            file_filled = ['E:\MeteoGrid\CMGHfilled\' vr '\' vr '_' num2str(yr) '.txt'];
        else
            headerline = 1;
            delim_str = ',';
            field_num = days + 4;
            file_filled = ['E:\MeteoGrid\MeteoFilled\' vr '_' num2str(yr) '_Filled.csv'];
        end
        disp(file_filled);
        if exist(file_filled, 'file')
            [gid, xd, n1] = readFilledbase(file_filled,field_num, headerline, delim_str);
            if yr >= 1980
                lat = xd(:,2); lon = xd(:,3); elv = xd(:,4);
                filled_data = xd(:,5:end);
            else
                filled_data = xd;
            end
            xs = [];
            for i = 1 : n1
                s0 = char(gid(i,:));
                ns = strcmp(sid, s0);
                nj = find(ns > 0);
                if ~isempty(nj)
                    XS(nj(1),tz) = filled_data(i,:);
                    
                end
            end
        end
    end
    fcsv = ['E:\MeteoGRid\Stations\' vr '_' num2str(yr1) '-' num2str(yr2) '.csv'];
    csvwrite(fcsv, XS);
end
