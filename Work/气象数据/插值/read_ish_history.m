function sid = read_ish_history(ff, fig)
% close all; clear all; clc;
% ff = '\\Px6-300d-thyqey\Database\ESAsia\LUCC数据收集\gsod\ish-history.txt';
if ~exist(ff, 'file')
    disp([ff ' is not exist!']);
    sid = -9999;
    return;
else
    fp = fopen(ff, 'r');
    i = 0; j = 1;
    sid = [];
    lat = []; lon = []; elv = [];
    while ~feof(fp)
        dl = fgetl(fp);
        if length(dl) > 79 && i > 21
            usaf = dl(1:6);
            wban = dl(8:12);
            stn_name = dl(14:43);
            ctry = dl(44:49);
            lats = dl(59:64);
            lons = dl(66:72);
            elvs = dl(74:79);
            if ~isempty(lats)
                x = str2double(lats);
                if x > -90000
                    lat = x / 1000;
                else
                    lat = -9999;
                end
            end

            if ~isempty(lons)
                x = str2double(lons);
                if x > -90000
                    lon = x / 1000;
                else
                    lon = -9999;
                end
            end

            if ~isempty(elvs)
                x = str2double(elvs);
                if x > -90000
                    elv = x / 10;
                else
                    elv = -9999;
                end
            end
            if lon > -900 && lat > -900
                sid{j,1} = usaf;
                sid{j,2} = ctry;
                sid{j,3} = lon;
                sid{j,4} = lat;
                sid{j,5} = elv;

                j = j + 1;
            end
            % disp([usaf lats lons elvs]);
            % disp([lat(i), lon(i), elv(i)]);
        end
        i = i + 1;
    end
    if fig > 1
        lon = cell2mat(sid(:,3));
        lat = cell2mat(sid(:,4));
        num = length(lat);

        figure(1);
        worldmap([15 55],[70 140])%纬度经度范围显示
        fshp = 'F:\SWAsia\WORLD\country.shp';
        geoshow(fshp, 'FaceColor', [0.5 1.0 0.5]);
        setm(gca,'MLineLocation',5)%设置经度间隔为5
        setm(gca,'PLineLocation',10)%设置经度间隔为10
        setm(gca,'MLabelLocation',5)%设置经度标签为每隔5度
        setm(gca,'PLabelLocation',10)%设置纬度标签为每隔10度  
        
        hold on;
        plot(lon, lat, '.');
        wlon = lon(lon<0 & lat > 0);
        nlat = lat(lon < 0 & lat > 0);
        % plot(wlon, nlat, 'x')
        step = round(num/100);
        for i = 1 : step : num
                text(lon(i), lat(i), sid{i,1});
        end
        title('World Meteorological Stations');
        grid on; box on;

        qh_lat = lat(lat > 30 & lat < 40 & lon > 89 & lon < 105);
        qh_lon = lon(lat > 30 & lat < 40 & lon > 89 & lon < 105);
        qh_sid = sid(lat > 30 & lat < 40 & lon > 89 & lon < 105, 1);
        qh_num = length(qh_lat);
        figure(2);
        fshp = 'E:\Sanjy250m\vector\Qinghai_Province.shp';
        geoshow(fshp);
        hold on;

        plot(qh_lon, qh_lat, '.');
        for i = 1 : 1 : qh_num
            text(qh_lon(i), qh_lat(i), qh_sid{i});
        end
        title('Stations across Qinghai Province');
        grid on; box on;
    end
end
