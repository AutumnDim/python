close all; clear all; clc

nbk = 41;
wks = '/Users/jbwang/Data/China1km/Annual';
owk = '/Users/jbwang/Data/China1km/Annual/Trend';
v_name = {'IM', 'PRCP', 'TMAX', 'TMIA'};
v = 1;

nlines = 4088;
npixels = 4998;

yr1 = 1980;
yr2 = 2018;
xt = yr1 : yr2;
brk = yr1 + 2 : yr2 - 2;
nyr = yr2 - yr1 + 1;

yt = [1980 2018; 1980 2000; 2000 2018; 1980 1990; 1990 2000; 2000 2010; 2010 2018];

pro = 1;

if pro == 100
ff = '/Users/jbwang/Downloads/EQI_2016.tif';
dat = imread(ff);

bnd = quantile(dat(dat > -9999), [0.01, 0.99]);
figure;
imagesc(dat, bnd); colorbar horz;
colormap([white(1); parula(250)])
axis equal off
end

if pro == 1
    v_str = {'slope', 'r2', 'p_value', 'mean'};

    s_name = {'Trend', 'R^2', 'P_{value}'};
    
    np = 2790;
    nl = 2282;

    for v = 1 : length(v_name)
        s_name{4} = v_name{v};
        figure(v);

        for s = 1 : 4
            file_name = [owk, filesep, v_name{v}, filesep, v_str{s}, '_1980_2018.tif'];
            if exist(file_name, 'file')
                fp = fopen(file_name, 'r');
                bs = fread(fp, [np, nl], 'float32');
                fclose(fp);
            else
                disp('The file is not exist!')
                return;
            end

            bnd = quantile(bs(bs > -9000 & bs < 32767), [0.05, 0.95]);
            disp([v_name{v}, '   ', v_str{s}, '  ', num2str([bnd, mean(bs(bs > -9000 & bs < 32767), 'omitnan')], '%9.2f')])

            if s == 2 || s == 3
                bnd = [0,1];
            end
            subplot(2, 2, s);
            imagesc(bs', bnd);colorbar horz;
            title(s_name{s});

        end
    end
end

if pro == 3
    if mod(nlines, nbk) == 0
        nk = nbk;
    else
        nk = nbk + 1;
    end
    nL = fix(nlines / nbk);
    bcd = [-100, 100];
    L = [];
    for bk = 1 : nk
        i1 = (bk - 1) * nL + 1;
        if bk <= nbk
            i2 = bk * nL;
        else
            i2 = nlines;
        end
        % L(bk,:) = [bk, i1, i2];
        X  = [];
        for yr = yr1 : yr2
            j = yr - yr1 + 1;
            ff = [wks, filesep, v_name{v}, filesep, v_name{v}, '_' num2str(yr) '.tif'];
            dat = imread(ff);
            x1 = dat(i1:i2,:);
            bnd = quantile(dat(dat > -9000), [0.05, 0.95]);
            imagesc(dat, bcd);colorbar horz;
            [n, m] = size(x1);
            x2 = reshape(x1, n * m, 1);
            X(:,j) = x2;
        end
        [n, m] = size(X);
        parfor i = 1 : n
            ys = X(i, :);
            y0 = ys(ys > -900);
            t0 = xt(ys > -900);
            if length(y0) < 39
                bs = -9999 * ones([1, 7]);
                rs = -9999 * ones([1, 7]);
                ps = -9999 * ones([1, 7]);
                ts = -9999 * ones([1, 12]);
            else
                for t = 1 : 7

                    t1 = yt(t, 1); t2 = yt(t,2);
                    j1 = t1 - 1980 + 1;
                    j2 = t2 - 1980 + 1;
                    tx = t1 : t2;
                    y0 = ys(:, j1 : j2);
                    % y0 = yx(i, :);
                    y1 = y0(y0 > -900);
                    x1 = tx(y0 > -900);
                    n1 = length(y1);
                    if length(y1) == t2 - t1 + 1
                        [b1, rs, r1, r2, p1] = regress(y1', [ones([n1,1]) x1']);
                    else
                        b1 = ones([1,2]) * (-9999);
                        p1 = ones([1,4]) * (-9999);
                    end
                    bs(1, t) = b1(2);
                    rs(1, t) = p1(1);
                    ps(1, t) = p1(3);
                    % if t == 0
                    %     % r1 =  min(rmse)
                    %     % tp = brk(rmse == r1)
                    %     % b1 = bs(rmse == r1)
                    %     % p1 = ps(rmse == r1)
                    %     [b1, r1, p1, tp] = mypiecewise(t0,y0,brk);
                    %     % plot(t0, y0, '.');
                    %     % x1 = t1 : tp;
                    %     % x2 = tp : t2;
                    %     % hold on;
                    %     % plot(x1, b1(1) + b1(2) * x1, 'r-');
                    %     % plot(x2, b1(3) + b1(4) * x2, 'b-');
                    %
                    %     ts = [b1, p1, r1, tp];
                    % end
                end
            end
            B(i, :) = bs;
            R(i, :) = rs;
            P(i, :) = ps;
            % T(i, :) = ts;
        end
        fout = [owk, filesep, v_name{v}, '_Slope_' num2str(bk) '.flt'];
        fop = fopen(fout, 'w');
        fwrite(fop, B, 'float32');
        fclose(fop);

        fout = [owk, filesep, v_name{v}, '_RSQ_' num2str(bk) '.flt'];
        fop = fopen(fout, 'w');
        fwrite(fop, R, 'float32');
        fclose(fop);

        fout = [owk, filesep, v_name{v}, '_Sig_' num2str(bk) '.flt'];
        fop = fopen(fout, 'w');
        fwrite(fop, P, 'float32');
        fclose(fop);

        % fout = [owk, filesep, v_name{v}, '_TP_' num2str(bk) '.flt'];
        % fop = fopen(fout, 'w');
        % fwrite(fop, T, 'float32');
        % fclose(fop);
    end
end