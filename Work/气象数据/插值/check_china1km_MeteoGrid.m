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
j = 1;
X_date = [];
for yr = yr2 : -1: yr1
    for i = 1 : 46
        X_date(j,:) = [j, yr, i];
        j = j + 1;
    end
end
for j = 1 : length(X_date)
    yr = X_date(j, 2);
    i = X_date(j,3);
    tic;
    if yr < 2007
        wks = 'H:\temp\China1km';
    else
        wks = 'H:\temp\China1km_0618';
    end
    disp(yr);
    dy = (i - 1) * 8 + 1;
%     X_mn = [];X_sd = [];X_mx = [];X_mi = [];
    for v = 1 : 7
        
        file_out = [owk '\'  vname{v} '\' vname{v} '_' num2str(yr * 1000 + dy) '.flt'];
        if exist(file_out, 'file')
            fip = fopen(file_out, 'r');
            xdt = fread(fip, [srg.ncols, srg.nrows], 'float32');
            fclose(fip);
            
        else
            
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
            clear dat;
        end
%         bnd = quantile(xdt(xdt > -900), [0.05, 0.95]);
%         if bnd(2) > bnd(1)
%             figure('visible', 'off');
%             imagesc(xdt', bnd); colorbar('horizonal'); title([vname{v} num2str(yr*1000+dy)]);
%             axis off;
%             file_out = [owk '\'  vname{v} '\' vname{v} '_' num2str(yr * 1000 + dy) '.png'];
%             saveas(gca, file_out);
%             
%             X_mn(1,v) = mean(xdt(xdt > -900));
%             X_sd(1, v) = std(xdt(xdt > -900));
%             X_mx(1, v) = max(xdt(xdt > -900));
%             X_mi(1, v) = min(xdt(xdt > -900));
%         else
%             X_mn(1,v) = -9999;
%             X_sd(1,v) = -9999;
%             X_mx(1,v) = -9999;
%             X_mi(1,v) = -9999;
%         end
    end
%     X_dat(j,:) = [yr, dy, X_mn, X_sd, X_mx, X_mi];
    toc
end
% hdr = {'Year','DOY','TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
% file_out = [owk '\China1km_MeteoGrid_' num2str(yr1) '-' num2str(yr2) .xls];
% xlswrite(file_out, hdr, 'Mean', 'A1');
% xlswrite(file_out, X_dat, 'Mean', 'a2');
% xlswrite(file_out, hdr, 'Std', 'A1');
% xlswrite(file_out, [X_date, X_sd], 'Std', 'C2');
% xlswrite(file_out, hdr, 'Max', 'A1');
% xlswrite(file_out, [X_date, X_mx], 'Max', 'C2');
% xlswrite(file_out, hdr, 'Min', 'A1');
% xlswrite(file_out, [X_date, X_mi], 'Min', 'C2');

disp(datestr(now()));