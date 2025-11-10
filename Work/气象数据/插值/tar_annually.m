vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};
yr1 = 2017;
yr2 = 2018;
iwks = 'H:\Workspace\China8km15days\MeteoGrid';
owks = 'H:\Database\China8km15days\MeteoGrid';
if ~exist(owks, 'dir')
    mkdir(owks);
end
process = 2;
switch process
    case 1
        parfor yr = yr1 : yr2
            ff = [iwks '\' num2str(yr) '.csv'];
            fout = [iwks '\' num2str(yr) '.csv.gz'];
            gunzip(fout);
            disp(ff);
        end
    case 2
        vc = 1:7;
        files_year = 24;
        parfor v = 1 : length(vc)
            tic
            for yr = yr1 : yr2
                ff = [iwks '\' vname{v} '\' vname{v} '_' num2str(yr) '*.flt'];
                fs = dir(ff);
                nf = length(fs);
                if nf == files_year
                    ff = [iwks '\' vname{v} '\' vname{v} '_' num2str(yr) '*.*'];
                    fout = [owks '\' vname{v} '_' num2str(yr) '.tar'];
                    tar(fout, ff);
                    disp(['tar ' vname{v} '_' num2str(yr)])
                else
                    disp(['Missing ' vname{v} '_' num2str(yr)])
                end
            end
            toc
        end
end
