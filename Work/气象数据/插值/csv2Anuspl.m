% function csv2Anuspl(yr, varname, outway, gid, geo, data)
% % write data file formated as (a12 2f10.5 f6.2 12f6.2)
% 
% %% Look for coordination for each station
% % read stid, lat, lon, xx, yy, elv from file
% % data = yy;
% dynum = datenum(yr+1,1,1)-datenum(yr,1,1);
% 
% [n m] = size(data); dm = m;
% if n <= 50
%     disp(['Data number (' num2str(n) ') is not enough for interpolation and return.']);
%     return;
% else
%     st = gid;
%     x0 = geo(:,1);
%     y0 = geo(:,2);
%     z0 = geo(:,3);
%     dat = data;
% end
% 
% if m == 46
%     dn = [1 12; 13 24; 25 36; 37 46];
%     for i = 1 : 4
%         xd = dat(:,dn(i,1):dn(i,2));
% %         if ~exist(outway,'dir')
% %             system(['mkdir ' outway]);
% %         end
%         sub = [outway '/' varname];
% %         if ~exist(sub, 'dir')
% %             system(['mkdir ' sub]);
% %         end
%         ff = [sub '/' varname '_' num2str(yr * 1000 + i) '.txt'];
%         fp = fopen(ff, 'w');
%         for j = 1 : length(xd)
%             fprintf(fp, '%12s%20.5f%20.5f%20.3f',st(j,:),x0(j), y0(j), z0(j));
%             for k = 1 : dn(i,2)-dn(i,1)+1
%                 fprintf(fp, '%12.3f', xd(j, k));
%             end
%             fprintf(fp, '\n');
%         end   % each line of data
%         fclose(fp);
%     end   % data was written to 4 files
% end
% if m == 24
%     dn = [1 12; 13 24];
%     for i = 1 : 2
%         xd = dat(:,dn(i,1):dn(i,2));
%         if ~exist(outway,'dir')
%             system(['mkdir ' outway]);
%         end
%         sub = [outway '/' varname];
%         if ~exist(sub, 'dir')
%             system(['mkdir ' sub]);
%         end
%         ff = [sub '/' varname '_' num2str(yr * 1000 + i) '.txt'];
%         fp = fopen(ff, 'w');
%         [xi ~] = size(xd);
%         for j = 1 : xi
%             fprintf(fp, '%12s%20.5f%20.5f%20.3f',st(j,:),x0(j), y0(j), z0(j));
%             for k = 1 : dn(i,2)-dn(i,1)+1
%                 fprintf(fp, '%12.3f', xd(j, k));
%             end
%             fprintf(fp, '\n');
%         end   % each line of data
%         fclose(fp);
%     end   % data was written to 4 files
% end
% 
% if m == 36
%     dn = [1 12; 13 24;25 36];
%     for i = 1 : 3
%         xd = dat(:,dn(i,1):dn(i,2));
%         if ~exist(outway,'dir')
%             system(['mkdir ' outway]);
%         end
%         sub = [outway '/' varname];
%         if ~exist(sub, 'dir')
%             system(['mkdir ' sub]);
%         end
%         ff = [sub '/' varname '_' num2str(yr * 1000 + i) '.txt'];
%         fp = fopen(ff, 'w');
%         for j = 1 : length(xd)
%             fprintf(fp, '%12s%20.5f%20.5f%20.3f',st(j,:),x0(j), y0(j), z0(j));
%             for k = 1 : dn(i,2)-dn(i,1)+1
%                 fprintf(fp, '%12.3f', xd(j, k));
%             end
%             fprintf(fp, '\n');
%         end   % each line of data
%         fclose(fp);
%     end   % data was written to 4 files
% end
% 
% if m == dynum   % daily output
%     im = fix(dm/12);
%     xd = dat;
%     if ~exist(outway,'dir')
%         system(['mkdir ' outway]);
%     end
%     sub = [outway '\' varname];
%     if ~exist(sub, 'dir')
%         system(['mkdir ' sub]);
%     end
%     for dy = 1 : im+1
%         if dy <= im
%             d1 = (dy - 1) * 12 + 1;
%             d2 = dy * 12;
%         else
%             d1 = im * 12 + 1;
%             d2 = dm;
%         end     
%         datf = sprintf('%s\\%s_%d%03d.txt', sub, varname, yr,dy);
%         fp = fopen(datf, 'w');
%         for j = 1 : length(xd)
%             fprintf(fp, '%12s%20.5f%20.5f%20.3f',st(j,:),x0(j), y0(j), z0(j));
%             for k = d1 : d2
%                 fprintf(fp, '%12.3f', xd(j, k));
%             end
%             fprintf(fp, '\n');
%         end   % each line of data
%         fclose(fp);
%     end
% end
% 
% if m == 1   % single output
%     im = fix(m/12);
%     for i = 1 : im+1
%         if i <= im
%             d1 = (i - 1) * 12 + 1;
%             d2 = i * 12;
%         else
%             d1 = im * 12 + 1;
%             d2 = m;
%         end
%         if ~exist(outway,'dir')
%             system(['mkdir ' outway]);
%         end
%         sub = [outway '\' varname];
%         if ~exist(sub, 'dir')
%             system(['mkdir ' sub]);
%         end
%         ff = [sub '\' varname '_' num2str(yr * 1000 + i) '.txt'];
%         fp = fopen(ff, 'w');
%         for j = 1 : n
%             fprintf(fp, '%12s%20.5f%20.5f%20.3f',st{j},x0(j), y0(j), z0(j));
%             for k = d1 : d2
%                 fprintf(fp, '%12.3f', dat(j, k));
%             end
%             fprintf(fp, '\n');
%         end   % each line of data
%         fclose(fp);
%     end   % data was written to 4 files
%     disp(['Write data to: ' ff]);
% end
% 
% %% monthly data
% if m == 12   % single output
%     im = 1; % fix(m/12);
%     for i = 1 : im+1
%         if i <= im
%             d1 = (i - 1) * 12 + 1;
%             d2 = i * 12;
%         else
%             d1 = im * 12 + 1;
%             d2 = m;
%         end
%         if ~exist(outway,'dir')
%             system(['mkdir ' outway]);
%         end
%         sub = [outway '\' varname];
%         if ~exist(sub, 'dir')
%             system(['mkdir ' sub]);
%         end
%         ff = [sub '\' varname '_' num2str(yr * 1000 + i) '.txt'];
%         fp = fopen(ff, 'w');
%         for j = 1 : n
%             fprintf(fp, '%12s%20.5f%20.5f%20.3f',st{j},x0(j), y0(j), z0(j));
%             for k = d1 : d2
%                 fprintf(fp, '%12.3f', dat(j, k));
%             end
%             fprintf(fp, '\n');
%         end   % each line of data
%         fclose(fp);
%     end   % data was written to 4 files
%     disp(['Write data to: ' ff]);
% end





% 插值
function csv2Anuspl(yr, varname, outway, gid, geo, data)
% csv2Anuspl
% 将聚合后的站点数据写成 Anusplin 前处理所需的文本块。
% 按列分组写出多份 txt：<outway>/<varname>/<varname>_<yr*1000+group>.txt
%
% 输入:
%   yr      : 年份 (数值)
%   varname : 变量名 (字符串，比如 'PRCP','TMIN'...)
%   outway  : 输出根目录
%   gid     : 站点 ID（向量、char矩阵或cellstr，行数=站点数）
%   geo     : [X Y Z] (nStations x 3)，与 data 行对齐
%   data    : (nStations x nCols) 聚合后的数值矩阵
%
% 说明:
% - 兼容分组列数 m==46/36/24/12/1，以及 "daily==dynum" 的情况；
% - 所有路径用 fullfile + mkdir 创建，避免 system('mkdir')；
% - 站点 ID 自适应格式化（数值/char/cellstr均可）。

    %% ---------- 基本检查 ----------
    if nargin < 6
        error('csv2Anuspl:NotEnoughInputs', 'Need yr, varname, outway, gid, geo, data.');
    end
    if isempty(data) || isempty(geo)
        warning('csv2Anuspl:EmptyData', 'Empty data/geo. Nothing to write.');
        return;
    end
    [nStations, nCols] = size(data);
    if size(geo,1) ~= nStations || size(geo,2) < 3
        error('csv2Anuspl:SizeMismatch', 'geo must be nStations x 3 and match data rows.');
    end

    % 规范化 gid（允许数值/char矩阵/cellstr）
    gid_type = detect_gid_type(char(gid), nStations);

    % 输出目录
    outdir = fullfile(outway, varname);
    ensure_dir(outdir);

    % 日数（该年天数，用于 daily 判断）
    dynum = datenum(yr+1,1,1) - datenum(yr,1,1);

    % 站点坐标
    x0 = geo(:,1);  y0 = geo(:,2);  z0 = geo(:,3);
    dat = data;  % 简写

    %% ---------- 根据列数分支 ----------
    if nStations <= 50
        % 与原版保持一致：站点少于等于 50 提示并返回
        fprintf('Data number (%d) is not enough for interpolation and return.\n', nStations);
        return;
    end

    wrote_any = false;

    % m == 46  -> 4 组 (1-12, 13-24, 25-36, 37-46)
    if nCols == 46
        dn = [1 12; 13 24; 25 36; 37 46];
        for i = 1:size(dn,1)
            write_group_block(outdir, varname, yr, i, dat(:, dn(i,1):dn(i,2)), ...
                              gid, gid_type, x0, y0, z0);
            wrote_any = true;
        end
    end

    % m == 36  -> 3 组 (1-12, 13-24, 25-36)
    if nCols == 36
        dn = [1 12; 13 24; 25 36];
        for i = 1:size(dn,1)
            write_group_block(outdir, varname, yr, i, dat(:, dn(i,1):dn(i,2)), ...
                              gid, gid_type, x0, y0, z0);
            wrote_any = true;
        end
    end

    % m == 24  -> 2 组 (1-12, 13-24)
    if nCols == 24
        dn = [1 12; 13 24];
        for i = 1:size(dn,1)
            write_group_block(outdir, varname, yr, i, dat(:, dn(i,1):dn(i,2)), ...
                              gid, gid_type, x0, y0, z0);
            wrote_any = true;
        end
    end

    % m == 12  -> 1 组（月度）
    if nCols == 12
        % 与原逻辑一致：im=1; 然后写第 1 组 (1..12)
        i = 1;
        write_group_block(outdir, varname, yr, i, dat(:, 1:12), ...
                          gid, gid_type, x0, y0, z0);
        wrote_any = true;
        fprintf('Write data to: %s\n', fullfile(outdir, sprintf('%s_%d%03d.txt', varname, yr, i)));
    end

    % m == dynum -> daily 输出（按每 12 列切块，最后一块可能不足 12）
    if nCols == dynum
        im = floor(nCols/12);
        % 分块数 = im（整除的块） + 可能的尾块
        nBlocks = im + (nCols > im*12);
        for i = 1:nBlocks
            if i <= im
                d1 = (i-1)*12 + 1; d2 = i*12;
            else
                d1 = im*12 + 1;    d2 = nCols;
            end
            write_group_block(outdir, varname, yr, i, dat(:, d1:d2), ...
                              gid, gid_type, x0, y0, z0);
            wrote_any = true;
        end
    end

    % m == 1 -> 单列
    if nCols == 1
        i = 1;
        write_group_block(outdir, varname, yr, i, dat(:, 1:1), ...
                          gid, gid_type, x0, y0, z0);
        wrote_any = true;
        fprintf('Write data to: %s\n', fullfile(outdir, sprintf('%s_%d%03d.txt', varname, yr, i)));
    end

    if ~wrote_any
        warning('csv2Anuspl:NoPatternMatched', ...
            'No writer branch matched: nCols=%d (dynum=%d). Nothing written.', nCols, dynum);
    end
end


%% ------------- 子函数：写一组数据块 -------------
function write_group_block(outdir, varname, yr, grpIdx, blockData, gid, gid_type, x0, y0, z0)
    % out 文件名：<varname>_<yr*1000 + grpIdx>.txt
    fname = fullfile(outdir, sprintf('%s_%d%03d.txt', varname, yr, grpIdx));
    fid = fopen(fname, 'w');
    if fid < 0
        error('csv2Anuspl:OpenFailed', 'Cannot open for write: %s', fname);
    end

    n = size(blockData, 1);    % 站点数
    m = size(blockData, 2);    % 本块列数

    for j = 1:n
        % 打印站点 ID（12 宽，左/右对齐都可；这里按右对齐）
        print_sid(fid, gid, gid_type, j);

        % 打印几何
        fprintf(fid, '%20.5f%20.5f%20.3f', x0(j), y0(j), z0(j));

        % 打印本块的列数据
        for k = 1:m
            fprintf(fid, '%12.3f', blockData(j, k));
        end
        fprintf(fid, '\n');
    end

    fclose(fid);
end


%% ------------- 子函数：检测 gid 类型 -------------
function gid_type = detect_gid_type(gid, nStations)
    % 返回 'numeric' | 'char' | 'cell'
    if isnumeric(gid)
        gid_type = 'numeric';
        if numel(gid) ~= nStations
            error('csv2Anuspl:GidSize', 'Numeric gid must have %d elements.', nStations);
        end
    elseif ischar(gid)
        gid_type = 'char';
        if size(gid,1) ~= nStations
            error('csv2Anuspl:GidSize', 'Char gid must have %d rows.', nStations);
        end
    elseif iscell(gid)
        gid_type = 'cell';
        if numel(gid) ~= nStations
            error('csv2Anuspl:GidSize', 'Cell gid must have %d elements.', nStations);
        end
    else
        error('csv2Anuspl:GidType', 'Unsupported gid type: %s', class(gid));
    end
end


%% ------------- 子函数：按类型打印站点 ID -------------
function print_sid(fid, gid, gid_type, j)
    switch gid_type
        case 'numeric'
            fprintf(fid, '%12d', gid(j));
        case 'char'
            % char 矩阵的每行一个 ID
            fprintf(fid, '%12s', strtrim(gid(j, :)));
        case 'cell'
            % cellstr
            gj = gid{j};
            if isnumeric(gj)
                fprintf(fid, '%12d', gj);
            else
                fprintf(fid, '%12s', char(gj));
            end
        otherwise
            error('csv2Anuspl:BadGidType', 'Unknown gid_type: %s', gid_type);
    end
end


%% ------------- 子函数：确保目录存在 -------------
function ensure_dir(p)
    if ~isfolder(p), mkdir(p); end
end



