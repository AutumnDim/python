% function varargout = utils_anusplin(funcName, varargin)
% %UTILS_ANUSPLIN 集中封装 Anusplin 用到的工具函数
% % 用法示例：
% %   utils_anusplin('ensure_dir', path)
% %   w = utils_anusplin('to_win', path)
% %   out = utils_anusplin('to_ext', basePath, extNoDot)
% %   utils_anusplin('assert_file_exists', filepath, label)
% %   [xlr,ylr,pix,line,siz,xul,yul] = utils_anusplin('read_hdr_geo', hdrfile)
% %   n = utils_anusplin('getname', filepath)
% %   utils_anusplin('ensure_master_initialized', master_bat)
% %   utils_anusplin('write_or_append', filename, content, mode)
% 
% switch lower(funcName)
% 
%     case 'ensure_dir'
%         p = varargin{1};
%         if ~exist(p,'dir'), mkdir(p); end
% 
%     case 'to_win'
%         p = varargin{1};
%         varargout{1} = strrep(p,'/','\');
% 
%     case 'to_ext'
%         basePath = varargin{1};
%         extNoDot = varargin{2};
%         [fp,fn,~] = fileparts(basePath);
%         varargout{1} = fullfile(fp,[fn '.' extNoDot]);
% 
%     case 'assert_file_exists'
%         fp = varargin{1};
%         label = varargin{2};
%         if exist(fp,'file')~=2
%             error('WriteCheckFail: %s not found: %s', label, fp);
%         end
% 
%     case 'read_hdr_geo'
%         fhdr = varargin{1};
%         if ~exist(fhdr,'file'), error('HDR not found: %s', fhdr); end
%         fid = fopen(fhdr,'r');
%         if fid<0, error('Cannot open HDR: %s', fhdr); end
%         C = textscan(fid,'%s%f','Delimiter',' \t','MultipleDelimsAsOne',true);
%         fclose(fid);
%         vals = C{2};
%         if numel(vals)<5, error('HDR parse failed: %s', fhdr); end
%         pix=vals(1); line=vals(2); xlr=vals(3); ylr=vals(4); siz=vals(5);
%         xul = xlr + siz*pix; yul = ylr + siz*line;
%         varargout = {xlr, ylr, pix, line, siz, xul, yul};
% 
%     case 'getname'
%         p = varargin{1};
%         [~,n0,e0] = fileparts(p);
%         varargout{1} = [n0 e0];
% 
%     case 'ensure_master_initialized'
%         master_bat = varargin{1};
%         if exist(master_bat,'file')==2, return; end
%         pdir = fileparts(master_bat);
%         if ~exist(pdir,'dir'), mkdir(pdir); end
%         fp = fopen(master_bat,'w');
%         if fp<0, error('Cannot create master BAT: %s', master_bat); end
%         fprintf(fp,'@echo off\r\n');
%         fprintf(fp,'setlocal enabledelayedexpansion\r\n');
%         fprintf(fp,'echo ========= MASTER SPL RUN START %%DATE%% %%TIME%% =========\r\n\r\n');
%         fclose(fp);
% 
%     case 'write_or_append'
%         fp = varargin{1};
%         content = varargin{2};
%         mode = varargin{3};
%         fid = fopen(fp, mode);
%         if fid<0, error('Cannot open: %s', fp); end
%         fwrite(fid, content, 'char');
%         fclose(fid);
% 
%     otherwise
%         error('Unknown util function: %s', funcName);
% end
% end




function varargout = utils_anusplin(funcName, varargin)
%UTILS_ANUSPLIN 集中封装 Anusplin 用到的工具函数
% 用法示例：
%   utils_anusplin('ensure_dir', path)
%   w = utils_anusplin('to_win', path)
%   out = utils_anusplin('to_ext', basePath, extNoDot)
%   utils_anusplin('assert_file_exists', filepath, label)
%   [xlr,ylr,pix,line,siz,xul,yul] = utils_anusplin('read_hdr_geo', hdrfile)
%   n = utils_anusplin('getname', filepath)
%   utils_anusplin('ensure_master_initialized', master_bat)
%   utils_anusplin('write_or_append', filename, content, mode)

switch lower(funcName)

    case 'ensure_dir'
        p = varargin{1};
        if ~exist(p,'dir'), mkdir(p); end

    case 'to_win'
        p = varargin{1};
        varargout{1} = strrep(p,'/','\');

    case 'to_ext'
        basePath = varargin{1};
        extNoDot = varargin{2};
        [fp,fn,~] = fileparts(basePath);
        varargout{1} = fullfile(fp,[fn '.' extNoDot]);

    case 'assert_file_exists'
        fp = varargin{1};
        label = varargin{2};
        if exist(fp,'file')~=2
            error('WriteCheckFail: %s not found: %s', label, fp);
        end

    case 'read_hdr_geo'
        fhdr = varargin{1};
        if ~exist(fhdr,'file'), error('HDR not found: %s', fhdr); end
        fid = fopen(fhdr,'r');
        if fid<0, error('Cannot open HDR: %s', fhdr); end
        C = textscan(fid,'%s%f','Delimiter',' \t','MultipleDelimsAsOne',true);
        fclose(fid);
        vals = C{2};
        if numel(vals)<5, error('HDR parse failed: %s', fhdr); end
        pix=vals(1); line=vals(2); xlr=vals(3); ylr=vals(4); siz=vals(5);
        xul = xlr + siz*pix; yul = ylr + siz*line;
        varargout = {xlr, ylr, pix, line, siz, xul, yul};

    case 'getname'
        p = varargin{1};
        [~,n0,e0] = fileparts(p);
        varargout{1} = [n0 e0];

    case 'ensure_master_initialized'
        master_bat = varargin{1};
        if exist(master_bat,'file')==2, return; end
        pdir = fileparts(master_bat);
        if ~exist(pdir,'dir'), mkdir(pdir); end
        fp = fopen(master_bat,'w');
        if fp<0, error('Cannot create master BAT: %s', master_bat); end
        fprintf(fp,'@echo off\r\n');
        fprintf(fp,'setlocal enabledelayedexpansion\r\n');
        fprintf(fp,'echo ========= MASTER SPL RUN START %%DATE%% %%TIME%% =========\r\n\r\n');
        fclose(fp);

    case 'write_or_append'
        fp = varargin{1};
        content = varargin{2};
        mode = varargin{3};
        fid = fopen(fp, mode);
        if fid<0, error('Cannot open: %s', fp); end
        fwrite(fid, content, 'char');
        fclose(fid);

    otherwise
        error('Unknown util function: %s', funcName);
end
end