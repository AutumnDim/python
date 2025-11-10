% Some guys need the on-site results from GLCV, okay, let's read them and
% output, just do it!
% Fistly, need sites' geolocation information
% Then, please define the projection from a DEM file with geotiff formation

close all; clear all; clc;

site_name = 'China8km';
interpolate_method = 'GLOPEM-CEVSA';

vname_ID = 1;
time_step = 15;
grd_fmt = 'flt';
if vname_ID == 5
    grd_scale = 10;
else
    grd_scale = 1;
end

vname = {'ET'; 'GPP'; 'NPP'; 'PET'; 'LUE'; 'PLUE';  'Rs'};
vad_value = [0 1000; 0 1000; 0 1000; 0 1000; 0 100; 0 100; 0 1000];
vname_unit = {'mm/d', 'gC/m2/d', 'gC/m2/d', 'mm/d', 'gC/MJ', 'gC/MJ', 'MJ/m2/d'};

fsite = 'D:\试验\内蒙古\ET\2012-草地样带经纬度信息.xlsx';

% ftif = 'E:\China1km\Parameters\AsiaDEM_1km.tif';
ftif = 'E:\China8km\Parameters\asia_dem_8km.tif';

meteogrid_wks = ['\\BA-37AEDE\Temporary\China8km\Results'];
% meteogrid_wks = ['\\BA-37AEDE\Workspace\China1km\AsiaMeteo'];
% meteogrid_wks = ['\\BA-37AEDE\Temporary\Shennj\MeteoGrid'];
% meteogrid_wks = ['D:\STSZHANGLI\HuanjGrid'];
% meteogrid_wks = 'F:\Shennj\MeteoGrid';

fxls_out = ['D:\temp\' interpolate_method '_' site_name '_' datestr(now,1) '.xlsx'];


if exist(fsite, 'file') && exist(ftif, 'file')
    % Read sites' geolocation informations
    [dat, txt, raw]  = xlsread(fsite, 'Sheet1', 'A2:F134');
    id0   = dat(:, 1);
    sid   = raw(:, 1);
    sname = raw(:, 2);
    lon   = dat(:, 5);
    lat   = dat(:, 6);
    
    proj = geotiffinfo(ftif);
    
    [srtm, R, bbox] = geotiffread(ftif);   
    srtm = double(srtm);
    
    [x1, y1] = projfwd(proj, lat, lon);

    figure
    bnd = quantile(srtm(srtm > -9000 & srtm < 9999), [0.05 0.95]);
    imagesc(srtm, bnd); colorbar('horizonal');colormap([[0.2 0.2 1]; jet]);
    %srtm(srtm<-9000) = NaN; mapshow(srtm, R);
    hold on;
    
    pix = fix((x1 - proj.SpatialRef.XWorldLimits(1,1)) / proj.PixelScale(1));
    lin = fix((proj.SpatialRef.YWorldLimits(1,2) - y1) / proj.PixelScale(1));
    plot(pix, lin, 'rx'); text(pix, lin, sname, 'FontSize', 10, 'Color', 'red');
    % plot(x0, y0, 'bx'); text(x0, y0, sname(js,:), 'FontSize', 8, 'Color', 'red');
    axis equal;   axis off;  

   
   
    yr = [1981,2015];
    % put all site together to extract their values from MeteoGrid
    glcv_sid = []; glcv_geo = [];glcv_dat = [];
    n1 = length(pix);
    for i = 1 : n1
        glcv_sid{i, 1} = sid{i};
        glcv_geo(i, 1) = pix(i);
        glcv_geo(i, 2) = lin(i);
    end
    for vname_ID = 1 : 7
        if strcmpi(grd_fmt, 'tif')
            [glcv_dt, sdat] = meteogeotiffsample([min(yr),max(yr)], proj, glcv_geo, meteogrid_wks, vname{vname_ID}, vad_value(vname_ID,:), time_step, 1000);
        else
            [glcv_dt, sdat, jneighbor] = meteosample([min(yr),max(yr)], proj, glcv_geo, meteogrid_wks, vname{vname_ID}, vad_value(vname_ID,:), time_step, 100, glcv_sid);
        end
        if ~strcmpi(vname{vname_ID}(1), 'T')
            sdat(sdat < 0) = 0;
        end
        sdat(:,3:end) = sdat(:,3:end) * grd_scale;
        xlswrite(fxls_out, {'YEAR','DOY'}, vname{vname_ID}, 'A1');
        xlswrite(fxls_out, sname', vname{vname_ID}, 'C1');
        xlswrite(fxls_out, sdat, vname{vname_ID}, 'A2');
    end
else
    disp(['Did not find: ' fsite]);
    disp(['      or:' ftif]);
end










