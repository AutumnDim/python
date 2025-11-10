function TAVG(yr1, yr2)
% TAVG = (TMAX + TMIN) / 2
% Data from China Meteorological Information Sharing System (CIMISS£©
%      TMAX = Maximum temperature (degrees C)
%      TMIN = Minimum temperature (degrees C)
% Output the average value of the above two data
%      TAVG = Average temperature (degrees C)
%_________________By:jbwang@igsnrr.ac.cn,On Dec.30, 2016___________________
% clear all
% close all
% clc
vname = {'PRCP'; 'TMIN'; 'TMAX'; 'TAVG'; 'RHU'; 'SSD';  'WIN'};
% yr1 = 2013;yr2 = 2014;
% wks_ghcnd = 'E:\Global8km\ghcn';
wks_cimiss= 'E:\MeteoGrid\CIMISS_table';
tic

v = 4;
sub  = ['E:\MeteoGrid\CIMISS_table\' vname{v}];
if ~exist(sub,'dir')
    system(['mkdir ' sub]);
end

for y = yr1:yr2
    days = datenum(y+1,1,1)-datenum(y,1,1);
    % READ CIMISS
    v = 2;
    ff = [wks_cimiss '\' vname{v} '\' vname{v} '_' num2str(y) '.txt'];
        disp(ff);
        xx1 = load(ff);
        [n1, m1] = size(xx1);
        id1 = xx1(:,1);
        tmin = xx1(:,5:end);
    v = 3;
    ff = [wks_cimiss '\' vname{v} '\' vname{v} '_' num2str(y) '.txt'];
        disp(ff);
        xx2 = load(ff);
        [n2, m2] = size(xx2);
        id2 = xx2(:,1);
        tmax = xx2(:, 5:end);
    if m1 == m2    
        if n1 == n2 && sum(id1 - id2) <= 0.1
            disp('Two IDs are matched!');
            tavg = (tmin + tmax) / 2;
            tavg(tavg > 1000 | tavg < -900) = -9999;
            xc = [xx1(:,1:4) tavg];
            n0 = n1;
        else
            disp('Two IDs are not matched!');
            j = 1; sid = []; tavg = [];
            for i = 1 : n1
                x1 = tmin(i,:);
                x2 = tmax(id2 == id1(i),:);
                if ~isempty(x2)
                    sid(j,:)  = xx1(i, 1:4);
                    tavg(j,:) = (x1 + x2) / 2;
                    j = j + 1;
                end
            end
            n0 = j - 1;
            xc = [sid tavg];    
        end
        v = 4;
        ff = [wks_cimiss '\' vname{v} '\' vname{v} '_' num2str(y) '.txt'];
        dlmwrite(ff, xc, 'delimiter','\t');    
        disp(num2str([y n1 n2 n0 mean(tmin(tmin < 1000 & tmin > -9000)) mean(tmax(tmax < 1000 & tmax > -9000)) mean(tavg(tavg < 1000 & tavg > -9000))]));
    else
        disp('Two data are not matched!');
    end
end
