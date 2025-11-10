close all;clear all; clc;

latf = 'C:\temp\NCEP2\lat_ncep2_reform.txt';
lonf = 'C:\temp\NCEP2\lon_ncep2_reform.txt';
iway = 'C:\temp\NCEP2\';

nrow = 94;
ncol = 193;
year = 1979;

ftif = 'C:\temp\NCEP2\NCEP2_reform.tif';
proj = geotiffinfo(ftif);
[dat, R, bbox] = geotiffread(ftif);

ftif = 'D:\STSZHANGLI\SRTM\SRTM_Shennj_250m.tif';
proj = geotiffinfo(ftif);
[dem, R, bbox] = geotiffread(ftif);

[box_lat,box_lon] = projinv(proj,bbox(:,1), bbox(:,2)); 
bbox_geo = [box_lat(1)-1 box_lon(1)-1; box_lat(2)+1 box_lat(2)+1];
cell_lat = (max(lat) - min(lat)) / nrow; 
cell_lon = (max(lon) - min(lon)) / ncol;

bbox_pix = round((max(lat) - bbox_geo(:,1)) / cell_lat);
bbox_lin = round((max(lon) - bbox_geo(:,2)) / cell_lon);

v = 1;
var = {'Tavg';'Tmin';'Tmax';'SWrad';'AVP'; 'Prcp'};
lat = load(latf);
lon = load(lonf);

datf = [iway  'NCEP2_' var{v} '_reform_' num2str(1979) '.dat'];

nday = datenum(year + 1, 1, 1) - datenum(year, 1,1);
x0 = 122.5167;
y0 = 52.96667;

p0 = find(abs(lon - x0) < 1);
l0 = find(abs(lat - y0) < 1);

if exist(datf, 'file')
    fp = fopen(datf, 'r');
    dat = fread(fp, [nday nrow * ncol], 'float32');
    fclose(fp);
    
    for iday = 1 : nday
        figure(1);
        xdt = reshape(dat(iday,:), ncol, nrow);
        z0(iday) = xdt(p0,l0);
        imagesc(xdt');
        colormap([white(1);jet(150)]);colorbar('horiz')
        axis equal; axis off  
        title(num2str(iday));
    end
end


