function csv2Anuspl_yh(yr, varname, outway, gid,geo, data, sta)
% write data file formated as (a12 2f10.5 f6.2 12f6.2)

%% Look for coordination for each station
% read stid, lat, lon, xx, yy, elv from file
% data = yy;
dynum = datenum(yr+1,1,1)-datenum(yr,1,1);

[n m] = size(data);
j = 1;
if sta ~= -1
    for i = 1 : n
       sdi = sta(i,:);
       ix = strmatch(sdi,gid);
       if ~isempty(ix)
           st(j,:) = sdi;
           x0(j,1) = geo(ix,1);
           y0(j,1) = geo(ix,2);
           z0(j,1) = geo(ix,3);
           dat(j,:) = data(i,:);
           j = j + 1;
       end
    end
else
    st = gid;
    x0 = geo(:,1);
    y0 = geo(:,2);
    z0 = geo(:,3);
    dat = data;
end

if m == 46
    dn = [1 12; 13 24; 25 36; 37 46];
    for i = 1 : 4
        xd = dat(:,dn(i,1):dn(i,2));
        if ~exist(outway,'dir')
            system(['mkdir ' outway]);
        end
        sub = [outway '\' varname];
        if ~exist(sub, 'dir')
            system(['mkdir ' sub]);
        end
        ff = [sub '\' varname '_' num2str(yr * 100 + i) '.txt'];
        fp = fopen(ff, 'w');
        [xi ~] = size(xd);
        for j = 1 : xi
            fprintf(fp, '%12s%20.5f%20.5f%20.3f',st(j,:),x0(j), y0(j), z0(j));
            for k = 1 : dn(i,2)-dn(i,1)+1
                fprintf(fp, '%12.3f', xd(j, k));
            end
            fprintf(fp, '\n');
        end   % each line of data
        fclose(fp);
    end   % data was written to 4 files
end
if m == 24
    dn = [1 12; 13 24];
    for i = 1 : 2
        xd = dat(:,dn(i,1):dn(i,2));
        if ~exist(outway,'dir')
            system(['mkdir ' outway]);
        end
        sub = [outway '\' varname];
        if ~exist(sub, 'dir')
            system(['mkdir ' sub]);
        end
        ff = [sub '\' varname '_' num2str(yr * 100 + i) '.txt'];
        fp = fopen(ff, 'w');
        [xi ~] = size(xd);
        for j = 1 : xi
            fprintf(fp, '%12s%20.5f%20.5f%20.3f',st(j,:),x0(j), y0(j), z0(j));
            for k = 1 : dn(i,2)-dn(i,1)+1
                fprintf(fp, '%12.3f', xd(j, k));
            end
            fprintf(fp, '\n');
        end   % each line of data
        fclose(fp);
    end   % data was written to 4 files
end

if m == 36
    dn = [1 12; 13 24;25 36];
    for i = 1 : 3
        xd = dat(:,dn(i,1):dn(i,2));
        if ~exist(outway,'dir')
            system(['mkdir ' outway]);
        end
        sub = [outway '\' varname];
        if ~exist(sub, 'dir')
            system(['mkdir ' sub]);
        end
        ff = [sub '\' varname '_' num2str(yr * 100 + i) '.txt'];
        fp = fopen(ff, 'w');
        [xi ~] = size(xd);
        for j = 1 : xi
            fprintf(fp, '%12s%20.5f%20.5f%20.3f',st(j,:),x0(j), y0(j), z0(j));
            for k = 1 : dn(i,2)-dn(i,1)+1
                fprintf(fp, '%12.3f', xd(j, k));
            end
            fprintf(fp, '\n');
        end   % each line of data
        fclose(fp);
    end   % data was written to 4 files
end

if m == dynum   % daily output
    for i = 1 : 31
        dn(i,1) = (i-1)*12+1;
        dn(i,2) = min(i*12, dynum);
        xd = dat(:,dn(i,1):dn(i,2));
        if ~exist(outway,'dir')
            system(['mkdir ' outway]);
        end
        sub = [outway '\' varname];
        if ~exist(sub, 'dir')
            system(['mkdir ' sub]);
        end
        ff = [sub '\' varname '_' num2str(yr * 100 + i) '.txt'];
        fp = fopen(ff, 'w');
        [xi ~] = size(xd);
        for j = 1 : xi
            fprintf(fp, '%12s%20.5f%20.5f%20.3f',st(j,:),x0(j), y0(j), z0(j));
            for k = 1 : dn(i,2)-dn(i,1)+1
                fprintf(fp, '%12.3f', xd(j, k));
            end
            fprintf(fp, '\n');
        end   % each line of data
        fclose(fp);
    end   % data was written to 4 files
end

if yr == 9999   % single output
    im = fix(m/12);
    for i = 1 : im+1
        if i <= im
            d1 = (i - 1) * 12 + 1;
            d2 = i * 12;
        else
            d1 = im * 12 + 1;
            d2 = m;
        end
        if ~exist(outway,'dir')
            system(['mkdir ' outway]);
        end
        sub = [outway '\' varname];
        if ~exist(sub, 'dir')
            system(['mkdir ' sub]);
        end
        ff = [sub '\' varname '_' num2str(yr * 100 + i) '.txt'];
        fp = fopen(ff, 'w');
        for j = 1 : n
            fprintf(fp, '%12s%20.5f%20.5f%20.3f',st{j},x0(j), y0(j), z0(j));
            for k = d1 : d2
                fprintf(fp, '%12.3f', dat(j, k));
            end
            fprintf(fp, '\n');
        end   % each line of data
        fclose(fp);
    end   % data was written to 4 files
    disp(['Write data to: ' ff]);
end