function Disp_MeteoGrid(v, wks, fmask, fhdr,yr1, yr2,nday)
% vname = {'PRCP'; 'TMIN'; 'TMAX'; 'TAVG'; 'RHU'; 'SSD';  'WIN'};
% v = 1;
% wks = '\\BA-37AEDE\Workspace\China8km\MetGrid15Days';
% fmask = '\\BA-37AEDE\Workspace\China8km\Parameters\Climate_4R.tif';
% fhdr = '\\BA-37AEDE\Workspace\China8km\Parameters\asia_dem_8km.hdr';
% yr1 = 1980;yr2 = 2015;
% nday = 24;

vname = {'PRCP'; 'TMIN'; 'TMAX'; 'TEM'; 'RHU'; 'SSD';  'WIN'};
reg_name = {'TQPlateau','SubTropical','Temperate','Continental'};
m = length(fhdr);
fprj = fhdr;
fprj(m-2:m) = 'prj';
grd = readgrdhdr(fhdr);
t1 = now();
if strcmp(fmask(end-2:end),'tif')
    luc = (imread(fmask))';
else
    fp = fopen(fmask, 'r');
    luc = fread(fp, [grd.ncols, grd.nrows], 'int8');
    fclose(fp);
end
lc = unique(luc(luc < 100));
nc = length(lc);
imagesc(luc',[0 10]);

temp_sub = ['D:\temp\' vname{v}];
if ~exist(temp_sub, 'dir')
    mkdir(temp_sub);
end

if nday == 24
    num_zero = 1000;
    dy = 1 : nday;
    mon = fix((dy - 1) / 2) + 1;
    di = mod(dy - 1,2) * 15 + 1;
else
    num_zero = 1000;
end
i = 1;xm = [];
    for yr = yr1: yr2
        tic
        for dy = 1 : nday
            if nday == 24
                jday =  datenum(yr, mon(dy), di(dy)) - datenum(yr, 1, 1)+ 1;
            else
                jday = (dy-1)*8+1;
            end
            ff = [wks '\' vname{v} '\' vname{v} '_' num2str(yr * num_zero + dy) '.flt'];
            if exist(ff, 'file')
                fp = fopen(ff, 'r');
                x0 = fread(fp, [grd.ncols, grd.nrows], 'float32')/10.0;
                fclose(fp);
                rg = quantile(x0(x0 > -900), [0.05 0.95]);
                
                if v == 1 || v > 4
                    x0 = x0 .* (x0 >=0);
                    rg(1) = 0;
                end

                xm(i,1:2) = [yr dy];
                for j = 1 : nc + 1
                    if j <= nc
                        xm(i,j+2) = mean(x0(x0 >= rg(1) & luc == lc(j)));
                    else
                        xm(i,j+2) = mean(x0(x0 >= rg(1) & luc < 100));
                    end
                end
                
                if rg(2) > rg(1) && mod(yr,10) == 0
                    figure('Visible','off')
                    imagesc(x0', rg);
                    title(datestr(datenum(yr,1,1)+(dy-1)*8));
                    colormap(jet(150));
                    colorbar('horiz');
                    axis equal
                    axis off
                    fig = [wks '\' vname{v} '\' vname{v} '_' num2str(yr * num_zero + dy) '.jpg'];
                    saveas(gca, fig);
                end
                i = i + 1;
                 
                ff = [temp_sub '\' vname{v} '\' vname{v} '_' num2str(yr * num_zero + dy) '.prj'];
                [status, results] = dos(['copy ' fprj ' ' ff ]);
                
                ff = [temp_sub '\' vname{v} '\' vname{v} '_' num2str(yr * num_zero + dy) '.hdr'];
                [status, results] = dos(['copy ' fhdr ' ' ff ]);
            end
        end
        % disp([yr dy rg]);toc
        t2 = toc;
        disp([vname{v} ' ' num2str(yr) ' Elapsed time is ' num2str(toc) ' seconds. And ' vname{v} ' will be finished at ' datestr(t1 + t2 * (yr2 - yr1), 14)]);
    end
    
fout =  [wks '\' vname{v} '_' num2str(yr1) '-' num2str(yr2) '_MeteoGrid.xls'];
xlswrite(fout, {'YEAR','DY'}, 'Raw_data', 'A1');
xlswrite(fout, reg_name, 'Raw_data', 'C1');
xlswrite(fout,xm,'Raw_data','A2');

% Calculate the mean and std of filled data in a year for each station
mn = []; st = [];XF = xm;
for yr = yr1 : yr2
    x0 = XF(xm(:,1) == yr,3:end);
    x1 = x0;
    if strcmp('PRCP', vname{v})
        mn(yr-yr1+1,:) = [yr sum(x1)];
    else
        mn(yr-yr1+1,:) = [yr mean(x1)];
    end
    st(yr-yr1+1,:) = [yr std(x1)];
end
xlswrite(fout, {'YEAR'}, 'Annual_data', 'A1');
xlswrite(fout, reg_name, 'Annual_data', 'C1');
xlswrite(fout,mn,'Annual_data','A2');

xlswrite(fout, {'YEAR'}, 'Annual_std', 'A1');
xlswrite(fout, reg_name, 'Annual_std', 'C1');
xlswrite(fout,st,'Annual_std','A2');
disp(['Writen results to ' fout '.']);