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
vname = {'PRCP'; 'TAVG'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
yr1 = 1980;yr2 = 2015;
wks_in  = 'E:\MeteoGrid\MeteoDbase\';
wks_out = 'D:\temp\Huanj';     % Database with Anusplin formation
wks_tmp = 'D:\temp\Huanj';    % Temporary fold for cmd files
wks_grd = 'D:\temp\HuanjGrid\';          % Database for interpolated grid

fdem = 'srtm_Huanj_250m.txt';
fhdr = 'D:\STSZHANGLI\CERN\srtm_Huanj_250m.hdr';
proj = geotiffinfo('D:\STSZHANGLI\SRTM\SRTM_Huanj_250m.tif');
[mcd, R, bbox] = geotiffread('D:\STSZHANGLI\SRTM\SRTM_Huanj_250m.tif');

yr_bat = [yr1 yr2];
direct = {{wks_out;wks_tmp;wks_grd};...         
    {[pwd '\' wks_out(4:end)];[pwd '\' wks_tmp(4:end)];[pwd '\' wks_grd(4:end)]}};% direct{1,1} is for Windows OS and direct{2,1} for Unix OS.
disp(datestr(now));
disp('Vname Year   day  Valid_Stn_Num  All_Stn_Num Used_time(sec.)');
% if matlabpool('size') <= 0  % determine whether par started
%     matlabpool('open', 'local',7)
% else
%     disp('Already initialized');
% end
for v = 1:1
    tic;
    sub  = [wks_tmp '\' vname{v}];
    if ~exist(sub,'dir')
        system(['mkdir ' sub]);
    else
       delete([wks_tmp '\' vname{v} '\*.*']);
       delete([wks_grd '\' vname{v} '\*.*'])
    end
    if strcmp(vname{v},'PRCP')
        mean_or_sum = 0;
    else
        mean_or_sum = 1;
    end
    cd('E:\MeteoGrid\Function_set');
    [status, results] = system(['copy splina.exe ' wks_tmp '\' vname{v} '\']);
    [status, results] = system(['copy splinb.exe ' wks_tmp '\' vname{v} '\']);
    [status, results] = system(['copy selnot.exe ' wks_tmp '\' vname{v} '\']);
    [status, results] = system(['copy lapgrd.exe ' wks_tmp '\' vname{v} '\']);
    [status, results] = system(['copy ' fdem ' ' wks_tmp '\' vname{v} '\']);
    % toc
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
        dy1 = 1:days;  % weekly average
        dy2 = fix((dy1 - 1) / 8) * 8 + 1;
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
            [n m] = size(sdat);
            j = 1;data = [];geo = []; gid = [];
            for i = 1 : n
                x0 = sdat(i,:);
                x1 = x0(x0 > -900 & x0 < 900);
                n1 = length(x1);
                if n1/m >= 0.8
                    data(j,:) = x0;
                    geo(j,:) = gxy(i,:);
                    gid(j,:) = sid(i,:);
                    j = j + 1;
                end
            end
            data(data < -900 | data > 30000) = 32766;
            
            % Fill missing data if the missing data less than 20%
            [filled_data qc sta,nf] = fillmissing(data, gid,geo);
            
            % Mean by DOY
            [averaged_data,q,sd] = meanbyxdays(filled_data, sta, dy2, mean_or_sum);
            
            % write to file with the formation of Anusplin
            csv2Anuspl(yr, vname{v}, wks_out, gid,geo, averaged_data);

            makesplinabat(yr, direct, size(averaged_data), vname{v}, fdem, fhdr);       

            disp([vname{v}, ' ', num2str([yr n,j-1])  ' ' num2str(toc)]);
        else
            nsd = []; xsd = []; n1 = 0;
        end
    end
    disp(datestr(now));
    % change to vname{v} sub and run vname{v}_spl.bat
    cd([wks_tmp '\' vname{v}]);
    dos([vname{v} '_spl.bat']);
end
disp(datestr(now));

% if matlabpool('size') > 0  % determine whether par started
%     matlabpool close force local;
% end

disp('That''s all, go home!');

