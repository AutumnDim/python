function grd = readgrdhdr(fdat)
[n m] = size(fdat);
fhdr = fdat;

fhdr(m-2:m) = 'hdr';
[hdr gid]  = textread(fhdr,'%s%s');

if strcmp(hdr{1},'NCOLS') || strcmp(hdr{1},'ncols')
    grd.ncols  = str2num(gid{1});
    grd.nrows  = str2num(gid{2});
    grd.xll    = str2num(gid{3});
    grd.yll    = str2num(gid{4});
    grd.csize  = str2num(gid{5});
    grd.nodata = str2num(gid{6});
%     grd.byte   = gid{7};
else
    disp('Error: wong header formation');
    return;
end