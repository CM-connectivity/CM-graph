% for iVC, plz change data_dir and subj before runing the script
% please change the name of .easy file and .txt file accordingly
% updates on July 12, 2021: include the case where EMG recording precede
% EEG recording, flake8 check fails, rename variables
% contact: aegean0045@outlook.com
clear 
close all;
data_dir = 'E:\masterSJTU\MultiEEGEMG_stroke\';
subj = 56;
output_fName = append('E:\masterSJTU\MultiEEGEMG_stroke\subj',int2str(subj),'\subj',int2str(subj),...
'_alignmentInfo.txt');
outputFile2write = fopen(output_fName,'w');
fprintf(outputFile2write,'%s%s%s%s\n','contraction_type,','sessionIdx,','EEG,','EMG');
for session_idx = 1:12
    if session_idx < 10
        emg=importdata(append(data_dir,'subj',int2str(subj),'\EMG\','subj',int2str(subj),'_iVC_s0',int2str(session_idx),'.txt'));
        eeg=importdata(append(data_dir,'subj',int2str(subj),'\','subj',int2str(subj),'_iVC_s0',int2str(session_idx),'.easy'));
    else
        emg=importdata(append(data_dir,'subj',int2str(subj),'\EMG\','subj',int2str(subj),'_iVC_s',int2str(session_idx),'.txt'));
        eeg=importdata(append(data_dir,'subj',int2str(subj),'\','subj',int2str(subj),'_iVC_s',int2str(session_idx),'.easy'));
    end
    emgdate=emg.textdata(1,1);
    emgdate=emgdate{1};
    emg_1stdate=[emgdate(1,12:13) emgdate(1,15:16) emgdate(1,18:19) emgdate(1,21:23)]; % emg_date
    emg_1stdate=str2double(emg_1stdate);
    eegdate=eeg(1:20000,37); % find aligned sample from first 20000 samples (40s), increase the value if no aligned time was found
    eeg_date_str=num2str(eegdate);
    eeg_ms=eeg_date_str(:,11:13);
    readable_date = datetime(eegdate/1000, 'ConvertFrom', 'posixtime' ,'TimeZone', 'local');
    zz=datestr(readable_date);
    eeg_new=[zz eeg_ms];
    eeg_date=[eeg_new(:,13:14) eeg_new(:,16:17) eeg_new(:,19:23)];
    eeg_1stdate=str2double(eeg_date(1,1:9)); % onset of EEG recording
    if eeg_1stdate <= emg_1stdate
    % eeg_date_n extract timestamps of EEG samples (h/m/s/ms)
        eeg_date_reorganized = zeros(1,length(eegdate));
        for i=1:length(eegdate)
            eeg_date_reorganized(i)=str2double(eeg_date(i,1:9));
        end

        [a,eeg_num]=find(eeg_date_reorganized==emg_1stdate);
        % eeg_num the eeg_num th point in EEG aligns with the first point in EMG

        if isempty(eeg_num)
            emg_1stdate_shifted=emg_1stdate+1;
            [a,eeg_num]=find(eeg_date_reorganized==emg_1stdate_shifted);
            % eeg_num EEG数据第N个数据点 与EMG第二个数据点对齐
            if isempty(eeg_num)
                disp('bug in somewhere');
            else
                if session_idx < 10
                    fprintf(outputFile2write,'%s%s%u%s%u\n','iVC,',append('s0',int2str(session_idx),','),...
                            eeg_num,',',2);
                else
                    fprintf(outputFile2write,'%s%s%u%s%u\n','iVC,',append('s',int2str(session_idx),','),...
                            eeg_num,',',2);
                end
            end
        else
            if session_idx < 10
                fprintf(outputFile2write,'%s%s%u%s%u\n','iVC,',append('s0',int2str(session_idx),','),...
                    eeg_num,',',1);
            else
                fprintf(outputFile2write,'%s%s%u%s%u\n','iVC,',append('s',int2str(session_idx),','),...
                    eeg_num,',',1);
            end
        end
    else
        emg_dates=zeros(1,60000); % increase the value if necessary (i.e. when the interval between EEG and EMG onsets is large)
        for i=1:length(emg_dates)
        emg_dates(i)=emg_1stdate+i-1;
        end
        [a,emg_num]=find(eeg_1stdate==emg_dates);
        if session_idx < 10
            fprintf(outputFile2write,'%s%s%u%s%u\n','iVC,',strcat('s0',int2str(session_idx),','),...
                    1,',',emg_num);
        else
            fprintf(outputFile2write,'%s%s%u%s%u\n','iVC,',strcat('s',int2str(session_idx),','),...
                    1,',',emg_num);
        end
    end
end
% for session_idx = 1:4
% % check whether there is resting state data
% eeg_rest_filename = append(data_dir,'subj',int2str(subj),'\','subj',int2str(subj),'_iVC_rest0',int2str(session_idx),'.easy');
% if isfile(eeg_rest_filename)
% % No need to synchronize resting state data    
% end
% end
fclose(outputFile2write);

