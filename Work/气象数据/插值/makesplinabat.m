function makesplinabat(yr, direct, data_size, varname, fdem, fhdr)
% close all
% clear all
% clc
% disp('MAKESPLINABAT: Produce Anusplin bat file');
% tic
% include files:
% 1.Splin.bat: splina < file.cmd > spl.log
%              lapgrd < filegrd.cmd > grd.log
% 2. file.cmd
% 3. filegrid.cmd
%
% ff = 'D:\China8km\CCTEC\Data\Observed\Storage\VGC.txt';
% m = length(ff);
% varname = ff(m-6:m-4);
% yr = 9999;
% [id x y z data] = textread(ff, '%s%f%f%f%f');
% n = length(id);
% gid = id;
% geo = [x y z];
% sta = id;
% Write file for Anusplin software
% disp(['      CSV2ANUSPL: Output Anusplin file: ' varname ' in ' num2str(yr)]);
% outway = 'D:\temp\Meteo10day';
% if ~exist(outway, 'dir')
%     system(['mkdir ' outway]);
% end                
% csv2Anuspl(yr, varname, outway,gid,geo, data, -1);
% [dn dm] = size(data);
dn = data_size(1);
dm = data_size(2);

station_number = fix(dn * 1.1);
knots_number = fix(dn / 4);

fdatway = direct{1,1}{1};
fcmdway = direct{1,1}{2};
fgrdway = direct{1,1}{3};

dfm = 'a12,2f20.5,f20.3,12f12.3';   %%'%12s%20.5f%20.5f%20.3f'%12.3f'
% fdem = 'asiadem8km.txt';
% fhdr = 'J:\temp\Storage\SOC\asiadem8km.hdr';
if ~exist(fhdr, 'file')
    disp(['Cannot find file: ' fhdr]);
    return;
end
fd = fopen(fhdr, 'r');
[res tmp] = textscan(fd, '%s%f');
fclose(fd);
pix = res{1,2}(1);
line = res{1,2}(2);
xlr = res{1,2}(3);
ylr = res{1,2}(4);
siz = res{1,2}(5);
xul = xlr + siz * pix;
yul = ylr + siz * line;

% meteosplin.bat file:
% disp(['MAKESPLINABAT data directory: ' fdatway]);
% disp(['MAKESPLINABAT cmd directory: ' fcdmway]);
% disp(['MAKESPLINABAT grid directory: ' fgrdway]);
% ny = length(yr);
% if ny > 1
%     yr1 = yr(1);    yr2 = yr(2);
% else
%     yr1 = yr;       yr2 = yr;
% end
ftpway = fcmdway;
% if ~exist(ftpway,'dir')
%     system(['mkdir ' ftpway]);
% end

sub = [ftpway '/' varname];
% if ~exist(sub)
%     system(['mkdir ' sub]);
% end
batf = [sub '/' varname '_' num2str(yr) '_spl.bat'];
batp = fopen(batf, 'a');
if batp < 0
    disp(['MAKESPLINABAT: Cannot creat BAT file: "' batf '"']);
    return;
end
if mod(dm, 12) == 0
    im = fix(dm/12);
    nn = im;
else
    im = fix(dm/12);
    nn = im + 1;
