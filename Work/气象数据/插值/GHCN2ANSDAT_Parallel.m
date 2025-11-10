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
vname = {'PRCP'; 'TMIN'; 'TMAX'; 'TAVG'; 'RHU'; 'SSD';  'WIN'};
yr1 = 1980;yr2 = 1986;
wks_in  = 'E:\MeteoGrid\MeteoDbase\';
wks_out = 'E:\MeteoGrid\temp';     % Database with Anusplin formation
wks_tmp = 'E:\MeteoGrid\temp';    % Temporary fold for cmd files
wks_grd = 'D:\China8km\';          % Database for interpolated grid

fdem = 'asiadem8km.txt';
fhdr = 'E:\China8km\MeteoGrid\asiadem8km.hdr';
proj = geotiffinfo('E:\China8km\Parameters\asia_mcd12q1-8km.tif');
[mcd, R, bbox] = geotiffread('E:\China8km\Parameters\asia_mcd12q1-8km.tif');

yr_bat = [yr1 yr2];
direct = {{wks_out;wks_tmp;wks_grd};...         
    {[pwd '\' wks_out(4:end)];[pwd '\' wks_tmp(4:end)];[pwd '\' wks_grd(4:end)]}};% direct{1,1} is for Windows OS and direct{2,1} for Unix OS.
disp(datestr(now));
disp('Vname Year   day  Valid_Stn_Num  All_Stn_Num Used_time(sec.)');
if matlabpool('size') <= 0  % determine whether par started
    matlabpool('open', 'local',7)
else
    disp('Already initialized');
end
parfor v = 1:7
    tic;
    [status, results] = system(['del ' wks_tmp '\' vname{v} '\*.bat']);
    sub  = [wks_tmp vname{v}];
    if ~exist(sub,'dir')
        system(['mkdir ' sub]);
    end
    [status, results] = system(['copy splina.exe ' wks_tmp '\' vname{v} '\']);
    [status, results] = system(['copy lapgrd.exe ' wks_tmp '\' vname{v} '\']);
    [status, results] = system(['copy ' fdem ' ' wks_tmp '\' vname{v} '\']);
    
    sub  = [wks_grd vname{v}];
    if ~exist(sub,'dir')
        system(['mkdir ' sub]);
    end
    
    sub  = [wks_in vname{v}];
    if ~exist(sub,'dir')
        system(['mkdir ' sub]);
    end
   
    for yr = yr1:yr2
        days = datenum(yr+1,1,1)-datenum(yr,1,1);
        % READ GHCN-CIMISS
        ff = [sub '\' vname{v} '_' num2str(yr) '.txt'];
        if exist(ff, 'file')
            % disp(ff);
            [id xd n1] = readDbase(ff,days+3);
            sd = char(id);
            lat = xd(:,1); lon = xd(:,2); elv = xd(:,3); dat = xd(:,4:end);
            [x, y] = projfwd(proj, lat, lon);
            s0 = [x, y, elv];
                    
            % Check coincident data points
            [sid, gxy, sdat] = LookCoincident(sd, s0, dat);
            

            for dy = 1 : days
                if dy == days
                    disp(dy);
                end
                
                x0   =  sdat(:,dy);
                data =  x0(x0 > -900 & x0 < 900);
                geo  =  s0(x0 > -900 & x0 < 900,:);
                gid  = sid(x0 > -900 & x0 < 900,:);
                nx = length(data);
                if ~isempty(data) && nx >= 50
                    
                    % write to file with the formation of Anusplin
                    csv2Anuspl(yr, dy, vname{v}, wks_out, gid,geo, data, sid);
                    
                    [dn dm] = size(data);
                    makesplinabat(yr, direct, dm, dy, vname{v}, fdem, fhdr);       
                    
                    if mod(dy - 1, 50) == 0
                        disp([vname{v} ' ' num2str([yr dy length(data) length(sdat)], '%6d') ' ' num2str(toc)]);
                    end
                end
            end
        else
            nsd = []; xsd = []; n1 = 0;
        end
    end
    disp(datestr(now));
end
disp(datestr(now));

if matlabpool('size') > 0  % determine whether par started
    matlabpool close force local;
end

disp('That''s all, go home!');

