close all
clear all
clc
%% Include 6 prceduals: 
% rps(2) = 1
                % calculate 8 days mean
% rps(3) = 1                
                % calculate half month mean/sum
% rps(4) = 1                  
                % calcuate 10 days mean or sum
% rps(5) = 1                  
                % calcuate regional mean or sum
% rps(6) = 1                     
                % MAKESPLINABAT: Produce Anusplin bat file
%%                
wks = 'E:\MeteoGrid\dbase'; 
var = {'PRCP';'TMIN';'TMAX';'WIN';'RHU';'SSD';'TEM';'WVP'};
% fs = [wks '\CMGH\CMGH\GHCN_CHINA_DEM_ACEA-ed.txt'];
fs = 'E:\MeteoGrid\Station\Stations_5k_ACEA.txt';
[no id lon lat elv dem dflg] = textread(fs,'%d%s%f%f%f%f%d','headerlines',1);
gid = cell2mat(id);
geo = [lon lat dem];

fi ='E:\MeteoGrid\CMGHfilled\'; 
if ~exist(fi, 'dir')
    mkdir(fi);
end

yr1 = 2015;
yr2 = 2016;
rps = [1 1 0 0 0];   % reprocess

tic
for v = 1 : 3  % 
    varname = var{v};
    sub = ['E:\MeteoGrid\CMGHfilled\' varname];
    if ~exist(sub,'dir')
        system(['mkdir ' sub]);
    end
        
    if v >= 8
        continue;
    end  
    YNS=[];
    for year = yr1: yr2
        days = datenum(year+1,1,1)-datenum(year,1,1);
           
        fin = [wks '\' num2str(year) '\' varname '_' num2str(year) '.txt'];
        if exist(fin,'file')
            disp(['Processing ' varname ' in ' num2str(year)]);

          %% Read daily data for each variable in a year
            % Import the file
            dat = importdata(fin);
            xid = dat.textdata;
            xid = char(xid);
            xdt = dat.data;
            [n m] = size(xdt);
            %xdt = xdt(:,4:m);
            sta = xid;
            days = min(days, m-3);
            %% calculate 8 days mean
            if rps(2) == 1
                disp('      REALPREC: Check missing values and remove them');
                %% REALPREC: specific code transfered to precipitation
                %            input:var, xdt(Numstations,days+1)
                %            output: xdt(Numstations, days+1)
                [y0] = realprec(varname(1), xdt);

                % Remove out station the completeness < 0.9
                % Input: xid-stationName, y0(Numstations, days+1)
                % Output: yc(Numstations,
                % days),sd(Numstations),ys(Numsta,mean sum std max min
                % numData)
                [yc sd ys n_completeness] = completeness(xid, y0,0.90,days);
				outway = 'E:\MeteoGrid\Completeness';
                if ~exist(outway,'dir')
                    system(['mkdir ' outway]);
                end				
				writemeteo2text(year, varname,outway,xid,n_completeness);
                [nx(1) ~] = size(yc);
                if year == yr1
                    S = sd;
                    Y = ys;
                else
                    S = [S; sd];
                    Y = [Y; ys];
                end

                % Output stations having geographic information
                [yg,sg,yns] = staselect(gid, yc, sd);
                [nx(2) tp] = size(yg);
                [nx(3) tp] = size(yns);
                YNS = [YNS;yns];
                unique(char(YNS),'rows')
                if nx(3) > 0
                    disp('Stations without geoinformation:');
                    disp(char(YNS));
                    disp(size(YNS));
                end

                % Fill missing values
                
                [yf_daily qc sta,nx(5)] = fillmissing(sg, yg,gid,geo);
                sta = char(sta);
                [nx(4) tp] = size(yf_daily);
                N(year-yr1+1,:) = [year v nx];
                
                % Write filled data to text file
%                 outway = 'F:\Yehui\CMGH2013\CMGHfilled\PRCP';
                outway = 'E:\MeteoGrid\GHCN\CMGHfilled';
                if ~exist(outway,'dir')
                    system(['mkdir ' outway]);
                end
                writemeteo2text(year, varname,outway,sta,yf_daily);
%                 outway = 'F:\Yehui\CMGH2013\CMGHfillQC';
                outway = 'E:\MeteoGrid\CMGHfillQC';
                if ~exist(outway, 'dir')
                    system(['mkdir ' outway]);
                end
                writemeteo2text(year, varname,outway,sta,qc);
                
                disp(['      MEANBYDOY: Calculating 8days mean or sum: ' varname, ' in ' num2str(year)]);
                if v == 1
                    ms = 0;% 0 for sum
                else
                    ms = 1;% 1 for mean
                end
                [ym_8days, q, sta] = meanbydoy(yf_daily, sta, days, 8, ms);
                
                % Write result to text file
                outway = [wks '\CMGH8days'];
                if ~exist(outway, 'dir')
                    system(['mkdir ' outway]);
                end                 
                writemeteo2text(year, varname,outway,sta,ym_8days);
                
                % Write file for Anusplin software
                disp(['      CSV2ANUSPL: Output Anusplin file: ' varname ' in ' num2str(year)]);
                outway = [wks '\CMGH8days'];
                if ~exist(outway, 'dir')
                    system(['mkdir ' outway]);
                end                
                csv2Anuspl(year, varname, outway,gid,geo, ym_8days, sta);
            end
             %% calculate half month mean/sum
            if rps(3) == 1
                disp(['      MEANBYHFMONTH: Calculating Half month mean or sum: ' varname, ' in ' num2str(year)]);
                if v == 1
                    ms = 0;% 0 for sum
                else
                    ms = 1;% 1 for mean
                end
                [ym_hmonth, q, sta] = meanbyhfmonth(yf_daily, sta, year,days, ms);
                
                % Write result to text file
                outway = [wks '\CMGH15days'];
                if ~exist(outway, 'dir')
                    system(['mkdir ' outway]);
                end                
                writemeteo2text(year, varname,outway,sta,ym_hmonth);
                
                % Write file for Anusplin software
                disp(['      CSV2ANUSPL: Output Anusplin file: ' varname ' in ' num2str(year)]);
                outway = [wks '\CMGH15days'];
                if ~exist(outway, 'dir')
                    system(['mkdir ' outway]);
                end                
                csv2Anuspl(year, varname, outway,gid,geo, ym_hmonth, sta);                
            end
            
            if rps(4) == 1
                disp(['      MEANBYHFMONTH: Calculating 10-days mean or sum: ' varname, ' in ' num2str(year)]);
                if v == 1
                    ms = 0;% 0 for sum
                else
                    ms = 1;% 1 for mean
                end
                dn = days2xday(yr, 10);
                [ym_hmonth, q, sta] = meanbyxday(yf_daily, sta, dn, ms);
                
                % Write result to text file
                outway = [wks '\CMGH10days'];
                if ~exist(outway, 'dir')
                    system(['mkdir ' outway]);
                end                
                writemeteo2text(year, varname,outway,sta,ym_hmonth);
                
                % Write file for Anusplin software
                disp(['      CSV2ANUSPL: Output Anusplin file: ' varname ' in ' num2str(year)]);
                outway = [wks '\CMGH10days'];
                if ~exist(outway, 'dir')
                    system(['mkdir ' outway]);
                end                
                csv2Anuspl(year, varname, outway,gid,geo, ym_hmonth, sta);                
            end          

            % calcuate regional mean or sum
            if rps(5) == 1
                [yst,qst] = regionalmean(xdt,xid,ms,year,days);
%                 [yst,qst] = regionalmean(yf,sta,ms,year,days);
                if year == yr1
                    YRS = yst;
                else
                    YRS = [YRS; yst];
                end
            end
        else
            disp(['      REALPREC: Input file not exist: ', fin]);
        end
    end  % LOOP of year
    if rps(5) == 1
        if ~exist([wks '\CMCN8days'],'dir')
            system(['mkdir ' wks '\Meteosta\CMCN8days']);
        end
        ff = [wks '\CMCN8days\' varname '_region_sta_obs.csv'];
        csvwrite(ff, YRS);
        STN_NOGEO(v) = length(YRS);
        disp(STN_NOGEO(v));
    end
    
end % LOOP of variables (j)

%% MAKESPLINABAT: Produce Anusplin bat file
% if rps(5) == 1
%     % direct data, cmd, grd for write and run annusplin
%     year = [yr1 yr2];
%     direct = {{'meteo/Weekly8012/';'meteo/MeteoGrid8012/TEMP/';'meteo/MeteoGrid8012/'};...
%         {'z:\\meteo\\Weekly8012\\';'z:\\meteo\\MeteoGrid8012\\TEMP\\';'z:\\meteo\\MeteoGrid8012\\'}};
% 
%     makesplinabat(year, direct);
% end
% %% output QC
% if rps(1) == 1
%     fout = [fo varname '/' varname '_' num2str(year) '_filled.csv'];
%     if exist(fout, 'file')% Number of data for each station
%         yr = yr1: yr2;
%         ny = length(yr);
%         D = [yr' qnum(1:ny,:)];
%         csvwrite([fo 'qnum.csv'], D);
%         csvwrite([fo 'qday.csv'], qday);
%         csvwrite([fo 'qsta.csv'], qsta);
%     end
% end
toc