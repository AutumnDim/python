% E:\MeteoGrid\Function_set\readghcnmetX.m
% The function included:
%        (1) select stations according to given geographic boundary and
%            save it as a file, or load stations from a file
%        (2) read data from each station file to a container map and save it,
%            or load a container map if it exists
%        (3) write data to file for each variable and each year with the
%            formation as: ID LAT LON ELV D1, D2, ..., DN. N is 365 or 366.
% Usage: (1) Define ghcnd_subset_stations file with its path or
%        (2) Define the ghcnd-stations and geographic boundary (x1, x2, y1,
%            y2) to select stations and save them to a file.
% By: JBWANG@IGSNRR.AC.CN, Dec. 30, 2016
% DAILY GLOBAL HISTORICAL CLIMATOLOGY NETWORK (GHCN-DAILY)
% Version 3.02
% 	   ACSH = Average cloudiness sunrise to sunset from manual
% 	          observations (percent)
% 	   AWND = Average daily wind speed (tenths of meters per second)
%      PRCP = Precipitation (tenths of mm)
%      TMAX = Maximum temperature (tenths of degrees C)
%      TMIN = Minimum temperature (tenths of degrees C)


close all
clear all
clc

tic
fsub = 'E:\MeteoGrid\ghcnd\ghcnd_subset_stations.txt';
if ~exist(fsub, 'file')
    fsta = 'E:\MeteoGrid\ghcnd\ghcnd-stations.txt';
    [id, lat, lon, elv] = readghcnstation(fsta, 50, 160, -10, 65);
    fop = fopen(fsub, 'w');
    fprintf(fop, 'SID\tLat\tLon\tElv\n');
    for i = 1 : length(elv)
        fprintf(fop, '%s\t%f\t%f\t%f\n', id(i,:), lat(i), lon(i), elv(i));
    end
    fclose(fop);
else
    [id, lat, lon, elv] = textread(fsub, '%s%f%f%f',  'headerlines',1);
    id = cell2mat(id);
end
num_id = length(id);

yr_pro = 2018;
num_days = datenum(yr_pro + 1, 1, 1) - datenum(yr_pro, 1, 1);
num_ele = 8;
ele = {'PRCP'; 'TMAX'; 'TMIN';'TAVG';'SNOW';'SNWD';'ACSH'; 'AWND'};

disp(datestr(now));

if exist(['H:\Workspace\Global8km\ghcn\ghcn_map_' num2str(yr_pro) '.mat'], 'file')
    load(['H:\Workspace\Global8km\ghcn\ghcn_map_' num2str(yr_pro) '.mat']); % load ghcn as container map';
else
    ghcn = containers.Map;
    % X = zeros([datenum(yr_pro+1, 1,1)-datenum(yr_pro, 1, 1), 5]) - 9999;
    % ff = ['\\BA-37AEDE\Temporary\Wangjuwu\ghcn\ghcnd_all\ghcnd_all\' fdir(i).name];
    ff = ['H:\Workspace\MeteoGrid\GHCN\' num2str(yr_pro) '.csv'];
    if exist(ff, 'file')
        [ID , YMD, ELEMENT, DATA, ~, ~, ~, ~]  = textread(ff, '%s%d%s%d%s%s%s%s', 'delimiter',',', 'emptyvalue',NaN);  %
    else
        return;
    end
    
    n = length(ID);
    conn = database('MeteoSQL/GHCND','wangjb','Wangjb2018');
    
    for i = 1 : n
        if mod(i-1, fix(n/1000)*100) == 0
            disp(['Read ' num2str(i, '%05d') '(' datestr(now) '): ' ff]);
        end
        
        sid = ID{i};
        vr = ELEMENT{i};
        v = find(strcmp(ele,vr));
        
        dt = YMD(i);
        dy = dt - fix(dt / 100) * 100;
        yr = fix(dt / 100 / 100);
        mn = fix((dt - yr * 100 * 100 - dy) / 100);
        jd = datenum(yr, mn, dy) - datenum(yr_pro, 1, 1) + 1;
        if ~ghcn.isKey(sid)
            x0 = zeros([num_days, num_ele]) - 9999;
            x0(jd,v) = DATA(i);
            % newMap = containers.Map, x0);
            ghcn(sid) = x0; % [ghcn; newMap];
        else
            x1 = ghcn(sid);
            x1(jd, v) = DATA(i);  % No. Lat, Lon, Elv
            ghcn(sid) = x1;
        end
        
    end % n = length(ID)
    save(['H:\Workspace\Global8km\ghcn\ghcn_map_' num2str(yr_pro) '.mat'], ghcn)
end        % if exist container then read it, or not read data frome each file. Cas#64874229
toc
nx = length(id);
cdat = zeros([1,num_ele]);
xid = keys(ghcn);
for v = 1 : num_ele
    sub =['E:\MeteoGrid\ghcnd\' ele{v}];
    if ~exist(sub,'dir')
        system(['mkdir ' sub]);
    end
    
    
    fc = [sub '\' ele{v} '_' num2str(yr_pro) '.txt'];
    fp = fopen(fc, 'w');
    for i = 1 : num_id
        sid = id(i,:);
        if ~ghcn.isKey(sid)
            dat = ghcn(sid);
            [nt, mt] = size(dat);
            
            xdt = dat(:,v);
            vdt = xdt(xdt > -9000);
            nd = length(xdt);
            nv = length(vdt);
            
            if ~isempty(xdt) && nv / nd >= 0.8
                fprintf(fp, '%s\t%f\t%f\t%f', id{i}, lat(i), lon(i), elv(i));
                for j = 1 : length(xdt)
                    fprintf(fp, '\t%f', xdt(j));
                end
                fprintf(fp, '\n');
                cdat(v) = cdat(v) + 1;
            end
        end
    end
    fclose(fp);
end
toc
disp(['Number of data file: ' num2str(cdat)]);


