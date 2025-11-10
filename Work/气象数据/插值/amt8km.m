% Anual mean calculation from every 8dys data.
%     clear all
%     close all
%     clc
function amt8km(fset, fmask, name_1_46, time_step, v)
vname = {'PRCP','TMAX','TMIN','SSD','RHU','WIN','TAVG','SWRad'};
sc  = [10 10 10 10 10 1 10, 1];
ng  = [0 1 1 1 0 0 1, 0];
dmx = [200 20 20 15 15 100 10 100];
ymx = [1500 20 20 15 15 100 10, 10000];
xmn  = [0 1 1 1 1 1 1,0];      % 0 for sum and 1 for mean
suf = '.flt';

%fset = 'E:\MeteoGrid\Function_set\Sanjy.set';

if exist(fset, 'file')
    [sname, svalue] = textread(fset, '%s%s');
    yr1 = str2double(svalue{1});yr2 = str2double(svalue{2});
    wks_in  = svalue{3};
    wks_out = svalue{4};     % Database with Anusplin formation
    wks_tmp = svalue{5};    % Temporary fold for cmd files
    wks_grd = svalue{6};          % Database for interpolated grid
    
    fdem = svalue{7};
    fhdr = svalue{8};
    ftif = svalue{9};
else
    disp('Error: DID NOT find site information file');
    return;
end
[hd,vr] = textread(fhdr, '%s%s');
npixels   =     str2double(vr{1});
nlines    =     str2double(vr{2});
mymap=[white(1); jet(150)];


