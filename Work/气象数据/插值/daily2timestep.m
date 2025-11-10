% [days, dy2, dn] = daily2timestep(yr, time_step)
% days = datenum(yr+1,1,1)-datenum(yr,1,1);
% dy1 = 1:days;  % weekly average
% dn = length(days) for annually, 8 for week, 36 for 10-day, 30 for monthly
%      and 15 for bi-weekly
% dy2 = ones([1,days]) for annually, and 1 : dn for others
% jbwang@igsnrr.ac.cn
% dec04,2018
% C2421@IGSNRR.CAS.CN

function [days, dy2, dn] = daily2timestep(yr, time_step)
days = datenum(yr+1,1,1)-datenum(yr,1,1);
dy1 = 1:days;  % weekly average
dy2 = [];
switch time_step
    case 1   % Annually
        dy2 = ones([1,days]);
    case 8
        dy2 = fix((dy1 - 1) / 8) * 8 + 1;
    case 10  % 10-day
        mon = month(datenum(yr,1,1) + dy1 - 1);
        dy  = day(datenum(yr,1,1) + dy1 - 1);
        mj  = dy;
        mj(dy <= 10) = 1; mj(dy > 10 & dy <= 20) = 2; mj(dy > 20) = 3;
        dy2 = (mon - 1) * 3 + mj;
    case 30  % Monthly
        dy2 = month(datenum(yr,1,1) + dy1 - 1);
    case 15  % Half-monthly
        mon = month(datenum(yr,1,1) + dy1 - 1);
        dy  = day(datenum(yr,1,1) + dy1 - 1);
        mj  = dy;
        mj(dy <= 15) = 1; mj(dy > 15) = 2;
        dy2 = (mon - 1) * 2 + mj;
end
dx = unique(dy2);
nx = length(dx);
dn = zeros([nx,1]);
for i = 1 : nx
    dn(i,1) = sum(dy2==dx(i));
end