fset = 'Sanjy.set';
Clear_outputs = 0;
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
    disp('Error: Not find site information file');
    return;
end
[hd,vr] = textread(fhdr, '%s%s');
npix = str2double(vr{1});
nlin = str2double(vr{2});
nimg = npix * nlin * 4;
vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN';'PRCP'};
vn = 6;
nn = 0;

CN = [];
for i = 1 : vn
    disp([vname{i}, ' ', num2str(i)]);
    % Check completity of files
    for yr = yr1 : yr2
        cn = 0;
        for j = 1 : 46
            k = (yr - yr1) * 46 + j;
            ff = ['H:\Database\qinghai\MeteoGrid\'  vname{i} '\' vname{i} '_' num2str(yr * 1000 + (j - 1) * 8 + 1) '.flt'];
            if exist(ff, 'file')
                fs = dir(ff);
                file_size = fs.bytes;
            else
                file_size =0;
            end
            if exist(ff, 'file') && file_size == nimg
                cn = cn + 1;
                CN(k, i) = 0;
            else
                ff = [wks_grd  vname{i} '\' vname{i} '_' num2str(yr * 1000 + (j - 1) * 8 + 1) '.flt'];
                if exist(ff, 'file')
                    fs = dir(ff);
                    file_size = fs.bytes;
                    if file_size == nimg
                        CN(k, i) = 0;
                        smove = ['move ' ff ' H:\Database\qinghai\MeteoGrid\'  vname{i} '\'];
                        [s, r] = system(smove);
                        file_name = [ff(1:end-4) '.hdr'];
                        smove = ['move ' file_name  ' H:\Database\qinghai\MeteoGrid\'  vname{i} '\'];
                        [s, r] = dos(smove);
                        CN(k, i) = 0;
                    else
                        CN(k, i) = 1;
                    end
                end
            end
        end
        disp(sum(CN(:)));
    end
end
for i = 1 : vn
    % change to vname{v} sub and run vname{v}_spl.bat
    ff = dir([wks_grd vname{i} '\*.flt']);
    nf = length(ff);
    if nf > 10
        parfor j = 1 : nf
            file_size = ff(j).bytes;
            if file_size == nimg
                nn = nn + 1;
                file_name = [wks_grd vname{i} '\' ff(j).name];
                smove = ['move ' file_name ' H:\Database\qinghai\MeteoGrid\'  vname{i} '\'];
                [s, r] = system(smove);
                file_name = [file_name(1:end-4) '.hdr'];
                smove = ['move ' file_name  ' H:\Database\qinghai\MeteoGrid\'  vname{i} '\'];
                [s, r] = dos(smove);
            end
        end
    else
        return;
    end
    fprintf('Has moved %d files.', nn);
end