% function read_stardex(file_name)

close all; clear all; clc;

inw = 'E:\MeteoGrid\Stations\CMA\';
ouw = [inw 'extrend\'];
if ~exist(ouw, 'dir')
    mkdir(ouw);
end


file_name = 'E:\MeteoGrid\Stations\station_list.dat';
if ~isempty(strfind(file_name, 'CERN'))
    fsite = 'D:\STSZHANGLI\CERN\张多才提供CNERN和CERN台站站点位置.xls';
    [~,sid,~] = xlsread(fsite,'cern站点位置', 'B2:B40');
    [yy,~,~] = xlsread(fsite,'cern站点位置', 'D2:D40');
    [xx,~,~] = xlsread(fsite,'cern站点位置', 'C2:C40');
    [zz,~,~] = xlsread(fsite,'cern站点位置', 'F2:F45');
    sid{strcmp(sid,'BNF')} = 'XSBN';
    sid{strcmp(sid,'MXF')} = 'MX';
else
    load sta_info;
    s0 = char(sta_info{1,1});
    xx = (sta_info{1,3});
    yy = (sta_info{1,2});
    zz = (sta_info{1,4});
    sid = [];
    for i = 1 : length(s0), sid{i,1} = s0(i,:);end
    ns = length(s0);
end
list_file = strfind(file_name,'list');
XT = []; XS = [];

file_ind_desp = 'E:\OneDrive\Documents\indices_description.xlsx';
[~,ind_name,~] = xlsread(file_ind_desp,'Sheet3','B2:B58');
[ind,~,~] = xlsread(file_ind_desp,'Sheet3','D2:D58');
[~,desp,~] = xlsread(file_ind_desp,'Sheet3','E2:E58');
[~,unit,~] = xlsread(file_ind_desp,'Sheet3','F2:F58');

ind_use = find(ind > 0);
dsp_use = desp(ind_use);
ind_eng = ind_name(ind_use);
ind_num = length(ind_use);
ind_unt = unit(ind_use);

season = {'DJF','MAM','JJA','SON','ANN'};
ssn_cl = {'k', 'r', 'g', 'y','b'};
col_nm = {'black', 'red', 'green', 'yellow','blue'};
hdr = [];
j = 1;
for v = 1 : ind_num
    for s = 1 : 5
        hdr{1,j} = ind_eng{v};
        hdr{2,j} = season{s};
        j = j + 1;
    end
end


if isempty(list_file)
    dat = dlmread(ff, ',', 2,3);
    nf = 1;
    XT(i,:) = dat(end-1,:);
    XS(i,:) = dat(end, :);
else
    
    files = textread(file_name,'%s');
    
    nf = length(files);
    XT = []; XS = []; gid = []; geo = [];
    for i = 1 : nf
        s0 = files{i}(1:end-4);
        n0 = strfind(s0,'_');
        if ~isempty(n0)
            s0 = s0(n0+1:end);
        end
        site = s0;
        ns = strcmp(sid, s0);
        nj = find(ns > 0);
        lon = xx(nj);
        lat = yy(nj);
        elv = zz(nj);
        gid{i,1} = s0;
        geo(i,:) = [lat,lon,elv];
        
        ff = [inw files{i} '.ind.csv'];
        fp = fopen(ff, 'r');
        hdr1 = fgetl(fp);
        hdr2 = fgetl(fp);
        fclose(fp);
        s0 = textscan(hdr1,'%s','Delimiter',',');
        hdr1 = s0{1};
        
        s0 = textscan(hdr2,'%s','Delimiter',',');
        hdr2 = s0{1};
        
        % dat = dlmread(ff, ',', 2,3);
        M = importdata(ff, ',', 2);
        dat = M.data;
        [n,m]= size(dat);
        
        disp([ff ' ', num2str([n,m])]);
        
        xt = dat(end-1,:);
        xs = dat(end, :);
        j = 1;
        for v = 1 : ind_num
            lnd = [];
            for s = 1 : 5
                vs = find(strcmp(hdr1, ind_eng{v}) & strcmp(hdr2, season{s}));
                if ~isempty(vs)
                    x0 = dat(:,1);
                    y0 = dat(:,vs);
                    nx = length(x0);
                    
                    x1 = x0(~isnan(y0));
                    y1 = y0(~isnan(y0));
                    ny = length(y1);
                    
                    if ny >= 0.8 * nx
                        plot(x0, y0, [ssn_cl{s} '-.'], 'LineWidth',2);
                        [b,bint,r,rint,p] = regress(y1,[ones([ny,1]) x1]);
                        hold on;
                        plot(x1, b(1)+b(2)*x1, [ssn_cl{s} '-'], 'LineWidth',2);
                        
                        ylabel([dsp_use{v} ' (' ind_unt{v} ')'], 'FontSize', 12);xlabel('Year', 'FontSize', 12);
                        title(site);
                        lnd{s,1} = ['\color{' col_nm{s} '}' season{s} ' (p = ' num2str(p(3),'%.2f'),')'];
                        set(gca, 'FontSize', 12);
                        
                        XT(i,j) = b(2);
                        XS(i,j) = p(3);
                        XR(i,j) = p(1);
                    else
                        XT(i,j) = NaN;
                        XS(i,j) = NaN;
                        XR(i,j) = NaN;
                    end
                else
                    XT(i,j) = NaN;
                    XS(i,j) = NaN;
                    XR(i,j) = NaN;
                end
                j = j + 1;
            end
            hold off;
            if ~isempty(lnd)
                text(min(x0),max(y0),lnd);
                
                fig = [ouw '\' site '_' ind_eng{v} '.jpg'];  % season{s} '_'
                saveas(gca, fig);
            end
        end
    end
    xlswrite(file_ind_desp, XT, 'Trend','E3');
    xlswrite(file_ind_desp, gid, 'Trend','A3');
    xlswrite(file_ind_desp, geo, 'Trend','B3');
    xlswrite(file_ind_desp, hdr, 'Trend','E1');
    xlswrite(file_ind_desp, {'StaID','Lat','Lon','Elv'}, 'Trend','A1');
    
    xlswrite(file_ind_desp, XS, 'TrdSIG','E3');
    xlswrite(file_ind_desp, gid, 'TrdSIG','A3');
    xlswrite(file_ind_desp, geo, 'TrdSIG','B3');
    xlswrite(file_ind_desp, hdr, 'TrdSIG','E1');
    xlswrite(file_ind_desp, {'StaID','Lat','Lon','Elv'}, 'TrdSIG','A1');
    
end
