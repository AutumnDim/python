% function Sites2Grid(fset,v, nots, time_step)
% fset
% v
% nots: 1 Write selnot.cmd file; 0 not use setnot function
% DAILY GLOBAL HISTORICAL CLIMATOLOGY NETWORK (GHCN-DAILY) 
% Version 3.02
% 	   ACSH = Average cloudiness sunrise to sunset from manual 
% 	          observations (percent)
% 	   AWND = Average daily wind speed (tenths of meters per second)
%      PRCP = Precipitation (tenths of mm)
%      TMAX = Maximum temperature (tenths of degrees C)
%      TMIN = Minimum temperature (tenths of degrees C)
%      The filling value is -9999
% Data from China Meteorological Information Sharing System (CIMISS£©
%      PRCP = Precipitation (mm)
%      TMAX = Maximum temperature (degrees C)
%      TMIN = Minimum temperature (degrees C)
%      RHU  = Rative humidity (%)
%      SSD  = Sunlit hour (hour)
%      WIN  = Average daily wind speed (meters per second)
%      The filling value is 999999
% Output merged data by the above two data
%      PRCP = Precipitation (tenths of mm)
%      TMAX = Maximum temperature (tenths of degrees C)
%      TMIN = Minimum temperature (tenths of degrees C)
%      WIN  = Average daily wind speed (tenths of meters per second)
%      RHU  = Rative humidity (%)
%      SSD  = Sunlit hour (tenths of hour)
%      The filling value is -9999
%_________________By:jbwang@igsnrr.ac.cn,On Dec.30, 2016___________________
clear all
close all
clc
vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};

fsid = 'E:\MeteoGrid\CIMISS_table\Qinghai_Stations.txt';
if exist(fsid,'file')
    % station_name:sname, station_id:sid, station_number: nsd
    [sname, sid] = textread(fsid, '%s%d');
    nsd = length(sid);

    tic;
v = 2;
yr0 = 1980; t0 = datenum(yr0, 1,1); 
yr1 = 1980;
yr2 = 2015;
total_day_num = datenum(yr2 + 1, 1, 1) - t0;
MSTN = zeros([nsd, total_day_num]);

sub = 'E:\MeteoGrid\MeteoDbase\';
    for yr = yr1:yr2
        days = datenum(yr+1,1,1)-datenum(yr,1,1);
        % READ GHCN-CIMISS
        ff = [sub '\' vname{v} '\'  vname{v} '_' num2str(yr) '.txt'];
        if exist(ff, 'file')
            % disp(ff);
            [id, xd, n1] = readDbase(ff,days+3);
            d1 = datenum(yr, 1, 1) - t0 + 1;
            d2 = datenum(yr + 1, 1, 1) - t0;
            gid = char(id); ID = str2num(gid(:,4:end));
            geo = xd(:,1:3);
            for i = 1 : nsd
                j = find(ID==sid(i), 1);
                if ~isempty(j)
                    MSTN(i,d1:d2) = xd(j,4:end);
                else
                    MSTN(i,d1:d2) = -9999*ones([1, days]);
                end
            end
        else
            nsd = []; xsd = []; n1 = 0;
        end
        disp(num2str([yr, toc]));
    end
    tx = (1:total_day_num) + datenum(yr0, 1, 1) - 1;
    mon = month(tx);
    yrn = year(tx);
    yri = unique(yrn);
    dat = (MSTN(1:nsd,:))';
    dat(dat < -9000) = NaN;
    num_yr = []; mn_yr = [];
    for i = 1 : length(yri)
        days = datenum(yri(i)+1,1,1)-datenum(yri(i),1,1);
        x0 = dat(yrn == yri(i),:);
        num_yr(i,:) = sum(~isnan(x0)) / days;
        mn_yr(i,:) = mean(x0, 'omitnan') * days / 10;
    end
    figure; plot(yri, mn_yr);
    
    mn_dat = mean(dat, 'omitnan');
    sd_dat = std(dat, 'omitnan');
    mx_dat = max(dat);
    mi_dat = min(dat);
    p05_dat = quantile(dat, 0.05);
    p95_dat = quantile(dat, 0.95);

    figure; plot(1:nsd, mn_dat,'b-x');hold on
    plot(1:nsd, mx_dat,'r-x');
    plot(1:nsd, mi_dat,'g-x');
    plot(1:nsd, p95_dat,'y-x');
    plot(1:nsd, p05_dat,'c-x');
    for i = 1 : nsd
        x0 = dat(~isnan(dat(:,i)), i);
        num_dat(i,1) = length(x0) / total_day_num;
        % figure;hist(dat(:,i));
    end

end
disp(datestr(now));
disp('That''s all, go home!');

