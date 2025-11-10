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

parfor yr = yr1 : yr2
    tic;
    if yr < 2007
        wks = 'H:\temp\China1km';
    else
        wks = 'H:\temp\China1km_0618';
    end
    disp(yr);
    for i = 1 : 46
        dy = (i - 1) * 8 + 1;
        for v = 1 : 7
            ff = [wks '\' vname{v} '\' vname{v} '_' num2str(yr * 1000 + i) '.flt'];
            fp = fopen(ff, 'r');
            dat = fread(fp, [grd.ncols, grd.nrows], 'float32');
            fclose(fp);
            
            % bnd = quantile(dat(dat > -900), [0.05, 0.95]);
            % imagesc(dat', bnd);
            % hold on
            % plot([pix_ll, pix_rl, pix_ru, pix_lu,pix_ll], [lin_ll, lin_rl, lin_ru, lin_lu,lin_ll], 'ro-');
            
            xdt = dat(pix_ll:pix_rl, lin_ru:lin_rl);
            % xbd = quantile(xdt(xdt > -900), [0.05, 0.95]);
            % figure; imagesc(xdt', xbd);
            file_out = [owk '\'  vname{v} '\' vname{v} '_' num2str(yr * 1000 + dy) '.flt'];
            fop = fopen(file_out, 'w');
            fwrite(fop, xdt, 'float32');
            fclose(fop);
            
            file_hdr = [owk '\'  vname{v} '\' vname{v} '_' num2str(yr * 1000 + dy) '.hdr'];
            [h1, h2] = system(['copy ' fhdr_china1km ' ' file_hdr]);
            
            file_prj = [owk '\'  vname{v} '\' vname{v} '_' num2str(yr * 1000 + dy) '.prj'];
            [p1, p2] = system(['copy ' fprj_china1km ' ' file_prj]);
        end
    end
    toc
end
disp(datestr(now()));