% fmask = 'E:\Sanjy250m\Parameters\SJYWuCover_2010_250m.tif';
% fp = fopen(fmask, 'r');
% xm = fread(fp,[npixels nlines], 'int16');
% fclose(fp);
% xm = double(imread(fmask))';
if exist(fmask)
    info = geotiffinfo(fmask);
    [mcd, R, bbox] = geotiffread(fmask);
    xm = mcd';
    bnd = max(xm(xm > -900 & xm < 100));
    vg_id = double(unique(xm));
    imagesc(xm',[0 bnd+1]); colorbar('horiz'); colormap([parula(20); white(1)]); axis off
end
j = 1;
i = 1;
k = 1;
x1_way = wks_grd;
x2_way = [wks_grd '\Figures'];
x3_way = [wks_grd '\annual'];
x4_way = [wks_grd '\Tables'];
dr = [-dmx(v) * ng(v) dmx(v)];     % ����ֵ��Χ
ar = [-ymx(v) * ng(v) ymx(v)];

if ~exist(x2_way, 'dir')
    mkdir(x2_way);
end
if ~exist(x3_way, 'dir')
    mkdir(x3_way);
end
if ~exist(x4_way, 'dir')
    mkdir(x4_way);
end

A = zeros([(yr2-yr1+1)*46*length(vg_id) 9]); B = zeros([(yr2-yr1+1)*length(vg_id) 8]);
for yr = yr1:1:yr2
    tic
    fprintf('Now processing %s in %d ...\n', vname{v}, yr);
    [days, dy2, dn] = daily2timestep(yr, time_step);
    num_in_a_year = length(dn);
    
    x3 = zeros([npixels nlines]);
    x1_num = 0;
    for dy = 1:num_in_a_year
        num = dn(dy);
        jday = (dy-1)*8+1;
        if name_1_46 == 1
            fyr = num2str(yr*1000+dy);
        else
            fyr = num2str(yr*1000+jday);
        end
        x1f = [x1_way '\' vname{v} '\' vname{v} '_' fyr suf];
        if i == 1
            disp(x1f);
        end
        if exist(x1f, 'file')
            x1p = fopen(x1f, 'r');
            x1  = fread(x1p, [npixels nlines], 'float32');
            fclose(x1p);
            
            [nx, mx] = size(x1);
            if nx ~= npixels || mx ~=nlines
                disp(['wrong size of ' x1f '!']);
            else
                
                x1(isnan(x1)) = -999;
                xc = x1;
                if ng(v) == 0
                    x1 = x1 .* (x1 >= 0);
                end
                x1(xc < -900) = -9999;
                for j = 1:length(vg_id)
                    cc = x1(find(xm == vg_id(j) & x1>-900));
                    nc = length(cc);
                    if ~isempty(cc)
                        % [xmn xsd xmax xmin nc] = stabigmatrix(cc);
                        A(i,:) = [i yr jday vg_id(j) mean(cc) max(cc) min(cc) std(cc) nc];
                        i = i + 1;
                        clear cc;
                    end
                end
                cc = x1(find(x1>-900));
                nc = length(cc);
                if ~isempty(cc)
                    %             [xmn xsd xmax xmin nc] = stabigmatrix(cc);
                    A(i,:) = [i yr jday 999 mean(cc) max(cc) min(cc) std(cc) nc];
                    clear cc;
                    i = i + 1;
                    figure('Visible','off');
                    x1(isnan(x1)) = -9999;
                    x1(isinf(x1)) = -9999;
                    bnd = quantile(x1(x1 > -900), [0.05, 0.95]);
                    disp([vname{v},' ', num2str([yr, dy, bnd])]);
                    if bnd(1) == bnd(2)
                        bnd(1) = dr(1);
                        bnd(2) = dr(2);
                    end
                    
                    h1 = imagesc(x1', bnd);
                    colormap(mymap);
                    colorbar('horiz');
                    axis equal
                    axis off
                    t=[vname{v} fyr];
                    title(t);
                    x1f = [x2_way '/' vname{v} fyr '.jpg'];
                    saveas(h1, x1f);
                    close(ancestor(h1,'figure'))
                    if v == 1   % PRCP is sum in a week
                        x3 = x3 + x1 / sc(v); %
                    else        % Others are mean in a week
                        x3 = x3 + x1 * num / sc(v); %
                    end
                end  % if ~isempty(cc)
                x1_num = x1_num + 1;
            end  % if the size is not matched
        end   % if exist(file)
    end     % used for "dy" loop
    if x1_num > num_in_a_year*0.7
        if xmn(v) == 1
            x3 = x3 / days; %
        end
        for j = 1:length(vg_id)
            cc = x3(find(xm == vg_id(j) & x3>-999));
            nc = length(cc);
            % [xmn xsd xmax xmin nc] = stabigmatrix(cc);
            B(k,:) = [k yr vg_id(j) mean(cc) max(cc) min(cc) std(cc) nc];
            k = k + 1;
            clear cc;
        end
        x3(isnan(x3)) = -9999;
        x3(isinf(x3)) = -9999;
        x3(x1 < -900) = -9999;
        cc = x3(find(xc > -900));
        nc = length(cc);
        if ~isempty(cc)
            %         [xmn xsd xmax xmin nc] = stabigmatrix(cc);
            B(k,:) = [k yr 999 mean(cc) max(cc) min(cc) std(cc) nc];
            k = k + 1;
            clear cc;
        end
        %        figure('Visible','on');
        bnd = quantile(x3(x3 > -900), [0.05, 0.95]);
        if isnan(bnd)
            bnd = ar;
        end
        if yr == yr1
            ax(1) = max(ar(1),bnd(1));
            ax(2) = min(ar(2),bnd(2));
        end
        xc = x3';
        h = imagesc(xc,bnd);
        % colormap(mymap);
        colorbar('horiz')
        axis equal
        axis off
        t=[vname{v} ' ' num2str(yr)];
        title(t);
        fig1 = [x3_way '\' vname{v} '_' num2str(yr) '.jpg'];
        saveas(h, fig1);
        %        close(ancestor(h,'figure'));
        %        close(gcbf);  % where gcbf stands for "get callback figure"
        %
        % x3f = [x3_way '\' vname{v} '_' num2str(yr) suf];
        % x3(xc <= -900) = -999;
        % x3p = fopen(x3f, 'wb');
        % fwrite(x3p, x3, 'float32');
        % fclose(x3p);
        x3f_tif = [x3_way '\' vname{v} '_' num2str(yr) '.tif'];
        geotiffwrite2(x3f_tif, xc, R, 'GeoKeyDirectoryTag', info.GeoTIFFTags.GeoKeyDirectoryTag);
        clear x3;
        %         writehdr(x3f, nlines, npixels, 1, 4,'bsq');
    end % x1_num > num_in_a_year*0.7
    toc
end         % used in for "yr" loop
if ~isempty(A)
    ftxta = [x4_way '/' vname{v} '_daily.csv'];
    csvwrite(ftxta, A);
end
if ~isempty(B)
    ftxtb = [x4_way '/' vname{v} '_annually.csv'];
    csvwrite(ftxtb, B);
end
disp('finish = ok!');