end 
if im > 1 && dn >= 5000
    for j = 1 : nn
        if j <= im
            d1 = (j - 1) * 12 + 1;
            d2 = j * 12;
        else
            d1 = im * 12 + 1;
            d2 = dm;
        end            
          % 2. spline.cmd file
            scmf = sprintf('%s/%s_%d%03d_spl.cmd',sub, varname, yr,j);
            gcmf = sprintf('%s/%s_%d%03d_grd.cmd',sub, varname, yr,j);

            
            scmp = fopen(scmf, 'w');
            if scmp < 0
                disp(['MAKESPLINABAT: Cannot creat SCMD FILE: "' scmf '"']);
                return;
            end
            gcmp = fopen(gcmf, 'w');
            if gcmp < 0
                disp(['MAKESPLINABAT: Cannot creat GCMD FILE: "' gcmf '"']);
                return;
            end
            
            %%% knot file
            ncmf = sprintf('%s/%s_%d%03d_snt.cmd',sub, varname, yr,j);
            ncmp = fopen(ncmf, 'w');
            if ncmp < 0
                disp(['MAKESPLINABAT: Cannot creat SELNOT FILE: "' ncmf '"']);
                return;
            end
            ncmf = sprintf('%s/%s/%s_%d%03d_snt.cmd', fcmdway, varname, varname, yr,j);
            fprintf(batp,'selnot < %s > %s_%d%03d_setnot.log\n',   ncmf, varname, yr,j);
            
            % change directory to DOS formation
            datf = sprintf('%s/%s/%s_%d%03d.txt', fdatway, varname, varname, yr,j);
            scmf = sprintf('%s/%s/%s_%d%03d_spl.cmd', fcmdway, varname, varname, yr,j);
            gcmf = sprintf('%s/%s/%s_%d%03d_grd.cmd', fcmdway, varname, varname, yr,j);
            resf = sprintf('%s/%s/%s_%d%03d.res', fcmdway, varname, varname, yr,j);
            
            % Write (1) bat file
            fprintf(batp,'rem Splin: %s\n', datf);
            fprintf(batp,'splinb < %s > %s_%d%03d_splinb.log\n',   scmf, varname, yr,j);
            fprintf(batp,'lapgrd < %s > %s_%d%03d_lapgrd.log\n\n', gcmf, varname, yr,j);

            % Write (2) scmf
            temp = sprintf('%s%s/%s_%d%03d',    fdatway, varname, varname, yr,j);
            fprintf(scmp,'%s\n',temp);
            fprintf(scmp,'5\n2\n1\n0\n0\n%f %f 0 1\n%.4f %.3f 0 1\n', xlr-100*siz, xul+100*siz, ylr-100*siz, yul+100*siz);

            if(j>im)
                fprintf(scmp,'0 9000.00 0 1\n0\n2\n%d\n0\n1\n1\n', mod(dm,12));
            else
                fprintf(scmp,'0 9000.00 0 1\n0\n2\n12\n0\n1\n1\n');
            end

            fprintf(scmp,'%s\n',datf);
            
            % a6,2f20.5,f12.3,12f12.3
            if j <= im
                dfm(18:19) = '12';
            else
                dfm(18:19) = num2str(mod(dm,12));
            end           

            fprintf(scmp,'%d\n%d\n(%s)\n',station_number, str2num(dfm(2:3)), dfm);

            
            n = length(resf);m=n-2;
            resf(m:n) = 'not';
            fprintf(scmp,'%s\n%d\n',resf, knots_number);

            resf(m:n) = 'res';
            fprintf(scmp,'%s\n',resf);

            resf(m:n) = 'opt';
            fprintf(scmp,'%s\n',resf);

            resf(m:n) = 'sur';
            fprintf(scmp,'%s\n',resf);

            resf(m:n) = 'lis';
            fprintf(scmp,'%s\n\n\n\n\n',resf);

            resf(m:n) = 'sur';
            fprintf(gcmp,'%s\n',resf);
            fprintf(gcmp,'0\n1\n\n1\n');
            fprintf(gcmp,'1\n%f %f %f\n', xlr, xul, siz);
            fprintf(gcmp,'2\n%f %f %f\n', ylr, yul, siz);
            fprintf(gcmp,'0\n2\n');
            fprintf(gcmp,'%s\n2\n-9999\n', fdem);

            for d=d1:d2
                grdf = sprintf('%s/%s/%s_%d.flt', fgrdway, varname, varname, yr * 1000 + d);
                fprintf(gcmp,'%s\n',grdf);
            end
            fprintf(gcmp,'\n\n\n\n');

            fclose(scmp);
            fclose(gcmp);
            
            % Write selnot.cmd file
            fprintf(ncmp,'2\n1\n0\n0\n%f %f 0 1\n%f %f 0 1\n', xlr-100*siz, xul+100*siz, ylr-100*siz, yul+100*siz);
            fprintf(ncmp,'0 9000 0 1\n0\n1\n0\n');
            fprintf(ncmp,'%s\n',datf);
            fprintf(ncmp,'%d\n12\n', station_number);
            fprintf(ncmp,'(%s)\n', dfm);
            
            resf(m:n) = 'not';
            fprintf(ncmp,'%s\n',resf);

            resf(m:n) = 'rej';
            fprintf(ncmp,'%s\n',resf);
            fprintf(ncmp,'%d', knots_number);
            fclose(ncmp);    
    end % FOR loop of 1~4 files
