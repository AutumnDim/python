% if matlabpool('size') <= 0  % determine whether par started
%     matlabpool('open', 'local',7)
% else
%     disp('Already initialized');
% end
% vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
%%   Steps to accomplish MeteoGrid
% step one ReadCIMISS_w1.m
% step two TAVG.m
% step three MergeGhcndCIMSSX.m
% step four Run_Sites2Grid.m
% step five Disp_MeteoGrid(v, wks, fmask, fhdr,yr1, yr2,nday)
% case 6: valid_check_station
% case 7: ReadGHCND: run
% run ('H:\Workspace\MeteoGrid\Function_set\readghcnmetX.m');
% case 8: move defined files to another folder
% case 9: count file's number for each variable in each year
% case 10: rename 1:1:46 to 1:8:361
% case 11: amt
%%
%         switch time_step
%             case 1   % Annually
%                 dy2 = dy1;
%             case 8
%                 dy2 = fix((dy1 - 1) / 8) * 8 + 1;
%             case 10  % 10-day
%                 mon = month(datenum(yr,1,1) + dy1 - 1);
%                 dy  = day(datenum(yr,1,1) + dy1 - 1);
%                 mj  = dy;
%                 mj(dy <= 10) = 1; mj(dy > 10 & dy <= 20) = 2; mj(dy > 20) = 3;
%                 dy2 = (mon - 1) * 3 + mj;
%             case 12  % Monthly
%                 dy2 = month(datenum(yr,1,1) + dy1 - 1);
%             case 24  % Half-monthly
%                 mon = month(datenum(yr,1,1) + dy1 - 1);
%                 dy  = day(datenum(yr,1,1) + dy1 - 1);
%                 mj  = dy;
%                 mj(dy <= 15) = 1; mj(dy > 15) = 2;
%                 dy2 = (mon - 1) * 2 + mj;
%         end

