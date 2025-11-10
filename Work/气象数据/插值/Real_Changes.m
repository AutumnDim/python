% There are lots of data from diferent source and different process, such as:
% Observations from CMA and CERN
% Interpolated based on observations from CMA with various procession
% Reanalysis data based on multi-source and multi-models
% Now for a given site, it should be a real mean, trend, variability and 
% the CMA's observations should be condisered as best one for us. So all data
% should be compared with them.
% 
% Therefor, this program firstly read data from CMA station, interpolated grid,
% CERN observation. Then all data are compared with the CMA observation for a given site.
% input lat and lon, and output time series and lots of statistic results
% compared with the others
close all; clear all; clc;

% function [X, xsta] = Real_Changes(fset, site)
% v is very important
%% Define your environment
% Reseach area, which must match with the name in DEM filename
site_name = 'AsiaMeteo';
vname_ID = 3;
time_step = 8;
grd_fmt = 'flt';
if vname_ID == 5
    grd_scale = 10;
else
    grd_scale = 1;
end
interpolate_method = 'Anusplin';

vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};

cname = {'T2', 'R2', 'T2', 'T2', 'RH2', 'D32', 'W2'};
cern_ID = [6,6,9,7,6,15,6];
cname_id = cern_ID(vname_ID);

vad_value = [-60 60; 0 1000; -60 60; -60 60; 0 100; 0 18; 0 20];
mean_or_sum = [1, 0, 1, 1, 1, 1, 1];

vname_unit = {'^oC', 'mm', '^oC', '^oC', '%', 'Hour', 'm/s'};

fdbs = 'Z:\workspace\MeteoGrid\Station\Stations_5k.txt';

fsite = 'Z:\workspace\MeteoGrid\Station\CNERN_CERN.xls';

% ftif = ['Z:\workspace\STSZHANGLI\SRTM\SRTM_' site_name '_250m.tif'];
ftif = ['Z:\workspace\China1km\Parameters\AsiaDEM_1km.tif'];


