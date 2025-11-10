% Apply Kriging to interpolate the observations on meteorological stations
% to regional grid (MeteoGrid) through using mGstat
% First of all, please add the folder with all subfolders in Matlab Enviroment,
% Then check and make sure the three file names following are right:
% #1 Determine DEM file
%    ftif = 'D:\STSZHANGLI\SRTM\SRTM_Shennj_250m.tif';
% #2 determine database file
%    ff = ['D:\Temp\MeteoDat\' vname{v_id}  '\'  vname{v_id}  '_' num2str(yr * 1000 + nfile) '.txt'];
% #3 determine output file
%    ff = ['F:\Shennj\MeteoGrid\' vname{v_id}  '\'  vname{v_id} '_' num2str(yr*1000+jday) '.flt'];

close all; clear all; clc;
% addpath('d:\workspace\mat');
vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
cname = {'T2', 'R2', 'T2', 'T2', 'RH2', 'D32', 'W2'};
long_name = {'Temperature', 'Precipitation', 'Daily minimum temperature',...
    'Daily maximum temperature', 'Relative humidy', 'Sunlit hour', 'Wind speed'};
vad_value = [-60 60; 0 1000; -60 60; -60 60; 0 100; 0 18; 0 20]*10;

vname_unit = {'^oC', 'mm', '^oC', '^oC', '%', 'Hour', 'm/s'};
vneighbor = [4 10 4 5 11 4  4];
v_id = 2;

% #1 Determine DEM file
ftif = '/data/MeteoGrid/Shennj/SRTM_Shennj_250m.tif';
proj = geotiffinfo(ftif);
out_proj = proj;
[dem, R, bbox] = geotiffread(ftif);
% figure;imagesc(dem)

[nl,np] = size(dem);
xc = bbox(1,1)+R(2,1)/2: R(2,1): bbox(2,1)-R(2,1)/2;
yc = bbox(1,2)+R(2,1)/2: R(2,1): bbox(2,2)-R(2,1)/2;

[xx, yy] = meshgrid(xc / 1000., yc / 1000.) ;

x_est = reshape(xx, nl*np, 1); 
y_est = reshape(yy, nl*np, 1);
z_est = double(reshape(dem, nl*np, 1))/1000;
csvwrite('/data/MeteoGrid/MeteoDat/shennj_xyz.csv', [x_est,y_est, z_est]);

csz = R(2,1) * 1000; 
rng = [bbox(1,1)-csz bbox(1,2)-csz; bbox(2,1)+csz bbox(2,2)+csz]/1000;

% load data
% dy = 1;
% yr = 2000;XB = [];
yr1 = 1980; yr2 = 2015;
XP = []; k = 1;
v_order = [1, 2, 5, 6, 3, 4];
mkdir('/data/MeteoGrid/Shennj_ANN/');

for i = 2 : length(v_order)
    v_id = v_order(i);
    sub = ['/data/MeteoGrid/Shennj_ANN/' vname{v_id}];
    if ~exist(sub, 'dir')
        mkdir(sub);
    end
    for yr = yr1: yr2
        tic
        for nfile = 1 : 3
            % #2 determine database file
            ff = ['/data/MeteoGrid/MeteoDat/' vname{v_id}  '/'  vname{v_id}  '_' num2str(yr * 1000 + nfile) '.txt'];
            disp(ff)
            dat = read_fixedDat(ff);
            x0 = dat(:,2) / 1000; y0 = dat(:,3) / 1000; z0 = dat(:,4) / 1000;

            x1 = x0(x0 >= rng(1,1) & x0 <= rng(2,1) & y0 >= rng(1,2) & y0 <= rng(2,2));
            y1 = y0(x0 >= rng(1,1) & x0 <= rng(2,1) & y0 >= rng(1,2) & y0 <= rng(2,2));
            z1 = z0(x0 >= rng(1,1) & x0 <= rng(2,1) & y0 >= rng(1,2) & y0 <= rng(2,2));
            val = dat(x0 >= rng(1,1) & x0 <= rng(2,1) & y0 >= rng(1,2) & y0 <= rng(2,2), 4 : end)/10;

            for dy = 1 : 12
                jday = (nfile - 1) * 12 + dy;
                val = dat(x0 >= rng(1,1) & x0 <= rng(2,1) & y0 >= rng(1,2) & y0 <= rng(2,2), dy + 4)/10;

                % if vname{v_id}(1) == 'T'
                %     b1 = robustfit(z1 - min(z1), val - val(z1 == min(z1)));
                %     b2 = robustfit(max(z1) - z1, val(z1 == max(z1)) - val);
                %     d1 = val + (-b1(1)-b1(2)*(z1 - min(z1)));
                %     d2 = val + 6.49 * z1; 
                %     figure; plot(z1 - min(z1), val - val(z1 == min(z1)), 'b.'); 
                %     plot(z1, val, 'ro'); 
                %     hold on; plot(z1, d1, 'y+', z1, d2, 'gx');
                % else
                %     d1 = (val - min(val)) / (max(val) - min(val));
                %     d2 = log(d1);
                % end

                % Setup Division of Data for Training, Validation, Testing
                trainFcn = 'trainlm';  % Levenberg-Marquardt backpropagation.
                net.divideParam.trainRatio = 100/100;
                net.divideParam.valRatio = 0/100;
                net.divideParam.testRatio = 0/100;

                if v_id == 1 || v_id == 3 || v_id == 4
                    xt = [x1, y1, z1]';
                    xp = [x_est, y_est, z_est]';
                else
                    xt = [x1,y1]';
                    xp = [x_est y_est]';
                end
                t = val';
                % Create a Fitting Network
                hiddenLayerSize = 10;
                net.trainParam.showWindow = 0;
                net = fitnet(hiddenLayerSize,trainFcn);
                % Train the Network
                [net,tr] = train(net,xt,t);

                % Test the Network
                y = net(xt);
                [b,~,~,~,p] = regress(t', [ones(length(y),1) y']);
                rmse = (sum((y - t).^2) / (length(y) - 1)) ^0.5;
                XP(k,:) = [v_id, yr, jday, mean(t), mean(y), std(t), std(y), rmse, b(1), b(2), p(1), p(3)];
                k = k + 1;
                % e = gsubtract(t,y);
                % performance = perform(net,t,y);

                % View the Network
                % view(net)
                
                % Estimation
                d_est = net(xp);
                if v_id == 2 || v_id > 4
                    d_est(d_est < 0) = 0;
                end
                figure('Visib','off');
                bnd = quantile(d_est(:), [0.01 0.99]);
                d_est_img = reshape(d_est, nl, np);
                figure(dy);
                imagesc(d_est_img, bnd); colorbar('horizonal');
                title([ vname{v_id} ' ' num2str(yr*1000+jday)]);
                ff = ['/data/MeteoGrid/Shennj_ANN/' vname{v_id}  '/'  vname{v_id} '_' num2str(yr*1000+jday) 'ann_elv.jpg'];
                saveas(gca, ff);
                % d_est_img = [];
                % parfor pix = 1 : np
                %     x_est = xx(:, pix);
                %     y_est = yy(:, pix);
                % 
                %     [d_2var,v_2var]=krig([x1 y1],[val val_var],[x_est y_est],V1,options);
                %     [d_3var,v_3var]=krig([x1 y1],val, [x1, y1], z1,[x_est y_est],V1,options);
                %     d_est_img(:,pix) = d_est;
                % end
                        
                % % 
                % bnd = quantile(d_est_img(:), [0.01 0.99]);
                % subplot(2,2,1); 
                % subplot(2,2,2); imagesc(d_img, bnd); colorbar('horizonal');
                % delta = (d_img - d_est_img);bnd = quantile(delta(:), [0.01 0.99]);
                % subplot(2,2,3); imagesc(delta, bnd); colorbar('horizonal');
                % mn_d_img = mean(d_img); mn_d_est_img = mean(d_est_img);
                % mn_delta = mean(delta);
                % subplot(2,2,4); 
                % plotyy(1:np, [mn_d_img',mn_d_est_img'], 1:np, mn_delta);
                % xlable('Longitude X'), ylable('TMIN (^oC)');
                
                 
                
                % % #3 determine output file
                % ff = ['F:\Shennj\MeteoGrid\' vname{v_id}  '\'  vname{v_id} '_' num2str(yr*1000+jday) '.flt'];
                % fp = fopen(ff, 'w');
                % fwrite(fp, d_est_img', 'float32');
                % fclose(fp);
                
                disp([vname{v_id} '_' num2str(yr*1000+jday) ' ' num2str(toc /60) ' min.']);
                ff = ['/data/MeteoGrid/Shennj_ANN/' vname{v_id}  '/'  vname{v_id} '_' num2str(yr*1000+jday) 'ann_elv.tif'];
                out_proj.Filenmae = ff; out_proj.FileModDate = datestr(now); out_proj.FielSize = size(d_est_img,1) * size(d_est_img,2) * 4;
                ouy_ptoj.BitDepth = 32; out_proj.RasterSize = size(d_est_img);
                geotiffwrite(ff, d_est_img, R, ...
                              'GeoKeyDirectoryTag', out_proj.GeoTIFFTags.GeoKeyDirectoryTag);
            end
        end
    end
end
csvwrite('/data/MeteoGrid/Shennj_ANN/MeteoKriging_Performance.csv', XP);
lpt = {'k:','c:','y:','m:','r-','m:','y:','c:','k:'};
close all;
for v_id = 1 : 7
    
    x0 = XP(XP(:,1) == v_id & XP(:,2) >= 1980, :);
    dt = datenum(x0(:,2), 1, 1) + x0(:,3) * 10 - 6;
    r_rmse = 100 * x0(:,8) ./ x0(:,4);
    x1 = x0(abs(r_rmse) > 10,:);
    % yr1 = min(x0(:,2));  yr2 = max(x0(:,2)); 
    sy1 = num2str(yr1);     sy2 = num2str(yr2); syr = [sy1(3:4) '-' sy2(3:4)];
    
    r_frq = quantile(r_rmse, [0 0.01 0.05 0.25 0.5 0.75 0.95 0.99 1]);
    rrmse_min = min(r_rmse); rrmse_max = max(r_rmse); 
    rrmse_mean = mean(r_rmse(r_rmse >= r_frq(3) & r_rmse <= r_frq(7)));
    figure(v_id + 7);
    hist(r_rmse); y_lim = get(gca, 'ylim');  yline = 0:y_lim(2);
    hold on; 
    for i = 1 : length(r_frq), plot(r_frq(:,i) * ones(length(yline),1), yline, lpt{i},'LineWidth', 2);end
    plot(r_frq(:,1) * ones(length(yline),1), yline, 'k:');
    xlabel([long_name{v_id} ' (' vname_unit{v_id} ')']); ylabel('Frequency'); 
    text(rrmse_mean, y_lim(2) * 0.9, sprintf('R-RMSE = %.1f %%',rrmse_mean),'color','r','Fontsize',18);
    saveas(gca, ['/data/MeteoGrid/Shennj_ANN/' vname{v_id} '_R-RMSE_Hist_' syr '.jpg']);
    
    disp(num2str([rrmse_min,rrmse_max]));
    disp(size(x1,1));
    
    figure(v_id);
    subplot(2,1,1); plot(dt, x0(:,4:5)); 
    datetick('x','yyyy'); xlim([min(dt),max(dt)]);
    ylim([min(min(x0(:,4:5)))*1.3, max(max(x0(:,4:5)))*1.3]);
    ylabel([long_name{v_id} ' (' vname_unit{v_id} ')']); xlabel('Year');
    legend('Observation', 'Estimation', 'Location', 'North', 'Orientation', 'horizontal');
    
    subplot(2,3,4); [ax, h1, h2] = plotyy(dt, x0(:,8), dt, r_rmse); 
    datetick(ax(1), 'x','yyyy'); set(ax(2),'XTick',[])
    xlim(ax(1), [min(dt),max(dt)]); xlim(ax(2), [min(dt),max(dt)]);
    ylim(ax(1),[min(min(x0(:,8)))*1.3, max(max(x0(:,8)))*1.3]);
    ylim(ax(2), [min(r_rmse),max(r_rmse)*1.2]);
    legend(['RMSE', 'R-RMSE'], 'Location', 'North', 'Orientation', 'horizontal'); legend('boxoff'); 
    
    subplot(2,3,5); plot(dt, x0(:,10)); 
    datetick('x','yyyy'); xlim([min(dt),max(dt)]);
    ylim([min(min(x0(:,10)))*1.3, max(max(x0(:,10)))*1.3]);
    legend('Slope', 'Location', 'North', 'Orientation', 'horizontal');  

    subplot(2,3,6); plot(dt, x0(:,11)); 
    datetick('x','yyyy'); xlim([min(dt),max(dt)]);
    ylim([0 1.2]);
    legend('R^2', 'Location', 'North', 'Orientation', 'horizontal');      
    saveas(gca, ['/data/MeteoGrid/Shennj_ANN/' vname{v_id} '_ANN_' syr '.jpg']);
end
disp(datestr(now));
disp('That''s all, go home!');
