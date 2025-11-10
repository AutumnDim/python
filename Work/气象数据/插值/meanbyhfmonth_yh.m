function [y,q,sd] = meanbyhfmonth_yh(xx, sd, year, dn,ms)

% ff = 'meteo/Daily8012Filled/PRE/PRE_2005_filled.csv';
% xx = meteo[stations days]
% sd = stations(stations,:)
% dn = 365,days
% week = 15;
% ms = 1 for mean 0 for sum
nn = 24;
mn = 1:12;

dy1 = datenum(year,mn,1)-datenum(year,1,1)+1;
dy2 = datenum(year,mn,15)-datenum(year,1,1)+1;
dy3 = datenum(year,mn+1,1)-datenum(year,1,1);

[xi ~] = size(sd);
% [dy' mn' dm'];
y = zeros([xi 24]);
q = zeros([xi 24]);

for i = 1 : xi
    for mon = 1 : 12
        d1 = dy1(mon); 
        d2 = dy2(mon);
        d3 = dy3(mon);
        
        for hf = 1 : 2
            if hf == 1
                xd = xx(i,d1:d2);
                dw = d2 - d1 + 1;
            else
                xd = xx(i,d2+1:d3);
                dw = d3 - d2 + 1;
            end
            if isempty(xd)
                disp(num2str([i mon hf d1 d2 d3 xx(i,d3) xd]));
            end
            
            x1 = find(xd < 30000);
            n1 = length(x1);

            j = (mon - 1) * 2 + hf;
%             disp([j mon hf d1 d2 d3 dw]);
            if n1 <= 0.6 * dw
                y(i,j) = -9999;
            else
                if ms == 1
                    y(i,j) = mean(xd);
                else
                    y(i,j) = sum(xd);
                end
            end
            q(i,j) = n1;
        end
    end
end
