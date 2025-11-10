% Read nc dataset provided by BGC (http://www.bgc-jena.mpg.de/geodb/)
% Written by Junbang Wang (IGSNRR, CAS) On Jan 24, 2015
%


clear all;close all;clc
mymap=[white(1); jet(150)];
wks = 'D:\Global8km\datm7\Windfactor';
owk = 'D:\Global8km\datm7\tmp';
if ~exist(owk, 'dir')
    mkdir(owk);
end

fmask = 'D:\Global8km\datm7\tmp\Wfactor_China01deg.tif';
info = geotiffinfo(fmask);
[mask, R, bbox] = geotiffread(fmask);

clat = [10.75, 55.25];
clon = [60.25, 155.25];
cy = clat(1) : 0.5 : clat(2);
cx = clon(1) : 0.5 : clon(2);
[X,Y] = meshgrid(cx,cy);
[n,m] = size(X);
DX = [reshape(X, 1, n*m); reshape(Y, 1, n * m)];


cl = fix((cy + 89.75) / 0.5) + 1;
cp = fix((cx -  0.25) / 0.5) + 1;

ccy = clat(1) : 0.1 : clat(2);
ccx = clon(1) : 0.1 : clon(2);
[CX,CY] = meshgrid(ccx,ccy);
[cn, cm] = size(CX);
GX = [reshape(CX, 1, cn * cm); reshape(CY, 1, cn * cm)];

% imagesc(lat'); colorbar
ilat = -89.75 : 0.5 : 89.75;
ilon = 0.25 : 0.5 : 359.75;

yr1 = 1999; yr2 = 2016;
parfor yr = yr1 : yr2
    disp(yr);
    for jd = 1 : 46
        file = [wks, '\Wfactor_' num2str(yr * 1000 + jd) '.tif'];
        [xt, Rd, bboxd] = geotiffread(file);
        
        x0 = (xt(cp, cl))';
        DY = reshape(x0, 1, n * m);
        st = tpaps(DX, DY);
        
        xd = fnval(st, GX);
        x4 = reshape(xd, cn, cm);
        
        bnd = quantile(x0(:), [0.05, 0.95]);
        figure('visible', 'off');
        imagesc(cx, cy, x4, bnd); colorbar; set(gca, 'Ydir', 'normal');
        title(datestr(datenum(yr, 1, 1)+(jd-1)*8)); set(gca, 'FontSize', 12);
        file_png = [owk, '\Wfactor_' num2str(yr * 1000 + jd) '.png'];
        print(file_png, '-dpng', '-r300');

        % file_out = [owk, '\Wfactor_' num2str(yr * 1000 + jd) '.flt'];
        % fop = fopen(file_out, 'w');
        % fwrite(fop, x4, 'float32');
        % fclose(fop);
        file_out = [owk, '\Wfactor_' num2str(yr * 1000 + jd) '.tif'];
        geotiffwrite2(file_out, x4, R, 'GeoKeyDirectoryTag', info.GeoTIFFTags.GeoKeyDirectoryTag);
    end
    toc
end
