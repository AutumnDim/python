confile = 'F:\Workspace\Sanjy250m\sanjy_8d250m_dyn_pc.txt';
fhdr = 'F:/Sanjy250m/Parameters/dem_sjy250m.hdr';
fprj = 'F:/Sanjy250m/Parameters/dem_sjy250m.prj';
% confile = 'F:\Workspace\China1km\China1km_8d1km_init_pc.txt';
% confile = 'F:\Workspace\China1km\China1km_8d1km_dyn_pc.txt';
% fhdr = 'F:\China1km\WIN_1980097.hdr';
% fprj = 'F:\China1km\WIN_1980097.prj';
day_or_year = 2;
% GLCV_Merge(confile, fhdr, fprj, day_or_year);

% function GLCV_Merge(confile, fhdr, fprj, day_or_year)
% GLCV_Merge.m
% close all; clear all; clc;
if ~exist(confile, 'file')
    errordlg(['Cannot find file: ', confile]);
    return;
end
[hdr, value] = textread(confile, '%s %s');

yr1 = str2double(value{2, 1});
yr2 = str2double(value{3, 1});
nk = str2double(value{8, 1});

nlines = str2double(value{6, 1});
npixels = str2double(value{7, 1});

wks = value{42, 1};
owk = wks;

hdr = fhdr;      % 'H:\Workspace\China1km\outway\china1km.hdr';
prj = fprj;         % 'H:\Workspace\China1km\outway\china1km.prj';

% Daily
dvar = {'Ra','NEP','Rn','Rh','PLUE','PET','LUE','ET','GPP','NPP','Rs','DIF'};

pvar = {'SW/snow','SW/SW','storage/soc','storage/vgc'};%

% Annually
avar = {'NPP', 'ET', 'GPP','NEP','Rn', 'Rs', 'Rh', 'Total_Ero', 'Water_Ero', 'Wind_Ero'}; % , 'PET'};
xnd = [0, 1500; 0, 1200; 0 3000; -1000, 1000; 0 3500; 0 3500; 0 1500; 0, 1.4e5; 0, 1.4e5; 0, 10; 0 1500];
dv = 4;
yr1 = 2000;yr2 = 2016;