close all; clear all; clc;
process = 4;
vname = { 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
nv = length(vname);
switch process
    case 0
        % run('H:\Workspace\MeteoGrid\Function_set\readghcnmetX.m');
        run('E:\MeteoGrid\Function_set\GHCND_CSV2Daily.m');
    case 1
        ReadCIMISS_w1;
    case 2
        yr1= 1980; yr2 = 1980;
        TAVG(yr1, yr2);
    case 3
        yr1= 2018; yr2 = 2018;
        wks_ghcnd = 'E:\MeteoGrid\ghcnd';
        wks_cimiss = 'E:\MeteoGrid\CIMISS_table';
        wks_meteobase = 'E:\MeteoGrid\MeteoDbase';
        for v = 1 : 7
            disp(vname{v});
            MergeGhcndCIMSSX(yr1, yr2, wks_ghcnd, [wks_cimiss '\' vname{v}], wks_meteobase, v);
        end
    case 4
        %% Run_Sites2Grid
        if contains(computer(),'PCWIN64')
            % fset = 'China8km10d.set';
            % fset = 'Benxi.set';
            fset = 'China1km.set';
            % fset = 'China8km15d.set';
            wks = pwd;
            % addpath('H:\Workspace\MeteoGrid\Function_set');  % 根据实际路径修改
            % addpath('D:\QX\Code\functionset');
            % addpath(pwd);  % 添加当前目录
            %fset = 'taihu.set';
            %fset = 'China1km.set';
            % v = [1, 2, 3, 4, 5, 6, 7];
            % v = [1, 2];
            %             nv = length(v);
            %             yr1 = 2016;
            %             yr2 = 2018;
            %             n = (yr2 - yr1 + 1) * nv;
            %             xv = []; i = 1;
            %             for k = 1 : nv
            %                 for yr = yr1 : yr2
            %                     xv(i,:) = [v(k), yr];
            %                     i = i + 1;
            %                 end
            %             end
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
                % 显示配置信息
                disp('=== 配置信息 ===');
                disp(['年份范围: ' num2str(yr1) ' - ' num2str(yr2)]);
                disp(['输入目录: ' wks_in]);
                disp(['输出目录: ' wks_out]);
                disp(['临时目录: ' wks_tmp]);
                disp(['网格目录: ' wks_grd]);
                disp('================');
            else
                disp('Error: Not find site information file');
                return;
            end
            for v = 4 : -1 :  1
                current_var = vname{v};
                fprintf('\n=== 开始处理变量 %s (索引 %d) ===\n', current_var, v);
                sub  = [wks_tmp '\' vname{v}];
                if ~exist(sub,'dir')
                    system(['mkdir ' sub]);
                else
                    % delete([wks_tmp '\' vname{v} '\*.*']);
                end
                
                sub  = [wks_grd '\' vname{v}];
                if ~exist(sub,'dir')
                    system(['mkdir ' sub]);
                else
                    % delete([wks_grd '\' vname{v} '\*.*'])
                end
                % fset
                % v
                % nots: 1 Write selnot.cmd file; 0 not use setnot function
                % time_step: 1 for annually, 8 for week, 10 for 10-day, 30 for monthly
                %      and 15 for bi-weekly
                cd(wks);
                Sites2Grid(wks, fset, v, 1, 8);
                % Sites2Kriging(fset, v, 0, 10);
            end
        elseif contains(computer(),'MACI64')
            % fset = 'China8km10d.set';
            % fset = 'Benxi.set';
            fset = 'China1km_mac.set';
            % fset = 'China8km15d.set';
            wks = pwd;
            %fset = 'taihu.set';
            %fset = 'China1km.set';
            % v = [1, 2, 3, 4, 5, 6, 7];
            % v = [1, 2];
            %             nv = length(v);
            %             yr1 = 2016;
            %             yr2 = 2018;
            %             n = (yr2 - yr1 + 1) * nv;
            %             xv = []; i = 1;
            %             for k = 1 : nv
            %                 for yr = yr1 : yr2
            %                     xv(i,:) = [v(k), yr];
            %                     i = i + 1;
            %                 end
            %             end
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
            for v = 6 : -1 :  1
                sub  = [wks_tmp '/' vname{v}];
                if ~exist(sub,'dir')
                    system(['mkdir ' sub]);
                else
                    delete([wks_tmp '/' vname{v} '/*.*']);
                end
                
                sub  = [wks_grd '/' vname{v}];
                if ~exist(sub,'dir')
                    system(['mkdir ' sub]);
                else
                    delete([wks_grd '/' vname{v} '/*.*'])
                end
                % fset
                % v
                % nots: 1 Write selnot.cmd file; 0 not use setnot function
                % time_step: 1 for annually, 8 for week, 10 for 10-day, 30 for monthly
                %      and 15 for bi-weekly
                cd(wks);
                Sites2Grid(wks, fset, v, 1, 8);
                % Sites2Kriging(fset, v, 0, 10);
            end
        else
            fset = 'Sanjy_unix.set';
            parfor v = 1 : 6
                Sites2Kriging(fset, v, 0, 10);
            end
        end
    case 5
        nlyr = 24;
        vnm = 'WIN';
        wks = '\\BA-37AEDE\Workspace\China8km\AsiaMeteo\temp';
        yr = 2015;
        valid_check_station(vnm, wks, yr, nlyr);
    case 6
        vname = {'PRCP'; 'TMIN'; 'TMAX'; 'TAVG'; 'RHU'; 'SSD';  'WIN'};
        v = 6;
        wks1 = '\\BA-37AEDE\Workspace\China8km\MetGrid15Days';
        wks2 = '\\BA-37AEDE\Workspace\China8km\MeteoGrid';
        fmask = '\\BA-37AEDE\Workspace\China8km\Parameters\Climate_4R.tif';
        fhdr = '\\BA-37AEDE\Workspace\China8km\Parameters\asia_dem_8km.hdr';
        num01 = 100; num02 = 100;
        yr1 = 1998;yr2 = 1998;
        nday = 24;
        % Disp_MeteoGrid(v, wks, fmask, fhdr,yr1, yr2,nday);
        for v = 4 : 4 % length(vname)
            disp(['Comparing MeteoGrid ' vname{v} '...']);
            Compare_MeteoGrid(v, wks1, wks2, num01, num02, fmask, fhdr,yr1, yr2,nday);
        end
    case 7
        fset = 'taihu.set';
        Clear_outputs = 0;
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
            % case 7: ReadGHCND: run
            run('readghcnmetX.m');
        else
            disp('Error: Not find site information file');
            return;
        end
        [r,s] = system('wmic LogicalDisk where "Caption=''E:''" get FreeSpace,Size /value');
        s1 = strfind(s,'=');
        FreeSpace = str2double(s(s1(1)+1:s1(2)-7))/1024/1024/1024;
        [hd,vr] = textread(fhdr, '%s%s');
        npix = str2double(vr{1});
        nlin = str2double(vr{2});
        
        vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN';'PRCP'};
        ny = yr2 - yr1 + 1;
        vn = ny * 6;
        NeedSpace = npix * nlin * 4 * vn * 46/1024/1024/1024 * 1.1;
        if FreeSpace < NeedSpace
            fprintf('FreeSpace (%.2f Gb) < NeedSpace (%.2f Gb), exiting!\n', FreeSpace, NeedSpace);
            return;
        end
        if Clear_outputs == 1
            ss = {'SUR','OPT','LIS','COV','RES','LOG'};
            for v = 1 : 6
                sdel = ['del /Q ' wks_grd vname{v} '\*.*'];
                disp(sdel);
                [s,r] = dos(sdel);
                % smkdir = ['mkdir H:\Database\qinghai\MeteoGrid\'  vname{v}];
                % disp(smkdir);
                % [s,r] = dos(smkdir);
                for j = 1 : 6
                    sdel = ['del /Q ' wks_tmp '\' vname{v} '\*.' ss{j}];
                    disp(sdel);
                    [s,r] = dos(sdel);
                end
            end
        end
        v = 1 : 6; yr = yr1 : yr2;
        [x,y] = meshgrid(v, yr);
        vy = [reshape(x, vn, 1), reshape(y, vn, 1)];
        
        for v = 1 : 2
            disp([vname{v}, ' ', num2str(v)]);
            if Clear_outputs == 1
                [r,s] = system('wmic LogicalDisk where "Caption=''E:''" get FreeSpace,Size /value');
                s1 = strfind(s,'=');
                FreeSpace = str2double(s(s1(1)+1:s1(2)-7))/1024/1024/1024;
                if FreeSpace < 5
                    fprintf('磁盘空间(%.2f Gb)不足5.0Gb, 暂时停止执行，按下任意键继续!\n', FreeSpace);
                    pause;
                end
            end
            % change to vname{v} sub and run vname{v}_spl.bat
            parfor yr = yr1 : yr2
                cd([wks_tmp '\' vname{v}]);
                dos([vname{v} '_' num2str(yr) '_spl.bat']);
            end
            smove = ['move ' wks_grd vname{v} '\*.flt H:\Database\qinghai\MeteoGrid\'  vname{v} '\'];
            dos(smove);
            smove = ['move ' wks_grd vname{v} '\*.hdr H:\Database\qinghai\MeteoGrid\'  vname{v} '\'];
            dos(smove);
        end
    case 8   % move defined files
        vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
        % move files1 : 
        for v = length(vname)
            [s1,s2] = system(['move H:\temp\Sjy10\MeteoGrid\' vname{v} '\' vname{v} '_2010*.* H:\temp\Sjy18\MeteoGrid\' vname{v} '\']);
            [s1,s2] = system(['move H:\temp\Sjy10\MeteoGrid\' vname{v} '\' vname{v} '_2011*.* H:\temp\Sjy18\MeteoGrid\' vname{v} '\']);
        end
    case 9  % check files existed in each year
        vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
        % move files
        num = [];
        for v = 1 : length(vname)
            j = 1;
            for yr = 2010:2018
                ff = ['H:\Database\qinghai\MeteoGrid\' vname{v} '\' vname{v} '_' num2str(yr) '*.flt'];
                ss = dir(ff);
                sn = length(ss);
                num(j,v) = sn;
                j = j + 1;
            end
        end
    case 10  % Rename 1:1:46 to 1:8:361
        vname = { 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
        % Rename 1:1:46 to 1:8:361
        num = [];
        for v = 1 : length(vname)
            j = 1;
            for yr = 2010:2018
                for i = 46 : -1 : 2
                    dy = (i - 1) * 8 + 1;
                    f1 = ['H:\temp\Sjy18\MeteoGrid\' vname{v} '\' vname{v} '_A' num2str(yr * 1000 +  i) '.hdr'];
                    f2 = [vname{v} '_A' num2str(yr * 1000 + dy) '.hdr'];
                    if exist(f1, 'file')
                        ss = ['rename ' f1 ' ' f2];
                        [s1,s2] = system(ss);
                        disp(ss);
                        num(j,v+2) = 1;
                    else
                        
                        
                        num(j,v+2) = 0;
                    end
                    num(j,1:2) = [yr, i];
                    j = j + 1;
                end
            end
        end
    case  11
        %% 
        % vname = {'PRCP','TMAX','TMIN','SSD','RHU','WIN','TAVG','SWRad'};
        % Sanjy 250m 8days
        fmask = 'E:\Sanjy250m\Parameters\SJYWuCover_2010_250m.tif';
        fset = 'H:\MeteoGrid\Function_set\Sanjy.set';
        % fset = 'E:\MeteoGrid\Function_set\China1km.set';
        % fmask = 'H:\Workspace\China1km\Parameters\chinaregion9.tif';
        % fset = 'E:\MeteoGrid\Function_set\Benxi.set';
        %% China8km10days
        % fmask = 'H:\Workspace\China8km10day\Parameters\chinaregion9_8km.tif';
        % fset = 'E:\MeteoGrid\Function_set\China8km.set';
        cd('F:\MeteoGrid\Function_set');
        name_1_46 = 0; % name_1_46 = 1;  % 0 for name_1_8:361
        time_step = 8;
        for v = 6:6
            amt8km(fset, fmask, name_1_46, time_step, v)
        end
    case 12
        % spatial analysis to calculate Q10 and WUE
        run('H:\Workspace\China8km\CEVSA\dynmd\Spatial_AllModelsDaily.m');
        run('H:\Workspace\China8km\CEVSA\dynmd\compare_modelsdata.m');
        run('H:\Workspace\China8km\CEVSA\dynmd\Q10_ANALYSIS.m');
        
        % Q10 on sites
        run('H:\Workspace\OneDrive\Manuscriptions\20160401_Acclimation\Luoyiqi_Q10_2006.m');
        
    case 13
        % Sites analysis
        run('H:\Workspace\China8km\CEVSA\dynmd\PRCP_Growth_Lag.m');
        run('H:\Workspace\China8km\mat\Regional_Trend_Sensitive_Tables_NRS.m');
        
    case 14
        % Read netCDF file
        run('H:\Workspace\Global8km\Arctic_h52bin.m');
    case 15
        % Inputs: day_of_year,ab,sunlit, latitude, elev, slope, aspect
        % Outpus: TS_rad BS_rad DS_rad
        run('E:\workspace\ssdtorad\SSD2RADnew.m');
    case 16
        st_cn = load('F:\MeteoGrid\National\Sta2411.txt');
        [dat, txt, ~] = xlsread('F:\MeteoGrid\GHCN\ghcnd-stations.xlsx');
        js = find(dat(:, 2) >= 50 & dat(:,2) <= 160 & dat(:, 1) >= -10 & dat(:, 1) <= 65);
        geo_gh = dat(js, 1:3);
        st_gh = txt(js, 1);
        sid_gh = [];
        for i = 1 : length(js)
            sid_gh(i,1) = str2double(st_gh{i}(4:end));
        end
        
        % plot(geo_gh(:, 2), geo_gh(:, 1), 'b.', st_cn(:, 3), st_cn(:, 2), 'r.');
        yr2 = 1979;
        yr1 = 1951;
        time_step = 8;
        for v = 2 : 7
            for yr = yr2:-1:yr1
                transfer_txt2csv(v, yr, st_cn, sid_gh, geo_gh)
            end
        end
        
    case 17
        [sub_name, sub_sta] = textread('F:\MeteoGrid\青海省\台站编号.txt', '%s%s');
        wks = 'F:\MeteoGrid\MeteoFilled';
        owk = 'F:\MeteoGrid\青海省';
        yr2 = 1979;
        yr1 = 1951;
        vs = 1:7;

        subset_dbase(yr1, yr2, sub_name, sub_sta, vs, wks, owk);
end
disp(datestr(now));

% if matlabpool('size') > 0  % determine whether par started
%     matlabpool close force local;
% end

disp('That''s all, go home!');