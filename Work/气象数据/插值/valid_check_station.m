function valid_check_station(vnm, wks, yr, nlyr)
% Check whether the finnal station data are in the valid range 
% Input: 
%        nlyr = 24;
%        vnm = 'WIN';
%        wks = '\\BA-37AEDE\Workspace\China8km\AsiaMeteo\temp';
%        yr = 2015;
vname = {'PRCP'; 'TMIN'; 'TMAX'; 'TAVG'; 'RHU'; 'SSD';  'WIN'};
sn = strcmpi(vname, vnm);
v  = find(sn > 0);
vad_value = [0 1000; -60 60; -60 60; -60 60; 0 100; 0 18; 0 20]*10;
m = mod(nlyr, 12); 
n = fix(nlyr / 12);
if m > 0
    nc = [ones([1, n]) * 12, m];
else
    nc = ones([1, n]) * 12;
end
days = datenum(yr+1,1,1)-datenum(yr,1,1);
for i = 1 : length(nc)
    % READ GHCN-CIMISS
    ff = [wks '\' vnm '\' vnm '_' num2str(yr * 1000 + i) '.txt'];
    if exist(ff, 'file')
        % disp(ff);
        [id, xd, n1] = readDbase(ff,nc(i)+3);
        sd = char(id);
        dat = xd(:,4:end); lat = xd(:,1); lon = xd(:,2); elv = xd(:,3); 
        
        [sn, sm] = size(dat);
        all_num = sn * sm;
        vad_dat = dat(dat >= vad_value(v, 1) & dat <= vad_value(v, 2));
        vad_num = length(vad_dat);
        vad_pct = (all_num - vad_num) * 100 / all_num;
        
        disp([vnm ' ' num2str(yr) ' Invalid_percent = ' num2str(vad_pct) ' %']);
        
        if vad_pct > 0
            [ni,nj] = find(dat < vad_value(v, 1) | dat > vad_value(v, 2));
            
            nn = length(ni);
            nx = lon(ni); ny = lat(ni);
            plot(lat, lon, 'b.'); hold on;
            plot(ny, nx, 'rx');
            
            for j = 1 : nn
                text(ny(j), nx(j), num2str(sd(ni(j),:), '%.0f'));
                % text(ny(j), nx(j), num2str(dat(ni(j),nj(j)), '%.0f'));
            end
        end
    end
end