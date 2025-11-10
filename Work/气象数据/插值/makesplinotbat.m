% function makesplinotbat(yr, direct, data_size, varname, fdem, fhdr)
% % close all
% % clear all
% % clc
% % disp('MAKESPLINABAT: Produce Anusplin bat file');
% % tic
% % include files:
% % 1.Splin.bat: splina < file.cmd > spl.log
% %              lapgrd < filegrd.cmd > grd.log
% % 2. file.cmd
% % 3. filegrid.cmd
% %
% % ff = 'D:\China8km\CCTEC\Data\Observed\Storage\VGC.txt';
% % m = length(ff);
% % varname = ff(m-6:m-4);
% % yr = 9999;
% % [id x y z data] = textread(ff, '%s%f%f%f%f');
% % n = length(id);
% % gid = id;
% % geo = [x y z];
% % sta = id;
% % Write file for Anusplin software
% % disp(['      CSV2ANUSPL: Output Anusplin file: ' varname ' in ' num2str(yr)]);
% % outway = 'D:\temp\Meteo10day';
% % if ~exist(outway, 'dir')
% %     system(['mkdir ' outway]);
% % end                
% % csv2Anuspl(yr, varname, outway,gid,geo, data, -1);
% % [dn dm] = size(data);
% dn = data_size(1);
% dm = data_size(2);
% 
% fdatway = direct{1,1}{1};
% fcmdway = direct{1,1}{2};
% fgrdway = direct{1,1}{3};
% dfm = 'a12,2f20.5,f20.3,12f12.3';   %%'%12s%20.5f%20.5f%20.3f'%12.3f'
% % fdem = 'asiadem8km.txt';
% % fhdr = 'J:\temp\Storage\SOC\asiadem8km.hdr';
% if ~exist(fhdr, 'file')
%     disp(['Cannot find file: ' fhdr]);
%     return;
% end
% fd = fopen(fhdr, 'r');
% [res tmp] = textscan(fd, '%s%f');
% fclose(fd);
% pix = res{1,2}(1);
% line = res{1,2}(2);
% xlr = res{1,2}(3);
% ylr = res{1,2}(4);
% siz = res{1,2}(5);
% xul = xlr + siz * pix;
% yul = ylr + siz * line;
% 
% % meteosplin.bat file:
% % disp(['MAKESPLINABAT data directory: ' fdatway]);
% % disp(['MAKESPLINABAT cmd directory: ' fcdmway]);
% % disp(['MAKESPLINABAT grid directory: ' fgrdway]);
% % ny = length(yr);
% % if ny > 1
% %     yr1 = yr(1);    yr2 = yr(2);
% % else
% %     yr1 = yr;       yr2 = yr;
% % end
% ftpway = fcmdway;
% if ~exist(ftpway,'dir')
%     system(['mkdir ' ftpway]);
% end
% 
% sub = [ftpway '\' varname];
% if ~exist(sub,'dir')
%     system(['mkdir ' sub]);
% end
% batf = [sub '\' varname  '_' num2str(yr) '_spl.bat'];
% batp = fopen(batf, 'a');
% if batp < 0
%     disp(['MAKESPLINABAT: Cannot creat BAT file: "' batf '"']);
%     return;
% end
% 
% im = fix(dm/12);
% if im > 1 && dn >= 1000
%     for j = 1 : im+1
%         if j <= im
%             d1 = (j - 1) * 12 + 1;
%             d2 = j * 12;
%         else
%             d1 = im * 12 + 1;
%             d2 = dm;
%         end            
%           % 2. spline.cmd file
%             scmf = sprintf('%s\\%s_%d%03d_spl.cmd',sub, varname, yr,j);
%             gcmf = sprintf('%s\\%s_%d%03d_grd.cmd',sub, varname, yr,j);
%             ncmf = sprintf('%s\\%s_%d%03d_snt.cmd',sub, varname, yr,j);
% 
%             ncmp = fopen(ncmf, 'w');
%             if ncmp < 0
%                 disp(['MAKESPLINABAT: Cannot creat SELNOT FILE: "' ncmf '"']);
%                 return;
%             end
% 
%             scmp = fopen(scmf, 'w');
%             if scmp < 0
%                 disp(['MAKESPLINABAT: Cannot creat SCMD FILE: "' scmf '"']);
%                 return;
%             end
%             gcmp = fopen(gcmf, 'w');
%             if gcmp < 0
%                 disp(['MAKESPLINABAT: Cannot creat GCMD FILE: "' gcmf '"']);
%                 return;
%             end
% 
%             % change directory to DOS formation
%             datf = sprintf('%s\\%s\\%s_%d%03d.txt', fdatway, varname, varname, yr,j);
%             ncmf = sprintf('%s\\%s\\%s_%d%03d_snt.cmd', fcmdway, varname, varname, yr,j);
%             scmf = sprintf('%s\\%s\\%s_%d%03d_spl.cmd', fcmdway, varname, varname, yr,j);
%             gcmf = sprintf('%s\\%s\\%s_%d%03d_grd.cmd', fcmdway, varname, varname, yr,j);
%             resf = sprintf('%s\\%s\\%s_%d%03d.res', fcmdway, varname, varname, yr,j);
% 
%             % Write (1) bat file
%             fprintf(batp,'rem Splin: %s\n', datf);
%             fprintf(batp,'selnot < %s > %s_%d%03d_setnot.log\n',   ncmf, varname, yr,j);
%             fprintf(batp,'splinb < %s > %s_%d%03d_splinb.log\n',   scmf, varname, yr,j);
%             fprintf(batp,'lapgrd < %s > %s_%d%03d_lapgrd.log\n\n', gcmf, varname, yr,j);
% 
%             % Write (2) scmf
%             temp = sprintf('%s%s\\%s_%d%03d',    fdatway, varname, varname, yr,j);
%             fprintf(scmp,'%s\n',temp);
%             fprintf(scmp,'5\n2\n1\n0\n0\n%f %f 0 1\n%.4f %.3f 0 1\n', xlr-100*siz, xul+100*siz, ylr-100*siz, yul+100*siz);
% 
%             if(j>im)
%                 fprintf(scmp,'0 9000.00 0 1\n0\n2\n%d\n0\n1\n1\n', mod(dm,12));
%             else
%                 fprintf(scmp,'0 9000.00 0 1\n0\n2\n12\n0\n1\n1\n');
%             end
% 
%             fprintf(scmp,'%s\n',datf);
% 
%             % a6,2f20.5,f12.3,12f12.3
%             if j <= im
%                 dfm(18:19) = '12';
%             else
%                 dfm(18:19) = num2str(mod(dm,12));
%             end           
% 
%             fprintf(scmp,'5200\n%d\n(%s)\n',str2num(dfm(2:3)), dfm);
% 
% 
%             n = length(resf);m=n-2;
%             resf(m:n) = 'not';
%             fprintf(scmp,'%s\n4000\n',resf);
% 
%             resf(m:n) = 'res';
%             fprintf(scmp,'%s\n',resf);
% 
%             resf(m:n) = 'opt';
%             fprintf(scmp,'%s\n',resf);
% 
%             resf(m:n) = 'sur';
%             fprintf(scmp,'%s\n',resf);
% 
%             resf(m:n) = 'lis';
%             fprintf(scmp,'%s\n\n\n\n\n',resf);
% 
%             resf(m:n) = 'sur';
%             fprintf(gcmp,'%s\n',resf);
%             fprintf(gcmp,'0\n1\n\n1\n');
%             fprintf(gcmp,'1\n%f %f %f\n', xlr, xul, siz);
%             fprintf(gcmp,'2\n%f %f %f\n', ylr, yul, siz);
%             fprintf(gcmp,'0\n2\n');
%             fprintf(gcmp,'%s\n2\n-9999\n', fdem);
% 
%             for d=d1:d2
%                 grdf = sprintf('%s\\%s\\%s_%d.flt', fgrdway, varname, varname, yr * 1000 + d);
%                 fprintf(gcmp,'%s\n',grdf);
%             end
%             fprintf(gcmp,'\n\n\n\n');
% 
%             fclose(scmp);
%             fclose(gcmp);
% 
%             % Write selnot.cmd file
%             fprintf(ncmp,'2\n1\n0\n0\n%f %f 0 1\n%f %f 0 1\n', xlr-100*siz, xul+100*siz, ylr-100*siz, yul+100*siz);
%             fprintf(ncmp,'0 9000 0 1\n0\n1\n0\n');
%             fprintf(ncmp,'%s\n',datf);
%             fprintf(ncmp,'5200\n12\n');
%             fprintf(ncmp,'(%s)\n', dfm);
% 
%             resf(m:n) = 'not';
%             fprintf(ncmp,'%s\n',resf);
% 
%             resf(m:n) = 'rej';
%             fprintf(ncmp,'%s\n',resf);
%             fprintf(ncmp,'1000');
%             fclose(ncmp);    
%     end % FOR loop of 1~4 files
% end
% if im > 1 && dn < 1000
%     for j = 1 : im+1
%         if j <= im
%             d1 = (j - 1) * 12 + 1;
%             d2 = j * 12;
%         else
%             d1 = im * 12 + 1;
%             d2 = dm;
%         end            
%        % 2. spline.cmd file
%         scmf = sprintf('%s\\%s_%d%03d_spl.cmd',sub, varname, yr,j);
%         gcmf = sprintf('%s\\%s_%d%03d_grd.cmd',sub, varname, yr,j);
% 
%         scmp = fopen(scmf, 'w');
%         if scmp < 0
%             disp(['MAKESPLINABAT: Cannot creat SCMD FILE: "' scmf '"']);
%             return;
%         end
%         gcmp = fopen(gcmf, 'w');
%         if gcmp < 0
%             disp(['MAKESPLINABAT: Cannot creat GCMD FILE: "' gcmf '"']);
%             return;
%         end
% 
%         % change directory to DOS formation
%         datf = sprintf('%s\\%s\\%s_%d%03d.txt', fdatway, varname, varname, yr,j);
%         scmf = sprintf('%s\\%s\\%s_%d%03d_spl.cmd', fcmdway, varname, varname, yr,j);
%         gcmf = sprintf('%s\\%s\\%s_%d%03d_grd.cmd', fcmdway, varname, varname, yr,j);
%         resf = sprintf('%s\\%s\\%s_%d%03d.res', fcmdway, varname, varname, yr,j);
% 
%         % Write (1) bat file
%         fprintf(batp,'rem Splin: %s\n', datf);
%         fprintf(batp,'splina < %s > %s_%d%03d_splina.log\n',   scmf, varname, yr,j);
%         fprintf(batp,'lapgrd < %s > %s_%d%03d_lapgrd.log\n\n', gcmf, varname, yr,j);
% 
%         % Write (2) scmf
%         temp = sprintf('%s\\%s\\%s_%d%03d',    fdatway, varname, varname, yr,j);
%         fprintf(scmp,'%s\n',temp);
%         fprintf(scmp,'5\n2\n1\n0\n0\n%f %f 0 1\n%f %f 0 1\n', xlr-100*siz, xul+100*siz, ylr-100*siz, yul+100*siz);
% 
%         if(j==4)
%             fprintf(scmp,'0 5000 1 1\n1000.0\n0\n2\n10\n0\n1\n1\n');
%         else
%             fprintf(scmp,'0 5000 1 1\n1000.0\n0\n2\n12\n0\n1\n1\n');
%         end
% 
%         fprintf(scmp,'%s\n',datf);
% 
%         % a6,2f20.5,f12.3,12f12.3
%         if j <= im
%             dfm(18:19) = '12';
%         else
%             dfm(18:19) = num2str(mod(dm,12));
%         end           
% 
%         fprintf(scmp,'30000\n%d\n(%s)\n',str2num(dfm(2:3)), dfm);
% 
% 
%         n = length(resf);m=n-2;
%         fprintf(scmp,'%s\n',resf);
% 
%         resf(m:n) = 'opt';
%         fprintf(scmp,'%s\n',resf);
% 
%         resf(m:n) = 'sur';
%         fprintf(scmp,'%s\n',resf);
% 
%         resf(m:n) = 'lis';
%         fprintf(scmp,'%s\n',resf);
% 
%         resf(m:n) = 'cov';
%         fprintf(scmp,'%s\n\n\n\n\n',resf);
% 
%         resf(m:n) = 'sur';
%         fprintf(gcmp,'%s\n',resf);
%         fprintf(gcmp,'0\n1\n\n1\n');
%         fprintf(gcmp,'1\n%f %f %f\n', xlr, xul, siz);
%         fprintf(gcmp,'2\n%f %f %f\n', ylr, yul, siz);
%         fprintf(gcmp,'0\n2\n');
%         fprintf(gcmp,'%s\n2\n-9999\n', fdem);
% 
%         for d=d1:d2
%             grdf = sprintf('%s%s\\%s_%d.flt', fgrdway, varname, varname, yr * 1000 + d);
%             fprintf(gcmp,'%s\n',grdf);
%         end
%         fprintf(gcmp,'\n\n\n\n');
% 
%         fclose(scmp);
%         fclose(gcmp);
%     end % FOR loop of 1~4 files
% end
% if dm == 1
%     dy = data_size(3);
%    % 2. spline.cmd file
%     scmf = sprintf('%s\\%s_%d%03d_spl.cmd',sub, varname, yr,dy);
%     gcmf = sprintf('%s\\%s_%d%03d_grd.cmd',sub, varname, yr,dy);
% 
%     scmp = fopen(scmf, 'w');
%     if scmp < 0
%         disp(['MAKESPLINABAT: Cannot creat SCMD FILE: "' scmf '"']);
%         return;
%     end
%     gcmp = fopen(gcmf, 'w');
%     if gcmp < 0
%         disp(['MAKESPLINABAT: Cannot creat GCMD FILE: "' gcmf '"']);
%         return;
%     end
% 
%     % change directory to DOS formation
%     datf = sprintf('%s\\%s\\%s_%d%03d.txt', fdatway, varname, varname, yr,dy);
%     scmf = sprintf('%s\\%s\\%s_%d%03d_spl.cmd', fcmdway, varname, varname, yr,dy);
%     gcmf = sprintf('%s\\%s\\%s_%d%03d_grd.cmd', fcmdway, varname, varname, yr,dy);
%     resf = sprintf('%s\\%s\\%s_%d%03d.res', fcmdway, varname, varname, yr,dy);
% 
%     % Write (1) bat file
%     fprintf(batp,'rem Splin: %s\n', datf);
%     fprintf(batp,'splina < %s > %s_%d%03d_splina.log\n',   scmf, varname, yr,dy);
%     fprintf(batp,'lapgrd < %s > %s_%d%03d_lapgrd.log\n\n', gcmf, varname, yr,dy);
% 
%     % Write (2) scmf
%     temp = sprintf('%s%s\\%s_%d%03d',    fdatway, varname, varname, yr,dy);
%     fprintf(scmp,'%s\n',temp);
%     fprintf(scmp,'5\n2\n1\n0\n0\n%f %f 0 1\n%f %f 0 1\n', xlr-100*siz, xul+100*siz, ylr-100*siz, yul+100*siz);
% 
%     fprintf(scmp,'0 5000 1 1\n1000.0\n0\n2\n1\n0\n1\n1\n');
%     fprintf(scmp,'%s\n',datf);
% 
%     % a6,2f20.5,f12.3,12f12.3
%     dfm(18:19) = ' 1';
%     fprintf(scmp,'30000\n%d\n(%s)\n',str2num(dfm(2:3)), dfm);
% 
% 
%     n = length(resf);m=n-2;
%     fprintf(scmp,'%s\n',resf);
% 
%     resf(m:n) = 'opt';
%     fprintf(scmp,'%s\n',resf);
% 
%     resf(m:n) = 'sur';
%     fprintf(scmp,'%s\n',resf);
% 
%     resf(m:n) = 'lis';
%     fprintf(scmp,'%s\n',resf);
% 
%     resf(m:n) = 'cov';
%     fprintf(scmp,'%s\n\n\n\n\n',resf);
% 
%     resf(m:n) = 'sur';
%     fprintf(gcmp,'%s\n',resf);
%     fprintf(gcmp,'0\n1\n\n1\n');
%     fprintf(gcmp,'1\n%f %f %f\n', xlr, xul, siz);
%     fprintf(gcmp,'2\n%f %f %f\n', ylr, yul, siz);
%     fprintf(gcmp,'0\n2\n');
%     fprintf(gcmp,'%s\n2\n-9999\n', fdem);
% 
%     grdf = sprintf('%s%s\\%s_%d.flt', fgrdway, varname, varname, yr * 1000 + dy);
%     fprintf(gcmp,'%s\n',grdf);
%     fprintf(gcmp,'\n\n\n\n');
% 
%     fclose(scmp);
%     fclose(gcmp);
% end
% fclose(batp);
% % toc
% % disp('  ANUSPLIN BAT File exported!!\n');
























function makesplinotbat(yr, direct, data_size, varname, fdem, fhdr)
% Robust makesplinotbat + Master aggregator (BY VARIABLE ACROSS YEARS)
% 需求：将相同变量（varname）的不同年份主 bat 合并到“同一个”总控 bat 中，
% 而不是按年份合并。
%
% 生成内容：
%   - 每年仍然生成：<var>_<yr>_spl.bat/.cmd/.bat.txt（放在 tmp/<var>/ 下）
%   - 同时将该年度主 bat 注册到：ALL_<var>_spl_run.bat（位于 wks_tmp 根目录）
%   - （可选）维护一个全变量总控 ALL_spl_run.bat，用于一键跑所有变量

    % ---------- 路径解包 ----------
    wks_out = direct{1}{1};
    wks_tmp = direct{1}{2};
    wks_grd = direct{1}{3};
    utils_anusplin('ensure_dir', wks_out);
    utils_anusplin('ensure_dir', wks_tmp);
    utils_anusplin('ensure_dir', wks_grd);

    out_txt_dir = fullfile(wks_out, varname);
    tmp_var_dir = fullfile(wks_tmp, varname);
    grd_var_dir = fullfile(wks_grd, varname);
    utils_anusplin('ensure_dir', out_txt_dir);
    utils_anusplin('ensure_dir', tmp_var_dir);
    utils_anusplin('ensure_dir', grd_var_dir);

    % 备用目录（用户文档）
    user_docs = fullfile(getenv('USERPROFILE'), 'Documents', 'QX', 'temp', varname);
    utils_anusplin('ensure_dir', user_docs);  % 先建好，后面可能要用

    % ---------- 解析 HDR ----------
    [xlr, ylr, ~, ~, siz, xul, yul] = utils_anusplin('read_hdr_geo', fhdr);

    % ---------- 数据分组信息 ----------
    dm = data_size(2);
    im = floor(dm / 12);
    tail_cols = mod(dm,12);
    nGroupsExpected = im + (tail_cols > 0);
    if nGroupsExpected == 0, nGroupsExpected = 1; end

    % ---------- 扫描已存在的 txt 文件（不依赖它也能生成脚本） ----------
    patt = sprintf('%s_%d*.txt', varname, yr);
    files = dir(fullfile(out_txt_dir, patt));

    % ---------- 主批处理文件（两种扩展 + 备份 .bat.txt） ----------
    bat_main = fullfile(tmp_var_dir, sprintf('%s_%d_spl.bat', varname, yr));
    cmd_main = fullfile(tmp_var_dir, sprintf('%s_%d_spl.cmd', varname, yr));
    txt_backup = fullfile(tmp_var_dir, sprintf('%s_%d_spl.bat.txt', varname, yr));

    % 打开 writer（先写入 bat；完后复制到 cmd/txt）
    batp = fopen(bat_main, 'w');
    if batp < 0, error('Cannot create BAT: %s', bat_main); end

    % ---------- 写 bat 头 ----------
    fprintf(batp, '@echo off\r\n');
    fprintf(batp, 'setlocal enabledelayedexpansion\r\n');
    fprintf(batp, 'REM Auto-generated (robust) makesplinotbat.m\r\n');
    fprintf(batp, 'set VAR=%s\r\n', varname);
    fprintf(batp, 'set YEAR=%d\r\n', yr);
    fprintf(batp, 'set WKS_OUT="%s"\r\n', utils_anusplin('to_win', wks_out));
    fprintf(batp, 'set WKS_TMP="%s"\r\n', utils_anusplin('to_win', wks_tmp));
    fprintf(batp, 'set WKS_GRD="%s"\r\n', utils_anusplin('to_win', wks_grd));
    fprintf(batp, 'set IN_DIR="%%WKS_OUT%%\\%s"\r\n', varname);
    fprintf(batp, 'set DEM="%s"\r\n', utils_anusplin('to_win', fdem));
    fprintf(batp, 'set HDR="%s"\r\n', utils_anusplin('to_win', fhdr));
    fprintf(batp, 'cd /d "%%WKS_TMP%%\\%s"\r\n\r\n', varname);

    if isempty(files)
        fprintf(batp, 'echo [WARN] No input files in %%IN_DIR%% for %%VAR%% %%YEAR%%.\r\n');
        fprintf(batp, 'echo Expect ~%d group(s) from data_size.\r\n\r\n', nGroupsExpected);
    end

    % ---------- 为每组生成 cmd 并写入 bat ----------
    for j = 1:nGroupsExpected
        % 数据 txt（遵循 csv2Anuspl 命名）
        txt_name = sprintf('%s_%d%03d.txt', varname, yr, j);
        txt_path = fullfile(out_txt_dir, txt_name);

        % 控制文件（输出在 tmp_var_dir）
        snt_cmd = fullfile(tmp_var_dir, sprintf('%s_%d%03d_snt.cmd', varname, yr, j));
        spl_cmd = fullfile(tmp_var_dir, sprintf('%s_%d%03d_spl.cmd', varname, yr, j));
        grd_cmd = fullfile(tmp_var_dir, sprintf('%s_%d%03d_grd.cmd', varname, yr, j));

        % 写 selnot 控制
        ncmp = fopen(snt_cmd, 'w');
        if ncmp < 0, error('Cannot create: %s', snt_cmd); end
        fprintf(ncmp, '2\n1\n0\n0\n%.6f %.6f 0 1\n%.6f %.6f 0 1\n', ...
            xlr - 100*siz, xul + 100*siz, ylr - 100*siz, yul + 100*siz);
        fprintf(ncmp, '0 9000 0 1\n0\n1\n0\n');
        fprintf(ncmp, '%s\n', utils_anusplin('to_win', txt_path));
        fprintf(ncmp, '5200\n12\n(a12,2f20.5,f20.3,12f12.3)\n');
        baseRes = fullfile(tmp_var_dir, sprintf('%s_%d%03d.res', varname, yr, j));
        fprintf(ncmp, '%s\n', utils_anusplin('to_ext', baseRes,'not'));
        fprintf(ncmp, '%s\n', utils_anusplin('to_ext', baseRes,'rej'));
        fprintf(ncmp, '1000\n');
        fclose(ncmp);
        utils_anusplin('assert_file_exists', snt_cmd, 'snt.cmd');

        % 写 splinb 控制
        scmp = fopen(spl_cmd, 'w');
        if scmp < 0, error('Cannot create: %s', spl_cmd); end
        tmp_prefix = fullfile(out_txt_dir, sprintf('%s_%d%03d', varname, yr, j));
        fprintf(scmp, '%s\n', utils_anusplin('to_win', tmp_prefix));
        fprintf(scmp, '5\n2\n1\n0\n0\n%.6f %.6f 0 1\n%.6f %.6f 0 1\n', ...
            xlr - 100*siz, xul + 100*siz, ylr - 100*siz, yul + 100*siz);
        ncols_this = (j <= im) * 12 + (j == (im+1)) * max(tail_cols, 12*(im==0));
        fprintf(scmp, '0 9000.00 0 1\n0\n2\n%d\n0\n1\n1\n', ncols_this);
        fprintf(scmp, '%s\n', utils_anusplin('to_win', txt_path));
        fprintf(scmp, '5200\n12\n(a12,2f20.5,f20.3,12f12.3)\n');
        fprintf(scmp, '%s\n4000\n', utils_anusplin('to_ext', baseRes,'not'));
        fprintf(scmp, '%s\n', utils_anusplin('to_ext', baseRes,'res'));
        fprintf(scmp, '%s\n', utils_anusplin('to_ext', baseRes,'opt'));
        fprintf(scmp, '%s\n', utils_anusplin('to_ext', baseRes,'sur'));
        fprintf(scmp, '%s\n\n\n\n\n', utils_anusplin('to_ext', baseRes,'lis'));
        fclose(scmp);
        utils_anusplin('assert_file_exists', spl_cmd, 'spl.cmd');

        % 写 lapgrd 控制
        gcmp = fopen(grd_cmd, 'w');
        if gcmp < 0, error('Cannot create: %s', grd_cmd); end
        fprintf(gcmp, '%s\n', utils_anusplin('to_win', utils_anusplin('to_ext', baseRes,'sur')));
        fprintf(gcmp, '0\n1\n\n1\n');
        fprintf(gcmp, '1\n%.6f %.6f %.6f\n', xlr, xul, siz);
        fprintf(gcmp, '2\n%.6f %.6f %.6f\n', ylr, yul, siz);
        fprintf(gcmp, '0\n2\n');
        fprintf(gcmp, '%s\n2\n-9999\n', utils_anusplin('to_win', fdem));
        d1 = (j-1)*12 + 1; d2 = min(j*12, dm); if d2 < d1, d2=d1; end
        for d = d1:d2
            out_flt = fullfile(grd_var_dir, sprintf('%s_%d.flt', varname, yr*1000 + d));
            fprintf(gcmp, '%s\n', utils_anusplin('to_win', out_flt));
        end
        fprintf(gcmp, '\n\n\n\n');
        fclose(gcmp);
        utils_anusplin('assert_file_exists', grd_cmd, 'grd.cmd');

        % 写 bat 中的调用序列
        fprintf(batp, 'echo Processing %s\r\n', utils_anusplin('to_win', txt_name));
        fprintf(batp, 'selnot < "%s" > "%s_%d%03d_setnot.log"\r\n', utils_anusplin('to_win', snt_cmd), varname, yr, j);
        fprintf(batp, 'splinb < "%s" > "%s_%d%03d_splinb.log"\r\n',  utils_anusplin('to_win', spl_cmd), varname, yr, j);
        fprintf(batp, 'lapgrd < "%s" > "%s_%d%03d_lapgrd.log"\r\n\r\n', utils_anusplin('to_win', grd_cmd), varname, yr, j);
    end

    fprintf(batp, 'echo Done. Bat written: "%s"\r\n', utils_anusplin('to_win', bat_main));
    fprintf(batp, 'endlocal\r\n');
    fclose(batp);

    % ---------- 强校验与冗余写入 ----------
    utils_anusplin('assert_file_exists', bat_main, '.bat');
    copyfile(bat_main, cmd_main, 'f');
    copyfile(bat_main, txt_backup, 'f');
    utils_anusplin('assert_file_exists', cmd_main,  '.cmd');
    utils_anusplin('assert_file_exists', txt_backup,'.bat.txt');

    % 若 .bat 或 .cmd 立刻被策略移除，则写入备用目录并提示
    fallbackUsed = false;
    if exist(bat_main,'file')~=2 || exist(cmd_main,'file')~=2
        fallbackUsed = true;
        bat_fb = fullfile(user_docs, sprintf('%s_%d_spl.bat', varname, yr));
        cmd_fb = fullfile(user_docs, sprintf('%s_%d_spl.cmd', varname, yr));
        txt_fb = fullfile(user_docs, sprintf('%s_%d_spl.bat.txt', varname, yr));
        utils_anusplin('ensure_dir', user_docs);
        copyfile(bat_main, bat_fb, 'f');
        if exist(bat_fb,'file')~=2 && exist(bat_main,'file')~=2
            copyfile(txt_backup, bat_fb, 'f');
        end
        if exist(cmd_main,'file')==2
            copyfile(cmd_main, cmd_fb, 'f');
        else
            copyfile(txt_backup, cmd_fb, 'f');
        end
        copyfile(txt_backup, txt_fb, 'f');
        utils_anusplin('assert_file_exists', bat_fb, '.bat(fallback)');
        utils_anusplin('assert_file_exists', cmd_fb, '.cmd(fallback)');
        utils_anusplin('assert_file_exists', txt_fb, '.bat.txt(fallback)');

        % 备份各组控制文件到备用目录
        for j = 1:nGroupsExpected
            snt_cmd = fullfile(tmp_var_dir, sprintf('%s_%d%03d_snt.cmd', varname, yr, j));
            spl_cmd = fullfile(tmp_var_dir, sprintf('%s_%d%03d_spl.cmd', varname, yr, j));
            grd_cmd = fullfile(tmp_var_dir, sprintf('%s_%d%03d_grd.cmd', varname, yr, j));
            if exist(snt_cmd,'file')==2, copyfile(snt_cmd, fullfile(user_docs, utils_anusplin('getname', snt_cmd)), 'f'); end
            if exist(spl_cmd,'file')==2, copyfile(spl_cmd, fullfile(user_docs, utils_anusplin('getname', spl_cmd)), 'f'); end
            if exist(grd_cmd,'file')==2, copyfile(grd_cmd, fullfile(user_docs, utils_anusplin('getname', grd_cmd)), 'f'); end
        end
        fprintf(2,'[NOTICE] .bat/.cmd may be blocked. Fallback copies written to:\n  %s\n', user_docs);
    end

    % ---------- 关键新增：注册到“按变量聚合”的总控 bat（跨年份合并） ----------
    % 以前是按年份：ALL_<yr>_spl_run.bat
    % 现在改为按变量：ALL_<varname>_spl_run.bat（将同一变量不同年份主 bat 合并在一起）
    master_bat = fullfile(wks_tmp, sprintf('ALL_%s_spl_run.bat', varname));
    master_cmd = fullfile(wks_tmp, sprintf('ALL_%s_spl_run.cmd', varname));
    master_txt = fullfile(wks_tmp, sprintf('ALL_%s_spl_run.bat.txt', varname));
    utils_anusplin('ensure_master_initialized', master_bat);  % 不存在则写入头部

    % 生成需要追加的调用行
    ln = sprintf('echo ==== CALL %%DATE%% %%TIME%% :: %s %d ====\r\ncall "%s"\r\n\r\n', ...
                 varname, yr, utils_anusplin('to_win', bat_main));

    % 去重：避免重复追加同一路径
    needAppend = true;
    if exist(master_bat,'file')==2
        try
            txt_master = fileread(master_bat);
            if contains(txt_master, utils_anusplin('to_win', bat_main))
                needAppend = false;
            end
        catch
            % 读取失败则默认允许追加
        end
    end
    if needAppend
        utils_anusplin('write_or_append', master_bat, ln, 'a');
    end

    % 同步镜像
    copyfile(master_bat, master_cmd, 'f');
    copyfile(master_bat, master_txt, 'f');

    % 针对可能策略移除的回退：总控也写回退目录（按变量分类）
    master_fallback_root = fullfile(getenv('USERPROFILE'), 'Documents', 'QX', 'temp', sprintf('ALL_%s', varname));
    utils_anusplin('ensure_dir', master_fallback_root);
    if exist(master_bat,'file')~=2 || exist(master_cmd,'file')~=2
        copyfile(master_bat, fullfile(master_fallback_root, utils_anusplin('getname', master_bat)), 'f');
        if exist(master_cmd,'file')==2
            copyfile(master_cmd, fullfile(master_fallback_root, utils_anusplin('getname', master_cmd)), 'f');
        else
            copyfile(master_txt, fullfile(master_fallback_root, utils_anusplin('getname', master_cmd)), 'f');
        end
        copyfile(master_txt, fullfile(master_fallback_root, utils_anusplin('getname', master_txt)), 'f');
    end

    % 最终提示
    if fallbackUsed
        fprintf('makesplinotbat: wrote (fallback) %s and %s\n', ...
            fullfile(user_docs, sprintf('%s_%d_spl.bat', varname, yr)), ...
            fullfile(user_docs, sprintf('%s_%d_spl.cmd', varname, yr)));
    else
        fprintf('makesplinotbat: wrote %s  and  %s  (plus .bat.txt)\n', bat_main, cmd_main);
    end
    fprintf('master-bat aggregated (by var): %s\n', master_bat);

    % ---------- （可选）全变量总控：首次遇到该变量时挂一次 ----------
    global_all = fullfile(wks_tmp, 'ALL_spl_run.bat');
    utils_anusplin('ensure_master_initialized', global_all);
    gline = sprintf('echo ==== CALL %%DATE%% %%TIME%% :: MASTER %s ====\r\ncall "%s"\r\n\r\n', ...
                    varname, utils_anusplin('to_win', master_bat));
    needAppendGlobal = true;
    if exist(global_all,'file')==2
        try
            gtxt = fileread(global_all);
            if contains(gtxt, utils_anusplin('to_win', master_bat))
                needAppendGlobal = false;
            end
        catch
        end
    end
    if needAppendGlobal
        utils_anusplin('write_or_append', global_all, gline, 'a');
        copyfile(global_all, fullfile(wks_tmp, 'ALL_spl_run.cmd'), 'f');
        copyfile(global_all, fullfile(wks_tmp, 'ALL_spl_run.bat.txt'), 'f');
    end
end








