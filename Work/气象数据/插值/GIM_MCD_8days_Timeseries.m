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

x1_way = 'H:\Workspace\China1km\ndvi3g_8days';

x3_way = 'E:\China1km\Fpar\';
x3_var = 'F';

tic
X = []; i = 1;
for yr = 1980 : 2018
    for j = 1 : 1 : 46
        jday = (j - 1) * 8 + 1;
        if yr < 2003
            ff = [x1_way, '\ndvi3g_8days_' , num2str(yr * 1000 + j) '.flt'];
            disp(ff);
            fp = fopen(ff, 'r');
            fpar = fread(fp, [npixels, nlines], 'float32');
            fclose(fp);
        else
            % Read MCD15A2 in 2003-2012
            ff = [x3_way, x3_var, num2str(yr * 1000 + jday) '.bil'];
            disp(ff);
            fp = fopen(ff, 'r');
            fpar = fread(fp, S, 'int8');
            fclose(fp);
            
            fpar(fpar < 0) = -9999;
        end
        
        for k = 1 : 10
            if k < 10
                x_fpar = fpar(msk == k & fpar >=0);
            else
                x_fpar = fpar(msk <10 & fpar >=0);
            end
            
            X(i,:) = [yr, j, k, jday, mean(x_fpar),  std(x_fpar)];
            
            i = i + 1;
        end
        
    end
end
toc
r = X(:,3);
yt = X(:,1);
XA = []; XS = [];
for k = 1 : 10
    x0 = X(r == k, :);
    t = datenum(x0(:,1), 1, 1) + x0(:,4);
    m = month(t);
    for yr = 1980 : 2018
        xa = x0(x0(:,1) == yr, 5);
        xs = x0(x0(:, 1) == yr & m >= 7 & m <=8, 5);
        j = yr - 1979;
        XA(j, k) = mean(xa);
        XS(j, k) = mean(xs);
    end
end
yr = (1980 : 2018)';
figure
plot(yr, XA(:,10), 'b.-', yr, XS(:,10), 'gx-');
B = [];
for k = 1 : 10
    figure(k)
    
    plotyy(yr, XA(:,k), yr, XS(:,k));
    
    ya = XA(:,k);
    [ba, bas, ra, ras, pa] = regress(ya, [ones([length(yr), 1]), yr]);
    
    ys = XS(:,k);
    [bs, bss, rs, rss, ps] = regress(ya, [ones([length(yr), 1]), yr]);    
    
    B(k, :) = [k, ba(2), pa(1), pa(3), bs(2), ps(1), ps(3)];
end