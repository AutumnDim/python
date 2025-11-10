function [ic, yc, xc, zc,ghcn_sid] = readghcnstation(fsta, x1,x2,y1,y2)
% usage: [id lat lon elv] = readghcnstation(ff, x1,x2,y1,y2)
% clear all
% close all
% clc
% --------------------------------------------------------------------------------
% 
% IV. FORMAT OF "ghcnd-stations.txt"
% 
% ------------------------------------------------------------
% Variable   Columns   Type
% ------------------------------------------------------------
% ID            1-11   Character
% LATITUDE     13-20   Real
% LONGITUDE    22-30   Real
% ELEVATION    32-37   Real         missing = -999.9
% STATE        39-40   Character    US postal code
% NAME         42-71   Character    station name
% GSNFLAG      73-75   Character    GSN station or blank
% HCNFLAG      77-79   Character    HCN station or blank
% WMOID        81-85   Character    WMO station or blank
% ------------------------------------------------------------

% ff = 'I:\Database\meteo\GHCN\ghcnd-stations.txt';
% restart
i = 1;
if exist(fsta, 'file')
    disp(['Read: ' fsta]);
    ghcn_sid = containers.Map;
    fd = fopen(fsta, 'r');
    while(~feof(fd))
        str = fgetl(fd);
        m = length(str);
        if m > 42
            id(i,:)  = str(1:11);
            lat(i,1) = str2double(str(13:21));
            lon(i,1) = str2double(str(22:31));
            elv(i,1) = str2double(str(32:38));
            name     = str(39:m);
            sta(i,:)   = str(39:41);
            dat = [lat(i,1), lon(i,1), elv(i,1)];
            ghcn_sid(id(i,:)) = dat;
            if mod(i-1,10000) == 0
                disp([num2str(i) '. ' id(i,:)]);
            end
%             ghwf  = str(74:76);
%             wmoid = str(82:m);
%             gsnf  = str(73:75);
%             hcnf  = str(77:79);
%             wmof  = str(81:85);
%             disp(['ID: ' id]);
            i = i + 1;  
        end
    end
    fclose(fd);
    % [sd hd] = textscan(fd, '%s%f%f%f%s');
    n = i - 1;
    xc = lon(lon >= x1 & lon <= x2 & lat >= y1 & lat <= y2);
    yc = lat(lon >= x1 & lon <= x2 & lat >= y1 & lat <= y2);
    zc = elv(lon >= x1 & lon <= x2 & lat >= y1 & lat <= y2);
    ic = id(lon >= x1 & lon <= x2 & lat >= y1 & lat <= y2,:);
    m = length(xc);
    d1 = strfind(fsta,'.');
    if ~isempty(d1)
        ff = [fsta(1:d1-1) '_Selected.txt'];
    else
        ff = [fsta '_Selected.txt'];
    end
    fd = fopen(ff,'w');
    for i = 1 : m
        if ic(i,1) ~= 'C' && ic(i,2) ~= 'H'
            fprintf(fd,'%s\t%f\t%f\t%f\n',ic(i,:), xc(i), yc(i), zc(i));
        end
    end
    fclose(fd);
    plot(lon,lat,'bx');
    hold on;
    plot(xc, yc,'r.');
    disp(['Number of all station: ' num2str(n) ' and selected: ' num2str(m)]);
else
    disp(['Not exist: ' ff]);
    id = -999; lat = -999; lon = -999; elv = -999;
%     ff = input('Input GHCN STATION file name (include complete path)', 's');
    return;
end