end
if im > 1 && dn < 5000
    for j = 1 : nn
        if j <= im
            d1 = (j - 1) * 12 + 1;
            d2 = j * 12;
        else
            d1 = im * 12 + 1;
            d2 = dm;
        end            
       % 2. spline.cmd file
        scmf = sprintf('%s/%s_%d%03d_spl.cmd',sub, varname, yr,j);
        gcmf = sprintf('%s/%s_%d%03d_grd.cmd',sub, varname, yr,j);

        scmp = fopen(scmf, 'w');
        if scmp < 0
            disp(['MAKESPLINABAT: Cannot creat SCMD FILE: "' scmf '"']);
            return;
        end
        gcmp = fopen(gcmf, 'w');
        if gcmp < 0
            disp(['MAKESPLINABAT: Cannot creat GCMD FILE: "' gcmf '"']);
            return;
        end

        % change directory to DOS formation
        datf = sprintf('%s/%s/%s_%d%03d.txt', fdatway, varname, varname, yr,j);
        scmf = sprintf('%s/%s/%s_%d%03d_spl.cmd', fcmdway, varname, varname, yr,j);
        gcmf = sprintf('%s/%s/%s_%d%03d_grd.cmd', fcmdway, varname, varname, yr,j);
        resf = sprintf('%s/%s/%s_%d%03d.res', fcmdway, varname, varname, yr,j);

        % Write (1) bat file
        fprintf(batp,'rem Splin: %s\n', datf);
        fprintf(batp,'splina < %s > %s_%d%03d_splina.log\n',   scmf, varname, yr,j);
        fprintf(batp,'lapgrd < %s > %s_%d%03d_lapgrd.log\n\n', gcmf, varname, yr,j);

        % Write (2) scmf
        temp = sprintf('%s/%s/%s_%d%03d',    fdatway, varname, varname, yr,j);
        fprintf(scmp,'%s\n',temp);
        fprintf(scmp,'5\n2\n1\n0\n0\n%f %f 0 1\n%f %f 0 1\n', xlr-100*siz, xul+100*siz, ylr-100*siz, yul+100*siz);

        if(j==4)
            fprintf(scmp,'0 5000 1 1\n1000.0\n0\n2\n10\n0\n1\n1\n');
        else
            fprintf(scmp,'0 5000 1 1\n1000.0\n0\n2\n12\n0\n1\n1\n');
        end

        fprintf(scmp,'%s\n',datf);

        % a6,2f20.5,f12.3,12f12.3
        if j <= im
            dfm(18:19) = '12';
        else
            dfm(18:19) = num2str(mod(dm,12));
        end           

        fprintf(scmp,'30000\n%d\n(%s)\n',str2num(dfm(2:3)), dfm);


        n = length(resf);m=n-2;
        fprintf(scmp,'%s\n',resf);

        resf(m:n) = 'opt';
        fprintf(scmp,'%s\n',resf);

        resf(m:n) = 'sur';
        fprintf(scmp,'%s\n',resf);

        resf(m:n) = 'lis';
        fprintf(scmp,'%s\n',resf);

        resf(m:n) = 'cov';
        fprintf(scmp,'%s\n\n\n\n\n',resf);

        resf(m:n) = 'sur';
        fprintf(gcmp,'%s\n',resf);
        fprintf(gcmp,'0\n1\n\n1\n');
        fprintf(gcmp,'1\n%f %f %f\n', xlr, xul, siz);
        fprintf(gcmp,'2\n%f %f %f\n', ylr, yul, siz);
        fprintf(gcmp,'0\n2\n');
        fprintf(gcmp,'%s\n2\n-9999\n', fdem);

        for d=d1:d2
            grdf = sprintf('%s%s/%s_%d.flt', fgrdway, varname, varname, yr * 1000 + d);
            fprintf(gcmp,'%s\n',grdf);
        end
        fprintf(gcmp,'\n\n\n\n');

        fclose(scmp);
        fclose(gcmp);
    end % FOR loop of 1~4 files
