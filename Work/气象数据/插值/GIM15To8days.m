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

x1_way = 'C:\Temp\modflt\';
x1_var = 'N';
x2_way = 'C:\Temp\MOD15A2_SG\';
x2_var = 'F';
x3_way = 'E:\China1km\Fpar\';
x3_var = 'F';
outway = 'C:\Temp\modtif';
ab = 'ab';
N = 5; F = 7;

% NDVI3g
yr1 = 2003;
yr2 = 2012;
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
n8 = i1 - 1;
n15 = i2 - 1;
tx15 = []; tx8 = []; i1 = 1; i2 = 1;
for yr = 1980:1:2003
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

nbk = 100;
n_box = fix(npix / nbk);
if mod(npix, nbk) == 0
    n_bk = nbk;
else
    n_bk = nbk + 1;
end

for bk = 1 : n_bk
    skp_pix4 = (bk - 1) * n_box * 4;
    skp_pix1 = (bk - 1) * n_box;
    % Read NDVI3g in 2003-2012
    k = 1; X = [];
    for yr = yr1:1:yr2
        for j = 1:24
            ff = [x1_way, x1_var, num2str(yr * 1000 + j) '.flt'];
            if exist(ff, 'file')
                disp([num2str(bk), ', ', ff]);
                fp = fopen(ff, 'r');
                fseek(fp, skp_pix4, -1);
                X(:,k) = fread(fp, [n_box, 1], 'float32');
                
                % dat = fread(fp, S, 'float32');
                fclose(fp);
                
                % xdat(j, yr - yr1 +1) = mean(mean(dat(1800:1900,2000:2100)));
                % figure(1); imagesc(dat', [0, 10000]);title(ff);
                k = k+ 1;
            end
        end
    end
    % Read NDVI3g in 1980-2003
    k = 1; X_83 = [];
    for yr = 1980:1:2003
        
        for j = 1:24
            ff = [x1_way, x1_var, num2str(yr * 1000 + j) '.flt'];
            if exist(ff, 'file')
                disp([num2str(bk), ', ', ff]);
                fp = fopen(ff, 'r');
                fseek(fp, skp_pix4, -1);
                X_83(:,k) = fread(fp, [n_box, 1], 'float32');
                fclose(fp);
                k = k+ 1;
            end
        end
    end
    
    
    % Read MCD15A2 in 2003-2012
    Y_mcd = []; k = 1;
    for yr = yr1 : yr2
        for dy = 1 : 46
            jday = (dy - 1) * 8 + 1;
            ff = [x3_way, x3_var, num2str(yr * 1000 + jday) '.bil'];
            disp(ff);
            fp = fopen(ff, 'r');
            fseek(fp, skp_pix1, -1);
            Y_mcd(:,k) = fread(fp, [n_box, 1], 'int8');
            fclose(fp);
            k = k + 1;
        end
    end
    [n, m] = size(X);
    Y = [];
    stp = fix(n/10);
    parfor i = 1 : n
        y0 = X(i, :);
        x0 = X_83(i, :);
        
        bnd = quantile(y0, [0, 1]);
        if bnd(2) > bnd(1)
            y_ndvi3g = pchip(t15, y0, t8);
            %
            x_ndvi3g = pchip(tx15, x0, tx8);
        else
            y_ndvi3g = bnd(1) * ones([n8,1]);
            
            x_ndvi3g = bnd(1) * ones([nx8, 1]);
        end
        
        % ndvi3g in 1980-2003
        % ndvi3g in 1982-2003 and adjusted to mcd15a2
        x0 = X_83(i, :);
        
        bnd = quantile(x0, [0, 1]);
        if bnd(2) > bnd(1)
            x_ndvi3g = pchip(tx15, x0, tx8);
            x_ndvi3g(x_ndvi3g < 0) = 0.0;
        else
            x_ndvi3g = bnd(1) * ones([nx8, 1]);
        end

        y_mcd = (Y_mcd(i,:))';
        bnd_mcd = quantile(y_mcd, [0.05, 0.95]);
        if bnd_mcd(2) > bnd_mcd(1)
            % [b, g]=sgolay(N,F);
            % ycenter = conv(y_mcd', b((F + 1) / 2,:), 'valid');
            % ybegin = b(end:-1:(F+3)/2,:) * x(F:-1:1);
            % yend = b((F-1)/2:-1:1,:) * x(end:-1:end-(F-1));
            % y_mcd_sgolay = [ybegin; ycenter; yend];
            % y_mcd_sgolay(y_mcd_sgolay < 0) = 0;
            % figure
            y_mcd_sg = sgolayfilt(y_mcd,N,F);
            ysd = y_mcd_sg';
            
            % plot(t8, y_mcd_sg, 'bx-', t8, y_mcd,'r-', t8, y_mcd_sgolay, 'c-');
            % hold on;
            % y_mcd_sg = sgolayfilt(y_mcd_sg,N,F);
            % plot(t8, y_mcd_sg, 'b-', t8, y_mcd,'rx');
            % y_mcd_sg = sgolayfilt(y_mcd_sg,N,F);
            % plot(t8, y_mcd_sg, 'ko', t8, y_mcd,'r-');
            
            % plot(t15, y0/100, 'bx', t8, y_ndvi3g/100, 'k-', t8, y_mcd,'ro-');
            % figure;plot(y_ndvi3g, y_mcd_sg, '.');
            
            x = y_ndvi3g(y_ndvi3g > 0 & y_mcd_sg > 0);
            y = y_mcd_sg(y_ndvi3g > 0 & y_mcd_sg > 0);
            
            [b, bs, r, rs,p] = regress(y, [ones(length(x),1), x]);
            
            y_ndvi3g_pre = b(1) + b(2) * y_ndvi3g;
            y_ndvi3g_pre(y_ndvi3g_pre < 0) = 0;
            net = feedforwardnet(20);
            net = configure(net,y_ndvi3g',y_mcd_sg');
            net.trainParam.showWindow = false;
            net.trainParam.showCommandLine = false;
            net = train(net,y_ndvi3g',y_mcd_sg');
            y_ndvi3g_ann = net(y_ndvi3g');
            x_ndvi3g_ann = net(x_ndvi3g');
            x_ndvi3g_ann(x_ndvi3g_ann < 0) = 0.0;
            % plot(y_ndvi3g,y_ndvi3g_pre,'x',y_ndvi3g,y_ndvi3g_ann,'*')
            % plot(y_ndvi3g_ann, y_mcd_sg, 'x');
            [bt, bs, r, rs,pt] = regress(y_mcd_sg, [ones(length(y_ndvi3g_ann'),1), y_ndvi3g_ann']);
            
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
            x_ndvi3g_ann = -9999 * ones([1, nx8]);
            bt = -9999 * ones([2, 1]);
            pt = -9999 * ones([1, 4]);
        end
        
        Y(i,:) = x_ndvi3g_ann;
        B(i,:) = [bt(1), bt(2), pt(1), pt(3)];
    end    % loop for pixels
    fout = ['C:\Temp\ndvi3g_8days\ndvi3g_8days_' num2str(bk) '_Br.flt'];
    fop = fopen(fout, 'w');
    fwrite(fop, B', 'float32');
    fclose(fop);
    
    fout = ['C:\Temp\ndvi3g_8days\ndvi3g_8days_' num2str(bk) '.flt'];
    fop = fopen(fout, 'w');
    fwrite(fop, Y', 'float32');
    fclose(fop);
end

t2 = now;
datestr(t1);
datestr(t2);

