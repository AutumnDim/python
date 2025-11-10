function Sites2Grid_unix(fset,v)
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
% bsub -o %J.log -e %J.err matlab -nodisplay -r Run_Sites2Grid
% clear all
% close all
% clc
% v = 2;
% fset = 'China1km.set';
%
vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};

if exist(fset, 'file')
    [sname, svalue] = textread(fset, '%s%s');
    yr1 = str2double(svalue{1});yr2 = str2double(svalue{2});
    wks_in  = svalue{3};
    wks_out = svalue{4};     % Database with Anusplin formation
    wks_tmp = svalue{5};    % Temporary fold for cmd files
    wks_grd = svalue{6};          % Database for interpolated grid

    fdem = svalue{7};
    fhdr = svalue{8};
    ftif = svalue{9};
else
    disp('Error: Not find site information file');
    return;
end
proj = geotiffinfo(ftif);
[mcd, R, bbox] = geotiffread(ftif);

yr_bat = [yr1 yr2];
direct = {{wks_out;wks_tmp;wks_grd};...         
    {[pwd '/' wks_tmp(4:end)];[pwd '/' wks_tmp(4:end)];[pwd '/' wks_grd(4:end)]}};% direct{1,1} is for Windows OS and direct{2,1} for Unix OS.
disp(datestr(now));
disp('Vname Year   day  Valid_Stn_Num  All_Stn_Num Used_time(sec.)');
% if matlabpool('size') <= 0  % determine whether par started
%     matlabpool('open', 'local',7)
% else
%     disp('Already initialized');
% end
%for v = 3:7
    tic;
    if ~exist(wks_tmp, 'dir')
        system(['mkdir ' wks_tmp]);
    end
    
    sub  = [wks_tmp '/' vname{v}];
    if ~exist(sub,'dir')
        system(['mkdir ' sub]);
    else
       delete([wks_tmp '/' vname{v} '/*.*']);
       % delete([wks_grd '/' vname{v} '/*.*'])
    end
    if strcmp(vname{v},'PRCP')
        mean_or_sum = 0;
    else
        mean_or_sum = 1;
    end
    cd('/wps/home/wangjb/MeteoGrid/Function_set');
    % [status, results] = system(['copy splina.exe ' wks_tmp '/' vname{v} '/']);
    % [status, results] = system(['copy splinb.exe ' wks_tmp '/' vname{v} '/']);
    % [status, results] = system(['copy selnot.exe ' wks_tmp '/' vname{v} '/']);
    % [status, results] = system(['copy lapgrd.exe ' wks_tmp '/' vname{v} '/']);
    % [status, results] = system(['copy ' fdem ' ' wks_tmp '/' vname{v} '/']);
    % toc
    % sub  = [wks_grd vname{v}];
    % if ~exist(sub,'dir')
    %    system(['mkdir ' sub]);
    % end
    
    sub  = [wks_in vname{v}];

    annual_value = [];
    for yr = yr1:yr2
        days = datenum(yr+1,1,1)-datenum(yr,1,1);
        dy1 = 1:days;  % weekly average
        dy2 = fix((dy1 - 1) / 8) * 8 + 1;
        % READ GHCN-CIMISS
        ff = [sub '/' vname{v} '_' num2str(yr) '.txt'];
        disp(ff);
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
                x1 = x0(x0 > -900 & x0 < 9000);
                n1 = length(x1);
                if n1/m >= 0.8 % including data if the missing data less than 20%
                    data(j,:) = x0;
                    geo(j,:) = gxy(i,:);
                    gid(j,:) = sid(i,:);
                    j = j + 1;
                end
            end
            [n,m] = size(data);
            data(data < -900 | data > 30000) = 32766;
            
            % Fill missing data if the missing data less than 20%
            [filled_data qc sta,nf] = fillmissing(data, gid,geo);
            
            % Calculate annual mean or sum on the national scale
            if mean_or_sum == 0
                annual_filled_value = sum(filled_data,2) * 0.1;
            else
                annual_filled_value = mean(filled_data,2) * 0.1;
            end
            x2 = [];
            for i = 1 : n
                x0 = data(i,:);
                x1 = x0(x0 > -900 & x0 < 9000);
                n1 = length(x1);
                if n1/m >= 0.95 % including data if the missing data less than 20%
                    if mean_or_sum == 0
                        x2(i,1) = sum(x1) * 0.1;
                    else
                        x2(i,1) = mean(x1) * 0.1;
                    end 
                else
                    x2(i,1) = -9999;
                end
            end       
            annual_raw_value = x2(x2 > -9000);
            annual_value(yr-yr1+1,:) = [yr mean(annual_filled_value) std(annual_filled_value) min(annual_filled_value) max(annual_filled_value)...
                                           mean(annual_raw_value) std(annual_raw_value) min(annual_raw_value) max(annual_raw_value)...
                                           length(annual_raw_value) length(annual_filled_value)];
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
    % write annual statistical value to excel file
    hdr_line = {'Year','Filled_Mean','Filled_STD','Raw_Mean','Raw_STD','Raw_number', 'Filled_number'};
    fxls = [wks_tmp '/' vname{v} '_' num2str(yr1) '-' num2str(yr2) '.xls'];
    xlswrite(fxls, hdr_line, 'Sheet1', 'A1');
    xlswrite(fxls, annual_value, 'Sheet1', 'A2');
	
    fcsv = [wks_tmp '/' vname{v} '_' num2str(yr1) '-' num2str(yr2) '_0406.csv'];
	csvwrite(fcsv, annual_value);
    
    disp(datestr(now));
    % change to vname{v} sub and run vname{v}_spl.bat
    % cd([wks_tmp '/' vname{v}]);
    % dos([vname{v} '_spl.bat']);
% end
disp(datestr(now));

% if matlabpool('size') > 0  % determine whether par started
%     matlabpool close force local;
% end

disp('That''s all, go home!');