end
if dm == 1
    dy = dm;
   % 2. spline.cmd file
    scmf = sprintf('%s/%s_%d%03d_spl.cmd',sub, varname, yr,dy);
    gcmf = sprintf('%s/%s_%d%03d_grd.cmd',sub, varname, yr,dy);

    scmp = fopen(scmf, 'w');
    if scmp < 0
        disp(['MAKESPLINABAT: Cannot creat SCMD FILE: "' scmf '"']);
        return;
    end
    gcmp = fopen(gcmf, 'w');
    if gcmp < 0
        disp(['MAKESPLINABAT: Cannot creat GCMD FILE: "' gcmf '"']);
        return;
    end

    % change directory to DOS formation
    datf = sprintf('%s/%s/%s_%d%03d.txt', fdatway, varname, varname, yr,dy);
    scmf = sprintf('%s/%s/%s_%d%03d_spl.cmd', fcmdway, varname, varname, yr,dy);
    gcmf = sprintf('%s/%s/%s_%d%03d_grd.cmd', fcmdway, varname, varname, yr,dy);
    resf = sprintf('%s/%s/%s_%d%03d.res', fcmdway, varname, varname, yr,dy);

    % Write (1) bat file
    fprintf(batp,'rem Splin: %s\n', datf);
    fprintf(batp,'splina < %s > %s_%d%03d_splina.log\n',   scmf, varname, yr,dy);
    fprintf(batp,'lapgrd < %s > %s_%d%03d_lapgrd.log\n\n', gcmf, varname, yr,dy);

    % Write (2) scmf
    temp = sprintf('%s%s/%s_%d%03d',    fdatway, varname, varname, yr,dy);
    fprintf(scmp,'%s\n',temp);
    fprintf(scmp,'5\n2\n1\n0\n0\n%f %f 0 1\n%f %f 0 1\n', xlr-100*siz, xul+100*siz, ylr-100*siz, yul+100*siz);

    fprintf(scmp,'0 5000 1 1\n1000.0\n0\n2\n1\n0\n1\n1\n');
    fprintf(scmp,'%s\n',datf);

    % a6,2f20.5,f12.3,12f12.3
    dfm(18:19) = ' 1';
    fprintf(scmp,'30000\n%d\n(%s)\n',str2num(dfm(2:3)), dfm);


    n = length(resf);m=n-2;
    fprintf(scmp,'%s\n',resf);

    resf(m:n) = 'opt';
    fprintf(scmp,'%s\n',resf);

    resf(m:n) = 'sur';
    fprintf(scmp,'%s\n',resf);

    resf(m:n) = 'lis';
    fprintf(scmp,'%s\n',resf);

    resf(m:n) = 'cov';
    fprintf(scmp,'%s\n\n\n\n\n',resf);

    resf(m:n) = 'sur';
    fprintf(gcmp,'%s\n',resf);
    fprintf(gcmp,'0\n1\n\n1\n');
    fprintf(gcmp,'1\n%f %f %f\n', xlr, xul, siz);
    fprintf(gcmp,'2\n%f %f %f\n', ylr, yul, siz);
    fprintf(gcmp,'0\n2\n');
    fprintf(gcmp,'%s\n2\n-9999\n', fdem);

    grdf = sprintf('%s%s/%s_%d.flt', fgrdway, varname, varname, yr * 1000 + dy);
    fprintf(gcmp,'%s\n',grdf);
    fprintf(gcmp,'\n\n\n\n');

    fclose(scmp);
    fclose(gcmp);
end
fclose(batp);
% toc
% disp('  ANUSPLIN BAT File exported!!\n');

