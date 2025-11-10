% function [y,q,sd] = meanbyxdays(xx, sid, dn, ms,c_r)
% % meanbyxday(yf_daily, sta, year,dn, ms);
% % ff = 'meteo/Daily8012Filled/PRE/PRE_2005_filled.csv';
% % xx = meteo[stations days]
% % sd = stations(stations,:)
% % dn = 365,days
% % week = 15;
% % ms = 1 for mean 0 for sum
% nj = unique(dn);
% nn = length(nj);
% 
% y = zeros([nn length(sid)]);
% q = zeros([nn length(sid)]);
% 
% for i = 1 : length(sid)
%     for j = 1 : nn
%         dw = sum(dn == nj(j));
%         if c_r == 1
%             xd = xx(i,dn == nj(j));
%         else
%             xd = xx(dn == nj(j), i);
%         end
%         x1 = xd(xd < 30000 & xd > -9000);
%         n1 = length(x1);
% 
%         if ms == 1
%             y(j,i) = mean(xd);
%         else
%             y(j,i) = sum(xd);
%         end        
%         sd(j,i) = std(xd);
%         q(j,i) = n1/dw;
%     end
% end




function [y, q, sd] = meanbyxdays(xx, sid, dn, ms, c_r)
% meanbyxdays
% 聚合逐日（或逐时段）数据到给定分组（周/旬/月等）
%
% 输入:
%   xx : 数据矩阵
%        c_r == 1 时: [stations x time]
%        c_r ~= 1 时: [time x stations]
%   sid: 站点 ID（只用于确定站点数量；不参与计算内容）
%   dn : 长度为 time 的分组向量（如 week-index / ten-day-index / month-index），
%        每个元素表示对应时间列属于哪个组
%   ms : 1=均值聚合, 0=求和聚合
%   c_r: 1 表示 xx 是 [stations x time]；否则 [time x stations]
%
% 输出:
%   y  : [numGroups x numStations] 聚合后的值
%   q  : [numGroups x numStations] 每组有效样本占比 (0~1)
%   sd : [numGroups x numStations] 每组样本标准差

    arguments
        xx
        sid
        dn
        ms (1,1) {mustBeMember(ms,[0 1])}
        c_r (1,1) {mustBeMember(c_r,[0 1])}
    end

    % ---------- 统一 xx 为 [stations x time] 方向 ----------
    if c_r == 1
        % xx: [stations x time]
        [nStations, nTime] = size(xx);
        X = xx;
    else
        % xx: [time x stations] -> 转置为 [stations x time]
        [nTime, nStations] = size(xx);
        X = xx.';  % [stations x time]
    end

    % ---------- 统一 dn 形状并与时间轴对齐 ----------
    dn = dn(:)';  % 行向量
    if numel(dn) ~= nTime
        mUse = min(nTime, numel(dn));
        warning('meanbyxdays:LengthMismatch', ...
            'Length of dn (%d) != time dimension (%d). Using first %d.', ...
            numel(dn), nTime, mUse);
        X  = X(:, 1:mUse);
        dn = dn(1:mUse);
        nTime = mUse;
    end

    % ---------- 计算分组顺序（保持原有出现顺序更直观） ----------
    nj = unique(dn, 'stable');
    nj = nj(~isnan(nj));           % 去掉 NaN 组
    nn = numel(nj);                % 组数
    nStations = size(X,1);

    % ---------- 预分配 ----------
    y  = zeros(nn, nStations);
    q  = zeros(nn, nStations);
    sd = zeros(nn, nStations);

    % ---------- 将无效值统一设为 NaN，便于 omitnan 处理 ----------
    % 你原逻辑的数值有效范围: (-9000, 30000)
    invalidMask = (X >= 30000) | (X <= -9000);
    X(invalidMask) = NaN;

    % ---------- 按组聚合 ----------
    for j = 1:nn
        g = nj(j);
        colMask = (dn == g);   % 逻辑索引，对应此组的时间列
        dw = sum(colMask);     % 该组的总样本数（分母）

        if dw == 0
            % 没有任何列属于该组，保持默认 0/NaN 即可
            y(j,:)  = NaN;   % 更合理：没有数据就返回 NaN
            q(j,:)  = 0;
            sd(j,:) = NaN;
            continue;
        end

        % 取出该组的所有样本（stations x dw）
        Xi = X(:, colMask);

        % 有效样本计数（非 NaN）
        validCount = sum(~isnan(Xi), 2);   % [stations x 1]

        % 聚合
        if ms == 0
            % 求和
            agg = sum(Xi, 2, 'omitnan');
        else
            % 均值
            agg = mean(Xi, 2, 'omitnan');
        end

        % 标准差（按列聚合后的行向量）
        sdi = std(Xi, 0, 2, 'omitnan');

        % 赋值（按输出定义: [groups x stations]）
        y(j, :)  = agg.';
        sd(j, :) = sdi.';
        q(j, :)  = (validCount / dw).';   % 有效比例
    end
end
