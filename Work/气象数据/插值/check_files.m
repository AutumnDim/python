close all; clear all; clc;
disp(datestr(now()));

% Asia2China1km
% clip China from Asia and save as float file.
fhdr_asia1km = 'AsiaDEM_1km.hdr';
grd = readgrdhdr(fhdr_asia1km);
% disp(grd);

fprj_china1km = 'H:\Workspace\China1km\China1km.prj';
fhdr_china1km = 'H:\Workspace\China1km\china1km.hdr';
srg = readgrdhdr(fhdr_china1km);
% disp(srg);

pix_ll = fix((srg.xll - grd.xll)/grd.csize);
lin = fix((srg.yll - grd.yll)/grd.csize);
lin_ll = grd.nrows - lin;

pix_rl = pix_ll + srg.ncols - 1;    lin_rl = lin_ll;

pix_lu = pix_ll;    lin_lu = grd.nrows - lin - srg.nrows + 1;

pix_ru = pix_rl;    lin_ru = lin_lu;

vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN';'PRCP'};
yr1 = 1980; yr2 = 2018;
wks = 'H:\temp\China1km';
owk = 'H:\Workspace\China1km\MeteoGrid';
for i = 1 : 7
    sub = [owk '\' vname{i}];
    if ~exist(sub, 'dir')
        mkdir(sub);
    end
end
j = 0; X_mn = [];X_sd = [];X_mx = [];X_mi = [];X_date = [];
X_file = [];
for yr = yr1 : yr2
    tic;
    if yr < 2007
        wks = 'H:\temp\China1km';
    else
        wks = 'H:\temp\China1km_0618';
    end
    disp(yr);
    for i = 1 : 46
        j = (yr - yr1) * 46 + i;
        dy = (i - 1) * 8 + 1;
        for v = 1 : 7
            ff = [wks '\' vname{v} '\' vname{v} '_' num2str(yr * 1000 + i) '.flt'];
            if exist(ff, 'file')
                XA_file(j,v) = 1;
            else
                XA_file(j,v) = 0;
            end
            file_out = [owk '\'  vname{v} '\' vname{v} '_' num2str(yr * 1000 + dy) '.flt'];
            if exist(file_out, 'file')
                XB_file(j,v) = 1;
            else
                XB_file(j,v) = 0;
            end
        end
        X_date(j,:) = [yr, dy];
    end
    toc
end
disp(datestr(now()));