% 按行读取图像数据，写出为
% Data sources:
%   (1) NDVI3g: 1982-2015, C:\Temp\modflt\n1981013.flt
%   (2) MOD15A2: 2000-2012, C:\Temp\MOD15A2_SG\F2000001.bil
%   (3) MCD15A2: 2003-2018, E:\China1km\Fpar\f2002185.bil
% Overlay period: 2003-2012

clear all
close all
tday = date();
t1 = now;
datestr(rem(now,1))
fx =  'H:\Workspace\China1km\Parameters\chinaregion9.tif';
msk = imread(fx);
h = imagesc(msk, [0,10]);
colorbar horz;
axis off
axis equal;
title(sprintf('Mask'))
[nlines, npixels] = size(msk);
S = [npixels nlines];
npix = npixels * nlines;
msk = msk;

% x1_way = 'H:\Workspace\China1km\outway\Results_Merged';
x1_way = 'H:\Workspace\China1km\MeteoGrid\annual';
x1_way = 'H:\Workspace\China1km\Fpar_8daily';
% Daily
dvar = {'GPP','NPP','NEP','Rs','Rn','Rh','PLUE','PET','LUE','ET','Ra','SW','storage','DIF'};%

% Annually
% avar = {'NPP', 'ET', 'GPP','NEP','Rn', 'Rs', 'Rh', 'Total_Ero', 'Water_Ero', 'Wind_Ero'};
% xnd = [0, 1500; 0, 1200; 0 3000; -1000, 1000; 0 3500; 0 3500; 0 1500; 0, 1.4e5; 0, 1.4e5; 0, 10];
avar = {'PRCP', 'TMAX', 'TMIN','TAVG','SSD', 'RHU', 'WIN'};
xnd = [0, 3000; -30, 30; -30 30; -30, 30; 0 12; 0 10; 0 60];

yr1 = 1980;
yr2 = 2018;
yt = (yr1 : yr2)';

c_var = 0; % meteogrid
tic
for v = 6 : 7
    X = []; i = 1;
    for yr = yr1 : yr2
        if c_var == 1
            ff = [x1_way, '\sum\' avar{v} , '_', num2str(yr ) '.flt'];
            disp(ff);
            fp = fopen(ff, 'r');
            dat = fread(fp, [npixels, nlines], 'float32');
            fclose(fp);
        else
            ff = [x1_way, '\' avar{v}, '_', num2str(yr), '.tif'];
            dat = imread(ff);
        end
        imagesc(dat, xnd(v,:)); colorbar('horizonal'); axis off; axis equal
        title([avar{v} ' in ' num2str(yr)]);
        fig = [x1_way '\' avar{v} '_' num2str(yr) '.png'];
        saveas(gca, fig);
        
        for k = 1 : 10
            if k < 10
                x_dat = dat(msk == k & dat >=0);
            else
                x_dat = dat(msk <10 & dat >=0);
            end
            
            X(i,:) = [yr, k,  mean(x_dat), std(x_dat), length(x_dat)];
            X_mn(yr - yr1 + 1, k) = mean(x_dat);
            i = i + 1;
        end
    end
    fxls = [x1_way, '\China1km_'  num2str(yr1)  '-' num2str(yr2) '.xls'];
    
    hdr = {'Year', 'Region_ID', avar{v}, 'Std', 'n'};
    xlswrite(fxls, X, [avar{v} '_all'], 'A2');
    xlswrite(fxls, hdr, [avar{v} '_all'], 'A1');
    
    hdr = {'Year'};
    xlswrite(fxls, X_mn, avar{v}, 'B2');
    xlswrite(fxls, yt, avar{v}, 'A2');
    xlswrite(fxls, hdr, avar{v}, 'B1');
end
toc
t2 = now;
datestr(t1);
datestr(t2);

