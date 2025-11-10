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

outway = 'H:\Workspace\China1km\ndvi3g_8days';

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

for bk = 1 : n_bk
    tic
    if bk <= nbk
        n_box = fix(npix / nbk);
    else
        n_box = npix - fix(npix / nbk) * nbk;
    end
    % Y(i,:) = x_ndvi3g_ann: ndvi3g in 1982-2003 and adjusted to mcd15a2
    % Y(i,:) = x_ndvi3g_ann;
    % B(i,:) = [bt(1), bt(2), pt(1), pt(3)];
    ff = ['C:\Temp\ndvi3g_8days\ndvi3g_8days_' num2str(bk) '_Br.flt'];
    fp = fopen(ff, 'r');
    bs = fread(fp, [4, n_box], 'float32');
    fclose(fp);
    
    if bk == 1
        BS = bs;
    else
        BS = [BS  bs];
    end
end
figure; hdr = {'Intcept', 'Slope', 'R_sqr', 'Sig_level'};
for k = 1 : 4
    % subplot(2,2,k)
    b = reshape(BS(k,:), npixels, nlines);
    bnd = quantile(b(b > -900), [0.05, 0.95]);
    figure;
    imagesc(b', bnd); colorbar('horizonal'); title(hdr{k});
    saveas(gca, [outway, '\ndvi3g_8days_validataion_' hdr{k} '.fig']);
end


tic
for bk = 1 : n_bk
    if bk <= nbk
        n_box = fix(npix / nbk);
    else
        n_box = npix - fix(npix / nbk) * nbk;
    end
    ff = ['C:\Temp\ndvi3g_8days\ndvi3g_8days_' num2str(bk) '.flt'];
    disp(ff)
    fp = fopen(ff, 'r');
    YN = fread(fp, [nx8, n_box], 'float32');
    fclose(fp);
    for k = 1 : nx8
        yr = tx8(k, 2);
        j   = tx8(k, 3);
        % dat = reshape(Y, npixels, nlines);
        % figure('visible', 'off');
        % imagesc(dat', [0, 100]);colorbar('horizonal'); title(num2str(yr * 1000 + j));
        % fout = [outway, '\ndvi3g_8days_' , num2str(yr * 1000 + j) '.png'];
        % saveas(gca, fout);
        
        fout = [outway, '\ndvi3g_8days_' , num2str(yr * 1000 + j) '.flt'];
        if bk == 1
        fop = fopen(fout, 'w');
        else
            fop = fopen(fout, 'a');
        end
        fwrite(fop, YN(k,:), 'float32');
        fclose(fop);
        % disp([num2str([bk, yr, j]), '-- ']);
        %  toc
    end
    toc
end
yr = 2003;
j = 25;
figure; k = 1;
for j = 1 : 12 : 46
    ff = [outway, '\ndvi3g_8days_' , num2str(yr * 1000 + j) '.flt'];
    disp(ff);
    fp = fopen(ff, 'r');
    dat = fread(fp, [npixels, nlines], 'float32');
    fclose(fp);
    
    subplot(2,2,min(k, 4));
    % figure
    imagesc(dat', [0, 100]); 
    colorbar('horizonal'); title(num2str(yr * 1000 + j));
    k = k + 1;
end
toc
t2 = now;
datestr(t1);
datestr(t2);

