function [XD, yr, cern_headline, cern_var_name] = Read_CERNMeteo(fxls, c_sid, vname_ID)
% fxls = 'D:\STSZHANGLI\CERN\T2.xls';
% fout = 'D:\STSZHANGLI\CERN\CERN_SITES_T2.xls';
vname = {'TAVG'; 'PRCP'; 'TMIN'; 'TMAX'; 'RHU'; 'SSD';  'WIN'};

cern_ID = [6,6,7,7,6,15,6];
cname_id = cern_ID(vname_ID);

[status,sheets] = xlsfinfo(fxls);
X =[];sid =[];
for i =1:length( sheets )
    [x0,s0,tmp] = xlsread(fxls, sheets{i});
    [n, m] = size(s0);
    s1 = s0(3:end,1);
    x1 = s0(3:end,2:m);
    X =[X;x1];
    sid =[sid;s1];
end
cern_headline = s0(2,:);
cern_var_name = s0{1,1};

yr = str2double(unique(X(:,1)));
dy1 = datenum(min(yr),  1,  1);
dy2 = datenum(max(yr), 12, 31);
dn = dy1 : dy2;
n = dy2 - dy1 + 1;

yt = str2double(X(:,1));
mn = str2double(X(:,2));
dy = str2double(X(:,3));
dt = datenum(yt, mn, dy);

c_num = length(c_sid);

D = zeros([n, c_num]);

for i = 1 : c_num
    d = strmatch(c_sid{i}, sid);
    x = X(d,:);
    ds = dt(d);
    
    for j = 1 : n
        % disp([c_sid{i} ' ' datestr(dn(j))]);
        js = find(ds == dn(j));
        
        if ~isempty(js)
            if strcmpi(vname{vname_ID}, 'SSD')
                % D(js,i) = D(:,15) + D(:,16) / 60;
                ht = str2double(x{js,15});
                mt = str2double(x{js,16});
                D(js,i) = ht + mt / 60;
            end
            D(js,i) = str2double(x{js,cname_id});
        else
            D(js,i) = NaN;
        end
    end
end
XD = [dn' D];
% ds = datenum(D(:,1), D(:,2), D(:,3));
% [n, m] = size(D); ms = m + 2;
% yr = [min(D(:,1)), max(D(:,1))];
% T = zeros([n, m+2]) + NaN;
% for yt = yr(1) : yr(2)
%     days = datenum(yt + 1, 1, 1) - datenum(yt, 1, 1);
%     for k = 1 : days
%         kd = datenum(yt, 1, 1) + k - datenum(yr(1), 1, 1);
%         dt = datenum(yt, 1, 1) + k - 1;
%         js = find(dt == ds);
%         if ~isempty(js)
%             T(kd, :) = [kd dt D(js,:)];
%         else
%             T(kd, :) = [kd dt yt month(dt) day(dt) ones([1 m-3])*NaN];
%         end
%         % if month(dt) == 1
%         %     disp(js)
%             % disp(num2str(T(kd,:), '%8.2f'))
%         % end
%     end    
%     xdat = T(T(:,3) == yt,:);
%     disp([yt size(xdat)]);
% end


            
        

