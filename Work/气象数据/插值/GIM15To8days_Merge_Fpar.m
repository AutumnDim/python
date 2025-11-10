% 按行读取图像数据，写出为
% Data sources:
%   (1) NDVI3g: 1982-2015, C:\Temp\modflt\n1981013.flt
%   (2) MCD15A2: 2003-2018, E:\China1km\Fpar\f2002185.bil
% 首先，采用样条曲线，将每半月NDVI3g数据插值为每8天，
% 然后基于2003-2015年数据在NDVI3g与MCD15A2的FPAR间建立关系，
% 这里采用ANN的方法，进行学习，得到net。利用1982-2015年数据，
% 以NET得到校正之后的FPAR数据。
% Overlay period: 2003-2015
clc
clear all
close all
tday = date();
t1 = now;
datestr(rem(now,1))
fx =  'H:\Workspace\China1km\Parameters\chinaregion9.tif';
msk = imread(fx);
% h = imagesc(msk, [0,10]);
% colorbar horz;
% axis off
% axis equal;
% title(sprintf('Mask'))
[nlines, npixels] = size(msk);
S = [npixels nlines];
npix = npixels * nlines;
msk = msk';

x1_way = 'Y:\Database\China1km\NDVI3g_15days\';
x1_var = 'N';
x2_way = 'C:\Temp\MCD_SG\';
x2_var = 'MCD15A2_SG_';
outway = 'C:\Temp\modtif';
ab = 'ab';
N = 5; F = 7;

% Period of MCD15A2 in 2003-2018
yr1 = 2003; yr2 = 2018;
t8 = [];t15 = [];
i1 = 1; i2 = 1;
for yr = yr1 : yr2
    for dy = 1 : 8 : 361
        t8(i1,1) = datenum(yr, 1, 1) + dy - 1;
        i1 = i1 + 1;
    end
    for j = 1 : 24
        if mod(j,2) == 1
            t15(i2,1) = datenum(yr, fix(j-1)/2+1, 1);
        else
            t15(i2,1) = datenum(yr, fix(j-1)/2+1, 16);
        end
        i2 = i2 + 1;
    end
end
yr_0318 = year(t8);
n8 = i1 - 1;
n15 = i2 - 1;
% Period of NDVI3g in 1980-2015
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
yr_8015 = year(tx8);
nx8 = i1 - 1;
nx15 = i2 - 1;

nbk = 20;
n_box = fix(npix / nbk);
if mod(npix, nbk) == 0
    n_bk = nbk;
else
    n_bk = nbk + 1;
end

