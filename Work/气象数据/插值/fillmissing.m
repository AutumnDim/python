function [y qc sta,nf] = fillmissing(dat, sta,geo)
%% 
% disp(['Missing Num.: ' num2str(length(dx))]);
% disp(['Missing Value: ' num2str(x(ix, jx))]);
[ns m1] = size(dat);

lon = geo(:,1);
lat = geo(:,2);
elv = geo(:,3);

if ns > 2
    %% Check the missing values
    ns = length(lon);
    dx = find(dat == 32766);
    [ix jx iv] = find(dat == 32766);
    qc = zeros(size(dat));
    if length(dx) < 1
        y = dat;
    else
        y = dat;
        [n m] = size(dx);
        for j = 1 : n
            jd = jx(j);
            i0 = ix(j);
            x0 = lon(i0);
            y0 = lat(i0);

            vx = dat(:,jd);
            dx = sqrt((lon-x0).^2 +(lat-y0).^2);

            vn = vx( vx ~= 32766 & dx > 0);
            if ~isempty(vn)
                xn = lon(vx ~= 32766 & dx > 0);
                yn = lat(vx ~= 32766 & dx > 0);

                % use IDW to interpolate the missing value
                nn(j) = min(5,length(xn));
                % 
                yp(j,1)= IDW(xn, yn, vn, x0, y0, -2, 'ng', nn(j));
            else
                vx = [dat(i0, max(1,jd-1)) dat(i0, min(jd+1,m1))];
                yp(j,1) = mean(vx(vx < 32000));
            end
            y(ix(j),jx(j)) = yp(j,1);
            qc(ix(j),jx(j)) = qc(ix(j),jx(j)) + 1;
        end
    end
    nf = length(ix);
    % m = sum(qc(:));
else
    disp('error');
    y = -1; qc = -1;  sta = -1;nf = -1;
end