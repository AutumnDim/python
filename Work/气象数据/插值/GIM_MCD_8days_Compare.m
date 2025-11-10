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
msk = msk';

x1_way = 'H:\Workspace\China1km\ndvi3g_8days';

x3_way = 'E:\China1km\Fpar\';
x3_var = 'F';

tx8 = []; i1 = 1;
for yr = 1980:1:2003
    for dy = 1 : 8 : 361
        tx8(i1, 1) = datenum(yr, 1, 1) + dy - 1;
        tx8(i1, 2) = yr;
        tx8(i1, 3) = fix((dy - 1) / 8) + 1;
        i1 = i1 + 1;
    end
end
nx8 = i1 - 1;

nbk = 100;
n_box = fix(npix / nbk);
if mod(npix, nbk) == 0
    n_bk = nbk;
else
    n_bk = nbk + 1;
end

yr = 2003;
j = 25;
tic
X = []; i = 1;
for yr = 2003 : 2003
    for j = 1 : 1 : 46
        ff = [x1_way, '\ndvi3g_8days_' , num2str(yr * 1000 + j) '.flt'];
        disp(ff);
        fp = fopen(ff, 'r');
        gim = fread(fp, [npixels, nlines], 'float32');
        fclose(fp);
        
        % Read MCD15A2 in 2003-2012
        jday = (j - 1) * 8 + 1;
        ff = [x3_way, x3_var, num2str(yr * 1000 + jday) '.bil'];
        disp(ff);
        fp = fopen(ff, 'r');
        mcd = fread(fp, S, 'int8');
        fclose(fp);
        
        mcd(mcd < 0) = -9999;
        
        for k = 1 : 10
            if k < 10
                x_mcd = mcd(msk == k & mcd >=0);
                x_gim = gim(msk == k & gim >=0);
            else
                x_mcd = mcd(msk <10 & mcd >=0);
                x_gim = gim(msk <10 & gim >=0);
            end
            
            X(i,:) = [yr, j, k, mean(x_mcd), mean(x_gim), std(x_mcd), std(x_gim)];
            
            i = i + 1;
        end
        x1 = mcd - gim;
        
        x2 = x1 .^2;
        
        if j == 1
            xs = x2;
        else
            xs = xs + x2;
        end
        
        % figure
        if j == 23
            
            subplot(2,2,1);
            imagesc(gim', [0, 100]);
            colorbar('horizonal'); title(['GIM ' num2str(yr * 1000 + j)]);
            
            subplot(2,2,2);
            imagesc(mcd', [0, 100]);
            colorbar('horizonal'); title(['MCD', num2str(yr * 1000 + j)]);
            
            subplot(2,2,3);
            imagesc(x1', [-100, 100]);
            colorbar('horizonal'); title('GIM-MCD');
        end
        
        if j == 46
            rmse = (xs / (j - 1)) .^0.5;
            
            subplot(2,2,4);
            imagesc(rmse', [0, 100]);
            colorbar('horizonal'); title('RMSE');
        end
    end
end
toc
t2 = now;
datestr(t1);
datestr(t2);

