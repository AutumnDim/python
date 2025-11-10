function Find_Stations(v, wks_in, wks_out, yr1, yr2,fsid)
% clear all; close all; clc;
% vname = {'PRCP'; 'TMIN'; 'TMAX'; 'TAVG'; 'RHU'; 'SSD';  'WIN'};
% v = 1;
% wks_in  = 'F:\MeteoGrid\MeteoDbase\';
% wks_out = 'D:\Xizang\Huanghe\MeteoSta';
% yr1 = 1980;yr2 = 2020;
% % fsid = 'E:\MeteoGrid\CIMISS_table\Qinghai_Stations.txt';
% fsid = 'D:\Xizang\Huanghe\Meteo_Stations.xlsx';
fs = 'F:\MeteoGrid\Station\station2410_forWANGJB.xls';
s24 = xlsread(fs);

vname = {'PRCP'; 'TMIN'; 'TMAX'; 'TMEAN'; 'RHU'; 'SSD';  'WIN'};

if exist(fsid,'file')
    % station_name:sname, station_id:sid, station_number: nsd
    % [sname, sid] = textread(fsid, '%s%d');
    [dat, txt, raw] = xlsread(fsid);
    sname = txt(2:160, 3);
    ss_name = txt(2:160, 2);
    sid = dat(:, 4);
    
    nsd = length(sid);
    
    t1 = now();
    k = 1; XF = []; X = [];
    for yr = yr1: yr2
        tic
        days = datenum(yr+1,1,1)-datenum(yr,1,1);
        ff = [wks_in vname{v} '\' vname{v} '_' num2str(yr) '_Filled.csv'];
        if ~exist(ff, 'file')
            continue;
        end
        if strfind(ff, 'Filled') > 0
            headerline = 1;
            [id, xd, n1] = readFilledbase(ff,days+3, headerline);
        else
            [id, xd, n1] = readDbase(ff,days+3);%
        end
        gid = char(id);
        geo = xd(:,2:4);
        xdat = xd(:, 5:end);
        %         % Fill missing data if the missing data less than 20%
        %         [filled_data qc sta,nf] = fillmissing(xdat, gid,geo);
        %
        ID = str2num(gid(:,4:end));
        x0 = [];
        for i = 1 : nsd
            j = find(ID==sid(i), 1);
            if ~isempty(j)
                x0(:,i) = xd(j,5:end)';
            else
                x0(:,i) = -9999*ones([days 1]);
            end
        end
        
        X = [X; yr * ones([days 1]) (1:days)' x0];
        %         xd(xd < -900 | xd > 30000) = 32766;
        
        x1 = [];
        for i = 1 : nsd
            j = find(ID==sid(i), 1);
            if ~isempty(j)
                x1(:,i) = xd(j,5:end)';
            else
                x1(:,i) = -9999*ones([days 1]);
            end
        end
        XF = [XF; yr * ones([days 1]) (1:days)' x1];
    end
    if ~isempty(X)
        n1 = strfind(fsid,'\');
        n2 =strfind(fsid,'.');
        site = fsid(n1(end)+1:n2(1)-1);
        fout = [wks_out '\' site '_' vname{v} '_' num2str(yr1) '-' num2str(yr2) '.xls'];
        xlswrite(fout, {'YEAR','DOY'}, 'Raw_data', 'A1');
        xlswrite(fout, sname', 'Raw_data', 'C1');
        xlswrite(fout,X,'Raw_data','A2');
    end
    if ~isempty(XF)
        xlswrite(fout, {'YEAR','DOY'}, 'Filled_data', 'A1');
        xlswrite(fout, sname', 'Filled_data', 'C1');
        xlswrite(fout,XF,'Filled_data','A2');
    end
    % Calculate the data number in each year for each station
    if ~isempty(X)
        nsta = [];
        for yr = yr1 : yr2
            x0 = X(X(:,1) == yr,3:end);
            x1 = x0;
            x1(x0 > -900 & x0 < 30000) = 1;
            x1(x0 <= -900 | x0 >= 30000) = 0;
            nsta(yr-yr1+1,:) = [yr sum(x1)];
        end
        xlswrite(fout, {'YEAR','DOY'}, 'Num_vad', 'A1');
        xlswrite(fout, sname', 'Num_vad', 'C1');
        xlswrite(fout,nsta,'Num_vad','A2');
        % Calculate the mean and std of filled data in a year for each station
        mn = []; st = [];
        for yr = yr1 : yr2
            x0 = XF(X(:,1) == yr,3:end);
            x1 = x0;
            if strcmp('PRCP', vname{v})
                mn(yr-yr1+1,:) = [yr sum(x1)];
            else
                mn(yr-yr1+1,:) = [yr mean(x1)];
            end
            st(yr-yr1+1,:) = [yr std(x1)];
        end
        xlswrite(fout, {'YEAR','DOY'}, 'Annual_data', 'A1');
        xlswrite(fout, sname', 'Annual_data', 'C1');
        xlswrite(fout,mn,'Annual_data','A2');
        
        xlswrite(fout, {'YEAR','DOY'}, 'Annual_std', 'A1');
        xlswrite(fout, sname', 'Annual_std', 'C1');
        xlswrite(fout,st,'Annual_std','A2');
        disp(['Find ' vname{v} ' observed on stations for ' site ' on ' datestr(now)]);
    end
else
    disp(['Error: cannot find stations list; ' fsid]);
    return
end