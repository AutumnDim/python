function Compare_MeteoGrid(v, wks1, wks2, num01, num02, fmask, fhdr,yr1, yr2,nday)
% vname = {'PRCP'; 'TMIN'; 'TMAX'; 'TAVG'; 'RHU'; 'SSD';  'WIN'};
% v = 1;
% wks = '\\BA-37AEDE\Workspace\China8km\MetGrid15Days';
% fmask = '\\BA-37AEDE\Workspace\China8km\Parameters\Climate_4R.tif';
% fhdr = '\\BA-37AEDE\Workspace\China8km\Parameters\asia_dem_8km.hdr';
% yr1 = 1980;yr2 = 2015;
% nday = 24;
warning off;
vname = {'PRCP'; 'TMIN'; 'TMAX'; 'TAVG'; 'RHU'; 'SSD';  'WIN'};
vad_value = [0 1000; -60 60; -60 60; -60 60; 0 100; 0 18; 0 20];
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
% imagesc(luc',[0 10]);

temp_sub = ['D:\temp\Comp_Meteo\' vname{v}];
if ~exist(temp_sub, 'dir')
    mkdir(temp_sub);
end

if nday == 24
    dy = 1 : nday;
    mon = fix((dy - 1) / 2) + 1;
    di = mod(dy - 1,2) * 15 + 1;
end
i = 1;xm = [];
    for yr = yr1: yr2
        tic
        for dy = 23 : nday
            if nday == 24
                jday =  datenum(yr, mon(dy), di(dy)) - datenum(yr, 1, 1)+ 1;
            else
                jday = (dy-1)*8+1;
            end
            ff1 = [wks1 '\' vname{v} '\' vname{v} '_' num2str(yr * num01 + dy) '.flt'];
            ff2 = [wks2 '\' vname{v} '\' vname{v} '_' num2str(yr * num02 + dy) '.flt'];
            if exist(ff1, 'file') && exist(ff2, 'file')
                fp = fopen(ff1, 'r');
                x1 = fread(fp, [grd.ncols, grd.nrows], 'float32')/10.0;
                fclose(fp);
                
                fp = fopen(ff2, 'r');
                x2 = fread(fp, [grd.ncols, grd.nrows], 'float32')/10.0;
                fclose(fp);
                
                rg = quantile(x2(x2 > -900), [0.05 0.95]);
                x01 = x1; x02 = x2;
                if v == 1 || v > 4
                    x1 = x1 .* (x1 >= 0);
                    x2 = x2 .* (x2 >= 0);
                    rg(1) = 0;
                end
                x1(x01 < -900) = -9999; x2(x02 < -9000) = -9999;
                
                % valid data check
                x01 = x1(x1 > -900 & luc < 100 & luc > 0);
                x11 = x1(x1 >= vad_value(v,1) & x1 <= vad_value(v, 2) & luc < 100 & luc > 0);
                n11 = (length(x01) - length(x11)) * 100 / length(x01);
                rg1 = quantile(x1(x1 > -900), [0.05 0.95]);
                
                x02 = x1(x2 > -900 & luc < 100 & luc > 0);
                x12 = x2(x2 >= vad_value(v,1) & x1 <= vad_value(v, 2) & luc < 100 & luc > 0);
                n12 = (length(x02) - length(x12)) * 100 / length(x02);
                rg2 = quantile(x2(x2 > -900), [0.05 0.95]);
                
                if n11 > 0 || n12 > 0
                    disp([vname{v} ' ' num2str(dy) ' Valid percent n1 = : ' num2str(n11) ' %, n2 = ' num2str(n12) ' %']);
                    disp(['      P_{1,0.05} = ' num2str(rg1(1)) ', P_{1,0.95} = ' num2str(rg1(2))]);
                    disp(['      P_{2,0.05} = ' num2str(rg2(1)) ', P_{1,0.95} = ' num2str(rg2(2))]);
                end
                
                xm(i,1:2) = [yr dy];
                for j = 1 : nc + 1
                    if j <= nc
                        xm(i,j+2) = mean(x1(x1 >= rg(1) & luc == lc(j)));
                    else
                        xm(i,j+2) = mean(x1(x1 >= rg(1) & luc < 100));
                    end
                end

                for j = 1 : nc + 1
                    if j <= nc
                        xm(i,j+7) = mean(x2(x2 >= rg(1) & luc == lc(j)));
                    else
                        xm(i,j+7) = mean(x2(x2 >= rg(1) & luc < 100));
                    end
                end
                
                if rg(2) > rg(1) % && mod(yr,10) == 0
                    figure('Visible','off')
                    subplot(1,2,1);
                    imagesc(x1', rg); text(50, -50, [vname{v} ' ' datestr(datenum(yr,1,1) + jday - 1)]);
                    colormap([white(1); jet(150)]); colorbar('horiz'); axis equal; axis off
                    subplot(1,2,2);
                    imagesc(x2', rg); text(50, -50, [vname{v} ' ' datestr(datenum(yr,1,1) + jday - 1)]);
                    colormap([white(1); jet(150)]); colorbar('horiz'); axis equal; axis off
                    
                    fig = [temp_sub '\' vname{v} '_' num2str(yr * num02 + dy) '.jpg'];
                    saveas(gca, fig);
                end
                i = i + 1;
            else
                disp('Did NOT find files:'); disp(ff1); disp(ff2);
            end
        end
        % disp([yr dy rg]);toc
        t2 = toc;
        disp([vname{v} ' ' num2str(yr) ' Elapsed time is ' num2str(toc) ' seconds. And ' vname{v} ' will be finished at ' datestr(t1 + t2 * (yr2 - yr1), 14)]);
    end
rmse = [];    
for i = 1 : 5 
    rmse(1,i) = (mean((xm(:,i+2) - xm(:,i+7)).^2))^0.5;
end
disp([vname{v} ' RMSE: ' num2str(rmse)]);
fout =  [wks2 '\' vname{v} '_' num2str(yr1) '-' num2str(yr2) '_MeteoGrid.xls'];
xlswrite(fout, {'YEAR','DY'}, 'Raw_data', 'A1');
xlswrite(fout, reg_name, 'Raw_data', 'C1');
xlswrite(fout,xm,'Raw_data','A2');

% Calculate the mean and std of filled data in a year for each station
mn = []; st = [];XF = xm;
for yr = yr1 : yr2
    x1 = XF(xm(:,1) == yr,3:end);
    x1 = x1;
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
