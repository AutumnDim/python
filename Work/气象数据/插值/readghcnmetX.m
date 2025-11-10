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
fsub = 'ghcnd_subset_stations.txt';
if ~exist(fsub, 'file')
    fsta = 'ghcnd-stations.txt';
    [id lat lon elv] = readghcnstation(fsta, 50, 160, -10, 65);
    fop = fopen(fsub, 'w');
    fprintf(fop, 'SID\tLat\tLon\tElv\n');
    for i = 1 : length(elv)
        fprintf(fop, '%s\t%f\t%f\t%f\n', id(i,:), lat(i), lon(i), elv(i));
    end
    fclose(fop);
else
    [id lat lon elv] = textread(fsub, '%s%f%f%f',  'headerlines',1);
    id = cell2mat(id);
end
toc
yr_begin = 1980;
yr_now = year(now);
% fdir = dir('\\BA-37AEDE\Temporary\Wangjuwu\ghcn\ghcnd_all\ghcnd_all\*.dly');
toc

disp(datestr(now));
if exist('lat','var')
    n = length(lat);
elseif exist('fdir','var')
    n = length(fdir);
else
    n = 1;
end

if n > 1
%     if matlabpool('size') <= 0  % determine whether par started
%         matlabpool('open', 'local',6)
%     else
%         disp('Already initialized');
%     end
    % parfor i = 1 : n
    tic;
    if exist('ghcn_map_1980-2016.mat', file)
        load('ghcn_map_1980-2016.mat'); % load ghcn as container map';
    else
        ghcn = containers.Map; vmax = 1;
        for i = 1 : n
            var = {'PRCP'; 'TMAX'; 'TMIN';'TAVG';'SNOW';'SNWD';'ACSH'; 'AWND'};
            X = zeros([datenum(yr_now+1, 1,1)-datenum(yr_begin, 1, 1), 5]) - 9999;
            sid = id(i,:);  j = 0;
            % ff = ['\\BA-37AEDE\Temporary\Wangjuwu\ghcn\ghcnd_all\ghcnd_all\' fdir(i).name];
            ff = ['\\BA-37AEDE\Temporary\Wangjuwu\ghcn\ghcnd_all\ghcnd_all\' sid '.dly'];
            if exist(ff, 'file')
                if mod(i-1, fix(n/1000)*100) == 0
                    disp(['Read ' num2str(i, '%05d') '(' datestr(now) '): ' ff]);
                end
                fp = fopen(ff, 'r');
                while ~feof(fp)
                    str = fgetl(fp);
                    if ~ischar(str)
                      break; 
                    else
                        j = j + 1;
                    end
                    sd = str( 1:11);
                    vr = str(18:21);
                    v = find(strcmp(var,vr));
                    if v > vmax, vmax = v; end
                    yr  = str2num(str(12:15));
                    mn = str2num(str(16:17));
                    days = datenum(yr,mn+1, 1)-datenum(yr,mn,1);
                    if yr >= 1980 && yr <= yr_now
                        for k = 1 : days
                            dy = datenum(yr, mn,k)-datenum(1980, 1, 1) + 1;
                            X(dy, 1) = datenum(yr, mn,k);
                            k1 = (k-1) * 8 + 22;
                            k2 = (k-1) * 8 + 26;
                            dt = str2double(str(k1:k2));
                            X(dy, v+1) = dt;
                        end  % for loop of k = 1 : dm
                    end
                end % while meet file end
                fclose(fp);
                X1 = X(X(:,1) > 0, :);
                Tmax = X1(X1(:,3) > - 9000,:);
                % plot(Tmax(:,1), Tmax(:,3), '-x');

                if ~ghcn.isKey(sid)
                    ghcn(sid) = X1;
                end    
                % if mod(n, 1e4) == 0
                %    disp(['Finished ' num2str(i*100/n, '%.2f') '% ( used ' toc ' sec.']);
                % end
            else
                disp(['No file: ' ff]);
            end % if file exist 
        end    %parfor loop FOR ALL STATION
        save 'E:\Global8km\ghcn\ghcn_map_1980-2016.mat' ghcn
    end        % if exist container then read it, or not read data frome each file.
    
    nx = length(ghcn);
    xid = keys(ghcn);
    disp(vmax);
    
    for v = 1 : vmax
       sub =['E:\Global8km\ghcn\' var{v}];
       if ~exist(sub,'dir')
           system(['mkdir ' sub]);
       end
       for yi = yr_begin : yr_now
           fc = [sub '\' var{v} '_' num2str(yi) '.txt'];
           fp = fopen(fc, 'w');            
           for i = 1 : nx
                dat = ghcn(xid{i});
                [nt mt] = size(dat);
                if mt >= v + 1
                    yr = year(dat(:,1));
                    xdt = dat(yr == yi,v + 1);
                    vdt = xdt(xdt > -9000);
                    nd = length(xdt);  nv = length(vdt);
                    if ~isempty(xdt) && nv / nd >= 0.8
                        fprintf(fp, '%s\t%f\t%f\t%f', xid{i}, lat(i), lon(i), elv(i));
                        for j = 1 : length(xdt)
                           fprintf(fp, '\t%f', xdt(j));
                        end
                        fprintf(fp, '\n');
                    end
                end
           end
           fclose(fp);
       end   % nn > 0 && ~isempty(yr)
    end   % variables
%     if matlabpool('size') > 0  % determine whether par started
%         matlabpool close;
%     end
    disp(['Number of data file: ' num2str(n)]);
else
    break;
end % if number is less than 1
% csvwrite('yr_STA.csv', XYR);
datestr(now)


