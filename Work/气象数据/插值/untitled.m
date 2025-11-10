% 网页基础URL和目标文件特征
baseUrl = 'https://www.glass.hku.hk/archive/LAI/MODIS/500M/2000/049/';
keyword1 = 'h25v05';   % 关键词1
keyword2 = 'h26v05';   % 关键词2
fileExt = '.hdf';      % 文件扩展名

% 设置本地保存路径（可自定义）
saveDir = fullfile(pwd, 'MODIS_HDF_files');
if ~exist(saveDir, 'dir')
    mkdir(saveDir);  % 若目录不存在则创建
end

for yr = 2000 : 2000
    for jd = 1 : 8 : 365
        baseUrl = ['https://www.glass.hku.hk/archive/LAI/MODIS/500M/', num2str(yr),...
            '/', num2str(jd, '%03d'), '/'];
        try
            % 1. 获取网页HTML内容
            disp('正在读取网页内容...');
            htmlContent = webread(baseUrl);  % 读取网页HTML源码

            % 2. 解析HTML，提取所有HDF文件链接（基于<a>标签中的href）
            % 正则表达式匹配: <a href="文件名.hdf">，提取文件名
            pattern = '<a\s+href="([^"]+\.hdf)"';  % 匹配HDF文件的href属性
            fileNames = regexp(htmlContent, pattern, 'tokens');
            fileNames = [fileNames{:}];  % 转换为字符串数组

            if isempty(fileNames)
                error('未找到任何HDF文件链接，请检查网页结构是否变化');
            end

            % 3. 筛选包含关键词的文件
            targetFiles = {};
            for i = 1:length(fileNames)
                fname = fileNames{i};
                % 检查文件名是否包含h25v05或h26v05，且为HDF格式
                if (contains(fname, keyword1) || contains(fname, keyword2)) && ...
                        endsWith(fname, fileExt)
                    targetFiles{end+1} = fname;
                end
            end

            if isempty(targetFiles)
                disp('未找到符合条件的文件（包含h25v05或h26v05的HDF文件）');
                return;
            end

            % 4. 下载筛选后的文件
            disp(['找到 ', num2str(length(targetFiles)), ' 个符合条件的文件，开始下载...']);
            for i = 1:length(targetFiles)
                fileName = targetFiles{i};
                fileUrl = [baseUrl, fileName];  % 拼接完整下载URL
                savePath = fullfile(saveDir, fileName);  % 本地保存路径

                % 检查文件是否已存在
                if exist(savePath, 'file')
                    disp(['文件已存在，跳过：', fileName]);
                    continue;
                end

                % 下载文件
                try
                    disp(['正在下载 ', num2str(i), '/', num2str(length(targetFiles)), '：', fileName]);
                    websave(savePath, fileUrl);  % 下载并保存文件
                catch e
                    disp(['下载失败 ', fileName, '：', e.message]);
                end
            end

            disp('所有文件处理完成！');

        catch e
            disp(['执行错误：', e.message]);
        end
    end
end