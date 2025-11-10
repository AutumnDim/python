function Sites2Kriging(fset,v, nots, time_step)
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
% clear all
% close all
% clc
% v = 2;
% nots = 1;
% fset = 'Shennj.set';
% time_step = 10;
vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
vad_value = [-60 60; 0 1000; -60 60; -60 60; 0 100; 0 18; 0 20]*10;
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
[dem, R, bbox] = geotiffread(ftif);
[nl,np] = size(dem);
xc = bbox(1,1)+R(2,1)/2: R(2,1): bbox(2,1)-R(2,1)/2;
yc = bbox(1,2)+R(2,1)/2: R(2,1): bbox(2,2)-R(2,1)/2;
[xx, yy] = meshgrid(xc, yc);
x_est = reshape(xx, nl*np, 1);
y_est = reshape(yy, nl*np, 1);
z_est = double(reshape(dem, nl*np, 1));

csz = R(2,1) * 1000; 
rng = [bbox(1,1)-csz bbox(1,2)-csz; bbox(2,1)+csz bbox(2,2)+csz]/1000;
disp(datestr(now));
disp('Vname Year   day  Valid_Stn_Num  All_Stn_Num Used_time(sec.)');
% if matlabpool('size') <= 0  % determine whether par started
%     matlabpool('open', 'local',7)
% else
%     disp('Already initialized');
% end
%for v = 3:7
    tic;
    sub  = fullfile(wks_tmp,  vname{v});
    if ~exist(sub,'dir')
        system(['mkdir ' sub]);
    end
    if strcmp(vname{v},'PRCP')
        mean_or_sum = 0;
    else
        mean_or_sum = 1;
    end
    % toc
    sub  = fullfile(wks_grd, vname{v});
    if ~exist(sub,'dir')
        system(['mkdir ' sub]);
    end
    
    sub  = [wks_in vname{v}];
    if ~exist(sub,'dir')
        system(['mkdir ' sub]);
    end
    annual_value = [];
    for yr = yr1:yr2
        days = datenum(yr+1,1,1)-datenum(yr,1,1);
        dy1 = 1:days;  % weekly average
        switch time_step
            case 1   % Annually
                dy2 = dy1;
            case 8
                dy2 = fix((dy1 - 1) / 8) * 8 + 1;
            case 10  % 10-day 
                mon = month(datenum(yr,1,1) + dy1 - 1);
                dy  = day(datenum(yr,1,1) + dy1 - 1);
                mj  = dy;
                mj(dy <= 10) = 1; mj(dy > 10 & dy <= 20) = 2; mj(dy > 20) = 3;
                dy2 = (mon - 1) * 3 + mj;
            case 12  % Monthly
                dy2 = month(datenum(yr,1,1) + dy1 - 1);
            case 24  % Half-monthly
                mon = month(datenum(yr,1,1) + dy1 - 1);
                dy  = day(datenum(yr,1,1) + dy1 - 1);
                mj  = dy;
                mj(dy <= 15) = 1; mj(dy > 15) = 2;
                dy2 = (mon - 1) * 2 + mj;
        end
        % READ GHCN-CIMISS
        ff = fullfile(sub, [vname{v} '_' num2str(yr) '.txt']);
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
                x1 = x0(x0 >= vad_value(v,1) & x0 <= vad_value(v,2));
                n1 = length(x1);
                if n1/m >= 0.8 % including data if the missing data less than 20%
                    data(j,:) = x0;
                    geo(j,:) = gxy(i,:);
                    gid(j,:) = sid(i,:);
                    j = j + 1;
                end
            end
            [n,m] = size(data);
            data(data < vad_value(v,1) | data > vad_value(v,2)) = 32766;
            
            % Fill missing data if the missing data less than 20%
            [filled_data qc sta,nf] = fillmissing(data, gid,geo);
            
            % Calculate annual mean or sum on the national scale
            if mean_or_sum == 0
                annual_filled_value = sum(filled_data,2) * 0.1;
            else
                annual_filled_value = mean(filled_data,2) * 0.1;
            end
            annual_raw_value = [];
            for i = 1 : n
                x0 = data(i,:);
                x1 = x0(x0 > -900 & x0 < 9000);
                n1 = length(x1);
                if n1/m >= 0.95 % including data if the missing data less than 20%
                    if mean_or_sum == 0
                        annual_raw_value(i,1) = sum(x1) * 0.1;
                    else
                        annual_raw_value(i,1) = mean(x1) * 0.1;
                    end 
                else
                    annual_raw_value(i,1) = -9999;
                end
            end         
            annual_value(yr-yr1+1,:) = [yr mean(annual_filled_value) std(annual_filled_value) mean(annual_raw_value) std(annual_raw_value) length(annual_raw_value) length(annual_filled_value)];
            % Mean by DOY
            [averaged_data,q,sd] = meanbyxdays(filled_data, sta, dy2, mean_or_sum);
            
            % Select data in the area extend outward cell_size km
            x0 = geo(:,1); y0 = geo(:,2);
            x1 = x0(x0 >= rng(1,1) & x0 <= rng(2,1) & y0 >= rng(1,2) & y0 <= rng(2,2));
            y1 = y0(x0 >= rng(1,1) & x0 <= rng(2,1) & y0 >= rng(1,2) & y0 <= rng(2,2));
             
            coord = [x1, y1];
            max_co = max(coord);
            min_co = min(coord);
            ix = abs(round((max_co(1) - min_co(1)) / R(2,1))) + 1;
            iy = abs(round((max_co(2) - min_co(1)) / R(2,1))) + 1; 
            
            j = 1; 
            dx = averaged_data(x0 >= rng(1,1) & x0 <= rng(2,1) & y0 >= rng(1,2) & y0 <= rng(2,2), j);
            
            % out_dat = matrixdisplay([x1 y1 dx],iy,ix); colorbar; hold on;
            [nx,mx] = size(averaged_data);
            
            if nx > 30
                for j = 1 : 1 % mx
                    tic
                    dx = averaged_data(x0 >= rng(1,1) & x0 <= rng(2,1) & y0 >= rng(1,2) & y0 <= rng(2,2), j);
                    [output,errorvariance] = vebyk([x1 y1 dx],[250 250],16,1,0,0.98,10000,0,0);

                    outdat = matrixdisplay(output,iy,ix); colorbar; hold on;
                    fout = fullfile(wks_grd, vname{v}, [vname{v} '_' num2str(yr * 1000 + j) '.flt']);
                    fop = fopen(fout, 'w');
                    fwrite(fop, outdat', 'float32');
                    fclose(fop);
                    fname = fullfile(wks_grd, vname{v}, [vname{v} '_' num2str(yr * 1000 + j) '.hdr']);
                    [nlines, npixels] = size(outdat); 
                    xll = min(x1); yll = min(y1); cellsize = R(2,1); NODATA_value = -9999; byteorder = 'LSBFIRST';
                    writegrdhdr(fname, nlines, npixels,  xll, yll, cellsize, NODATA_value, byteorder,proj);

                    outerr = matrixdisplay(errorvariance,iy,ix); colorbar; hold on;
                    fout = fullfile(wks_grd, vname{v},  ['Error_' vname{v} '_' num2str(yr * 1000 + j) '.flt']);
                    fop = fopen(fout, 'w');
                    fwrite(fop, outerr', 'float32');
                    fclose(fop);
                    bands = 1; data_type = 4;  interleave = 'BSQ';
                    fout = fullfile(wks_grd, vname{v},  ['Error_' vname{v} '_' num2str(yr * 1000 + j) '.hdr']);
                    writehdr(fout, nlines, npixels, bands, data_type, interleave);

                    % 
                    % outvar = matrixdisplay(errorvariance,iy,ix); colorbar; hold on;
                    % contour(outdat,10);
                    
                    disp([vname{v}, ' ', num2str([yr, n, length(dx),j])  ' ' num2str(toc)]);
                end       
            else
                disp(['Too small sample number (' num2str(nx) ')!']);
            end
            % % write to file with the formation of Anusplin
            % csv2Anuspl(yr, vname{v}, wks_out, gid,geo, averaged_data);
            % 
            % if nots == 1
            %     makesplinotbat(yr, direct, size(averaged_data), vname{v}, fdem, fhdr);    
            % else
            %     splinabat_no_cov(yr, direct, size(averaged_data), vname{v}, fdem, fhdr);
            % end

            
        else
            nsd = []; xsd = []; n1 = 0;
        end
    end
    % write annual statistical value to excel file
    hdr_line = {'Year','Filled_Mean','Filled_STD','Raw_Mean','Raw_STD','Raw_number', 'Filled_number'};
    fxls = fullfile(wks_grd, [vname{v} '_' num2str(yr1) '-' num2str(yr2) '.xls']);
    xlswrite(fxls, hdr_line, 'Sheet1', 'A1');
    xlswrite(fxls, annual_value, 'Sheet1', 'A2');
        
    disp(datestr(now));
    % change to vname{v} sub and run vname{v}_spl.bat
    % cd([wks_tmp '\' vname{v}]);
    % dos([vname{v} '_spl.bat']);
% end
disp(datestr(now));

% if matlabpool('size') > 0  % determine whether par started
%     matlabpool close force local;
% end

disp('That''s all, go home!');

