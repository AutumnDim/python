function [dt, sdat,js] = meteosample(yr, proj, meteo_geo, meteogrid_wks, vname, vad_value, time_step, num_zeros, meteo_sid)
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

pix = meteo_geo(:,1);
lin = meteo_geo(:,2);
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

sdat = []; js = [];
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
        case {24,15}  % Half-monthly
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
        fdat = [meteogrid_wks '/' vname '/' vname '_' num2str(yt * num_zeros + mn) '.flt'];
        if exist(fdat, 'file')
            


            fp = fopen(fdat);
            dat = fread(fp, [proj.Width, proj.Height],'float32');
            fclose(fp);
            
            dat = dat';
            
            if yt == yr(1) && mod(mn-1, 10) == 0
                % disp(fdat);
                bnd = quantile(dat(dat >-9000), [0.05 0.95]);
                if bnd(2) > bnd(1)
                    figure
                    imagesc(dat, bnd);   % 1:proj.Height, proj.Width:-1:1, 
                    colormap([white(1);jet(100)]); colorbar('horiz');
                    hold on;
                    plot(pix, lin, 'rx');
                    % set(gca,'YDir','normal')
                    text(pix, lin, meteo_sid);
                end
            end

            [nline, npix] = size(dat);
            sdat(k,1:2) = [yt dy];
            for i = 1 : num
                j = 0;
                if pix(i) <= npix && lin(i) <= nline
                    mdat = dat(lin(i),pix(i));
                    
                    while mdat < -9000 && j <= 50
                        j = j + 1;
                        disp([i,j]);
                        
                        p = pix(i) - j : pix(i) + j; 
                        l = lin(i) - j:lin(i) + j;
                        [pp, ll] = meshgrid(p, l);
                        [np,ml] = size(pp);
                        rng = [reshape(pp, np*ml, 1), reshape(ll, np*ml, 1)];
                        xdat = [];
                        for dx = 1 : np*ml
                            xdat(dx,1) = dat(rng(dx,2), rng(dx,1));
                        end
                        xc = xdat(xdat > -9000);
                        if ~isempty(xc)
                            mdat = mean(xc);
                        else
                            mdat = -9999;
                        end
                        
                    end
                    if j <= 50
                        sdat(k, i + 2) = mdat / 10;
                    else
                        sdat(k,i + 2) = NaN;
                    end
                else
                    sdat(k, i + 2) = NaN;
                end
                js(k,i) = j;
            end
            k = k + 1;
        else
            disp(['Cannot find file: ' fdat]);
            disp('Be careful the dash line in the file name of MeteoGrid, ');
            disp('   which was defined as:');
            disp('    TMIN_yyyyddd.flt, where ddd is from 001 to 046');
            return;
        end
    end % mn = 1: dn(12 or 10)
end  % year loop
% fs = ['/nfshome/junbang.wang/China/MeteoGrid/flux_sites_' vname{v} '.txt'];
% dlmwrite(fs,sdat,'delimiter','\t','-append');
