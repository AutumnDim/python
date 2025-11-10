% % function Sites2Grid(wks, fset,v, nots, time_step)
% 
% %_________________By:jbwang@igsnrr.ac.cn,On Dec.30, 2016___________________
% clear all
% close all
% clc
% vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN';'PRCP'};
% vad_value = [-90 90; 0 300; -90 90; -90 90; 0 100; 0 24; 0 50; 0 300]*10;
% fset = "D:\QX\Code\functionset\China1km_Rfactor.set";
% if exist(fset, 'file')
%     [sname, svalue] = textread(fset, '%s%s');
%     yr1 = str2double(svalue{1});yr2 = str2double(svalue{2});
%     wks_in  = svalue{3};
%     wks_out = svalue{4};     % Database with Anusplin formation
%     wks_tmp = svalue{5};    % Temporary fold for cmd files
%     wks_grd = svalue{6};          % Database for interpolated grid
% 
%     fdem = svalue{7};
%     fhdr = svalue{8};
%     ftif = svalue{9};
% else
%     disp('Error: Not find site information file');
%     return;
% end
% proj = geotiffinfo(ftif);
% [dem, R, cc] = geotiffread(ftif);
% [nlines, npixels] = size(dem);
% 
% xs = cc(1,1)+500:R(2,1):cc(2,1)-500;
% ys = cc(2,2)-500:-R(2,1):cc(1,2)+500;
% [XX, YY] = meshgrid(xs, ys);
% imagesc(xs, ys, dem, [0, 5000]);
% hold on;
% set(gca, 'Ydir', 'normal');
% 
% v = 2;
% yr_bat = [yr1 yr2];
% direct = {{wks_out;wks_tmp;wks_grd};...
%     {[pwd '/' wks_tmp(4:end)];[pwd '/' wks_tmp(4:end)];[pwd '/' wks_grd(4:end)]}};% direct{1,1} is for Windows OS and direct{2,1} for Unix OS.
% disp(datestr(now));
% 
% % disp(['Processing ' vname{v}, ' in ', num2str(yr), ' begining at ' datestr(now)]);
% disp('Vname Year   day  Valid_Stn_Num  All_Stn_Num Used_time(sec.)');
% tic;
% out_name = 'R_factor';
% out_wks = 'K:\AsiaMeteo\RainfallFactor\R_factor_tpaps';
% fxls_out = [out_wks, '\Rfactor.xls'];
% 
% sub  = [wks_tmp '\' out_name];
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
% end
% if strcmp(vname{v},'PRCP')
%     mean_or_sum = 0;
% else
%     mean_or_sum = 1;
% end
% % cd('F:\MeteoGrid\Function_set');
% % [status, results] = system(['copy splina.exe ' wks_tmp '\' out_name '\']);
% % [status, results] = system(['copy splinb.exe ' wks_tmp '\' out_name '\']);
% % [status, results] = system(['copy selnot.exe ' wks_tmp '\' out_name '\']);
% % [status, results] = system(['copy lapgrd.exe ' wks_tmp '\' out_name '\']);
% % [status, results] = system(['copy ' fdem ' ' wks_tmp '\' out_name '\']);
% % toc
% sub  = [wks_grd out_name];
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
% end
% 
% sub  = [wks_out '\' out_name];
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
% end
% 
% sub  = [wks_in, 'MeteoFilled\R_factor'];
% if ~exist(sub,'dir')
%     mkdir(sub);
% end
% mean_or_sum = 0; % sum
% 
% hdr = {'sid', 'lon', 'lat', 'elv', 'R_week'};
% for i = 1 : 46
%     hdr{1, i + 5} = ['D', num2str((i - 1) * 8 + 1, '%03d')];
% end
% 
% %% observed soil erosion data were used to calibrate the model
% fxls = "E:\Fpar\土壤侵蚀_三江源.xlsx";
% [s1, s2] = xlsfinfo(fxls);
% [sid_dat, sid_txt, sid_raw] = xlsread(fxls, 'Site_Obs');
% [ns, ms] = size(sid_dat);
% [sid_x, sid_y] = projfwd(proj, sid_dat(:, 5), sid_dat(:, 4));
% % sid_R = [];
% tic;
% for yr = yr2:-1:yr1
%     [~, dy_monthly, ~] = daily2timestep(yr, 30);
%     [~, dy24, ~] = daily2timestep(yr, 15);
%     [days, dy46, ~] = daily2timestep(yr, 8);
% 
%     % READ GHCN-CIMISS
%     file_filled = [wks_in, '\MeteoFilled\', vname{v}, '\', vname{v}, '_' num2str(yr) '_Filled.csv'];
% 
%     disp(file_filled);
% 
%     % file_filled = 'C:\OneDrive\cprogram\Data\PRCP_2010_Filled.csv';
%     if exist(file_filled, 'file')
%         headerline = 1;
%         [gid, xd, n1] = readFilledbase(file_filled,days+3, headerline);
%         sid = {};
%         for i = 1 : length(gid)
%             sid{i, 1} = char(gid(i,:));
%         end
%         lat = xd(:,2); lon = xd(:,3); elv = xd(:,4);
% 
%         [x, y] = projfwd(proj, lat, lon);
%         % plot(x, y, 'r.');
% 
%         % Daily mean
%         filled_data = xd(:,5:end) * 0.1;
% 
%         % Annually sum
%         atp = sum(filled_data,2);     % sum of prcp in whole year
%         filled_data(filled_data < 12) = NaN;
%         py12 = mean(filled_data,2, 'omitnan') ;   % sum of prcp less than 12 mm
% 
%         % Bi-weekly sum
%         dy = unique(dy24);
%         [nd, ~] = size(filled_data);
%         md = length(dy);
%         pd_24 = zeros(nd, md);
%         for i = 1 : md
%             x1 = filled_data(:, dy24 == dy(i));
% 
%             pd12 = mean(x1, 2, 'omitnan');
% 
%             beta = 0.8363 + 18.144 ./ pd12 + 24.455 ./ py12;
%             alpha = 21.586 * beta.^(-7.1891);
% 
%             x1(isnan(x1)) = 0;
%             [n,m] = size(x1);
%             Md = [];
%             for j = 1 : m
%                 Md(:,j) = alpha .* x1(:, j).^beta;
%             end
%             Mn = sum(Md, 2, 'omitnan');
%             pd_24(:, i) = Mn;
%         end
%         R24 = sum(pd_24, 2, 'omitnan');
%         % x1 = x(~isnan(R24));
%         % y1 = y(~isnan(R24));
%         % z1 = elv(~isnan(R24));
%         % R1 = R24(~isnan(R24));
%         % xy = [x1'; y1'];
%         % st = tpaps(xy, R1');
%         % R = [];
%         % for i = 1 : nl
%         %     R(i,:) = fnval(st, [XX(i,:); YY(i,:)]);
%         % end
%         % imagesc(xs, ys, R)
% 
%         % Monthly R factor
%         dy = unique(dy_monthly);
%         md = length(dy);
%         pd_month = zeros(nd, md);
%         for i = 1 : md
%             x1 = filled_data(:, dy_monthly == dy(i));
% 
%             pd12 = mean(x1, 2, 'omitnan');
% 
%             beta = 0.8363 + 18.144 ./ pd12 + 24.455 ./ py12;
%             alpha = 21.586 * beta.^(-7.1891);
% 
%             x1(isnan(x1)) = 0;
%             [n,m] = size(x1);
%             Md = [];
%             for j = 1 : m
%                 Md(:,j) = alpha .* x1(:, j).^beta;
%             end
%             Mn = sum(Md, 2, 'omitnan');
%             pd_month(:, i) = Mn;
%         end
%         R_month = sum(pd_month, 2, 'omitnan');
% 
%         % Weekly R factor
%         dy = unique(dy46);
%         md = length(dy);
%         pd_week = zeros(nd, md);
%         sid_R = [];
%         for i = 1 : md
%             x1 = filled_data(:, dy46 == dy(i));
%             pd12 = mean(x1, 2, 'omitnan');
% 
%             beta = 0.8363 + 18.144 ./ pd12 + 24.455 ./ py12;
%             alpha = 21.586 * beta.^(-7.1891);
% 
%             x1(isnan(x1)) = 0;
%             [n,m] = size(x1);
%             Md = [];
%             for j = 1 : m
%                 Md(:,j) = alpha .* x1(:, j).^beta;
%             end
%             R_week = sum(Md, 2, 'omitnan');
%             pd_week(:, i) = R_week;
% 
% %             x1 = x(~isnan(R_week));
% %             y1 = y(~isnan(R_week));
% %             z1 = elv(~isnan(R24));
% %             R1 = R_week(~isnan(R_week));
% %             xy = [x1'; y1'];
% %             st = tpaps(xy, R1');
% %             sid_rr = [i, yr, (i-1)*8+1, fnval(st, [sid_x'; sid_y'])];
% %             
% %             sid_R(i, :) = sid_rr;
%             % R_img = [];
%             % parfor Line = 1 : nlines
%             %     R_img(Line,:) = fnval(st, [XX(Line,:); YY(Line,:)]);
%             % end
%             %
%             % R_img(dem < -9000) = -9999;
%             % bnd = quantile(R_img(R_img >= 0), [0.05, 0.95]);
%             % imagesc(xs, ys, R_img, bnd);
%             % colormap([white(1); parula(254)]);
%             %
%             % ftif_out = [out_wks, '\Rfactor_Asia1km_', num2str(yr * 1000 + i), '.tif'];
%             % geotiffwrite2(ftif_out,single(R_img), R, 'GeoKeyDirectoryTag', proj.GeoTIFFTags.GeoKeyDirectoryTag);
%         end
%         % Fill missing data if the missing data less than 20%
%         ftxt = [wks_in, '\MeteoFilled\R_factor\R_factor_' num2str(yr) '.csv'];
%         headerline = {'Year'; 'LATI'; 'LONG'; 'Elva'};
%         for i = 1 : md
%             headerline{i+4,1} = ['D' num2str(i, '%03d')];
%         end
% 
%         fop = fopen(ftxt, 'w');
%         for i = 1 : md + 4
%             fprintf(fop, '%s,', headerline{i}');
%         end
% 
%         for i = 1 : n
%             fprintf(fop, '\n%s, %d,%f,%f,%f', char(gid(i,:)), yr, lat(i),lon(i),elv(i));
%             for j = 1 : md
%                 fprintf(fop, ',%.3f', pd_week(i,j));
%             end
%         end
%         fclose(fop);
% 
%         % R_week = sum(pd_week, 2, 'omitnan');
%         % xlswrite(fxls_out, [lon, lat, elv, R_week, pd_week], num2str(yr), 'B2');
%         % xlswrite(fxls_out, sid, num2str(yr), 'A2');
%         % xlswrite(fxls_out, hdr, num2str(yr), 'A1');
% 
%         % figure; plot(R24, R_week, 'b.', R24, R_month, 'r.');
%         % figure; hist([R24, R_week, R_month]);
% 
%         % p = anova1([R24, R_week, R_month]);
%         % c=multcompare(s)
%         % write to file with the formation of Anusplin
%         geo = [x, y, elv];
% 
%         csv2Anuspl(yr, out_name, wks_out, char(gid), geo, pd_week);
% 
%         makesplinotbat(yr, direct, size(pd_week), out_name, fdem, fhdr);
% 
%         disp([vname{v}, ' ', num2str([yr n,j-1])  ' ' num2str(toc)]);
%     end
% end
% % hdr = {'No.', 'Year', 'Doy'};
% % for i = 1 : length(sid_x)
% %     hdr{1, i + 3} = sid_txt{i+1, 7};
% % end
% % xlswrite(fxls_out, hdr, 'Qinghai', 'A1');
% % xlswrite(fxls_out, sid_R, 'Qinghai', 'A2');
% 
% 
% 
% 
% 











% function Sites2Grid(wks, fset,v, nots, time_step)

%_________________By:jbwang@igsnrr.ac.cn,On Dec.30, 2016___________________
clear all
close all
clc
vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN';'PRCP'};
vad_value = [-90 90; 0 300; -90 90; -90 90; 0 100; 0 24; 0 50; 0 300]*10;
fset = "D:\QX\Code\functionset\China1km_Rfactor.set";
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
[dem, R, cc] = geotiffread(ftif);
[nlines, npixels] = size(dem);

xs = cc(1,1)+500:R(2,1):cc(2,1)-500;
ys = cc(2,2)-500:-R(2,1):cc(1,2)+500;
[XX, YY] = meshgrid(xs, ys);
imagesc(xs, ys, dem, [0, 5000]);
hold on;
set(gca, 'Ydir', 'normal');

v = 2;
yr_bat = [yr1 yr2];
direct = {{wks_out;wks_tmp;wks_grd};...
    {[pwd '/' wks_tmp(4:end)];[pwd '/' wks_tmp(4:end)];[pwd '/' wks_grd(4:end)]}};% direct{1,1} is for Windows OS and direct{2,1} for Unix OS.
disp(datestr(now));

% disp(['Processing ' vname{v}, ' in ', num2str(yr), ' begining at ' datestr(now)]);
disp('Vname Year   day  Valid_Stn_Num  All_Stn_Num Used_time(sec.)');
tic;
out_name = 'R_factor';
out_wks = 'K:\AsiaMeteo\RainfallFactor\R_factor_tpaps';
fxls_out = [out_wks, '\Rfactor.xls'];

sub  = [wks_tmp '\' out_name];
if ~exist(sub,'dir')
    system(['mkdir ' sub]);
end
if strcmp(vname{v},'PRCP')
    mean_or_sum = 0;
else
    mean_or_sum = 1;
end
% cd('F:\MeteoGrid\Function_set');
% [status, results] = system(['copy splina.exe ' wks_tmp '\' out_name '\']);
% [status, results] = system(['copy splinb.exe ' wks_tmp '\' out_name '\']);
% [status, results] = system(['copy selnot.exe ' wks_tmp '\' out_name '\']);
% [status, results] = system(['copy lapgrd.exe ' wks_tmp '\' out_name '\']);
% [status, results] = system(['copy ' fdem ' ' wks_tmp '\' out_name '\']);
% toc
sub  = [wks_grd out_name];
if ~exist(sub,'dir')
    system(['mkdir ' sub]);
end

sub  = [wks_out '\' out_name];
if ~exist(sub,'dir')
    system(['mkdir ' sub]);
end

sub  = [wks_in, 'MeteoFilled\R_factor'];
if ~exist(sub,'dir')
    mkdir(sub);
end
mean_or_sum = 0; % sum

hdr = {'sid', 'lon', 'lat', 'elv', 'R_week'};
for i = 1 : 46
    hdr{1, i + 5} = ['D', num2str((i - 1) * 8 + 1, '%03d')];
end

%% observed soil erosion data were used to calibrate the model
fxls = "E:\Fpar\土壤侵蚀_三江源.xlsx";
[s1, s2] = xlsfinfo(fxls);
[sid_dat, sid_txt, sid_raw] = xlsread(fxls, 'Site_Obs');
[ns, ms] = size(sid_dat);
[sid_x, sid_y] = projfwd(proj, sid_dat(:, 5), sid_dat(:, 4));
% sid_R = [];
tic;
for yr = yr2:-1:yr1
    [~, dy_monthly, ~] = daily2timestep(yr, 30);
    [~, dy24, ~] = daily2timestep(yr, 15);
    [days, dy46, ~] = daily2timestep(yr, 8);

    % READ GHCN-CIMISS
    file_filled = [wks_in, '\MeteoFilled\', vname{v}, '\', vname{v}, '_' num2str(yr) '_Filled.csv'];

    disp(file_filled);

    % file_filled = 'C:\OneDrive\cprogram\Data\PRCP_2010_Filled.csv';
    if exist(file_filled, 'file')
        headerline = 1;
        [gid, xd, n1] = readFilledbase(file_filled,days+3, headerline);
        sid = {};
        for i = 1 : length(gid)
            sid{i, 1} = char(gid(i,:));
        end
        lat = xd(:,2); lon = xd(:,3); elv = xd(:,4);

        [x, y] = projfwd(proj, lat, lon);
        % plot(x, y, 'r.');

        % Daily mean
        filled_data = xd(:,5:end) * 1;

        % Annually sum
        atp = sum(filled_data,2);     % sum of prcp in whole year
        filled_data(filled_data < 12) = NaN;
        py12 = mean(filled_data,2, 'omitnan') ;   % sum of prcp less than 12 mm

        % Bi-weekly sum
        dy = unique(dy24);
        [nd, ~] = size(filled_data);
        md = length(dy);
        pd_24 = zeros(nd, md);
        for i = 1 : md
            x1 = filled_data(:, dy24 == dy(i));

            pd12 = mean(x1, 2, 'omitnan');

            beta = 0.8363 + 18.144 ./ pd12 + 24.455 ./ py12;
            alpha = 21.586 * beta.^(-7.1891);

            x1(isnan(x1)) = 0;
            [n,m] = size(x1);
            Md = [];
            for j = 1 : m
                Md(:,j) = alpha .* x1(:, j).^beta;
            end
            Mn = sum(Md, 2, 'omitnan');
            pd_24(:, i) = Mn;
        end
        R24 = sum(pd_24, 2, 'omitnan');
        % x1 = x(~isnan(R24));
        % y1 = y(~isnan(R24));
        % z1 = elv(~isnan(R24));
        % R1 = R24(~isnan(R24));
        % xy = [x1'; y1'];
        % st = tpaps(xy, R1');
        % R = [];
        % for i = 1 : nl
        %     R(i,:) = fnval(st, [XX(i,:); YY(i,:)]);
        % end
        % imagesc(xs, ys, R)

        % Monthly R factor
        dy = unique(dy_monthly);
        md = length(dy);
        pd_month = zeros(nd, md);
        for i = 1 : md
            x1 = filled_data(:, dy_monthly == dy(i));

            pd12 = mean(x1, 2, 'omitnan');

            beta = 0.8363 + 18.144 ./ pd12 + 24.455 ./ py12;
            alpha = 21.586 * beta.^(-7.1891);

            x1(isnan(x1)) = 0;
            [n,m] = size(x1);
            Md = [];
            for j = 1 : m
                Md(:,j) = alpha .* x1(:, j).^beta;
            end
            Mn = sum(Md, 2, 'omitnan');
            pd_month(:, i) = Mn;
        end
        R_month = sum(pd_month, 2, 'omitnan');

        % Weekly R factor
        dy = unique(dy46);
        md = length(dy);
        pd_week = zeros(nd, md);
        sid_R = [];
        for i = 1 : md
            x1 = filled_data(:, dy46 == dy(i));
            pd12 = mean(x1, 2, 'omitnan');

            beta = 0.8363 + 18.144 ./ pd12 + 24.455 ./ py12;
            alpha = 21.586 * beta.^(-7.1891);

            x1(isnan(x1)) = 0;
            [n,m] = size(x1);
            Md = [];
            for j = 1 : m
                Md(:,j) = alpha .* x1(:, j).^beta;
            end
            R_week = sum(Md, 2, 'omitnan');
            pd_week(:, i) = R_week;

%             x1 = x(~isnan(R_week));
%             y1 = y(~isnan(R_week));
%             z1 = elv(~isnan(R24));
%             R1 = R_week(~isnan(R_week));
%             xy = [x1'; y1'];
%             st = tpaps(xy, R1');
%             sid_rr = [i, yr, (i-1)*8+1, fnval(st, [sid_x'; sid_y'])];
%             
%             sid_R(i, :) = sid_rr;
            % R_img = [];
            % parfor Line = 1 : nlines
            %     R_img(Line,:) = fnval(st, [XX(Line,:); YY(Line,:)]);
            % end
            %
            % R_img(dem < -9000) = -9999;
            % bnd = quantile(R_img(R_img >= 0), [0.05, 0.95]);
            % imagesc(xs, ys, R_img, bnd);
            % colormap([white(1); parula(254)]);
            %
            % ftif_out = [out_wks, '\Rfactor_Asia1km_', num2str(yr * 1000 + i), '.tif'];
            % geotiffwrite2(ftif_out,single(R_img), R, 'GeoKeyDirectoryTag', proj.GeoTIFFTags.GeoKeyDirectoryTag);
        end
        % Fill missing data if the missing data less than 20%
        % Fill missing data if the missing data less than 20%
        ftxt = [wks_in, '\MeteoFilled\R_factor\R_factor_' num2str(yr) '.csv'];
        
        % 修复表头 - 添加SID作为第一列
        headerline = {'SID', 'Year', 'LAT1', 'LONG', 'Elva'};  % 添加SID列
        for i = 1 : md
            headerline{1, i + 5} = ['D' num2str(i, '%03d')];  % 注意索引从5改为6
        end
        
        fop = fopen(ftxt, 'w');
        
        % 写入表头
        header_str = strjoin(headerline, ',');
        fprintf(fop, '%s', header_str);
        
        % 写入数据行 - 现在表头和数据列数匹配了
        for i = 1 : n
            fprintf(fop, '\n%s,%d,%.6f,%.6f,%.1f', ...
                char(gid(i,:)), yr, lat(i), lon(i), elv(i));
            for j = 1 : md
                fprintf(fop, ',%.3f', pd_week(i,j));
            end
        end
        fclose(fop);

        % R_week = sum(pd_week, 2, 'omitnan');
        % xlswrite(fxls_out, [lon, lat, elv, R_week, pd_week], num2str(yr), 'B2');
        % xlswrite(fxls_out, sid, num2str(yr), 'A2');
        % xlswrite(fxls_out, hdr, num2str(yr), 'A1');

        % figure; plot(R24, R_week, 'b.', R24, R_month, 'r.');
        % figure; hist([R24, R_week, R_month]);

        % p = anova1([R24, R_week, R_month]);
        % c=multcompare(s)
        % write to file with the formation of Anusplin
        geo = [x, y, elv];

        csv2Anuspl(yr, out_name, wks_out, char(gid), geo, pd_week);

        makesplinotbat(yr, direct, size(pd_week), out_name, fdem, fhdr);

        disp([vname{v}, ' ', num2str([yr n,j-1])  ' ' num2str(toc)]);
    end
end
% hdr = {'No.', 'Year', 'Doy'};
% for i = 1 : length(sid_x)
%     hdr{1, i + 3} = sid_txt{i+1, 7};
% end
% xlswrite(fxls_out, hdr, 'Qinghai', 'A1');
% xlswrite(fxls_out, sid_R, 'Qinghai', 'A2');