fxls = ['Z:\workspace\STSZHANGLI\CERN\' cname{vname_ID} '.xls'];

cma_wks = 'Z:\workspace\MeteoGrid\CIMISS_table';

meteogrid_wks = ['X:\China1km\AsiaMeteo'];
% meteogrid_wks = ['X:\Temporary\Shennj\MeteoGrid'];
% meteogrid_wks = ['Z:\workspace\STSZHANGLI\HuanjGrid'];
% meteogrid_wks = 'Z:\workspace\Shennj\MeteoGrid';

fxls_out = ['Z:\workspace\temp\' interpolate_method '_' site_name '_' datestr(now,1) '.xlsx'];


if exist(fdbs, 'file') && exist(fsite, 'file') && exist(ftif, 'file') && exist(fxls, 'file')
    % Read site from CERN
    [dat, txt, raw]  = xlsread(fsite, 'cnernÕ¾µãÎ»ÖÃ', 'A2:G53');
    id0   = dat(:, 1);
    sid   = txt(:, 1);
    sname = txt(:, 2);
    lon   = dat(:, 4);
    lat   = dat(:, 5);
    
    proj = geotiffinfo(ftif);
    x1 = proj.SpatialRef.XWorldLimits(1,1) + proj.PixelScale(1) / 2; 
    x2 = proj.SpatialRef.XWorldLimits(1,2) - proj.PixelScale(1) / 2;
    X1 = x1: proj.PixelScale(1) : x2;
    
    y1 = proj.SpatialRef.YWorldLimits(1,1) + proj.PixelScale(1) / 2;
    y2 = proj.SpatialRef.YWorldLimits(1,2) - proj.PixelScale(1) / 2;
    Y1 = y1:proj.PixelScale(1):y2;
    [X, Y] = meshgrid(X1, Y1);
    
    [srtm, R, bbox] = geotiffread(ftif);   
    srtm = double(srtm);
    disp((bbox(2,:) - bbox(1,:))/2000);
    
    [x0, y0] = projfwd(proj, lat, lon);
    cern_x1 = x0(x0 >= bbox(1,1) & x0 <= bbox(2,1) & y0 >= bbox(1,2) & y0 <= bbox(2,2));
    cern_y1 = y0(x0 >= bbox(1,1) & x0 <= bbox(2,1) & y0 >= bbox(1,2) & y0 <= bbox(2,2));
    js = find(x0 >= bbox(1,1) & x0 <= bbox(2,1) & y0 >= bbox(1,2) & y0 <= bbox(2,2));
    cern_sid = sid(js,:);
    disp([sid(js,:), sname(js)]);
    
    %% Read observations on a given CERN station
    [D, yr, cern_headline, cern_var_name] = Read_CERNMeteo(fxls, sid(js,:), vname_ID);
    disp(cern_var_name);
    disp(cern_headline);
 
        
    cern_dt = D(:,1); 
    

    figure
    bnd = quantile(srtm(srtm > -9000 & srtm < 9999), [0.05 0.95]);
    imagesc(srtm, bnd); colorbar('horizonal');colormap([[0.2 0.2 1]; jet]);
    %srtm(srtm<-9000) = NaN; mapshow(srtm, R);
    hold on;
    
    cern_pix = fix((cern_x1 - proj.SpatialRef.XWorldLimits(1,1)) / proj.PixelScale(1));
    cern_lin = fix((proj.SpatialRef.YWorldLimits(1,2) - cern_y1) / proj.PixelScale(1));
    plot(cern_pix, cern_lin, 'rx'); text(cern_pix, cern_lin, sname(js,:), 'FontSize', 10, 'Color', 'red');
    % plot(x0, y0, 'bx'); text(x0, y0, sname(js,:), 'FontSize', 8, 'Color', 'red');
    axis equal;   axis off;  

    yt = 1980;
    days = datenum(yt + 1, 1, 1) - datenum(yt, 1, 1);
    ff = [cma_wks '\' vname{vname_ID} '\' vname{vname_ID} '_' num2str(yt) '.txt'];
    [db_sid, c_xd, c_n1] = readDbase(ff,days+3);
    db_lat = c_xd(:,1); db_lon = c_xd(:,2); db_elv = c_xd(:,3);
    % [db_id, db_sid, db_lat, db_lon, db_elv, db_dem] = textread(fdbs, '%d%s%f%f%f%f', 'headerlines', 1);
    [db_x0, db_y0] = projfwd(proj, db_lat, db_lon);
    db_x1 = db_x0(db_x0 >= bbox(1,1) & db_x0 <= bbox(2,1) & db_y0 >= bbox(1,2) & db_y0 <= bbox(2,2));
    db_y1 = db_y0(db_x0 >= bbox(1,1) & db_x0 <= bbox(2,1) & db_y0 >= bbox(1,2) & db_y0 <= bbox(2,2));
    db_js = db_sid(db_x0 >= bbox(1,1) & db_x0 <= bbox(2,1) & db_y0 >= bbox(1,2) & db_y0 <= bbox(2,2)); 
    db_num = length(db_js);
    
    db_pix = fix((db_x1 - proj.SpatialRef.XWorldLimits(1,1)) / proj.PixelScale(1));
    db_lin = fix((db_y1 - proj.SpatialRef.YWorldLimits(1,1)) / proj.PixelScale(1));

    % plot(db_pix, db_lin, 'ro');
    near_sd = [];near_id = [];
    for i = 1 : length(cern_sid)
        dst = ((db_x0 - cern_x1(i)) .^2 + (db_y0 - cern_y1(i)) .^2) .^0.5;
        [near_dst, near_js] = min(dst); % disp(near_dst/1000);
        near_id{i,1} = ['CH' char(db_sid(near_js,:))];
        near_sd(i,1:6) = [i, db_lon(near_js), db_lat(near_js), db_elv(near_js), near_dst/1000, near_js];
    end
    figure;plot(near_sd(:,2), near_sd(:,3), 'bo'); text(near_sd(:,2), near_sd(:,3), near_id(:,1), 'FontSize', 8, 'Color', 'blue');

    dst = near_sd(:,5)/1000;
    figure; hist(dst);
    xlswrite(fxls_out, {'Near_ID','id','X','Y','ELV','Distance','Near_no'}, 'Near_SD', 'A1');
    xlswrite(fxls_out, near_id, 'Near_SD', 'A2');
    xlswrite(fxls_out, near_sd, 'Near_SD', 'B2');
    
    cx = [];
    %% Read CMA observations
    site_sid = []; site_dat = [];  cma_dt = [];
    for yt = min(yr) : max(yr)
        days = datenum(yt + 1, 1, 1) - datenum(yt, 1, 1);
       
        for k = 1 : days
            kd = datenum(yt, 1, 1) + k - datenum(min(yr), 1, 1);
            cma_dt(kd,1:2) = [datenum(yt, 1, 1) + k - 1 kd];
        end
        
        % Read observation from CMA
        
        ff = [cma_wks '\' vname{vname_ID} '\' vname{vname_ID} '_' num2str(yt) '.txt'];
        if exist(ff, 'file')
            % disp(ff); 
            [c_id, c_xd, c_n1] = readDbase(ff,days+3);
            % cma_sid = [ones([length(c_id),1]) * 'CH' c_id];
            cma_sid = [];
            for i = 1 : length(c_id)
                cma_sid{i,1}= ['CH' char(c_id(i,:))];  
            end
            
            for j = 1 : length(cern_sid)
                c_js = strcmp(cma_sid, near_id(j));
                jn = find(c_js > 0);
                if ~isempty(jn)
                    % disp(i);
                    site_sid{j,1} = cma_sid{jn};
                    site_lat(j,1) = c_xd(jn, 1);
                    site_lon(j,1) = c_xd(jn, 2);
                    site_elv(j,1) = c_xd(jn, 3);
                    for k = 1 : days
                        kd = datenum(yt, 1, 1) + k - datenum(min(yr), 1, 1);
                        site_dat(kd,j) = c_xd(jn,k + 3);
                    end
                else
                    site_sid{j,1} = NaN;
                    site_lat(j,1) = NaN;
                    site_lon(j,1) = NaN;
                    site_elv(j,1) = NaN;
                    site_dat(j,1) = NaN;
                end
            end
        end
    end
    XMN = []; j = 1;XID = [];
    x0 = D(:,1);
    disp('sname     mean(delta) std(delta) mean(y10) mean(y20) std(y10) std(y20)');
    site_dat(site_dat < vad_value(vname_ID,1) | site_dat > vad_value(vname_ID,2)) = NaN;
    for i = 1 : length(cern_sid)
        y1 = site_dat(:,i);
        y2 = D(:, i + 1);
        
        x01 = x0(~isnan(y1) & ~isnan(y2) & y2 ~= 0);
        y10 = y1(~isnan(y1) & ~isnan(y2) & y2 ~= 0);
        y20 = y2(~isnan(y1) & ~isnan(y2) & y2 ~= 0);
        
        delta = y10 - y20;
        if length(y10) > 30
            plotyy(x01, [y10,y20], x01, delta);
            title(sname{i});
            xmn = [i dst(i),mean(delta) std(delta) mean(y10) mean(y20) std(y10) std(y20)];
            disp([sname{i} ' ' num2str(xmn, '%6.2f')]);
            XMN(j,:) = xmn;
            XID{j,1} = sname{i};
            j = j + 1;
        end
        x = [ones([length(y10) 1])*i x01 y10 y20 delta];
        if i == 1
            X = x;
        else
            X = [X; x];
        end
    end
    xlswrite(fxls_out, {'Name','id','Distance','Delta', 'Delta_SD', 'Mean_CMA','Mean_CERN', 'SD_CMA','SD_CERN'}, 'Mean_Delta', 'A1');
    xlswrite(fxls_out, XID, 'Mean_Delta', 'A2');
    xlswrite(fxls_out, XMN, 'Mean_Delta', 'B2');
   
    % yr = [2000,2001];
    % put all site together to extract their values from MeteoGrid
    meteo_sid = []; meteo_geo = [];meteo_dat = [];
    n1 = length(cern_pix);
    for i = 1 : n1
        meteo_sid{i, 1} = cern_sid{i};
        meteo_geo(i, 1) = cern_pix(i);
        meteo_geo(i, 2) = cern_lin(i);
    end
    if strcmpi(grd_fmt, 'tif')
        [meteo_dt, sdat] = meteogeotiffsample([min(yr),max(yr)], proj, meteo_geo, meteogrid_wks, vname{vname_ID}, vad_value(vname_ID,:), time_step, 1000);
    else
        % Be careful the dash line in the file name of MeteoGrid, which was defined as:
        % TMIN_yyyyddd.flt, where ddd is from 001 to 046
        [meteo_dt, sdat, jneighbor] = meteosample([min(yr),max(yr)], proj, meteo_geo, meteogrid_wks, vname{vname_ID}, vad_value(vname_ID,:), time_step, 1000, meteo_sid);
    end
    if ~strcmpi(vname{vname_ID}(1), 'T')
        sdat(sdat < 0) = 0;
    end
    sdat(:,3:end) = sdat(:,3:end) * grd_scale;
    xlswrite(fxls_out, {'YEAR','DOY'}, 'MeteoGrid', 'A1');
    xlswrite(fxls_out, sname', 'MeteoGrid', 'C1');
    xlswrite(fxls_out, sdat, 'MeteoGrid', 'A2');

    
    %% Calculate CERN mean or sum by time step
    doy = D(:,1) - datenum(year(D(:,1)), 1, 1) + 1;
    
    d8 = year(D(:,1)) * 1000 + 8 * fix((doy - 1) / 8) + 1;
    
    [averaged_D,q_D,sd_D] = meanbyxdays(D(:,2:end), cern_sid, d8, mean_or_sum(vname_ID), 0);
    
    cern_dt = unique(d8); cern_yr = fix(cern_dt / 1000); cern_doy = cern_dt - cern_yr * 1000;
    
    cern_data = [cern_yr cern_doy averaged_D];
    
    xlswrite(fxls_out, {'YEAR','DOY'}, 'MeteoCERN', 'A1');
    xlswrite(fxls_out, sname', 'MeteoCERN', 'C1');
    xlswrite(fxls_out, cern_data, 'MeteoCERN', 'A2');
    
    %% Calculate STATION mean or sum by time step
    d8 = meteo_dt(:,1) * 1000 + meteo_dt(:,2);
    
    [averaged_site_dat,q_site_dat,sd_site_dat] = meanbyxdays(site_dat, site_sid, d8, mean_or_sum(vname_ID), 0);
    
    site_dt = unique(d8); site_yr = fix(site_dt / 1000); site_doy = site_dt - site_yr * 1000;
    
    site_data = [site_yr site_doy averaged_site_dat];
    
    xlswrite(fxls_out, {'YEAR','DOY'}, 'MeteoSite', 'A1');
    xlswrite(fxls_out, site_sid', 'MeteoSite', 'C1');
    xlswrite(fxls_out, site_data, 'MeteoSite', 'A2');

    %% Delta MeteoGrid - CERN
    delta_Grid_CERN = site_data(:,3:end) - cern_data(:,3:end);
    delta_Grid_CERN(isnan(cern_data(:,3:end))) = NaN;
    delta_Grid_CERN(cern_data(:,3:end) == 0) = NaN;

    % 
    [cd, xd] = hist(delta_Grid_CERN(:), 100); 
    [emn, esd] = normfit(delta_Grid_CERN(~isnan(delta_Grid_CERN)));
    nxd = normpdf(min(xd):max(xd), emn, esd);
    figure
    histogram(delta_Grid_CERN, 'Normalization','probability'); hold on;
    plot(min(xd):max(xd), nxd, 'k-');
    
    bnd = quantile(delta_Grid_CERN(:), [0.05, 0.95]);
    % delta_Grid_CERN(delta_Grid_CERN < bnd(1) | delta_Grid_CERN > bnd(2)) = NaN;

    d8 = unique(site_doy);
    [delta_doy,q_delta,sd_delta] = meanbyxdays(delta_Grid_CERN, sname, site_doy, mean_or_sum(vname_ID), 0);
    
    delta_allsite = mean(delta_doy, 2, 'omitnan');
    delta_sd_allsite = std(delta_doy', 'omitnan');
    bnd = quantile(delta_doy', [0.05, 0.95]);
    figure
    h2 = area([d8; d8(end:-1:1)], [bnd(1,:) bnd(2,end:-1:1)]); h2.FaceColor = [0.8 0.8 0.2];
    hold on; plot(d8, delta_allsite, 'k-', 'Linewidth',2) %plot(d8, delta_doy(:,1:end)); %
    xlim([0 361]); xlabel('DOY'); ylabel('\delta_{Grid-CERN} (^oC)');
    
    
    %%
    st_yr  = year(cma_dt(:,1)); 
    st_sid = site_sid(~isnan(site_dat(1,:)));
    % st_dat = [site_lat, site_lon, site_elv, site_dat];
    % st_dat = st_dat(~isnan(site_dat(:,1)),:);
    
    site_yr = unique(st_yr);
    % site_lat = st_dat(:,1);
    % site_lon = st_dat(:,2);
    % site_elv = st_dat(:,3);
    % site_dat = st_dat(:,4:end);
%      
%     site_dat(site_dat < vad_value(vname_ID,1) | site_dat > vad_value(vname_ID, 2)) = NaN;
%     site_ann = [];
%     for yt = min(site_yr) : max(site_yr)
%         % meteorological station
%         x0 = site_dat(st_yr == yt,:);
%         xm = mean(x0, 'omitnan');
%         xs = std(x0, 'omitnan');
%         
%         % CERN station
%         x1 = D(D(:,3) == yt, cname_id);
%         if ~isempty(x1)
%             xc = mean(x1, 'omitnan');
%         else
%             xc = NaN;
%         end
%         
%         site_ann(yt - min(site_yr)+1,:) = [yt, xm, xc];
%     end
%     xlswrite(['Z:\workspace\temp\' site_name '_meteo.xlsx'], {'SID', 'LAT', 'LON','ELV'}, 'Sta_info','A1');
%     xlswrite(['Z:\workspace\temp\' site_name '_meteo.xlsx'], st_sid, 'Sta_info','A2');
%     xlswrite(['Z:\workspace\temp\' site_name '_meteo.xlsx'], st_dat(:,1:3), 'Sta_info','B2');
%     xlswrite(['Z:\workspace\temp\' site_name '_meteo.xlsx'], {'Year'}, vname{vname_ID},'A1');
%     xlswrite(['Z:\workspace\temp\' site_name '_meteo.xlsx'], st_sid', vname{vname_ID},'B1');
%     xlswrite(['Z:\workspace\temp\' site_name '_meteo.xlsx'], {site_name}, vname{vname_ID},[char('A'+length(st_sid)+1) '1']);
%     xlswrite(['Z:\workspace\temp\' site_name '_meteo.xlsx'], site_ann, vname{vname_ID},'A2');
%     site_dat = site_dat(:, st_yr >= yr(1) & st_yr <= yr(2));
% 
%     [x0, y0] = projfwd(proj, site_lat, site_lon);
%     cma_x1 = x0(x0 >= bbox(1,1) & x0 <= bbox(2,1) & y0 >= bbox(1,2) & y0 <= bbox(2,2));
%     cma_y1 = y0(x0 >= bbox(1,1) & x0 <= bbox(2,1) & y0 >= bbox(1,2) & y0 <= bbox(2,2));
%     
%     cma_pix = fix((cma_x1 - proj.SpatialRef.XWorldLimits(1,1)) / proj.PixelScale(1));
%     cma_lin = fix((cma_y1 - proj.SpatialRef.YWorldLimits(1,1)) / proj.PixelScale(1));
% 
%     cma_dst = ((cma_x1 - cern_x1) .^2 + (cma_y1 - cern_y1) .^2) .^0.5;
%     cma_near_dst = sort(cma_dst,'ascend'); disp(cma_near_dst/1000);
%     cma_jnst = find(cma_dst == cma_near_dst(1));
%     plot(cma_pix, cma_lin, 'rx', 'Markersize', 12);
%     plot(cma_pix, cma_lin, 'ro', 'Markersize', 12);
%     text(cma_pix(cma_jnst), cma_lin(cma_jnst), site_sid(cma_jnst), 'FontSize', 18);
%     saveas(gca, ['Z:\workspace\temp\' site_name 'Stations.jpg']);
%     
%     % use IDW to interpolate the missing value
%     yp = []; v = vname_ID;
%     for i = 1 : length(cma_dt)
%         xv = site_dat(:,i); 
%         vv = xv(xv >= vad_value(v, 1) & xv <= vad_value(v, 2));
%         vx = cma_x1(xv >= vad_value(v, 1) & xv <= vad_value(v, 2));
%         vy = cma_y1(xv >= vad_value(v, 1) & xv <= vad_value(v, 2));
%         yp(i,1)= IDW(vx, vy, vv, cern_x1, cern_y1, -2, 'ng', min(5,length(cma_x1)));    
%     end
%     figure
%     plot(cern_dt, D(:,cname_id), 'b-', 'Linewidth', 1.0);
%     hold on
%     plot(cma_dt(:,1), yp, 'r-', 'Linewidth', 1.0);
%     plot(cma_dt(:,1), site_dat(cma_jnst, :), 'g-', 'Linewidth', 0.5);
%     datetick('x', 'yyyy');
%     legend('CERN','IDW','Nearest');
%     ylabel([vname{v} ' (' vname_unit{v} ')']); xlabel('Year');
%     saveas(gca, ['Z:\workspace\temp\' site_name 'CERN-IDW-NearNeighbor.jpg']);
%     
%     
%     meteo_sid{n1+1} = 'CERN_IDW';
%     meteo_geo(n1+1, 1) = cern_pix;
%     meteo_geo(n1+1, 2) = cern_lin;
%     
%     n2 = length(cma_pix);
%     for i = 1 : n2
%         meteo_sid{i + n1 + 1} = cma_sid{i};
%         meteo_geo(i + n1 + 1, 1) = cma_pix(i);
%         meteo_geo(i + n1 + 1, 2) = cma_lin(i);
%     end
%     meteo_dat = [D(:,cname_id) yp site_dat'];
%     meteo_dat(meteo_dat > 9999 | meteo_dat < -999) = NaN;
% 
%     
%     dy2 = meteo_dt(:,1) * 1000 + meteo_dt(:,2);
%     [averaged_data,q,sd] = meanbyxdays(meteo_dat, meteo_sid, dy2, mean_or_sum(vname_ID), 0);
%     %% regression between observation and interpolation
%     % XMN: CERN, IDW, CMA
%     XMN = averaged_data';
%     y0 = XMN(:,1);       % CERN observations
%     x1 = XMN(:,2);       % IDW
%     x2 = sdat(:,3);      % Interpolate methods
%     
%     rmse1 = (mean((x1 - y0).^2, 'omitnan'))^0.5;
%     rmse2 = (mean((x2 - y0).^2, 'omitnan'))^0.5;
%     
%     XDAT = [y0,x1,x2]; 
%     bnd(1) = min(XDAT(:)); bnd(2) = round(max(XDAT(:))*1.1);
%     [b1, bint1, r1, rint1, p1] = regress(y0, [ones([length(x1) 1]) x1]);
%     [b2, bint2, r2, rint2, p2] = regress(y0, [ones([length(x2) 1]) x2]);
%     
%     xmn_mn = mean(XDAT, 'omitnan');
%     xmn_sd = std(XDAT, 'omitnan');
%     r_rmse1 = p1(4)^0.5 / mean(y0, 'omitnan');
%     r_rmse2 = p2(4)^0.5 / mean(y0, 'omitnan');
%     
%     disp([xmn_mn', xmn_sd']); 
%     disp(num2str([b1', p1(1:3), p1(4)^0.5, r_rmse1], '%12.4f'));
%     disp(num2str([b2', p2(1:3), p2(4)^0.5, r_rmse2], '%12.4f'));
%     
%     figure
%     plot(x1, y0, 'b.', x2, y0, 'ro'); legend('IDW', interpolate_method);
%     hold on; plot(bnd, bnd, 'k:');
%     plot(x1, b1(1) + b1(2) * x1, 'b-', x2, b2(1) + b2(2) * x2, 'r-');
%     axis([bnd bnd]);
%     xlabel(['Interpolated ' vname{vname_ID} ' (' vname_unit{vname_ID} ')']);
%     ylabel(['Observed ' vname{vname_ID} ' (' vname_unit{vname_ID} ')']);
%     text(bnd(1),bnd(2)*.9, ['R^2 = ', num2str(p1(1), '%.2f')], 'color', 'blue', 'FontSize', 12);
%     text(bnd(1),bnd(2)*.8, ['R^2 = ', num2str(p2(1), '%.2f')], 'color', 'red', 'FontSize', 12);
%     text(bnd(2)*.9, bnd(2)*.9, '1 : 1 Line', 'color', 'black', 'FontSize', 12);
%     set(gca, 'FontSize', 12);
%     saveas(gca, ['Z:\workspace\temp\' site_name '_' vname{vname_ID} '_' interpolate_method '_regression.jpg']);
% 
%     %% Write all results to excel
%     xlswrite(fxls_out,{'YEAR','DOY'}, [site_name '_OBS'],'A1');
%     xlswrite(fxls_out,meteo_sid, [site_name '_OBS'], 'C1');
%     xlswrite(fxls_out,[sdat(:,1:2), averaged_data'], [site_name '_OBS'], 'A2');
%     
%     xlswrite(fxls_out,{'YEAR','DOY'}, [site_name '_EST'],'A1');
%     xlswrite(fxls_out,meteo_sid, [site_name '_EST'], 'C1');
%     xlswrite(fxls_out,sdat, [site_name '_EST'], 'A2');
% 
%     xlswrite(fxls_out,{'YEAR','DOY',interpolate_method}, vname{vname_ID},'A1');
%     xlswrite(fxls_out,meteo_sid, vname{vname_ID}, 'C1');
%     xlswrite(fxls_out,[sdat(:,1:3), averaged_data'], vname{vname_ID}, 'A2');
%     
%     %% Seasonal and Annual analysis
%     if time_step == 8
%         mgd_dt = datenum(sdat(:,1), 1, 1) + sdat(:,2) - 1;
%     else
%         mgd_dt = datenum(sdat(:,1), 1, 1) + sdat(:, 2) * 10;
%     end
%     %sdat(sdat < 0) = 0;
%     
%     % Calculate the seasonal mean or sum
%     figure
%     plot(mgd_dt, XMN(:,1:2), 'Linewidth', 1.5); hold on;
%     plot(mgd_dt, sdat(:,3), 'g-.', 'Linewidth', 1.5);
%     datetick('x', 'yyyy');
%     xlabel('Date'); ylabel([vname{vname_ID} ' (' vname_unit{vname_ID} ')']);
%     legend('CERN', 'IDW', 'MeteoGrid');
%     set(gca, 'FontSize', 12);
%     saveas(gca, ['Z:\workspace\temp\' site_name '_CERN_CMA_MeteoGrid_' vname{vname_ID} '_Season.jpg']);
%     
%     % Calculate the annual mean or sum
%     dt = meteo_dt(:,1);
%     dn = unique(dt); xmn = [];
%     ds = sdat(:,1);  tmn = [];
%     for i = 1 : length(dn)
%         dat = meteo_dat(dt == dn(i),:);
%         [nd, md] = size(dat);
%         xmn(i,:) = [nd mean(dat, 'omitnan')];
%         
%         dat = sdat(ds == dn(i),:);
%        if strcmpi(vname{vname_ID}, 'PRCP')
%            tmn(i,:) = sum(dat);
%        else
%            tmn(i,:) = mean(dat);
%        end
%     end
%     TMN = [];
%     if strcmpi(vname{vname_ID}, 'PRCP')
%         for i = 1 : md
%             TMN(:,i) = xmn(:,i + 1) .* xmn(:,1);
%         end
%     else
%         TMN = xmn(:, 2:end);
%     end    
%     figure
%     plot(dn, TMN(:,1:2)); hold on;
%     plot(dn, tmn(:,3), 'g-.');
%     xlabel('Year'); ylabel([vname{vname_ID} ' (' vname_unit{vname_ID} ')']);
%     legend('CERN', 'IDW', 'MeteoGrid');
%     saveas(gca, [meteogrid_wks '\CERN_CMA_MeteoGrid_' vname{vname_ID} '_Annual.jpg']);
    
    
else
    disp(['Did not find station database file: ' fdbs]);
    disp(['      or:' fsite]);
    disp(['      or:' ftif]);
end










