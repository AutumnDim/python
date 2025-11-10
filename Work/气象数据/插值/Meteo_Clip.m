% function Meteo_Clip()
lon = [500000, 1100000];
lat = [2400000, 3100000];
pnt = [lon(1), lat(2); lon(2), lat(1)];

npix = (lon(2) - lon(1)) / 1000;
nlin = (lat(2) - lat(1)) / 1000;

ftif = 'H:\Workspace\China1km\Parameters\chinaregion9.tif';
proj = geotiffinfo(ftif);
[mcd, R, bbox] = geotiffread(ftif);
imagesc(mcd, [0 10]);
hold on;
pix = fix((lon - proj.SpatialRef.XWorldLimits(1,1)) / proj.PixelScale(1));
lin = fix((proj.SpatialRef.YWorldLimits(1,2) - lat) / proj.PixelScale(1));
plot(pix, lin, 'rx'); % text(cern_pix, cern_lin, sname(js,:), 'FontSize', 10, 'Color', 'red');
hold off;

vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
vbnd = [-10, 30; 0, 2000; -10, 20; 0, 25; 0 100; 0 8; 0 8];

dat = imread('e:\temp\prcp.png');
[~,m,z] = size(dat);
prcp_color =reshape(dat(1,:,:), m, z);
dat = imread('e:\temp\temperature.png');
[~,m,z] = size(dat);
temp_color =reshape(dat(1,:,:), m, z);

vcolor{1,1} = [white(1); parula(350)];
vcolor{2,1} = [white(1); double(prcp_color) / 255.0]; % [white(1); flipud(parula)];
vcolor{3,1} = [white(1); parula(350)];
vcolor{4,1} = [white(1); parula(350)];
vcolor{5,1} = [white(1); flipud(parula)];
vcolor{6,1} = [white(1); double(temp_color) / 255.0]; %
vcolor{7,1} = [white(1); parula(350)];

fxls = 'e:\temp\ET_QC\Color_tables.xlsx';
hdr = {'R','G','B'};
for i = 1 : 7
    xlswrite(fxls, fix(vcolor{i, 1} * 255), vname{i}, 'A2');
    xlswrite(fxls, hdr, vname{i}, 'A1');
end

wks_in = 'H:\Workspace\China1km\MeteoGrid';
wks_out = 'E:\Fujian';
file_hdr = 'E:\Fujian\fujian_prcp.hdr';
file_prj = 'E:\Fujian\fujian_prcp.prj';

v = 7;
yr1 = 2000;
yr2 = 2018;
annual = 1;
close all;
ftif = 'E:\Fujian\PRCP_1980.tif';
info = geotiffinfo(ftif);
proj = geotiffinfo(ftif);
[mcd, R, bbox] = geotiffread(ftif);

if annual == 1
    sub = [wks_out '\annual'];
    if ~exist(sub,'dir')
        mkdir(sub);
    end
    
    for v = 1 : 7
        for yr = yr1 : yr2
            ff = [wks_in '\annual\', vname{v}, '_' num2str(yr), '.tif' ];
            if exist(ff, 'file')
                dat = imread(ff);
                
                x = dat(lin(2):lin(1), pix(1):pix(2));
                bnd = quantile(x(x > -900), [0.05, 0.95]);
                disp(bnd);
                
                figure('visible', 'off')
                imagesc(x, bnd); colorbar('horizonal');
                colormap(vcolor{v,1});
                title([vname{v} ' ' num2str(yr)]);
                axis equal; axis off;
                
                % file_out = [wks_out '\annual\' vname{v}, '_' num2str(yr) '.flt'];
                % fop = fopen(file_out, 'w');
                % fwrite(fop, x', 'float32');
                % fclose(fop);
                %
                % file_out = [wks_out '\annual\' vname{v} '_' num2str(yr) '.hdr'];
                % [s1, s2] = system(['copy ', file_hdr, ' ', file_out]);
                %
                % file_out = [wks_out '\annual\' vname{v} '_' num2str(yr) '.prj'];
                % [s1, s2] = system(['copy ', file_prj, ' ', file_out]);
                
                file_out = [wks_out '\annual\' vname{v} '_' num2str(yr) '.tif'];
                geotiffwrite2(file_out, x, R, 'GeoKeyDirectoryTag', info.GeoTIFFTags.GeoKeyDirectoryTag);
                
            end
        end
    end
else
    for yr = yr1 : yr2
        ff = [wks_in '\' vname{v} '\' , vname{v}, '_' num2str(yr), '.tif' ];
    end
end
