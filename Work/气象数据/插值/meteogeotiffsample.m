function [dt, sdat] = meteogeotiffsample(yr, proj, meteo_dat, meteogrid_wks, vname, vad_value, time_step, num_zeros)
% check data from 3 aspects as follows:
% (1) unit, to check station data
% (2) observed and interpolated value compare
% (3) time series compare
% vname = {'TMAX'; 'TMIN'; 'PRCP'};
% dlim = [-4500 4500];
k = 1;
% fs = '/nfshome/junbang.wang/China/MeteoGrid/flux_sites.txt';
% [id site lat lon xx yy] = textread(fs, '%d%s%f%f%f%f', 'headerlines', 1);
% fdat = '/nfshome/junbang.wang/China/MeteoGrid/TMAX_2005001.hdr';

pix = meteo_dat(:,1);
lin = meteo_dat(:,2);
num = length(pix);

% grd = readgrdhdr(fhdr);
% disp(grd);
% pix = fix((xx - grd.xll)/grd.csize);
% lin = fix((yy - grd.yll)/grd.csize);
% lin = grd.nrows - lin;

% id1 = site_sid(pix > 0 & pix <= grd.ncols & lin > 0 & lin <= grd.nrows,:);
% px1 = pix(pix > 0 & pix <= grd.ncols & lin > 0 & lin <= grd.nrows);
% ln1 = lin(pix > 0 & pix <= grd.ncols & lin > 0 & lin <= grd.nrows);
% C_lim = [max(px1) min(px1) max(ln1) min(ln1)];

% fs = ['/nfshome/junbang.wang/China/MeteoGrid/flux_sites_' vname{v} '.txt'];
% fp = fopen(fs, 'w');
% fprintf(fp, 'YEAR\tDOY');
% for i = 1 : length(pix)
%     fprintf(fp, '\t%s', site{i});
% end
% fprintf(fp, '\n');
% fclose(fp);

sdat = [];
for yt = yr(1) : yr(2)
    days = datenum(yt+1,1,1)-datenum(yt,1,1);
    dy1 = 1:days;  % weekly average
    switch time_step
        case 1   % Annually
            dy2 = dy1;
        case 8
            dy2 = fix((dy1 - 1) / 8) * 8 + 1;
        case 10  % 10-day 
            mon = month(datenum(yt,1,1) + dy1 - 1);
            dy  = day(datenum(yt,1,1) + dy1 - 1);
            mj  = dy;
            mj(dy <= 10) = 1; mj(dy > 10 & dy <= 20) = 2; mj(dy > 20) = 3;
            dy2 = (mon - 1) * 3 + mj;
        case 12  % Monthly
            dy2 = month(datenum(yt,1,1) + dy1 - 1);
        case 24  % Half-monthly
            mon = month(datenum(yt,1,1) + dy1 - 1);
            dy  = day(datenum(yt,1,1) + dy1 - 1);
            mj  = dy;
            mj(dy <= 15) = 1; mj(dy > 15) = 2;
            dy2 = (mon - 1) * 2 + mj;
    end   
    if yt == yr(1)
        dt = [ones([days 1]) * yt dy2'];
    else
        dt = [dt;ones([days 1]) * yt dy2'];
    end
    dmn = unique(dy2);
    nlyr = length(dmn);
    for mn = 1 : nlyr
        dy = dmn(mn);
        fdat = [meteogrid_wks '/' vname '/' vname '_' num2str(yt * num_zeros + mn) 'ann.tif'];
        if exist(fdat, 'file')
            [dat, R, bbox] = geotiffread(fdat);


            % fp = fopen(fdat);
            % dat = fread(fp, [proj.Width, proj.Height],'float32');
            % fclose(fp);
            % 
            % dat = dat';
            
            if yt == yr(1) && mod(mn-1, 10) == 0
                disp(fdat);
                bnd = quantile(dat(dat >= vad_value(1) & dat <= vad_value(2)), [0.05 0.95]);
                if bnd(2) > bnd(1)
                    figure
                    imagesc(dat, bnd);
                    colormap([white(1);jet(100)]); colorbar('horiz');
                    axis off;  axis equal
                    hold on;
                    plot(pix, lin, 'rx');
                    text(pix(1),lin(1),'CERN');
                    
                end
            end

            [np, nl] = size(dat);
            sdat(k,1:2) = [yt dy];
            for i = 1 : num
                if pix(i) <= np && lin(i) <= nl
                    sdat(k, i + 2) = dat(pix(i),lin(i));
                else
                    sdat(k, i + 2) = NaN;
                end
            end
            k = k + 1;
        else
            disp(['Cannot find file: ' fdat]);
            break;
        end
    end % mn = 1: dn(12 or 10)
end  % year loop
% fs = ['/nfshome/junbang.wang/China/MeteoGrid/flux_sites_' vname{v} '.txt'];
% dlmwrite(fs,sdat,'delimiter','\t','-append');
