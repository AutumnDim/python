% 按行读取图像数据，写出为
% Data sources:
%   (1) NDVI3g: 1982-2015, C:\Temp\modflt\n1981013.flt
%   (2) MOD15A2: 2000-2012, C:\Temp\MOD15A2_SG\F2000001.bil
%   (3) MCD15A2: 2003-2018, E:\China1km\Fpar\f2002185.bil
% Overlay period: 2003-2012

clear all
close all
clc
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
msk = msk';

x1_way = 'Y:\Database\China1km\NDVI3g_15days';

out_way = 'E:\China1km\temp\';
x3_var = 'F';

tic
X = []; i = 1;
for yr = 2000 : 2002
    for j = 1 : 1 : 46
        jday = (j - 1) * 8 + 1;
        if yr == 2002 && jday >= 185
            break;
        else
            ff = [x1_way, '\ndvi3g_8days_' , num2str(yr * 1000 + j) '.flt'];
            disp(ff);
            fp = fopen(ff, 'r');
            fpar = fread(fp, [npixels, nlines], 'float32');
            fclose(fp);
            fpar(fpar < 0) = 255;
            
            % Read MCD15A2 in 2003-2012
            fout = [out_way, x3_var, num2str(yr * 1000 + jday) '.bil'];
            disp(fout);
            fop = fopen(fout, 'w');
            fwrite(fop, fpar, 'uint8');
            fclose(fop);
        end
    end
end
toc