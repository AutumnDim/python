% function Station_VPD(yr1, yr2)
% TAVG = (TMAX + TMIN) / 2
% Data from China Meteorological Information Sharing System (CIMISS£©
%      TMAX = Maximum temperature (degrees C)
%      TMIN = Minimum temperature (degrees C)
%      RHU  = Ralative humidy (%)
% Output the average value of the above two data
%      VPD = Vapor Pressure Deficit (kPa)
% 	satvp = 0.6108 * exp ( 17.27 * t / ( t + 237.3 ) );			/* kPa */
% 	vpd = satvp * ( 1 - rh );
%_________________By:jbwang@igsnrr.ac.cn,On Sep.05, 2022___________________
%_________________By:jbwang@igsnrr.ac.cn,On Dec.30, 2016___________________

clear all
close all
clc
vname = {'PRCP'; 'TMIN'; 'TMAX'; 'TAVG'; 'RHU'; 'SSD';  'WIN'; 'VPD'};
yr1 = 1951;yr2 = 2020;
% wks_ghcnd = 'E:\Global8km\ghcn';
% wks_cimiss= 'E:\MeteoGrid\CIMISS_table';
wks_dbase = '/Users/jbwang/Data/MeteoGrid/MeteoDbase_yuanbin0905';
owk = '/Users/jbwang/Data/MeteoGrid/MeteoDbase_4regions';
if ~exist(owk, 'dir')
    mkdir(owk);
end
tic


fshp = '/Users/jbwang/Data/China1km/Parameters/Climate4region/CClimate4Regions_4R.shp';
reg = shaperead(fshp);

disp('Read meteodbase to calculate regional mean...');
disp('')
disp('By jbwang@igsnrr.ac.cn');
disp('')
disp('On Sep 7, 2022, the final day of a isolated week')
disp('')
disp('due to Coronavirus disease (COVID-19) case found at IGSNRR, CAS');
disp('')

v = 8;
sub  = [wks_dbase, filesep, vname{v}];
if ~exist(sub,'dir')
    system(['mkdir ' sub]);
end
headerline = 1;
vpd_reg = []; tmin_reg = []; tmax_reg = [];rhu_reg = [];
prc_reg = []; ssd_reg = [];  N_sta = [];
for y = yr1:yr2
    tic
    yk = y - yr1 + 1;
    days = datenum(y+1,1,1)-datenum(y,1,1);
    if y < 2019
        dat_scale = 0.1;
    else
        dat_scale = 1.0;
    end
    % READ CIMISS
    v = 2;
    ff = [wks_dbase, filesep, vname{v}, filesep, vname{v} '_' num2str(y) '_Filled.csv'];
        % disp(ff);
        % xx1 = load(ff);
        [id_db, xd_db, ~] = readFilledbase(ff,days+3, headerline);
        id1 = id_db;
        TMIN = xd_db(:,5:end) * dat_scale;
        tmin_db = xd_db(:, 2:4);
        n1 = size(TMIN, 2);
    v = 3;
    ff = [wks_dbase, filesep, vname{v}, filesep, vname{v} '_' num2str(y) '_Filled.csv'];
        % disp(ff);
        [id_db, xd_db, ~] = readFilledbase(ff,days+3, headerline);
        id2 = id_db;
        TMAX = xd_db(:, 5:end) * dat_scale;
        tmax_db = xd_db(:, 2:4);
        n2 = size(TMAX, 2);
    v = 5;
    ff = [wks_dbase, filesep, vname{v}, filesep, vname{v} '_' num2str(y) '_Filled.csv'];
        % disp(ff);
        [id_db, xd_db, ~] = readFilledbase(ff,days+3, headerline);
        id3 = id_db;
        RHU = xd_db(:, 5:end) * 0.01;
        rhu_db = xd_db(:, 2:4);
        n3 = size(RHU, 2);
    v = 1;
    ff = [wks_dbase, filesep, vname{v}, filesep, vname{v} '_' num2str(y) '_Filled.csv'];
        % disp(ff);
        [id_db, xd_db, ~] = readFilledbase(ff,days+3, headerline);
        id4 = id_db;
        PRC = xd_db(:, 5:end) * dat_scale;
        prc_db = xd_db(:, 2:4);
        n4 = size(PRC, 2);
    v = 6;
    ff = [wks_dbase, filesep, vname{v}, filesep, vname{v} '_' num2str(y) '_Filled.csv'];
        % disp(ff);
        [id_db, xd_db, ~] = readFilledbase(ff,days+3, headerline);
        id5 = id_db;
        SSD = xd_db(:, 5:end) * dat_scale;
        ssd_db = xd_db(:, 2:4);
        n4 = size(SSD, 2);
    if n1 == n2 && n2 == n3
        sid1 = cellstr(char(id1));
        sid2 = cellstr(char(id2));
        sid3 = cellstr(char(id3));
        
        sid = cellstr(char(unique(char([(id1); (id2); (id3)]), 'rows')));
        n_sid = length(sid);
        
        lat = []; lon = []; elv = [];
                
        v = 8;
        fvpd_out = [wks_dbase, filesep, vname{v}, filesep, vname{v} '_' num2str(y) '_Filled.csv'];
        fop_vpd = fopen(fvpd_out, 'w');
        fprintf(fop_vpd, 'SID,Year,Lat,Lon,Elv');
        for j = 1 : days
            fprintf(fop_vpd,',%03d', j);
        end
        
        v = 4;
        ftavg_out = [wks_dbase, filesep, vname{v}, filesep, vname{v} '_' num2str(y) '_Filled.csv'];
        fop_tavg = fopen(ftavg_out, 'w');
        fprintf(fop_tavg, 'SID,Year,Lat,Lon,Elv');
        for j = 1 : days
            fprintf(fop_tavg,',%03d', j);
        end
        
        k = 1;
        VPD = []; TAVG = [];
        for i = 1 : n_sid
            j1 = find(strcmp(sid1, sid{i}) > 0);
            j2 = find(strcmp(sid2, sid{i}) > 0);
            j3 = find(strcmp(sid3, sid{i}) > 0);
                        
            if isempty(j1) || isempty(j2) || isempty(j3)
                % disp([k,j1,j2,j3])
                continue;
            end
            % disp([num2str(i), ', ', sid{i}, ', ', sid1{j1}, ', ', sid2{j2}, ', ', sid3{j3}]);

            lat(k,1) = tmax_db(j2,1);
            lon(k,1) = tmax_db(j2,2);
            elv(k,1) = tmax_db(j2,3);
                        
            tmin = TMIN(j1, :);
            tmax = TMAX(j2, :);
            rhu  = RHU(j3, :);
            tavg = (tmin + tmax) * 0.5;
            TAVG(k,:) = tavg;
            
            satvp_avg = 0.6108 * exp ( 17.27 * tavg ./ ( tavg + 237.3 ) );			%/* kPa */
            satvp_max = 0.6108 * exp ( 17.27 * tmax ./ ( tmax + 237.3 ) );			%/* kPa */
            satvp_min = 0.6108 * exp ( 17.27 * tmin ./ ( tmin + 237.3 ) );			%/* kPa */
            satvp_mean = (satvp_max + satvp_min) * 0.5;
            
            vpd_mean = satvp_mean .* ( 1 - rhu );           %/* kPa */
            vpd_avg = satvp_avg .* ( 1 - rhu );
            
            % jday = 1 : days;
            % subplot(2, 2, 1);
            % plot(jday, satvp_avg, 'r-', jday, satvp_mean, 'b-'); legend('satvp_{avg}', 'satvp_{mean}');
            % plotyy(jday, rhu, jday, satvp_mean); legend('RHU', 'satvp_{mean}');
            % plot(vpd_mean, vpd_avg, '.', 'MarkerSize', 13);
            
            fprintf(fop_vpd, '\n%s,%d,%f,%f,%f', sid{i}, y, lat(k),lon(k),elv(k));
            for j = 1 : days
                fprintf(fop_vpd,',%f', vpd_mean(j));
            end
            VPD(k,:) = vpd_mean;
            
            fprintf(fop_tavg, '\n%s,%d,%f,%f,%f', sid{i}, y, lat(k),lon(k),elv(k));
            for j = 1 : days
                fprintf(fop_tavg,',%f', tavg(j));
            end
            
            k = k + 1;
        end
        fclose(fop_vpd);
        fclose(fop_tavg);
        
        vpd_db = [lat, lon, elv];
        % plot(lon, lat, '.');
        
        vpd_annual = mean(VPD, 2);
        tmin_annual = mean(TMIN, 2);
        tmax_annual = mean(TMAX, 2);
        rhu_annual = mean(RHU, 2);
        prc_annual = sum(PRC, 2);
        ssd_annual = mean(SSD, 2);
        % pnt_color = 'rgbc';
        for j = 1 : 4
            s = inpolygon(vpd_db(:,2), vpd_db(:,1), reg(j).X, reg(j).Y);
            p1 = vpd_db(s>0,:);
            N_sta(yk,j) = length(p1);
            vpd_reg(yk,j) = mean(vpd_annual(s>0,:));
            
            s = inpolygon(tmin_db(:,2), tmin_db(:,1), reg(j).X, reg(j).Y);
            tmin_reg(yk,j) = mean(tmin_annual(s>0,:));
            
            s = inpolygon(tmax_db(:,2), tmax_db(:,1), reg(j).X, reg(j).Y);
            tmax_reg(yk,j) = mean(tmax_annual(s>0,:));
            
            s = inpolygon(rhu_db(:,2), rhu_db(:,1), reg(j).X, reg(j).Y);
            rhu_reg(yk,j) = mean(rhu_annual(s>0,:));

            s = inpolygon(prc_db(:,2), prc_db(:,1), reg(j).X, reg(j).Y);
            prc_reg(yk,j) = mean(prc_annual(s>0,:));
            
            s = inpolygon(ssd_db(:,2), ssd_db(:,1), reg(j).X, reg(j).Y);
            ssd_reg(yk,j) = mean(ssd_annual(s>0,:));
            % plot(p1(:,2), p1(:,1), [pnt_color(j),'o']);
            % hold on;
        end
        vpd_reg(yk,5) = mean(vpd_annual);
        tmin_reg(yk,5) = mean(tmin_annual);
        tmax_reg(yk,5) = mean(tmax_annual);
        rhu_reg(yk,5) = mean(rhu_annual);
        prc_reg(yk,5) = mean(prc_annual);
        ssd_reg(yk,5) = mean(ssd_annual);
        N_sta(yk, 5) = length(vpd_annual);
        % hold off;
        X = [y, tmin_reg(yk,5), tmax_reg(yk,5), rhu_reg(yk,5), prc_reg(yk,5), ssd_reg(yk,5), vpd_reg(yk,5)];
        disp(num2str(X));
    else
        disp('Two data are not matched!');
    end
    disp(num2str([y, k - 1, toc]))
end
fcsv = [owk, filesep, 'VPD_', num2str(yr1), '-', num2str(yr2), '.csv'];
csvwrite(fcsv, [(yr1:yr2)', vpd_reg]);

fcsv = [owk, filesep, 'TMIN_', num2str(yr1), '-', num2str(yr2), '.csv'];
csvwrite(fcsv, [(yr1:yr2)', tmin_reg]);

fcsv = [owk, filesep, 'TMAX_', num2str(yr1), '-', num2str(yr2), '.csv'];
csvwrite(fcsv, [(yr1:yr2)', tmax_reg]);

fcsv = [owk, filesep, 'RHU_', num2str(yr1), '-', num2str(yr2), '.csv'];
csvwrite(fcsv, [(yr1:yr2)', rhu_reg]);


fcsv = [owk, filesep, 'PRC_', num2str(yr1), '-', num2str(yr2), '.csv'];
csvwrite(fcsv, [(yr1:yr2)', prc_reg]);


fcsv = [owk, filesep, 'SSD_', num2str(yr1), '-', num2str(yr2), '.csv'];
csvwrite(fcsv, [(yr1:yr2)', ssd_reg]);

fcsv = [owk, filesep, 'Num_Station_', num2str(yr1), '-', num2str(yr2), '.csv'];
csvwrite(fcsv, [(yr1:yr2)', N_sta]);


tavg = -50:0.1:50;
r = 0:0.01:1;
[T, R] = grid(tavg, r);

VPD = [];
for i = 1 : length(tavg)
    t = tavg(i);
    for j = 1 : length(r)
        rh = r(j);
        satvp = 0.6108 * exp ( 17.27 * t / ( t + 237.3 ) );			% /* kPa */
        vpd = satvp * ( 1 - rh );
        VPD(i,j) = vpd;
    end
end
bnd = quantile(VPD(:), [0.05, 0.95]);
imagesc(r, tavg, VPD, bnd);
xlabel('RHU');
ylabel('Tavg');
colorbar horz
colormap([white(1);parula(254)]);
set(gca, 'Fontsize', 16)

