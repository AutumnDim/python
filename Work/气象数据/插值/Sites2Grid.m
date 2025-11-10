% function Sites2Grid(wks, fset,v, nots, time_step)
% % fset
% % v
% % nots: 1 Write selnot.cmd file; 0 not use setnot function
% % time_step: 1 for annually, 8 for week, 10 for 10-day, 30 for monthly
% %      and 15 for bi-weekly
% % DAILY GLOBAL HISTORICAL CLIMATOLOGY NETWORK (GHCN-DAILY)
% % Version 3.02
% % 	   ACSH = Average cloudiness sunrise to sunset from manual
% % 	          observations (percent)
% % 	   AWND = Average daily wind speed (tenths of meters per second)
% %      PRCP = Precipitation (tenths of mm)
% %      TMAX = Maximum temperature (tenths of degrees C)
% %      TMIN = Minimum temperature (tenths of degrees C)
% %      The filling value is -9999
% % Data from China Meteorological Information Sharing System (CIMISS）
% %      PRCP = Precipitation (mm)
% %      TMAX = Maximum temperature (degrees C)
% %      TMIN = Minimum temperature (degrees C)
% %      RHU  = Rative humidity (%)
% %      SSD  = Sunlit hour (hour)
% %      WIN  = Average daily wind speed (meters per second)
% %      The filling value is 999999
% % Output merged data by the above two data
% %      PRCP = Precipitation (tenths of mm)
% %      TMAX = Maximum temperature (tenths of degrees C)
% %      TMIN = Minimum temperature (tenths of degrees C)
% %      WIN  = Average daily wind speed (tenths of meters per second)
% %      RHU  = Rative humidity (%)
% %      SSD  = Sunlit hour (tenths of hour)
% %      The filling value is -9999
% %_________________By:jbwang@igsnrr.ac.cn,On Dec.30, 2016___________________
% % clear all
% % close all
% % clc
% % v = 2;
% % nots = 1;
% % fset = 'Shennj.set';
% % time_step = 10;
% vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN';'PRCP'};
% vad_value = [-90 90; 0 300; -90 90; -90 90; 0 100; 0 24; 0 50; 0 300]*10;
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
% [mcd, R, bbox] = geotiffread(ftif);
% 
% dist_x = 0.3820 * abs(proj.CornerCoords.X(1) - proj.CornerCoords.X(2));
% disp_y = 0.3820 * abs(proj.CornerCoords.Y(1) - proj.CornerCoords.Y(3));
% range_x(1) = proj.CornerCoords.X(1) - dist_x;
% range_x(2) = proj.CornerCoords.X(2) + dist_x;
% range_y(1) = proj.CornerCoords.Y(1) + dist_x;
% range_y(2) = proj.CornerCoords.Y(3) - dist_x;
% 
% yr_bat = [yr1 yr2];
% if ~(wks_grd(end) == '\' || wks_grd(end) == '/')
%     wks_grd  = [wks_grd '/'];
% end
% 
% direct = {{wks_out;wks_tmp;wks_grd};...
%     {[pwd '/' wks_out(4:end)];[pwd '/' wks_tmp(4:end)];[pwd '/' wks_grd(4:end)]}};% direct{1,1} is for Windows OS and direct{2,1} for Unix OS.
% % disp(['Processing ' vname{v}, ' in ', num2str(yr), ' begining at ' datestr(now)]);
% disp('Vname Year   day  Valid_Stn_Num  All_Stn_Num Used_time(sec.)');
% % if matlabpool('size') <= 0  % determine whether par started
% %     matlabpool('open', 'local',7)
% % else
% %     disp('Already initialized');
% % end
% %for v = 3:7
% tic;
% sub  = [wks_tmp '/' vname{v}];
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
%     % else
%     %     delete([wks_tmp '/' vname{v} '/*.*']);
%     %     delete([wks_grd '/' vname{v} '/*.*'])
% end
% if strcmp(vname{v},'PRCP')
%     mean_or_sum = 0;
% else
%     mean_or_sum = 1;
% end
% cd(wks);
% [status, results] = system(['copy splina.exe ' wks_tmp '/' vname{v} '/']);
% [status, results] = system(['copy splinb.exe ' wks_tmp '/' vname{v} '/']);
% [status, results] = system(['copy selnot.exe ' wks_tmp '/' vname{v} '/']);
% [status, results] = system(['copy lapgrd.exe ' wks_tmp '/' vname{v} '/']);
% [status, results] = system(['copy ' fdem ' ' wks_tmp '/' vname{v} '/']);
% % toc
% sub = wks_grd;
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
% end
% 
% sub = [wks_grd vname{v}];
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
% end
% 
% sub  = wks_out;
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
% end
% 
% 
% sub  = [wks_out '/' vname{v}];
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
% end
% 
% sub_filled  = [wks_in '/MeteoFilled'];
% if ~exist(sub_filled,'dir')
%     system(['mkdir ' sub_filled]);
% end
% 
% sub_filled  = [wks_in '/MeteoFilled/' vname{v}];
% if ~exist(sub_filled,'dir')
%     system(['mkdir ' sub_filled]);
% end
% sub_dbase  = [wks_in 'MeteoDbase/' vname{v}]; % 
% % if ~exist(sub_dbase,'dir')
% %     system(['mkdir ' sub_dbase]);
% % end
% annual_value = [];
% for yr = yr2:-1:yr1
%     [days, dy2, ~] = daily2timestep(yr, time_step);
%     % READ GHCN-CIMISS
%     file_filled = [sub_filled '/' vname{v} '_' num2str(yr) '_Filled.csv'];
%     file_raw    = [sub_dbase  '/' vname{v} '_' num2str(yr) '.csv'];
%     fd = dir(file_filled);
%     %     if exist(file_filled, 'file') && fd.bytes > 1000
%     %         headerline = 1;
%     %         [gid, xd, n1] = readFilledbase(file_filled,days+3, headerline);
%     %         lat = xd(:,2); lon = xd(:,3); elv = xd(:,4);
%     %         [x, y] = projfwd(proj, lat, lon);
%     %         geo = [x, y, elv];
%     %         filled_data = xd(:,5:end);
%     %     else
%     if exist(file_raw, 'file')
%         % disp(ff);
%         if contains(file_raw, 'txt')
%             [id_db, xd_db, n1] = readDbase(file_raw,days+3);
%         else
%             dat = readmatrix(file_raw);
%             dat(isnan(dat)) = 32767;
%             dat(dat < -900) = 32767;
%             id_db = dat(:,1);
%             xd_db = dat(:,2:end);
%             n1 = length(id_db);
%         end
% 
%         % plot(xd_db(:,2), xd_db(:,1), '.')
% 
%         % title(length(xd_db(:,2)));
% 
%         xd_up = max(xd_db(:,1:2));
%         xd_low = min(xd_db(:,1:2));
%         if abs(xd_up(1)) <= 1000 && abs(xd_low(2)) < 1000  
%             if xd_up(2) > 90
%                 lon = xd_db(:,2);
%                 lat = xd_db(:,1);
%             else
%                 lon = xd_db(:,1);
%                 lat = xd_db(:,2);
%             end
%             [x0, y0] = projfwd(proj, lat, lon);
%         else
%             x0 = xd_db(:,1); y0 = xd_db(:, 2);
%         end
% 
%         figure; plot(x0, y0, '.'); title(length(x0));
% 
%         xd = xd_db(x0 >= range_x(1) & x0 <= range_x(2) & y0 >= range_y(2) & y0 <= range_y(1),:);
%         id = id_db(x0 >= range_x(1) & x0 <= range_x(2) & y0 >= range_y(2) & y0 <= range_y(1),:);
% 
%         sd = (id_db);
%         % lat = xd(:,2); lon = xd(:,1); 
%         elv = xd(:,3); dat = xd(:,5:end);
%         % [x, y] = projfwd(proj, lat, lon);
%         s0 = [x0, y0, elv]; % xd_db(:,1:3); %, elv];
% 
%         % Check coincident data points
%         [sid, gxy, sdat] = LookCoincident(sd, s0, dat);
% 
%         figure; plot(gxy(:,1), gxy(:,2), '.'); title(length(gxy(:,1)));
% 
% 
%         [n m] = size(sdat);
%         j = 1;data = [];geo = []; gid = [];
%         for i = 1 : n
%             x0 = sdat(i,:);
%             x1 = x0(x0 >= vad_value(v,1) & x0 <= vad_value(v,2));
%             n1 = length(x1);
%             if n1/m >= 0.8 % including data if the missing data less than 20%
%                 data(j,:) = x0;
%                 geo(j,:) = gxy(i,:);
%                 gid(j,:) = sid(i,:);
%                 j = j + 1;
%             end
%         end
%         [n,m] = size(data);
%         if n > 100
%             data(data < vad_value(v,1) | data > vad_value(v,2)) = 32766;
% 
%             % Fill missing data if the missing data less than 20%
%             [filled_data, qc, sta,nf] = fillmissing(data, gid,geo);
%             ftxt = [sub_filled '/' vname{v} '_' num2str(yr) '_Filled.csv'];
%             headerline = {'SID';'Year'; 'LATI'; 'LONG'; 'Elva'};
%             for i = 1 : m
%                 headerline{i+5,1} = ['D' num2str(i, '%03d')];
%             end
% 
%             fop = fopen(ftxt, 'w');
%             for i = 1 : days + 5
%                 fprintf(fop, '%s,', headerline{i}');
%             end
% 
%             for i = 1 : n
%                 fprintf(fop, '\n%d, %d,%f,%f,%f', (gid(i,:)), yr, lat(i),lon(i),elv(i));
%                 for j = 1 : m
%                     fprintf(fop, ',%.3f', filled_data(i,j));
%                 end
%             end
%             fclose(fop);
%             % Calculate annual mean or sum on the national scale
%             if mean_or_sum == 0
%                 annual_filled_value = sum(filled_data,2) * 0.1;
%             else
%                 annual_filled_value = mean(filled_data,2) * 0.1;
%             end
%             annual_raw_value = [];
%             for i = 1 : n
%                 x0 = data(i,:);
%                 x1 = x0(x0 > -900 & x0 < 9000);
%                 n1 = length(x1);
%                 if n1/m >= 0.95 % including data if the missing data less than 20%
%                     if mean_or_sum == 0
%                         annual_raw_value(i,1) = sum(x1) * 0.1;
%                     else
%                         annual_raw_value(i,1) = mean(x1) * 0.1;
%                     end
%                 else
%                     annual_raw_value(i,1) = -9999;
%                 end
%             end
%             annual_value = [yr mean(annual_filled_value) std(annual_filled_value) mean(annual_raw_value) std(annual_raw_value) length(annual_raw_value) length(annual_filled_value)];
% 
%             disp(num2str(annual_value(2),'%8.1f'));
%         end
%     end
% 
%     if exist('filled_data', 'var')
%         % Mean by DOY
%         [averaged_data,q,sd] = meanbyxdays(filled_data, gid, dy2, mean_or_sum, 1);
%         averaged_data = averaged_data';
% 
%         [n,j] = size(averaged_data);
% 
%         % exd = 0.0;
%         % subset is extracted for aimed area.
%         % geo_set = geo(geo(:,1) > bbox(1,1)-exd & geo(:,1) <= bbox(2,1)+exd & geo(:,2) > bbox(1,2)-exd & geo(:,2) <= bbox(2,2)+exd, :);
%         % dat_set = averaged_data(geo(:,1) > bbox(1,1)-exd & geo(:,1) <= bbox(2,1)+exd & geo(:,2) > bbox(1,2)-exd & geo(:,2) <= bbox(2,2)+exd, :);
%         % gid_set = gid(geo(:,1) > bbox(1,1)-exd & geo(:,1) <= bbox(2,1)+exd & geo(:,2) > bbox(1,2)-exd & geo(:,2) <= bbox(2,2)+exd, :);
% 
%         % Read monthly or annual data
% 
% 
%         % write to file with the formation of Anusplin
%         csv2Anuspl(yr, vname{v}, wks_out, char(gid),geo, averaged_data);
% 
%         if nots == 1
%             makesplinotbat(yr, direct, size(averaged_data), vname{v}, fdem, fhdr);
%         else
%             % splinabat_no_cov(yr, direct, size(averaged_data), vname{v}, fdem, fhdr);
%             makesplinabat(yr, direct, size(averaged_data), vname{v}, fdem, fhdr);
%         end
% 
%         disp([vname{v}, ' ', num2str([yr n,j-1])  ' ' num2str(toc)]);
% 
%         %         % change to vname{v} sub and run vname{v}_spl.bat
%         % cd([wks_tmp '/' vname{v}]);
%         % dos([vname{v} '_' num2str(yr) '_spl.bat']);
%     else
%         nsd = []; xsd = []; n1 = 0;
%     end
% end
% % if exist('annual_value', 'var')
% %     if ~isempty(annual_value)
% %         % write annual statistical value to excel file
% %         hdr_line = {'Year','Filled_Mean','Filled_STD','Raw_Mean','Raw_STD','Raw_number', 'Filled_number'};
% %         fxls = [wks_grd '/' vname{v} '_' num2str(yr1) '-' num2str(yr2) '.xls'];
% %         xlswrite(fxls, hdr_line, 'Sheet1', 'A1');
% %         xlswrite(fxls, annual_value, 'Sheet1', 'A2');
% %     end
% % end
% % disp(datestr(now));
% % end
% % disp(datestr(now));
% 
% % if matlabpool('size') > 0  % determine whether par started
% %     matlabpool close force local;
% % end
% 
% % disp('That''s all, go home!');
% % 






% function Sites2Grid(wks, fset, v, nots, time_step)
% % fset
% % v
% % nots: 1 Write selnot.cmd file; 0 not use setnot function
% % time_step: 1 for annually, 8 for week, 10 for 10-day, 30 for monthly
% %      and 15 for bi-weekly
% % DAILY GLOBAL HISTORICAL CLIMATOLOGY NETWORK (GHCN-DAILY)
% % Version 3.02
% % 	   ACSH = Average cloudiness sunrise to sunset from manual
% % 	          observations (percent)
% % 	   AWND = Average daily wind speed (tenths of meters per second)
% %      PRCP = Precipitation (tenths of mm)
% %      TMAX = Maximum temperature (tenths of degrees C)
% %      TMIN = Minimum temperature (tenths of degrees C)
% %      The filling value is -9999
% % Data from China Meteorological Information Sharing System (CIMISS）
% %      PRCP = Precipitation (mm)
% %      TMAX = Maximum temperature (degrees C)
% %      TMIN = Minimum temperature (degrees C)
% %      RHU  = Rative humidity (%)
% %      SSD  = Sunlit hour (hour)
% %      WIN  = Average daily wind speed (meters per second)
% %      The filling value is 999999
% % Output merged data by the above two data
% %      PRCP = Precipitation (tenths of mm)
% %      TMAX = Maximum temperature (tenths of degrees C)
% %      TMIN = Minimum temperature (tenths of degrees C)
% %      WIN  = Average daily wind speed (tenths of meters per second)
% %      RHU  = Rative humidity (%)
% %      SSD  = Sunlit hour (tenths of hour)
% %      The filling value is -9999
% %_________________By:jbwang@igsnrr.ac.cn,On Dec.30, 2016___________________
% % clear all
% % close all
% % clc
% % v = 2;
% % nots = 1;
% % fset = 'Shennj.set';
% % time_step = 10;
% 
% % ===================== 改动 1：移除 TAVG =====================
% % 原始：
% % vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN';'PRCP'};
% % vad_value = [-90 90; 0 300; -90 90; -90 90; 0 100; 0 24; 0 50; 0 300]*10;
% % 现用（不含 TAVG）：
% vname = {'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD'; 'WIN'; 'PRCP'};
% vad_value = [ 0 300; -90 90; -90 90; 0 100; 0 24; 0 50; 0 300] * 10;
% 
% % ===================== 改动 2：向后兼容旧索引 =====================
% orig_vname = {'TAVG','PRCP','TMIN','TMAX','RHU','SSD','WIN','PRCP'};
% 
% % 若传入旧索引且指向 TAVG（旧 v=1），直接跳过返回
% if v >= 1 && v <= numel(orig_vname) && strcmp(orig_vname{v}, 'TAVG')
%     disp('Skip: TAVG is no longer processed in Sites2Grid.');
%     return;
% end
% 
% % 若传入旧索引（非 TAVG），自动映射到新索引（不含 TAVG）
% if v >= 1 && v <= numel(orig_vname)
%     target_var = orig_vname{v};
%     new_idx = find(strcmp(vname, target_var), 1);
%     if ~isempty(new_idx)
%         v = new_idx;
%     else
%         error('Variable mapping failed for v=%d (%s).', v, target_var);
%     end
% end
% % ===================== 改动部分结束 =====================
% 
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
% [mcd, R, bbox] = geotiffread(ftif);
% 
% dist_x = 0.3820 * abs(proj.CornerCoords.X(1) - proj.CornerCoords.X(2));
% disp_y = 0.3820 * abs(proj.CornerCoords.Y(1) - proj.CornerCoords.Y(3));
% range_x(1) = proj.CornerCoords.X(1) - dist_x;
% range_x(2) = proj.CornerCoords.X(2) + dist_x;
% range_y(1) = proj.CornerCoords.Y(1) + dist_x;
% range_y(2) = proj.CornerCoords.Y(3) - dist_x;
% 
% yr_bat = [yr1 yr2];
% if ~(wks_grd(end) == '\' || wks_grd(end) == '/')
%     wks_grd  = [wks_grd '/'];
% end
% 
% direct = {{wks_out;wks_tmp;wks_grd};...
%     {[pwd '/' wks_out(4:end)];[pwd '/' wks_tmp(4:end)];[pwd '/' wks_grd(4:end)]}};% direct{1,1} is for Windows OS and direct{2,1} for Unix OS.
% % disp(['Processing ' vname{v}, ' in ', num2str(yr), ' begining at ' datestr(now)]);
% disp('Vname Year   day  Valid_Stn_Num  All_Stn_Num Used_time(sec.)');
% % if matlabpool('size') <= 0  % determine whether par started
% %     matlabpool('open', 'local',7)
% % else
% %     disp('Already initialized');
% % end
% %for v = 3:7
% tic;
% sub  = [wks_tmp '/' vname{v}];
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
%     % else
%     %     delete([wks_tmp '/' vname{v} '/*.*']);
%     %     delete([wks_grd '/' vname{v} '/*.*'])
% end
% if strcmp(vname{v},'PRCP')
%     mean_or_sum = 0;
% else
%     mean_or_sum = 1;
% end
% cd(wks);
% [status, results] = system(['copy splina.exe ' wks_tmp '/' vname{v} '/']);
% [status, results] = system(['copy splinb.exe ' wks_tmp '/' vname{v} '/']);
% [status, results] = system(['copy selnot.exe ' wks_tmp '/' vname{v} '/']);
% [status, results] = system(['copy lapgrd.exe ' wks_tmp '/' vname{v} '/']);
% [status, results] = system(['copy ' fdem ' ' wks_tmp '/' vname{v} '/']);
% % toc
% sub = wks_grd;
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
% end
% 
% sub = [wks_grd vname{v}];
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
% end
% 
% sub  = wks_out;
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
% end
% 
% sub  = [wks_out '/' vname{v}];
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
% end
% 
% sub_filled  = [wks_in '/MeteoFilled'];
% if ~exist(sub_filled,'dir')
%     system(['mkdir ' sub_filled]);
% end
% 
% sub_filled  = [wks_in '/MeteoFilled/' vname{v}];
% if ~exist(sub_filled,'dir')
%     system(['mkdir ' sub_filled]);
% end
% sub_dbase  = [wks_in 'MeteoDbase/' vname{v}]; % 
% % if ~exist(sub_dbase,'dir')
% %     system(['mkdir ' sub_dbase]);
% % end
% annual_value = [];
% for yr = yr2:-1:yr1
%     [days, dy2, ~] = daily2timestep(yr, time_step);
%     % READ GHCN-CIMISS
%     file_filled = [sub_filled '/' vname{v} '_' num2str(yr) '_Filled.csv'];
%     file_raw    = [sub_dbase  '/' vname{v} '_' num2str(yr) '.csv'];
%     fd = dir(file_filled);
%     %     if exist(file_filled, 'file') && fd.bytes > 1000
%     %         headerline = 1;
%     %         [gid, xd, n1] = readFilledbase(file_filled,days+3, headerline);
%     %         lat = xd(:,2); lon = xd(:,3); elv = xd(:,4);
%     %         [x, y] = projfwd(proj, lat, lon);
%     %         geo = [x, y, elv];
%     %         filled_data = xd(:,5:end);
%     %     else
%     if exist(file_raw, 'file')
%         % disp(ff);
%         if contains(file_raw, 'txt')
%             [id_db, xd_db, n1] = readDbase(file_raw,days+3);
%         else
%             dat = readmatrix(file_raw);
%             dat(isnan(dat)) = 32767;
%             dat(dat < -900) = 32767;
%             id_db = dat(:,1);
%             xd_db = dat(:,2:end);
%             n1 = length(id_db);
%         end
% 
%         % plot(xd_db(:,2), xd_db(:,1), '.')
% 
%         % title(length(xd_db(:,2)));
% 
%         xd_up = max(xd_db(:,1:2));
%         xd_low = min(xd_db(:,1:2));
%         if abs(xd_up(1)) <= 1000 && abs(xd_low(2)) < 1000
%             if xd_up(2) > 90
%                 lon = xd_db(:,2);
%                 lat = xd_db(:,1);
%             else
%                 lon = xd_db(:,1);
%                 lat = xd_db(:,2);
%             end
%             [x0, y0] = projfwd(proj, lat, lon);
%         else
%             x0 = xd_db(:,1); y0 = xd_db(:, 2);
%         end
% 
%         figure; plot(x0, y0, '.'); title(length(x0));
% 
%         xd = xd_db(x0 >= range_x(1) & x0 <= range_x(2) & y0 >= range_y(2) & y0 <= range_y(1),:);
%         id = id_db(x0 >= range_x(1) & x0 <= range_x(2) & y0 >= range_y(2) & y0 <= range_y(1),:);
% 
%         sd = (id_db);
%         % lat = xd(:,2); lon = xd(:,1);
%         elv = xd(:,3); dat = xd(:,5:end);
%         % [x, y] = projfwd(proj, lat, lon);
%         s0 = [x0, y0, elv]; % xd_db(:,1:3); %, elv];
% 
%         % Check coincident data points
%         [sid, gxy, sdat] = LookCoincident(sd, s0, dat);
% 
%         figure; plot(gxy(:,1), gxy(:,2), '.'); title(length(gxy(:,1)));
% 
%         [n, m] = size(sdat);
%         j = 1; data = []; geo = []; gid = [];
%         for i = 1 : n
%             x0 = sdat(i,:);
%             x1 = x0(x0 >= vad_value(v,1) & x0 <= vad_value(v,2));
%             n1 = length(x1);
%             if n1/m >= 0.8 % including data if the missing data less than 20%
%                 data(j,:) = x0;
%                 geo(j,:) = gxy(i,:);
%                 gid(j,:) = sid(i,:);
%                 j = j + 1;
%             end
%         end
%         [n,m] = size(data);
%         if n > 100
%             data(data < vad_value(v,1) | data > vad_value(v,2)) = 32766;
% 
%             % Fill missing data if the missing data less than 20%
%             [filled_data, qc, sta, nf] = fillmissing(data, gid, geo);
%             ftxt = [sub_filled '/' vname{v} '_' num2str(yr) '_Filled.csv'];
%             headerline = {'SID';'Year'; 'LATI'; 'LONG'; 'Elva'};
%             for i = 1 : m
%                 headerline{i+5,1} = ['D' num2str(i, '%03d')];
%             end
% 
%             fop = fopen(ftxt, 'w');
%             for i = 1 : days + 5
%                 fprintf(fop, '%s,', headerline{i}');
%             end
% 
%             for i = 1 : n
%                 fprintf(fop, '\n%d, %d,%f,%f,%f', (gid(i,:)), yr, lat(i), lon(i), elv(i));
%                 for j = 1 : m
%                     fprintf(fop, ',%.3f', filled_data(i,j));
%                 end
%             end
%             fclose(fop);
%             % Calculate annual mean or sum on the national scale
%             if mean_or_sum == 0
%                 annual_filled_value = sum(filled_data,2) * 0.1;
%             else
%                 annual_filled_value = mean(filled_data,2) * 0.1;
%             end
%             annual_raw_value = [];
%             for i = 1 : n
%                 x0 = data(i,:);
%                 x1 = x0(x0 > -900 & x0 < 9000);
%                 n1 = length(x1);
%                 if n1/m >= 0.95 % including data if the missing data less than 20%
%                     if mean_or_sum == 0
%                         annual_raw_value(i,1) = sum(x1) * 0.1;
%                     else
%                         annual_raw_value(i,1) = mean(x1) * 0.1;
%                     end
%                 else
%                     annual_raw_value(i,1) = -9999;
%                 end
%             end
%             annual_value = [yr mean(annual_filled_value) std(annual_filled_value) mean(annual_raw_value) std(annual_raw_value) length(annual_raw_value) length(annual_filled_value)];
% 
%             disp(num2str(annual_value(2),'%8.1f'));
%         end
%     end
% 
%     if exist('filled_data', 'var')
%         % Mean by DOY
%         [averaged_data, q, sd] = meanbyxdays(filled_data, gid, dy2, mean_or_sum, 1);
%         averaged_data = averaged_data';
% 
%         [n, j] = size(averaged_data);
% 
%         % exd = 0.0;
%         % subset is extracted for aimed area.
%         % geo_set = geo(geo(:,1) > bbox(1,1)-exd & geo(:,1) <= bbox(2,1)+exd & geo(:,2) > bbox(1,2)-exd & geo(:,2) <= bbox(2,2)+exd, :);
%         % dat_set = averaged_data(geo(:,1) > bbox(1,1)-exd & geo(:,1) <= bbox(2,1)+exd & geo(:,2) > bbox(1,2)-exd & geo(:,2) <= bbox(2,2)+exd, :);
%         % gid_set = gid(geo(:,1) > bbox(1,1)-exd & geo(:,1) <= bbox(2,1)+exd & geo(:,2) > bbox(1,2)-exd & geo(:,2) <= bbox(2,2)+exd, :);
% 
%         % Read monthly or annual data
% 
%         % write to file with the formation of Anusplin
%         csv2Anuspl(yr, vname{v}, wks_out, char(gid), geo, averaged_data);
% 
%         if nots == 1
%             makesplinotbat(yr, direct, size(averaged_data), vname{v}, fdem, fhdr);
%         else
%             % splinabat_no_cov(yr, direct, size(averaged_data), vname{v}, fdem, fhdr);
%             makesplinabat(yr, direct, size(averaged_data), vname{v}, fdem, fhdr);
%         end
% 
%         disp([vname{v}, ' ', num2str([yr n, j-1])  ' ' num2str(toc)]);
% 
%         %         % change to vname{v} sub and run vname{v}_spl.bat
%         % cd([wks_tmp '/' vname{v}]);
%         % dos([vname{v} '_' num2str(yr) '_spl.bat']);
%     else
%         nsd = []; xsd = []; n1 = 0;
%     end
% end





% function Sites2Grid(wks, fset, v, nots, time_step)
% % Sites2Grid
% % 在站点数据基础上，填补缺测、按时间步聚合，并导出 Anusplin 所需格式与中间 CSV。
% %
% % 参数
% %   wks        : 工作目录（例如 D:\project\）
% %   fset       : 配置文件路径（包含年份、路径、DEM/HDR/TIF 等）
% %   v          : 变量索引（已移除 TAVG；见 vname 下标）
% %   nots       : 1 写 selnot.cmd；0 不用 setnot（转为 makesplinabat）
% %   time_step  : 1=年, 8=周, 10=旬, 30=月, 15=双周
% %
% % 说明
% % - 已移除 TAVG；若仍传入旧索引中的 TAVG（旧 v=1），将直接跳过返回；
% % - 已对 copy/mkdir 调用做了跨平台与路径健壮化处理；
% % - 修复了 x0/y0 与筛选后数据长度不一致导致的拼接错误；
% % - 修复了表头长度越界；
% % - 在调用 meanbyxdays 前对齐 dy2 与数据列数；
% % - 写 CSV 用对齐后的 lat/lon，防止错位。
% %
% % 作者（原始版本）: jbwang@igsnrr.ac.cn, 2016-12-30
% % 当前版本整修: 2025-09-05
% 
% %% =============== 变量列表（移除 TAVG） ===============
% % 原始：{'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD'; 'WIN'; 'PRCP'}
% % vname    = {'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD'; 'WIN'; 'PRCP'};
% % vad_value = [ 0 300; -90 90; -90 90; 0 100; 0 24; 0 50; 0 300] * 10;
% vname      = {'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD'; 'WIN'};
% vad_value  = [ 0 300; -90 90; -90 90; 0 100; 0 24; 0 50] * 10;
% % 旧索引兼容（含 TAVG）
% orig_vname = {'TAVG','PRCP','TMIN','TMAX','RHU','SSD','WIN','PRCP'};
% if v >= 1 && v <= numel(orig_vname) && strcmp(orig_vname{v}, 'TAVG')
%     disp('Skip: TAVG is no longer processed in Sites2Grid.');
%     return;
% end
% if v >= 1 && v <= numel(orig_vname)
%     target_var = orig_vname{v};
%     new_idx = find(strcmp(vname, target_var), 1);
%     if ~isempty(new_idx), v = new_idx; else
%         error('Variable mapping failed for v=%d (%s).', v, target_var);
%     end
% end
% 
% % %% =============== 读取配置 ===============
% if exist(fset, 'file')
%     [~, svalue] = textread(fset, '%s%s');
%     yr1   = str2double(svalue{1}); yr2 = str2double(svalue{2});
%     wks_in  = svalue{3};
%     wks_out = svalue{4};    % Anusplin 格式数据库输出目录
%     wks_tmp = svalue{5};    % 临时目录（脚本等）
%     wks_grd = svalue{6};    % 插值结果栅格目录
%     fdem    = svalue{7};
%     fhdr    = svalue{8};
%     ftif    = svalue{9};
% else
%     disp('Error: Not find site information file');
%     return;
% end
% 
% % 可选：Anusplin 可执行文件目录（留空则不拷贝）
% exedir = ''; % 例如 exedir = 'D:\tools\anusplin';
% 
% % 绝对路径 & 目录准备
% if ~isfolder(wks), error('Workspace not found: %s', wks); end
% if ~isfolder(wks_in), error('wks_in not found: %s', wks_in); end
% wks_out = absolute_dir(wks, wks_out);
% wks_tmp = absolute_dir(wks, wks_tmp);
% wks_grd = absolute_dir(wks, wks_grd);
% 
% %% =============== 地理信息 ===============
% proj = geotiffinfo(ftif);
% [~, R, bbox] = geotiffread(ftif); %#ok<ASGLU>
% 
% dist_x = 0.3820 * abs(proj.CornerCoords.X(1) - proj.CornerCoords.X(2));
% dist_y = 0.3820 * abs(proj.CornerCoords.Y(1) - proj.CornerCoords.Y(3));
% range_x = [proj.CornerCoords.X(1) - dist_x, proj.CornerCoords.X(2) + dist_x];
% range_y = [proj.CornerCoords.Y(1) + dist_y, proj.CornerCoords.Y(3) - dist_y];
% 
% if ~(wks_grd(end) == '\' || wks_grd(end) == '/')
%     wks_grd = [wks_grd filesep];
% end
% 
% direct = {{wks_out; wks_tmp; wks_grd}; ...
%           {fullfile(pwd, strip_leading_sep(wks_out)); ...
%            fullfile(pwd, strip_leading_sep(wks_tmp)); ...
%            fullfile(pwd, strip_leading_sep(wks_grd))}};
% 
% disp('Vname Year   day  Valid_Stn_Num  All_Stn_Num Used_time(sec.)');
% tic;
% 
% %% =============== 目录与依赖 ===============
% sub_tmp_var = fullfile(wks_tmp, vname{v});
% ensure_dir(sub_tmp_var);
% ensure_dir(wks_grd);
% ensure_dir(fullfile(wks_grd, vname{v}));
% ensure_dir(wks_out);
% ensure_dir(fullfile(wks_out, vname{v}));
% ensure_dir(fullfile(wks_in, 'MeteoFilled'));
% ensure_dir(fullfile(wks_in, 'MeteoFilled', vname{v}));
% sub_dbase = fullfile(wks_in, 'MeteoDbase', vname{v});
% 
% % 拷贝可执行文件（仅当 exedir 非空）
% if ~isempty(exedir)
%     safe_copy(fullfile(exedir, 'splina.exe'), sub_tmp_var);
%     safe_copy(fullfile(exedir, 'splinb.exe'), sub_tmp_var);
%     safe_copy(fullfile(exedir, 'selnot.exe'), sub_tmp_var);
%     safe_copy(fullfile(exedir, 'lapgrd.exe'), sub_tmp_var);
% else
%     % 可根据需要打开提醒
%     % warning('exedir is empty; skip copying Anusplin executables.');
% end
% % DEM 一定要拷
% safe_copy(fdem, sub_tmp_var);
% 
% % 降水按和，其它按均值
% if strcmp(vname{v},'PRCP'), mean_or_sum = 0; else, mean_or_sum = 1; end
% 
% % 切换到 wks
% cd(wks);
% 
% %% =============== 主循环 ===============
% for yr = yr2:-1:yr1
%     [days, dy2, ~] = daily2timestep(yr, time_step);
% 
%     file_filled = fullfile(wks_in, 'MeteoFilled', vname{v}, sprintf('%s_%d_Filled.csv', vname{v}, yr));
%     file_raw    = fullfile(sub_dbase, sprintf('%s_%d.csv', vname{v}, yr));
% 
%     if exist(file_raw, 'file')
%         % 原始读入
%         if contains(file_raw, 'txt')
%             [id_db, xd_db, ~] = readDbase(file_raw, days+3);
%         else
%             dat = readmatrix(file_raw);
%             dat(isnan(dat)) = 32767;
%             dat(dat < -900) = 32767;
%             id_db = dat(:,1);
%             xd_db = dat(:,2:end);
%         end
% 
%         % 判定前两列是经纬还是投影
%         xd_up  = max(xd_db(:,1:2));
%         xd_low = min(xd_db(:,1:2));
%         haveLatLon = false;
%         if abs(xd_up(1)) <= 1000 && abs(xd_low(2)) < 1000
%             % (lon, lat) 两列
%             if xd_up(2) > 90
%                 lon = xd_db(:,2); lat = xd_db(:,1);
%             else
%                 lon = xd_db(:,1); lat = xd_db(:,2);
%             end
%             [x0, y0] = projfwd(proj, lat, lon);
%             haveLatLon = true;
%         else
%             % 已是投影坐标
%             x0 = xd_db(:,1); y0 = xd_db(:,2);
%         end
% 
%         % 地理范围筛选
%         mask = (x0 >= range_x(1) & x0 <= range_x(2) & ...
%                 y0 >= range_y(2) & y0 <= range_y(1));
% 
%         xd = xd_db(mask, :);
%         id = id_db(mask, :);
% 
%         % 对齐后的坐标/经纬度
%         x0m = x0(mask);
%         y0m = y0(mask);
%         if haveLatLon
%             latm = lat(mask);
%             lonm = lon(mask);
%         else
%             latm = nan(size(x0m));
%             lonm = nan(size(y0m));
%         end
% 
%         elv = xd(:,3);
%         dat = xd(:,5:end);
% 
%         % 组合坐标（与筛选后数据对齐）
%         s0 = [x0m, y0m, elv];
% 
%         % 重合点合并（使用筛选后的 id/s0/dat）
%         [sid_all, gxy_all, sdat_all] = LookCoincident(id, s0, dat);
% 
%         % 过滤出有效站（缺测<20%）
%         [n_all, m_all] = size(sdat_all);
%         j = 1; data = []; geo = []; gid = [];
%         for i = 1:n_all
%             row = sdat_all(i,:);
%             inRange = (row >= vad_value(v,1) & row <= vad_value(v,2));
%             if sum(inRange)/m_all >= 0.8
%                 data(j,:) = row;           %#ok<AGROW>
%                 geo(j,:)  = gxy_all(i,:);  %#ok<AGROW>
%                 gid(j,:)  = sid_all(i,:);  %#ok<AGROW>
%                 j = j + 1;
%             end
%         end
% 
%         [n, m] = size(data);
%         if n > 100
%             % 越界值置 32766（原逻辑）
%             data(data < vad_value(v,1) | data > vad_value(v,2)) = 32766;
% 
%             % 填补缺测
%             [filled_data, qc, sta, nf] = fillmissing(data, gid, geo); %#ok<ASGLU>
% 
%             % 写 Filled CSV
%             ftxt = file_filled;
%             headerline = {'SID';'Year'; 'LATI'; 'LONG'; 'Elva'};
%             for ii = 1:m
%                 headerline{ii+5,1} = ['D' num2str(ii, '%03d')]; %#ok<AGROW>
%             end
% 
%             fop = fopen(ftxt, 'w');
%             % —— 用 headerline 实际长度，防越界 —— %
%             numCols = numel(headerline);
%             for ii = 1:numCols
%                 fprintf(fop, '%s,', headerline{ii});
%             end
% 
%             % 写每站数据（lat/lon 使用对齐后的 latm/lonm；如无经纬则为 NaN）
%             % 注意：此处 geo(:,3) 就是 elv
%             for ii = 1:n
%                 lati = get_or_nan(latm, ii);
%                 loni = get_or_nan(lonm, ii);
%                 fprintf(fop, '\n%d, %d,%f,%f,%f', (gid(ii,:)), yr, lati, loni, geo(ii,3));
%                 for jj = 1:m
%                     fprintf(fop, ',%.3f', filled_data(ii,jj));
%                 end
%             end
%             fclose(fop);
% 
%             % 年尺度统计
%             if mean_or_sum == 0
%                 annual_filled_value = sum(filled_data,2) * 0.1;
%             else
%                 annual_filled_value = mean(filled_data,2) * 0.1;
%             end
%             annual_raw_value = nan(n,1);
%             for ii = 1:n
%                 xi = data(ii,:);
%                 x1 = xi(xi > -900 & xi < 9000);
%                 if numel(x1)/m >= 0.95
%                     if mean_or_sum == 0
%                         annual_raw_value(ii,1) = sum(x1) * 0.1;
%                     else
%                         annual_raw_value(ii,1) = mean(x1) * 0.1;
%                     end
%                 else
%                     annual_raw_value(ii,1) = -9999;
%                 end
%             end
%             annual_value = [yr mean(annual_filled_value) std(annual_filled_value) ...
%                             mean(annual_raw_value) std(annual_raw_value) ...
%                             length(annual_raw_value) length(annual_filled_value)];
%             disp(num2str(annual_value(2), '%8.1f'));
%         end
%     end
% 
%     % ========== 聚合到 time_step（调用 meanbyxdays 前对齐列数） ==========
%     if exist('filled_data', 'var')
%         mData = size(filled_data, 2);
%         mDn   = numel(dy2);
%         mUse  = min(mData, mDn);
%         if mUse < mData
%             warning('Data has fewer columns than dy2. Truncating dy2 to %d entries.', mUse);
%         end
%         if mUse < mDn
%             % 进一步在 meanbyxdays 内也会警告一次，这里仅提示一次即可
%         end
%         filled_data_use = filled_data(:, 1:mUse);
%         dy2_use         = dy2(1:mUse);
% 
%         [averaged_data, q, sd] = meanbyxdays(filled_data_use, gid, dy2_use, mean_or_sum, 1); %#ok<ASGLU>
%         averaged_data = averaged_data';  % 转成 [stations x groups]
% 
%         [n_out, j_out] = size(averaged_data); %#ok<ASGLU>
% 
%         % 写入 Anusplin 格式
%         csv2Anuspl(yr, vname{v}, wks_out, gid, geo, averaged_data);
% 
%         % 写批处理
%         if nots == 1
%             makesplinotbat(yr, direct, size(averaged_data), vname{v}, fdem, fhdr);
%         else
%             makesplinabat(yr, direct, size(averaged_data), vname{v}, fdem, fhdr);
%         end
% 
%         disp([vname{v}, ' ', num2str([yr n_out, j_out-1])  ' ' num2str(toc)]);
%     else
%         % 没有 filled_data
%         % nsd = []; xsd = []; n1 = 0;  % 保留为空
%     end
% end
% 
% end % === function Sites2Grid ===
% 
% 
% %% ==================== 工具函数 ====================
% function ensure_dir(p)
%     if ~isfolder(p), mkdir(p); end
% end
% 
% function safe_copy(src, dst_folder)
%     if ~isfolder(dst_folder), mkdir(dst_folder); end
%     if ~exist(src, 'file')
%         warning('File not found: %s (skip copy)', src);
%         return;
%     end
%     [status,msg] = copyfile(src, dst_folder);
%     if ~status
%         error('copyfile failed: %s -> %s (%s)', src, dst_folder, msg);
%     end
% end
% 
% function out = absolute_dir(root, maybeRel)
%     if isfolder(maybeRel)
%         out = char(java.io.File(maybeRel).getCanonicalPath());
%         return;
%     end
%     if startsWith(maybeRel, filesep) || (ispc && ~isempty(regexp(maybeRel,'^[A-Za-z]:\\','once')))
%         out = maybeRel;
%     else
%         out = fullfile(root, strip_leading_sep(maybeRel));
%     end
%     if ~isfolder(out), mkdir(out); end
% end
% 
% function s = strip_leading_sep(p)
%     if isempty(p), s = p; return; end
%     if p(1) == '/' || p(1) == '\', s = p(2:end); else, s = p; end
% end
% 
% function v = get_or_nan(arr, idx)
%     if isempty(arr) || idx > numel(arr) || isnan(arr(idx))
%         v = NaN;
%     else
%         v = arr(idx);
%     end
% end










function Sites2Grid(wks, fset, v, nots, time_step)
% Sites2Grid
% 在站点数据基础上，填补缺测、按时间步聚合，并导出 Anusplin 所需格式与中间 CSV。
%
% 参数
%   wks        : 工作目录（例如 D:\project\）
%   fset       : 配置文件路径（包含年份、路径、DEM/HDR/TIF 等）
%   v          : 变量（支持新索引/旧索引/变量名字符串）
%   nots       : 1 写 selnot.cmd；0 不用 setnot（转为 makesplinabat）
%   time_step  : 1=年, 8=周, 10=旬, 30=月, 15=双周
%

%% =============== 变量列表（去重，无 TAVG） ===============
vname     = {'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD'; 'WIN'};
vad_value = [ 0 300; -90 90; -90 90; 0 100; 0 24; 0 50] * 10;

% 保留旧顺序，仅在必要时用于兼容旧工程的“位置号”
orig_vname = {'TAVG','PRCP','TMIN','TMAX','RHU','SSD','WIN','PRCP'};

% —— 解析参数 v（新索引优先；必要时旧->新映射；也支持变量名）——
if ischar(v) || isstring(v)
    v_char = upper(strtrim(string(v)));
    idx = find(strcmp(vname, v_char), 1);
    if isempty(idx)
        error('Unknown variable name: %s. Valid: %s', v_char, strjoin(vname', ', '));
    end
    v = idx;
elseif isnumeric(v) && isscalar(v)
    if v >= 1 && v <= numel(vname)
        % 新索引（1..6）：直接使用
        % no-op
    elseif v > numel(vname) && v <= numel(orig_vname)
        % 看起来传的是旧索引（7 或 8 等）
        target_var = orig_vname{v};
        if strcmp(target_var, 'TAVG')
            disp('Skip: TAVG is no longer processed in Sites2Grid.');
            return;
        end
        idx = find(strcmp(vname, target_var), 1);
        if isempty(idx)
            error('Legacy index v=%d (%s) could not be mapped to new list.', v, target_var);
        end
        v = idx; % 旧->新
    else
        error('Index v=%d out of range. Use 1..%d (new) or a variable name.', v, numel(vname));
    end
else
    error('Parameter v must be a scalar index or a variable name string.');
end

%% =============== 读取配置 ===============
if exist(fset, 'file')
    [~, svalue] = textread(fset, '%s%s');
    yr1   = str2double(svalue{1}); yr2 = str2double(svalue{2});
    wks_in  = svalue{3};
    wks_out = svalue{4};    % Anusplin 格式数据库输出目录
    wks_tmp = svalue{5};    % 临时目录（脚本等）
    wks_grd = svalue{6};    % 插值结果栅格目录
    fdem    = svalue{7};
    fhdr    = svalue{8};
    ftif    = svalue{9};
else
    error('Not find site information file: %s', fset);
end

% 可选：Anusplin 可执行文件目录（留空则不拷贝）
exedir = ''; % 例如 exedir = 'D:\tools\anusplin';

% 绝对路径 & 目录准备
if ~isfolder(wks),    error('Workspace not found: %s', wks);    end
if ~isfolder(wks_in), error('wks_in not found: %s', wks_in);    end
wks_out = absolute_dir(wks, wks_out);
wks_tmp = absolute_dir(wks, wks_tmp);
wks_grd = absolute_dir(wks, wks_grd);

%% =============== 地理信息 ===============
proj = geotiffinfo(ftif);
[~, R, bbox] = geotiffread(ftif); %#ok<ASGLU>

dist_x  = 0.3820 * abs(proj.CornerCoords.X(1) - proj.CornerCoords.X(2));
dist_y  = 0.3820 * abs(proj.CornerCoords.Y(1) - proj.CornerCoords.Y(3));
range_x = [proj.CornerCoords.X(1) - dist_x, proj.CornerCoords.X(2) + dist_x];
range_y = [proj.CornerCoords.Y(1) + dist_y, proj.CornerCoords.Y(3) - dist_y];

if ~(wks_grd(end) == '\' || wks_grd(end) == '/')
    wks_grd = [wks_grd filesep];
end

direct = {{wks_out; wks_tmp; wks_grd}; ...
          {fullfile(pwd, strip_leading_sep(wks_out)); ...
           fullfile(pwd, strip_leading_sep(wks_tmp)); ...
           fullfile(pwd, strip_leading_sep(wks_grd))}};

fprintf('Vname  Year  Step  Valid_Stn  All_Stn  Used_time(s)\n');
t_all = tic;

%% =============== 目录与依赖 ===============
sub_tmp_var = fullfile(wks_tmp, vname{v});
ensure_dir(sub_tmp_var);
ensure_dir(wks_grd);
ensure_dir(fullfile(wks_grd, vname{v}));
ensure_dir(wks_out);
ensure_dir(fullfile(wks_out, vname{v}));
ensure_dir(fullfile(wks_in, 'MeteoFilled'));
ensure_dir(fullfile(wks_in, 'MeteoFilled', vname{v}));
sub_dbase = fullfile(wks_in, 'MeteoDbase', vname{v});

% 拷贝可执行文件（仅当 exedir 非空）
if ~isempty(exedir)
    safe_copy(fullfile(exedir, 'splina.exe'), sub_tmp_var);
    safe_copy(fullfile(exedir, 'splinb.exe'), sub_tmp_var);
    safe_copy(fullfile(exedir, 'selnot.exe'), sub_tmp_var);
    safe_copy(fullfile(exedir, 'lapgrd.exe'), sub_tmp_var);
end
% DEM 一定要拷
safe_copy(fdem, sub_tmp_var);

% 降水按和，其它按均值
if strcmp(vname{v},'PRCP'), mean_or_sum = 0; else, mean_or_sum = 1; end

% 切换到 wks
cd(wks);

%% =============== 主循环 ===============
for yr = yr2:-1:yr1
    % 清理上轮年度的变量，避免“遗留命中 exist('filled_data','var')”
    clear filled_data averaged_data qc sta nf q sd

    [days, dy2, ~] = daily2timestep(yr, time_step);

    file_filled = fullfile(wks_in, 'MeteoFilled', vname{v}, sprintf('%s_%d_Filled.csv', vname{v}, yr));
    file_raw    = fullfile(sub_dbase, sprintf('%s_%d.csv', vname{v}, yr));

    if exist(file_raw, 'file')
        % 原始读入
        if endsWith(lower(file_raw), '.txt')
            [id_db, xd_db, ~] = readDbase(file_raw, days+3);
        else
            dat = readcell(file_raw);
            % dat(isnan(dat)) = 32767;
            % dat(dat < -900) = 32767;
            id_db = cell2mat(dat(:,1));
            xd_db = cell2mat(dat(:,2:end));
        end

        % 判定前两列是经纬还是投影
        xd_up  = max(xd_db(:,1:2));
        xd_low = min(xd_db(:,1:2));
        haveLatLon = false;
        if abs(xd_up(1)) <= 1000 && abs(xd_low(2)) < 1000
            % (lon, lat)
            if xd_up(2) > 90
                lon = xd_db(:,2); lat = xd_db(:,1);
            else
                lon = xd_db(:,1); lat = xd_db(:,2);
            end
            [x0, y0] = projfwd(proj, lat, lon);
            haveLatLon = true;
        else
            % 已是投影坐标
            x0 = xd_db(:,1); y0 = xd_db(:,2);
        end

        % 地理范围筛选
        mask = (x0 >= range_x(1) & x0 <= range_x(2) & ...
                y0 >= range_y(2) & y0 <= range_y(1));

        xd = xd_db(mask, :);
        id = id_db(mask, :);

        % 对齐后的坐标/经纬度
        x0m = x0(mask);
        y0m = y0(mask);
        if haveLatLon
            latm = lat(mask);
            lonm = lon(mask);
        else
            latm = nan(size(x0m));
            lonm = nan(size(y0m));
        end

        elv = xd(:,3);
        dat = xd(:,4:end);

        % 组合坐标（与筛选后数据对齐）
        s0 = [x0m, y0m, elv];

        % 重合点合并（使用筛选后的 id/s0/dat）
        [sid_all, gxy_all, sdat_all] = LookCoincident(id, s0, dat);

        % 过滤出有效站（缺测<20%）
        [n_all, m_all] = size(sdat_all);
        j = 1; data = []; geo = []; gid = [];
        for i = 1:n_all
            row = sdat_all(i,:);
            row(row >= 999999 | isnan(row)) = 32766;
            inRange = (row >= vad_value(v,1) & row <= vad_value(v,2));
            if sum(inRange)/m_all >= 0.8
                data(j,:) = row;           %#ok<AGROW>
                geo(j,:)  = gxy_all(i,:);  %#ok<AGROW>
                gid(j,:)  = sid_all(i,:);  %#ok<AGROW>
                j = j + 1;
            end
        end

        [n, m] = size(data);
        if n > 100
            % 越界值置 32766（原逻辑）
            data(data < vad_value(v,1) | data > vad_value(v,2)) = 32766;

            % 填补缺测
            [filled_data, qc, sta, nf] = fillmissing(data, gid, geo); %#ok<ASGLU>

            % 写 Filled CSV
            ftxt = file_filled;
            headerline = {'SID','Year','LATI','LONG','Elva'};
            for ii = 1:m
                headerline{ii+5} = ['D' num2str(ii, '%03d')]; %#ok<AGROW>
            end

            fop = fopen(ftxt, 'w');
            % 标题
            fprintf(fop, '%s', headerline{1});
            for ii = 2:numel(headerline)
                fprintf(fop, ',%s', headerline{ii});
            end
            % 逐行写数
            for ii = 1:n
                lati = get_or_nan(latm, ii);
                loni = get_or_nan(lonm, ii);
                % fprintf(fop, '\n%d,%s,%.6f,%.6f,%.2f', char(gid(ii,:)), yr, lati, loni, geo(ii,3));
                fprintf(fop,'\n%s,%d,%.6f,%.6f,%.2f',char(gid(ii,:)),yr, lati, loni, geo(ii,3));
                for jj = 1:m
                    fprintf(fop, ',%.3f', filled_data(ii,jj));
                end
            end
            fclose(fop);

            % 年尺度统计日志
            if mean_or_sum == 0
                annual_filled_value = sum(filled_data,2) * 0.1;
            else
                annual_filled_value = mean(filled_data,2) * 0.1;
            end
            annual_raw_value = nan(n,1);
            for ii = 1:n
                xi = data(ii,:);
                x1 = xi(xi > -900 & xi < 9000);
                if numel(x1)/m >= 0.95
                    if mean_or_sum == 0
                        annual_raw_value(ii,1) = sum(x1) * 0.1;
                    else
                        annual_raw_value(ii,1) = mean(x1) * 0.1;
                    end
                else
                    annual_raw_value(ii,1) = -9999;
                end
            end
            annual_value = [yr mean(annual_filled_value) std(annual_filled_value) ...
                            mean(annual_raw_value) std(annual_raw_value) ...
                            length(annual_raw_value) length(annual_filled_value)];
            fprintf('STAT  %s  %4d  mean=%.2f  std=%.2f\n', vname{v}, yr, annual_value(2), annual_value(3));
        end
    end

    % ========== 聚合到 time_step（调用 meanbyxdays 前对齐列数） ==========
    if exist('filled_data', 'var')
        mData = size(filled_data, 2);
        mDn   = numel(dy2);
        mUse  = min(mData, mDn);
        if mUse < mData
            warning('Data has %d cols but dy2 has %d; truncating data to %d.', mData, mDn, mUse);
        elseif mUse < mDn
            warning('dy2 has %d entries but data has %d; truncating dy2 to %d.', mDn, mData, mUse);
        end
        filled_data_use = filled_data(:, 1:mUse);
        dy2_use         = dy2(1:mUse);

        [averaged_data, q, sd] = meanbyxdays(filled_data_use, gid, dy2_use, mean_or_sum, 1); %#ok<ASGLU>
        averaged_data = averaged_data';  % 转成 [stations x groups]

        [n_out, j_out] = size(averaged_data); %#ok<ASGLU>

        % 写入 Anusplin 格式
        csv2Anuspl(yr, vname{v}, wks_out, char(gid), geo, averaged_data);

        % 写批处理
        if nots == 1
            makesplinotbat(yr, direct, size(averaged_data), vname{v}, fdem, fhdr);
        else
            makesplinabat(yr, direct, size(averaged_data), vname{v}, fdem, fhdr);
        end

        fprintf('DONE  %s  %4d  n=%d  groups=%d  t=%.2fs\n', vname{v}, yr, n_out, j_out-1, toc(t_all));
    else
        fprintf('SKIP  %s  %4d  no filled_data\n', vname{v}, yr);
    end
end

end % === function Sites2Grid ===


%% ==================== 工具函数 ====================
function ensure_dir(p)
    if ~isfolder(p), mkdir(p); end
end

function safe_copy(src, dst_folder)
    if ~isfolder(dst_folder), mkdir(dst_folder); end
    if ~exist(src, 'file')
        warning('File not found: %s (skip copy)', src);
        return;
    end
    [status,msg] = copyfile(src, dst_folder);
    if ~status
        error('copyfile failed: %s -> %s (%s)', src, dst_folder, msg);
    end
end

function out = absolute_dir(root, maybeRel)
    if isfolder(maybeRel)
        out = char(java.io.File(maybeRel).getCanonicalPath());
        return;
    end
    if startsWith(maybeRel, filesep) || (ispc && ~isempty(regexp(maybeRel,'^[A-Za-z]:\\','once')))
        out = maybeRel;
    else
        out = fullfile(root, strip_leading_sep(maybeRel));
    end
    if ~isfolder(out), mkdir(out); end
end

function s = strip_leading_sep(p)
    if isempty(p), s = p; return; end
    if p(1) == '/' || p(1) == '\', s = p(2:end); else, s = p; end
end

function v = get_or_nan(arr, idx)
    if isempty(arr) || idx > numel(arr) || (numel(arr) >= idx && isnan(arr(idx)))
        v = NaN;
    else
        v = arr(idx);
    end
end
























