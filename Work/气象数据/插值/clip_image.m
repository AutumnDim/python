%**********************************************
%**********************************************
%***********##############*********************
%***********##############*********************
%***********##############*********************
%*****(6,10)##############*********************
%**********************************************
%**********************************************
%**********************************************
%(10,40)***************************************
close all
clear all
clc
[dat, R, bbox] = geotiffread(fdat);
lline = 4089;
lpixel = 4998;
% coordination at lower left
lmap = [-3121854.814  1793290.052 999.929 999.929];
% coordination at lower left
smap = [-1833946.262  4337701.777 999.929 999.929];
sline = 902;
spixel = 1219;
% delta x
delta_x = smap(1) - lmap(1);
delta_y = smap(2) - lmap(2);
% delta col, row
delta_l = fix(delta_x / lmap(3));
delta_p = fix(delta_y / lmap(3));

xul = 1289;
yul = 1544;

xlr = 2508;
ylr = 2446;

lgf = 'F:\temp\chn_dem_1km.img';
fp = fopen(lgf, 'r');
lgd = fread(fp, [lpixel lline], 'int16');
fclose(fp);
figure
lgd = lgd';
subplot(2,2,1)
imagesc(lgd);

% smf = 'H:\Qinghai\auxiliary\elv';
% fp = fopen(lgf, 'r', 'b');
% smd = fread(fp, [spixel sline ], 'long');
% fclose(fp);
subplot(2,2,2)
smd = imread('f:\temp\qh_dem.tif');
imagesc(smd);

subplot(2,2,3)
nmap = lgd(yul:ylr,xul:xlr);
imagesc(nmap);
max(nmap(:))
min(nmap(:))
hold on
y = 10:1200;
x = ones(size(y)) * 500;
plot(y,x,'b.')
comp = [smd(100:150,500) nmap(100:150,500)];
subplot(2,2,4)
plot(comp)