% E:\MeteoGrid\Function_set\GHCND_CSV2Daily.m
% jbwang@igsnrr.ac.cn
% May 07 2019

close all; clear all; clc;

vname = {'PRCP', 'TMAX', 'TMIN','TAVG','SNOW','SNWD','ACSH', 'AWND'};
v_num = length(vname);

fsta = 'E:\MeteoGrid\ghcnd\ghcnd-stations.txt';
[id, lat, lon, elv,ghcnd_sid] = readghcnstation(fsta, 50, 160, -30, 65);

yr1 = 1950; yr2 = 2018;

flog = fopen(['E:\MeteoGrid\ghcnd\GHCND_CSV2Daily_Running_' datestr(now,30) '.log'], 'w');
fprintf(flog, 'E:\\MeteoGrid\\Function_set\\GHCND_CSV2Daily.m\njbwang@igsnrr.ac.cn\nMay-07-2019\n\nYear');
for i = 1 : v_num, fprintf(flog, '\t%s', vname{i}); end
time_begin = now;
% Check files
n_files = 0;
for yr = yr1 : yr2
    filename = ['H:/Workspace/MeteoGrid/GHCN/' num2str(yr) '.csv'];
    if ~exist(filename, 'file')
        disp(['Cannot find: ' filename]);
        n_files = n_files + 1;
    else
        disp(['Find: ' filename]);
    end
end
if n_files > 0
    disp(n_files);
end
for js = 1 : 68
    yr = 2018 - js;
    num_days = datenum(yr + 1, 1, 1) - datenum(yr, 1, 1);
    % .csv ÎÄ¼þÂ·¾¶ÅäÖÃ
    filename = ['H:/Workspace/MeteoGrid/GHCN/' num2str(yr) '.csv'];
    tic
    fip = fopen(filename, 'r');
    % s0 = fgetl(fip);
    n0 = 0;
    ghcn = containers.Map;
    while(~feof(fip))
        s1 = textscan(fip, '%11s%8s%4s%5d%1s%1s%1s%4s',10000, 'delimiter',',');
        n1 = length(s1{1,1});
        n0 = n0 + n1;
        
        mvr = s1{1,3}{1,1};
        if strcmp(mvr, 'PRCP')
            disp([num2str(n0), ' ', s1{1,1}{1,1}, ' ', s1{1,2}{1,1}, ' ', s1{1,3}{1,1}, ' ', num2str(s1{1,4}(1))]);
        end
        
        ymd = str2num(cell2mat(s1{1,2}));
        
        dy = ymd - fix(ymd / 100) * 100;
        yr_pro = fix(ymd / 100 / 100);
        mn = fix((ymd - yr_pro * 100 * 100 - dy) / 100);
        jday = datenum(yr_pro, mn, dy) - datenum(yr_pro, 1, 1) + 1;
        for i = 1 : n1
            sid = s1{1,1}{i,1};
            mvr = s1{1,3}{i,1};
            v = find(strcmp(vname,mvr));
            jd = jday(i);
            
            if ~ghcn.isKey(sid)
                x0 = zeros([num_days, v_num]) - 9999;
                x0(jd,v) = s1{1,4}(i);
                % newMap = containers.Map, x0);
                ghcn(sid) = x0; % [ghcn; newMap];
            else
                x1 = ghcn(sid);
                x1(jd, v) = s1{1,4}(i);  % No. Lat, Lon, Elv
                ghcn(sid) = x1;
            end
        end
        
    end
    fclose(fip);
    t1 = toc
    
    xid = keys(ghcn);
    x_num = ghcn.Count;
    cdat = zeros([1,v_num]);
    tic
    for v = 1 : v_num
        sub =['E:\MeteoGrid\ghcnd\' vname{v}];
        if ~exist(sub,'dir')
            system(['mkdir ' sub]);
        end
        
        
        fname = [sub '\' vname{v} '_' num2str(yr) '.txt'];
        fop = fopen(fname, 'w');
        for i = 1 : x_num
            sid = xid{i};
            if ghcn.isKey(sid) && ghcnd_sid.isKey(sid)
                dat = ghcn(sid);
                loc = ghcnd_sid(sid);
                [nt, mt] = size(dat);
                
                tmi = dat(:,2);
                tmx = dat(:,3);
                tem = (tmi + tmx)/2;
                tem(tmi < -9000 | tmx < -9000) = -9999;
                
                dat(:,4) = tem;
                
                xdt = dat(:,v);
                vdt = xdt(xdt > -9000);
                nd = length(xdt);
                nv = length(vdt);
                
                if ~isempty(xdt) && nv / nd >= 0.8
                    fprintf(fop, '%s\t%f\t%f\t%f', sid, loc);
                    for j = 1 : length(xdt)
                        fprintf(fop, '\t%f', xdt(j));
                    end
                    fprintf(fop, '\n');
                    cdat(v) = cdat(v) + 1;
                end
            end
        end
        fclose(fop);
    end
    t2 = toc
    disp(['Number of data file: ' num2str(cdat) ' in ' num2str(yr)]);
    fprintf(flog, '\n%d', yr);
    for i = 1 : v_num, fprintf(flog, '\t%d', cdat(i)); end
    fprintf(flog, '\nUsed time %.1f s for reading, %.1f s for writting, and totally %.1f s.\n', t1, t2, t1 + t2);

end
time_end = now;
fprintf(flog, '\n\nGHCND annual data were re-writed as station and its daily data for each element.');
fprintf(flog, '\nThe begin and end time are %s and %s, and used %.1f s\n', datestr(time_begin,30), datestr(time_end,30), time_end - time_begin);
fclose(flog);
disp('That''s all! Now go home for your yum food!!');