switch day_or_year
    case 1        %% Annually
        % sub = [owk '\sum'];
        for v = 1 :   length(avar)
            mvar = avar{v};
            sub = [wks '\sum'];
            if ~exist(sub, 'dir')
                mkdir(sub);
            end
            for yr = yr1 : yr2
                X = [];
                for bk = 1 : nk
                    % sub = [wks '\Results' num2str(bk) '\sum'];
                    ff = [wks, num2str(bk), '\sum\',  mvar num2str(yr) '.flt'];
                    fip = fopen(ff, 'r');
                    xd = fread(fip, 'float32');
                    fclose(fip);
                    [n, m] = size(xd);
                    
                    % disp([yr, bk, n, m]);
                    
                    if bk == 1
                        X = xd;
                    else
                        X = [X; xd];
                    end
                end
                [p, l] = size(X);
                
                dat = reshape(X, npixels, nlines);
                bnd = quantile(dat(dat > -900), [0.05, 0.95]);
                if bnd(2) > bnd(1)
                    if bnd(2) > 0 && bnd(1) < 0
                        x = max(abs(bnd));
                        if x > 1000, x = 1000; end
                        bnd = [-x, x];
                    end
                    imagesc(dat', bnd); colorbar('horizonal'); axis off; axis equal
                    title([mvar ' in ' num2str(yr)]);
                    fig = [owk '\sum\' mvar '_' num2str(yr) '.png'];
                    saveas(gca, fig);
                    
                    ff = [owk '\sum\' mvar '_' num2str(yr) '.flt'];
                    fop = fopen(ff, 'w');
                    fwrite(fop, dat, 'float32');
                    fclose(fop);
                    
                    ff = [owk '\sum\' mvar '_' num2str(yr) '.hdr'];
                    ff(ff == '/') = '\';
                    [s1, s2] = system(['copy ' hdr ' ' ff]);
                    
                    ff = [owk '\sum\' mvar '_' num2str(yr) '.prj'];
                    ff(ff == '/') = '\';
                    [p1, p2] = system(['copy ' prj ' ' ff]);
                    
                end
                disp([mvar, ' ', num2str([yr, bnd])]);
            end
        end
    case 2       % Daily
        for v = 6 : 6 %1 : length(dvar)
            mvar = dvar{v};
            for yr = 2000 : 2018
                for dy = 1 : 46
                    jday = (dy - 1) * 8 + 1;
                    X = [];
                    for bk = 1 : nk
                        ff = [wks, num2str(bk) '\' mvar,'\', mvar, num2str(yr * 1000 + jday) '.flt'];
                        fip = fopen(ff, 'r');
                        xd = fread(fip, 'float32');
                        fclose(fip);
                        [n, m] = size(xd);
                        
                        % disp([yr, bk, n, m]);
                        
                        if bk == 1
                            X = xd;
                        else
                            X = [X; xd];
                        end
                    end
                    
                    [p, l] = size(X);
                    
                    dat = reshape(X, npixels, nlines);
                    
                    bnd = quantile(dat(dat > -900), [0.05, 0.95]);
                    if bnd(2) > bnd(1)
                        imagesc(dat', bnd); colorbar('horizonal'); axis off; axis equal
                        title([mvar ' on ' num2str(jday) ' of ', num2str(yr)]);
                        fig = [owk '\' mvar  '\' mvar, '_' num2str(yr * 1000 + jday) '.png'];
                        saveas(gca, fig);
                    end
                    
                    fout = [wks '\' mvar, '\' mvar,  '_', num2str(yr * 1000 + jday) '.flt'];
                    fop = fopen(fout, 'w');
                    fwrite(fop, dat, 'float32');
                    fclose(fop);
                    
                    ff =  [wks '\' mvar, '\' mvar,  '_', num2str(yr * 1000 + jday), '.hdr'];
                    ff(ff == '/') = '\';
                    [s1, s2] = system(['copy ' hdr ' ' ff]);
                    
                    ff =  [wks '\' mvar, '\' mvar,  '_', num2str(yr * 1000 + jday), '.prj'];
                    ff(ff == '/') = '\';
                    [p1, p2] = system(['copy ' prj ' ' ff]);
                    
                    disp([mvar, ' ', num2str([yr, jday, bnd])]);
                end
            end
        end
    case 3        %% Annually carbon pool and soil water content balance
        % sub = [owk '\sum'];
        for v = 1 :  length(pvar)
            mvar = pvar{v};
            for yr = yr1+1 : yr2
                X = [];
                for bk = 1 : nk
                    % sub = [wks '\Results' num2str(bk) '\sum'];
                    ff = [wks, num2str(bk), '\',  mvar num2str(yr) '.flt'];
                    fip = fopen(ff, 'r');
                    xd = fread(fip, 'float32');
                    fclose(fip);
                    [n, m] = size(xd);
                    
                    % disp([yr, bk, n, m]);
                    
                    if bk == 1
                        X = xd;
                    else
                        X = [X; xd];
                    end
                end
                [p, l] = size(X);
                
                dat = reshape(X, npixels, nlines);
                bnd = quantile(dat(dat > -900), [0.05, 0.95]);
                if bnd(2) > bnd(1)
                    if bnd(2) > 0 && bnd(1) < 0
                        x = max(abs(bnd));
                        if x > 1000, x = 1000; end
                        bnd = [-x, x];
                    end
                else
                    bnd = [0, 1000];
                end
                imagesc(dat', bnd); colorbar('horizonal'); axis off; axis equal
                title([mvar ' in ' num2str(yr)]);
                fig = [owk '\' mvar '_' num2str(yr) '.png'];
                saveas(gca, fig);
                
                ff = [owk '\' mvar '_' num2str(yr) '.flt'];
                fop = fopen(ff, 'w');
                fwrite(fop, dat, 'float32');
                fclose(fop);
                
                ff = [owk '\' mvar '_' num2str(yr) '.hdr'];
                ff(ff=='/') = '\';
                [s1, s2] = system(['copy ' hdr ' ' ff]);
                
                ff = [owk '\' mvar '_' num2str(yr) '.prj'];
                ff(ff=='/') = '\';
                [p1, p2] = system(['copy ' prj ' ' ff]);
                
                
                disp([mvar, ' ', num2str([yr, bnd])]);
            end
        end
    case 4   %% sum daily to annuall value
        for v = 8 : 8 % length(avar)
            mvar = dvar{v};
            parfor bk = 1 : nk
                tic;
                for yr = yr1 : yr2
                    day_num = datenum(yr + 1, 1, 1) - datenum(yr, 1,1);
                    for dy = 1 : 46
                        if dy < 46
                            num = 8;
                        else
                            num = mod(day_num, 8);
                        end
                        
                        jday = (dy - 1) * 8 + 1;
                        sub = [wks '\Results' num2str(bk) '\' mvar];
                        ff = [sub '\' mvar num2str(yr * 1000 + jday) '.flt'];
                        fip = fopen(ff, 'r');
                        xd = fread(fip, [nP, 1], 'float32');
                        fclose(fip);
                        [n, m] = size(xd);
                        if dy == 1
                            X = xd * num;
                        else
                            X = X + xd * num;
                        end
                    end
                    sub = [wks '\Results' num2str(bk) '\sum\' mvar];
                    if ~exist(sub, 'dir')
                        mkdir(sub);
                    end
                    ff = [sub '\' mvar num2str(yr) '.flt'];
                    fop = fopen(ff, 'w');
                    fwrite(fop, X, 'float32');
                    fclose(fop);
                    
                    ff = [sub '\' mvar num2str(yr), '.hdr'];
                    ff(ff=='/') = '\';
                    [s1, s2] = system(['copy ' hdr ' ' ff]);
                    
                    ff = [sub '\' mvar num2str(yr), '.prj'];
                    ff(ff=='/') = '\';
                    [p1, p2] = system(['copy ' prj ' ' ff]);
                    disp(num2str([v, bk, yr, quantile(X(X > -900), [0.05, 0.5, 0.95])], '%6.0f'));
                    % jk = yr - yr1 + 1;
                    % C(jk, bk) = mean(X(X > -900), 'omitnan');
                end
                toc
            end
            % csvwrite([sub '\' mvar '_' num2str(yr1) '-' num2str(yr2) '.csv'], C);
        end
end
% end