% GIM15To8days_Merge_singlefile
% this file used to read the outputs from GIM15To8days_Merge_Fpar.m
% and write them as a small file for each regression coefficient, and
% fpar3g of each 8-days after adjusting through GIM15To8days_Merge_Fpar.m
% Firstly, read regressed results (layer = 20) from 21 files as nbk = 21
% layer_method_or_data = {'linear_test', 'linear_all', 'ANN_test', 'ANN_all', 'Annual'};
% layer_coefficients  = {'Slope', 'Rsqr', 'Sig', 'RMSE'};
% write 21 block into a file named as method_coefficient.flt
% Secondly, read the estimated fpar3g using ndvi3g in
% 1980-2015 as inputs through ANN method based on the data of
% mcd15a2 and ndvi3g in 2003-2015


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

x1_way = 'C:\Temp\MCD_SG\';
x1_var = 'MCD15A2_SG_';

% switch sub_mod
% sub_mod:
% 1 for merging slope
%     2 for merging time series
%         3 for draw map for slope
%             4 for drawing map of time series

sub_mod = 2;

hdr_file = 'H:\Workspace\China1km\mat\china1km.hdr';
prj_file = 'H:\Workspace\China1km\mat\china1km.prj';

outway = 'Y:\ZXL\Fpar3g_8days';
sub = [outway '\br'];
if ~exist(sub, 'dir')
    mkdir(sub);
end
tx15 = []; tx8 = []; i1 = 1; i2 = 1;
for yr = 1980:1:2015
    for dy = 1 : 8 : 361
        tx8(i1,1) = datenum(yr, 1, 1) + dy - 1;
        i1 = i1 + 1;
    end
    for j = 1 : 24
        if mod(j,2) == 1
            tx15(i2,1) = datenum(yr, fix(j-1)/2+1, 1);
        else
            tx15(i2,1) = datenum(yr, fix(j-1)/2+1, 16);
        end
        i2 = i2 + 1;
    end
end
nx8 = i1 - 1;
nx15 = i2 - 1;

nbk = 20;
n_box = fix(npix / nbk);
if mod(npix, nbk) == 0
    n_bk = nbk;
else
    n_bk = nbk + 1;
end
% B_annual = [bt(2), pt(1), pt(3), rmse]
% B(i,:) = [B_linear_test, B_linear_all, B_ANN_test, B_ANN_all, B_annual];
% ff = ['C:\Temp\Fpar3g_8days\Fpar3g_8days_' num2str(bk) '_Br.flt'];
hdr_mt = {'linear_test', 'linear_all', 'ANN_test', 'ANN_all', 'Annual'};
hdr_br  = {'Slope', 'Rsqr', 'Sig', 'RMSE'};
j = 1; for m = 1 : 5, for b = 1 : 4, hdr{j,1} = [hdr_mt{m} '_' hdr_br{b}]; j = j + 1; end, end


for bk = 1 : n_bk
    tic
    if bk <= nbk
        n_box = fix(npix / nbk);
    else
        n_box = npix - fix(npix / nbk) * nbk;
    end
    
    
    
    switch sub_mod
        case 1
            
            % Y(i,:) = x_ndvi3g_ann: ndvi3g in 1982-2003 and adjusted to mcd15a2
            % Y(i,:) = x_ndvi3g_ann;
            % B(i,:) = [bt(1), bt(2), pt(1), pt(3)];
            % B_annual = [bt(2), pt(1), pt(3), rmse]
            % B(i,:) = [B_linear_test, B_linear_all, B_ANN_test, B_ANN_all, B_annual];
            
            ff = ['C:\Temp\Fpar3g_8days\Fpar3g_8days_' num2str(bk) '_Br.flt'];
            fp = fopen(ff, 'r');
            bs = fread(fp, [20, n_box], 'float32');
            fclose(fp);
            for i = 1 : 20
                ff = ['H:\Workspace\China1km\Fpar3g_8days\br\' hdr{i} '.flt' ];
                if bk == 1
                    fop = fopen(ff, 'w');
                else
                    fop = fopen(ff, 'a');
                end
                fwrite(fop, bs(i,:), 'float32');
                fclose(fop);
            end
            
            
        case 2
            ff = ['C:\Temp\Fpar3g_8days\Fpar3g_8days_' num2str(bk) '.flt'];
            fp = fopen(ff, 'r');
            YN = fread(fp, [nx8, n_box], 'float32');
            fclose(fp);
            [nc, mc] = size(YN);
            if nc ~= nx8 || mc ~= n_box
                disp([nc, mc]);
                disp(ff);
            end
            
            for yr = 1980:1:2015
                for j = 1:46
                    jday = (j - 1) * 8 + 1;
                    fout = [outway, '\fpar3g_8days_ann' , num2str(yr * 1000 + jday) '.flt'];
                    if bk == 1
                        fop = fopen(fout, 'w');
                    else
                        fop = fopen(fout, 'a');
                    end
                    
                    k = (yr - 1980) * 46 + j;
                    fwrite(fop, YN(k, :), 'float32');
                    fclose(fop);
                    
                    %             if bk == 1
                    %                 Y = YN(k,:);
                    %             else
                    %                 Y = [Y  YN(k,:)];
                    %             end
                end
            end
    end
    disp([num2str(bk), ', ', num2str(toc)]);
    
end
yr = 2003;
j = 23;
switch sub_mod
    case 4
        for yr = 1980 : 2015
            for j = 1 : 46
                ff = [outway, '\fpar3g_8days_ann' , num2str(yr * 1000 + jday) '.flt'];
                
                fp = fopen(ff, 'r');
                dat = fread(fp, [npixels, nlines], 'float32');
                fclose(fp);
                
                imagesc(dat', [0, 100]);colorbar('horizonal');
                axis off; title(['FPAR3g ' , num2str(yr * 1000 + jday)]);
                ff = [outway, '\fpar3g_8days_ann' , num2str(yr * 1000 + jday) '.png'];
                saveas(gca, ff);
                
                ff = [outway, '\fpar3g_8days_ann' , num2str(yr * 1000 + jday) '.hdr'];
                [s1, s2] = system(['copy ' hdr_file ' ' ff]);
                
                ff = [outway, '\fpar3g_8days_ann' , num2str(yr * 1000 + jday) '.prj'];
                [s1, s2] = system(['copy ' prj_file ' ' ff]);
                
            end
        end
        
    case 3
        
        for i = 1 : 20
            ff = ['H:\Workspace\China1km\Fpar3g_8days\br\' hdr{i} '.flt' ];
            
            fip = fopen(ff, 'r');
            b = fread(fip, [npixels, nlines], 'float32');
            fclose(fip);
            
            bnd = quantile(b(b > -900), [0.05, 0.95]);
            if mod(i,4) == 2 || mod(i,4) == 3
                bnd = [0, 1];
            end
            imagesc(b', bnd); colorbar('horizonal');
            axis off; title(hdr{i});
            ff = ['H:\Workspace\China1km\Fpar3g_8days\br\' hdr{i} '.png' ];
            saveas(gca, ff);
            
            ff = ['H:\Workspace\China1km\Fpar3g_8days\br\' hdr{i} '.hdr' ];
            [s1, s2] = system(['copy ' hdr_file ' ' ff]);
            
            ff = ['H:\Workspace\China1km\Fpar3g_8days\br\' hdr{i} '.prj' ];
            [s1, s2] = system(['copy ' prj_file ' ' ff]);
        end
end
t2 = now;
datestr(t1);
datestr(t2);

