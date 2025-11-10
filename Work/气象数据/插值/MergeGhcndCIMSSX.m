function MergeGhcndCIMSSX(yr1, yr2, wks_ghcnd, wks_cimiss, wks_meteobase, v)
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
vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
% yr1 = 2015;yr2 = 2015;
% wks_ghcnd = 'E:\Global8km\ghcn';
% wks_cimiss= 'E:\MeteoGrid\CIMISS_table';
tic

% for v = 4:4
sub  = [wks_meteobase '\' vname{v}];
if ~exist(sub,'dir')
    system(['mkdir ' sub]);
end
disp('Vname    Year    GHCN     CIMISS    Total   (Process time)');
for y = yr1:yr2
    days = datenum(y+1,1,1)-datenum(y,1,1);
    days_ghcn = days;
    days_cimiss = days;
    % READ GHCN
    ff = [wks_ghcnd '\' vname{v} '\' vname{v} '_' num2str(y) '.txt'];
    if exist(ff, 'file')
        % disp(ff);
        [id xd n1] = readghcn(ff,days_ghcn+3);
        nsd = id;
        xsd = xd;
    else
        nsd = []; xsd = []; n1 = 0;
    end
    [n, m] = size(xsd);
    if days_ghcn < days
        xsd = [xsd, -9999*ones([n, days - m+3])];
    end
    % READ CIMISS
    ff = [wks_cimiss '\' vname{v} '_' num2str(y) '.txt'];
    if exist(ff, 'file')
        % disp(ff);
        % xx = dlmread(ff, '\t', 1, 0);
        i = 1;
        xid = [];
        xdt = [];
        fip = fopen(ff, 'r');
        s0 = fgetl(fip);
        while fip > 0 && ~feof(fip)
            s0 = fgetl(fip);
            if length(s0) > 0
                s1 = textscan(s0,'%s','Delimiter','\t');
                s2 = s1{1,1};
                gstr = s2{1};
                dx = str2double(s2(2:end));
                if length(dx) == days_cimiss+3 && gstr(1) == '5'
                    xid(i,:) = gstr;
                    xdt(i,:) = dx';
                    i = i + 1;
                end
            end
        end
        fclose(fip);
        [n2 m] = size(xdt);
        ncd = xid;
        if strcmp(vname{v}, 'RHU')
            xcd = xdt;   % No scale for RHU
        else
            xcd = [xdt(:,1:3) xdt(:,4:m) * 10];  % scaled 10 times
        end
        xcd(xcd < -9000 | xcd > 9000) = -9999;
    else
        ncd = [];   xcd = [];   n2 = 0;
    end
    for i = 1 : n2
        j = n1 + i;
        nsd(j,:) = ['CH0000' char(ncd(i,:))];
        xsd(j,:) = xcd(i,:);%\scale
        % disp([var2 ' ' num2str(i) '. ' nsd(i,:) num2str(xcd(i,1:5)) '; ' num2str(xsd(j,1:5))]);
    end
    
    if n1 + n2 > 0
        ff = [sub '\' vname{v} '_' num2str(y) '.txt'];
        fp = fopen(ff, 'w');
        nt = 0;
        for i = 1 : n2 + n1
            if abs(xsd(i,1)) <= 90 && abs(xsd(i,2)) <= 180 && abs(xsd(i,3)) <= 9000
                fprintf(fp,'%s\t%f\t%f\t%f', nsd(i,:), xsd(i,1:3));
                for j = 1 : days
                    fprintf(fp,'\t%d',round(xsd(i,j+3)));
                end
                fprintf(fp, '\n');
                nt = nt + 1;
            end
        end
        fclose(fp);
    end
    disp([vname{v} ' ' num2str([y n1 n2 nt])  ' (' datestr(now) ')']);
end
figure;
lat = xsd(:,1); lon = xsd(:,2); elv = xsd(:,3);
plot(lon, lat, '.');
title(vname{v});
% end
toc
disp('Go home now!');

