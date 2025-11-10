% use: site_table = grid2points(id, site, lon,lat)
% close all; clear all; clc;
function [DAT, bad_dat, sid, hdr_name] = grid2points(id, site, lon,lat)
% use: site_table = grid2points(id, site, lon,lat)
% check data from 3 aspects as follows:
% (1) unit, to check station data
% (2) observed and interpolated value compare
% (3) time series compare
% vname = {'TMAX'; 'TMIN'; 'PRCP'};
% dlim = [-4500 4500];
% k = 1;
% fs = '/Users/jbwang/cprogram/mat/AsiaFLUX_Sites.txt';
% [id site lon lat] = textread(fs, '%d%s%f%f', 'headerlines', 1);
% fdat = '/nfshome/junbang.wang/China/MeteoGrid/TMAX_2005001.hdr';
fig_site = 0;

% pix = meteo_geo(:,1);
% lin = meteo_geo(:,2);
wks = '/Users/jbwang/Data/China1km/Parameters';

npix = 4998; nline = 4088;


% TAVG
file_name = [wks, filesep, 'TAVG_0020mean.tif'];
if ~exist(file_name, 'file')
    disp(['Cannot find file: ', file_name]);
    site_table = -1;
    return;
end
prj = geotiffinfo(file_name);

[XX, YY] = projfwd(prj, lat, lon);
[TAVG, R, ~] = geotiffread(file_name);
% TAVG = reshape(dat', npix * nline, 1);
[map_lin, map_pix] = map2pix(R, XX, YY);

pix = fix(map_pix(map_pix <= npix & map_pix >= 1 & map_lin <= nline & map_lin >= 1));
lin = fix(map_lin(map_pix <= npix & map_pix >= 1 & map_lin <= nline & map_lin >= 1));
sid = id(map_pix <= npix & map_pix >= 1 & map_lin <= nline & map_lin >= 1);
s_name = site(map_pix <= npix & map_pix >= 1 & map_lin <= nline & map_lin >= 1);
s_lat = lat(map_pix <= npix & map_pix >= 1 & map_lin <= nline & map_lin >= 1);
s_lon = lon(map_pix <= npix & map_pix >= 1 & map_lin <= nline & map_lin >= 1);

num = length(pix);
if fig_site == 1
    figure;
    imagesc(TAVG, [-10, 25]); axis normal
    hold on;
    plot(pix, lin, '.')
    for i = 1 : num
        tavg = TAVG(pix(i), lin(i));
        text(pix(i), lin(i), site{i});
    end
end

DAT = {};
hdr_name = {};  % {'SID','Name','Lat', 'Lon'};
for i = 1 : num
    DAT{i,1} = sid(i);
    DAT{i,2} = s_name{i};
    DAT{i,3} = s_lat(i);
    DAT{i,4} = s_lon(i);
end

s_dat = DAT;

var_name = {'PRCP_0020mean.tif','TAVG_0020mean.tif','NDVI_0019mean.tif',...
    'DEM_China1km.flt','Slope_China1km.flt','Aspect_China1km.flt', 'LAT_China1km.flt', 'LON_China1km.tif'};
vad = [0, -60, 0, -900, -900, -900, -900, -900];
k = 1;
DAT = [];

file_name = [wks, filesep, var_name{4}];
fip = fopen(file_name, 'r');
dat = fread(fip, [npix, nline], 'float32');
fclose(fip);
DEM = dat';

if fig_site == 1
    figure
    imagesc(DEM, [0, 5000]);
    hold on
    plot(pix,lin, 'r.')
    num = length(lin);
    elv = [];
    for i = 1 : num
        elv(i,1) = DEM(pix(i), lin(i));
        if elv(i,1) < -9000
            text(pix(i), lin(i), num2str(i));
            disp([i, elv(i,1)]);
        end
    end
end

bnd = [];
for j = 1 : length(var_name)
    s0 = var_name{j};
    suffix = s0(end-2:end);
    s1 = s0(1:end-4);
    file_name = [wks, filesep, s0];
    % disp(file_name)
    if exist(file_name, 'file')
        if strcmp(suffix, 'tif')
            [dat, ~, ~] = geotiffread(file_name);
        else
            fip = fopen(file_name, 'r');
            dat = fread(fip, [npix, nline], 'float32');
            fclose(fip);
            dat = dat';
        end
        bnd(j,:) = quantile(dat(dat > -9000), [0.00, 0.01, 0.05, 0.25, 0.50, 0.75,0.90, 0.99, 1.00]);
        % disp([j, bnd(j,:)]);
        for i = 1 : num
            if dat(lin(i), pix(i)) < vad(j)
                dw_num = 0; dw = 1;
                while dw <= 10 && dw_num == 0
                    L1 = max(1,     lin(i) - dw);
                    L2 = min(nline, lin(i) + dw);
                    P1 = max(1,     pix(i) - dw);
                    P2 = min(npix,  pix(i) + dw);
                    x0 = dat(L1:L2, P1 : P2);
                    x1 = x0(x0 >= vad(j));
                    if isempty(x1)
                        DAT(i,k) = NaN;
                        bad_dat(i,k) = dw;
                        dw_num = 0;
                        dw = dw + 1;
                    else
                        DAT(i,k) = mean(x1, 'omitnan');
                        bad_dat(i,k) = dw - 1;
                        dw_num = 1;
                    end
                end
            else
                DAT(i,k) = dat(lin(i), pix(i));
                bad_dat(i,k) = 0;
            end
            
        end
        hdr_name{k,1} = s1;
        k = k + 1;
    end
end

%
%% Soil data
file_xls = '/Users/jbwang/Documents/Ouyang_Xihuang/BNPP_V0/Data/cjpe_2022_0174_D1.xlsx';

[s1, s2] = xlsfinfo(file_xls);
%
% Read plot soil data
% 样方号	经度	纬度	海拔	亚类名	5剖面厚	6石砾	7粗砂	8细砂	9粉砂	10粘粒
% 11有机质	12PH_H2O	13PH_KCL	14全氮	15全磷	16全钾	TAVG	PRCP
[~, ~, raw] = xlsread(file_xls, s2{1});
soil_dat_name = raw(1, 2:19);
soil_var_name = {'Longitude','Latitude','Elevation','Subclass','Thickness',...
    'Gravel','Coarse','Sand','Silt','Clay','SOM','PH_H2O','PH_KCL','TN',...
    'TP', 'TK', 'TAVG', 'PRCP'};

v_soil_dat = [5, 6, 7, 8, 9, 10, 11, 12, 14,15,16];

vad_soil = [0, 100];

n = length(v_soil_dat);
soil_wks = '/Users/jbwang/Data/China1km/BNU_Soil/China_1km';

% read sand to determine bad data and replace them with the mean of 3 x 3
file_name = [soil_wks, filesep, soil_dat_name{v_soil_dat(4)}, '.tif'];
% disp(file_name)
[sand, ~, ~] = geotiffread(file_name);

for j = 1 : n
    file_name = [soil_wks, filesep, soil_dat_name{v_soil_dat(j)}, '.tif'];
    
    [dat, ~, ~] = geotiffread(file_name);
    dat = single(dat);
    bnd(k,:) = quantile(dat(dat > -9000), [0.00, 0.01, 0.05, 0.25, 0.50, 0.75,0.90, 0.99, 1.00]);
    
    for i = 1 : num
        if dat(lin(i), pix(i)) <= vad_soil(1) || dat(lin(i), pix(i)) > vad_soil(2)
            dw_num = 0; dw = 1;
            while dw <= 50 && dw_num == 0
                L1 = max(1,     lin(i) - dw);
                L2 = min(nline, lin(i) + dw);
                P1 = max(1,     pix(i) - dw);
                P2 = min(npix,  pix(i) + dw);
                x0 = dat(L1:L2, P1 : P2);
                x1 = x0(x0 > vad_soil(1) & x0 <= vad_soil(2));
                if isempty(x1)
                    DAT(i,k) = NaN;
                    bad_dat(i,k) = dw;
                    dw_num = 0;
                    dw = dw + 1;
                else
                    DAT(i,k) = mean(x1, 'omitnan');
                    bad_dat(i,k) = dw - 1;
                    dw_num = 1;
                end
            end
        else
            DAT(i,k) = dat(lin(i), pix(i));
            bad_dat(i,k) = 0;
        end
    end
    hdr_name{k,1} = soil_var_name{v_soil_dat(j)};
    k = k + 1;
end
%dem = DAT(:, 4);
vad_id = id; %(dem > -9000);
vad_sd = s_dat; % (vad_id,:);
% DAT = DAT(dem > -9000, :);
% site_table = array2table(DAT, 'VariableNames', hdr_name);