for bk = 21 : n_bk
    skp_pix4 = (bk - 1) * n_box * 4;
    skp_pix1 = (bk - 1) * n_box;
    % Read NDVI3g in 1980-2015
    yr1 = 1980; yr2 = 2015;
    k = 1; X = []; X_gim  = [];
    for yr = yr1:1:yr2
        for j = 1:24
            ff = [x1_way, x1_var, num2str(yr * 1000 + j) '.flt'];
            if exist(ff, 'file')
                disp([num2str(bk), ', ', ff]);
                fp = fopen(ff, 'r');
                fseek(fp, skp_pix4, -1);
                X_gim(:,k) = fread(fp, [n_box, 1], 'float32');
                % dat = fread(fp, S, 'float32');
                fclose(fp);
                % xdat(j, yr - yr1 +1) = mean(mean(dat(1800:1900,2000:2100)));
                % figure(1); imagesc(dat', [0, 10000]);title(ff);
                k = k+ 1;
            end
        end
    end
    % Read MCD15A2 in 2003-2018
    yr1 = 2003; yr2 = 2018;
    Y_mcd = []; k = 1;
    for yr = yr1 : yr2
        for dy = 1 : 46
            jday = (dy - 1) * 8 + 1;
            ff = [x2_way, x2_var, num2str(yr * 1000 + jday) '.bil'];
            disp(ff);
            fp = fopen(ff, 'r');
            fseek(fp, skp_pix1, -1);
            Y_mcd(:,k) = fread(fp, [n_box, 1], 'int8');
            fclose(fp);
            k = k + 1;
        end
    end
    [n, m] = size(X_gim);
    Y = [];
    stp = fix(n/10);
    for i = 1 : 10000 : n
        y_mcd = (Y_mcd(i,:))';   % MCD15A2 in 2003-2018
        x_gim = X_gim(i, :) * 0.01;    % NDVI3g in 1980-2015
        X_GIM = reshape(x_gim, 24, 36);
        
        bnd_gim = quantile(x_gim, [0, 1]);
        bnd_mcd = quantile(y_mcd, [0.05, 0.95]);
        
        if bnd_gim(2) > bnd_gim(1) && bnd_mcd(2) > bnd_mcd(1)
            % Biweekly to Weekly in 1980-2015
            x0_ndvi3g = pchip(tx15, x_gim, tx8);
            % figure; plot(tx8, x0_ndvi3g, 'b-', tx15, x_gim, 'rx'); datetick('x');
            
            % Weekly NDVI3g in 2003-2015 of overlay period
            x_ndvi3g = x0_ndvi3g(yr_8015 >= 2003 & yr_8015 <= 2015);
            y_mcd_sg = y_mcd(yr_0318 >= 2003 & yr_0318 <= 2015);
            t_0315 = tx8(yr_8015 >= 2003 & yr_8015 <= 2015);
            % pso_net = PSO_BP(x_ndvi3g', y_mcd_sg', 3);
            % figure; plot(t_0315, x_ndvi3g, 'b-', t_0315, y_mcd_sg, 'rx'); datetick('x');
            % y_ndvi3g = sim(pso_net, x_ndvi3g');
            % [bn, bs, r, rs,pn] = regress(y_mcd_sg, [ones(length(y_ndvi3g),1), y_ndvi3g']);
                        
            % rmse_pso = (sum((y_ndvi3g' - y_mcd_sg).^2)/(length(y_mcd_sg) - 1))^0.5;
            % B_pso = [bn(2), pn(1), pn(3), rmse_pso];

            m = length(t_0315);
            m1 = fix(m * 0.7);
            k_0315 = 1 : m;
            sample_index = randi(m, m, 1);
            train_index = sample_index(1:m1);
            test_index = sample_index(m1+1:end);
            
            xs_ndvi3g = x_ndvi3g(train_index);
            ys_mcd_sg = y_mcd_sg(train_index);
            ts_0315 = t_0315(train_index);
            
            xt_ndvi3g = x_ndvi3g(test_index);
            yt_mcd_sg = y_mcd_sg(test_index);
            tt_0315 = t_0315(test_index);
            
            % close all
            % plot(t8, y_ndvi3g/100, 'b-', t8, y_mcd,'r-');
            % hold on
            % plot(tx8, x_ndvi3g/100, 'b-');
            % ylim([0 55]);
            % datetick('x','yyyy');
            % xlabel('Date'); ylabel('NDVI or FPAR');
            % legend('NDVI3g in 1980-2015', 'MCD15A2 in 2003-2015');
            % fig = 'E:\China1km\Figures\NDVI3g_MCD15A2FPAR_2003-2015.png';
            % print('-dpng', '-r600', fig )
            
            % plot(t15, y0/100, 'bx', t8, y_ndvi3g/100, 'k-', t8, y_mcd,'ro-');
            % figure;plot(y_ndvi3g, y_mcd, '.');
            
            % Linear regression to predict fpar by ndvi3g
            % using trainning data 2003-2015
            x = xs_ndvi3g(xs_ndvi3g > 0 & ys_mcd_sg > 0);
            y = ys_mcd_sg(xs_ndvi3g > 0 & ys_mcd_sg > 0);
            
            [b, bs, r, rs,p] = regress(y, [ones(length(x),1), x]);
            
            % test with test  samples
            x_ndvi3g_test = b(1) + b(2) * xt_ndvi3g;
            x_ndvi3g_test(x_ndvi3g_test < 0) = 0;
            [bn, bns, rn, rns,pn] = regress(yt_mcd_sg, [ones(length(x_ndvi3g_test),1), x_ndvi3g_test]);
            rmse_linear = (sum((x_ndvi3g_test - yt_mcd_sg).^2)/(length(yt_mcd_sg) - 1))^0.5;
            B_linear_test = [bn(2), pn(1), pn(3), rmse_linear];
            
            % Linear regression to predict fpar by ndvi3g
            % using all data 2003-2015
            x = x_ndvi3g;
            y = y_mcd_sg;
            
            [b, bs, r, rs,p] = regress(y, [ones(length(x),1), x]);
            
            % test with test  samples
            x_ndvi3g_linear = b(1) + b(2) * x_ndvi3g;
            x_ndvi3g_linear(x_ndvi3g_linear < 0) = 0;
            [bn, bns, rn, rns,pn] = regress(y_mcd_sg, [ones(length(x_ndvi3g_linear),1), x_ndvi3g_linear]);
            rmse_linear = (sum((x_ndvi3g_linear - y_mcd_sg).^2)/(length(yt_mcd_sg) - 1))^0.5;
            B_linear_all = [bn(2), pn(1), pn(3), rmse_linear];
            
            % ANN training and test
            % for kn = 1 : 50
            kn = 24;
            net = feedforwardnet(kn + 10);
            net = configure(net,xs_ndvi3g',ys_mcd_sg');
            net.trainParam.showWindow = false;
            net.trainParam.showCommandLine = false;
            net = train(net,xs_ndvi3g',ys_mcd_sg');
            xt_ndvi3g_ann = net(xt_ndvi3g');
            
            [ba, bas, ra, ras,pa] = regress(yt_mcd_sg, [ones(length(xt_ndvi3g_ann),1), xt_ndvi3g_ann']);
            rmse_ann = (sum((xt_ndvi3g_ann' - yt_mcd_sg).^2)/(length(yt_mcd_sg) - 1))^0.5;
            B_ANN_test = [ba(2), pa(1), pa(3), rmse_ann];
            
            
            % training with all samples in 2003-2015
            kn = 24;
            net = feedforwardnet(kn + 10);
            net = configure(net,xs_ndvi3g',ys_mcd_sg');
            net = train(net, x_ndvi3g',y_mcd_sg');
            x_ndvi3g_ann = net(x_ndvi3g');
            x_ndvi3g_ann(x_ndvi3g_ann < 0) = 0.0;
            [bt, bs, r, rs,pt] = regress(y_mcd_sg, [ones(length(x_ndvi3g_ann'),1), x_ndvi3g_ann']);
            
            x_ndvi3g_pre_ann = b(1) + b(2) * x_ndvi3g_ann;
            
            rmse_ann = (sum((x_ndvi3g_ann' - y_mcd_sg).^2)/(length(y_mcd_sg) - 1))^0.5;
            
            B_ANN_all = [bt(2), pt(1), pt(3), rmse_ann];
            
            % By ANN to predict FPAR in 1980-2015
            x0_ndvi3g_ann = net(x0_ndvi3g');
            X_NDVI3g = reshape(x0_ndvi3g_ann, 46, 36);
            Y_MCD = reshape(y_mcd, 46, 16);
            
            NDVI3g_ANN = mean(X_NDVI3g); yt_8015 = 1980:2015;
            MCD_ANN = mean(Y_MCD);           yt_0318 = 2003:2018;
            
            Fpar3g = NDVI3g_ANN(yt_8015 >2002 & yt_8015 < 2016);
            Fparmcd = MCD_ANN(yt_0318 > 2002 & yt_0318 < 2016);
            [bt, bs, r, rs,pt] = regress(Fparmcd', [ones(length(Fpar3g'),1), Fpar3g']);
            rmse =  (sum((Fpar3g - Fparmcd).^2)/(length(Fparmcd) - 1))^0.5;
            B_annual = [bt(2), pt(1), pt(3), rmse];
            % end
             
            % figure;
            % plot(yt_8015, NDVI3g_ANN, 'b-x');
            % hold on;
            % plot(yt_0318, MCD_ANN, 'r-o');
            % 
            % figure;
            % plot(tx8, x0_ndvi3g_ann, 'b-.');
            % hold on;
            % plot(t8, y_mcd, 'r-.');
            
            % figure
            % plot(y_ndvi3g, y_mcd_sg, '.');
            % hold on
            % plot(y_ndvi3g_pre,y_mcd_sg,'r.')
            % plot(y_ndvi3g_ann,y_mcd_sg,'b.')
            %
            % plot(y_ndvi3g, y_ndvi3g_pre, 'b:');
            % plot(y_ndvi3g_ann,y_ndvi3g_pre_ann, 'r-');
            
            
            % br  = robustfit(y_ndvi3g(y_ndvi3g > 0 & y_mcd_sg' > 0), y_mcd_sg(y_ndvi3g > 0 & y_mcd_sg' > 0));
            % y_ndvi3g_rob = br(1) + br(2) * y_ndvi3g;
            
            % hold on
            % plot(y_ndvi3g, y_ndvi3g_pre, '-');
            
            % figure
            % plot(tx8, x_ndvi3g_ann, 'k-', t8, y_mcd,'r-');
            % legend('NDVI3g_{ANN}',  'MCD15A2');
            %
            % figure
            % plot(t15, y0/100, 'b-', t8, y_ndvi3g/100, 'k-', t8, y_mcd,'r-', t8, y_ndvi3g_pre, 'c-', t8, y_ndvi3g_ann, 'g-');
            % legend('NDVI3g_{biweekly}', 'NDVI3g_{weekly}', 'MCD15A2', 'NDVI3g_{predicted}', 'NDVI3g_{ann}');
        else
            x0_ndvi3g_ann = -9999 * ones([1, nx8]);
            B_linear_test = -9999 * ones([1, 4]); 
            B_linear_all = -9999 * ones([1, 4]);
            B_ANN_test =-9999 * ones([1, 4]);
            B_ANN_all = -9999 * ones([1, 4]);
            B_annual = -9999 * ones([1, 4]);
        end
        
        Y(i,:) = x0_ndvi3g_ann;
        B(i,:) = [B_linear_test, B_linear_all, B_ANN_test, B_ANN_all, B_annual];
    end    % loop for pixels
    fout = ['C:\Temp\Fpar3g_8days\Fpar3g_8days_' num2str(bk) '_Br.flt'];
    fop = fopen(fout, 'w');
    fwrite(fop, B', 'float32');
    fclose(fop);
    
    fout = ['C:\Temp\Fpar3g_8days\Fpar3g_8days_' num2str(bk) '.flt'];
    fop = fopen(fout, 'w');
    fwrite(fop, Y', 'float32');
    fclose(fop);
end

t2 = now;
datestr(t1);
datestr(t2);

