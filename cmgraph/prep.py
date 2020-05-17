"""
prep
==============

A module for io and preprocessing

"""

def emg_io(emg_fName, skiprows, sep = ' ', emg_chs_selected='all'):
    
    """
    this function takes .txt format emg file and renders to a pandas dataframe for further processing.
    
    Parameters
    -----------
    emg_fName : string
        emg_fName should be in .txt or in .csv form. 
    emg_chs_selected : list of int
        the index of emg channels (columns) that are supposed to be used in further analysis, defaults to 'all'
    sep : string
        the seperator to be specified when reading the txt file with pandas.read_csv
    skiprows : int
        rows to be skipped. This applies for data containing emg information at the begining of the data file.
    
    Returns
    -------
    pandas's dataframe 
    
    Examples
    --------
    >>>emg_fName = r'D:\Data\RuiJinFirstStroke11Jan\EMG\subj1_healthy_session1.txt'
    >>>emg_io(emg_fName, skiprows = 3, emg_chs_selected='all')

    See Also
    --------

    Warnings
    --------
    
    Notes
    --------
    The .txt file or .csv file should not have headers. If so, please use skiprow to trim them. The first column should be 0 in the emg_chs_selected parameter
    """
    import pandas as pd  
    emg_data = pd.read_csv(emg_fName, header = None, skiprows=skiprows, sep = sep, engine = 'python')
    if emg_chs_selected == 'all':
        return emg_data
    else:
        emg_data = emg_data[emg_chs_selected]
    return emg_data
    
def eeg_emg_alignment(eeg_fName, emg_df, sfreq_final, emg_freq, report_fName = None, start_marker = True, fir=[1,None], PREP=True,
                       montage = 'standard_1020'):
    """
    this function takes .set format for eeg and txt format for emg.
    
    Parameters
    -----------
    eeg_fName : string 
        eeg_fName should be in .set form
    emg_fName : string
        emg_fName should be in .txt form
    report_fName: string
        optional, default to None which will not generate a report for the reprocessing result. When reproty_fName is specified, two reports will be generated at the suggested directory including one in HTML,
        and one in .h5 format. The .h5 format is an edittable report.
    montage: string
        The defaut montage is set to standard 1020 montage
    start_marker : boolean
        if start_marker is true, the segment before the first marker will be cropped, defaults to True
    fir: list
        the lower and upper boundary of filter. If the boundary is set to None, then the filter become high-pass or low-pass filter.
    PREP: boolean
        the EEG preprocessing pipeline process, defauts to True. It can de deactivated when set to false.
    emg_chs_selected : list of int
        the index of emg channels (columns) that are supposed to be used in further analysis, defaults to 'all'
    
    Returns
    -------
    mne raw object containing aligned eeg and emg data
    
    Examples
    --------
    >>>eeg_fName = r'D:\Data\RuiJinFirstStroke11Jan\EEG\subj1_healthy_session1.set'
    >>>emg_fName = r'D:\Data\RuiJinFirstStroke11Jan\EMG\subj1_healthy_session1.txt'
    >>>emg_df = pd.read_csv(emg_fName, header = None, skiprows=3,
                               sep = ' ',engine = 'python')
    >>>eeg_emg_alignment(eeg_fName,emg_df,emg_freq=1000,sfreq_final=500,report_fName=None,PREP=False)
    
    See Also
    --------

    Warnings
    --------
    
    Notes
    --------
    Make sure the eeg recording are no less than the emg recording. The current version of this function crop emg signal
    with respect to emg in order to keep these data aligned.
    """

    import mne,os
    import pandas as pd
    raw_eeg = mne.io.read_raw_eeglab(eeg_fName)
    raw_eeg.set_montage(montage)
    if start_marker==True:
        eeg_onset=mne.events_from_annotations(raw_eeg)[0][0,0]
        raw_eeg.crop(tmin = eeg_onset/raw_eeg.info["sfreq"])
      
    if report_fName != None:
    #### report raw properties ###
        report = mne.Report(verbose=True)
        report_fname_editable = os.path.join(report_fName,'.h5')
        report_fname_2check = os.path.join(report_fName,'.html')
        fig_raw = raw_eeg.plot(scalings=4e-5,n_channels=32,duration =8)
        fig_raw_psd = raw_eeg.plot_psd()
        report.add_figs_to_section(fig_raw, captions='raw_data', section='raw')
        report.add_figs_to_section(fig_raw_psd, captions='raw_psd', section='raw')
    
    raw_eeg.filter(fir[0], h_freq= fir[1])
    if PREP ==True:
    #### prep steps, require pyprep        
        eeg_index = mne.pick_types(raw_eeg.info, eeg=True, eog=False, meg=False,emg=False)
        ch_names = raw_eeg.info["ch_names"]
        ch_names_eeg = list(np.asarray(ch_names)[eeg_index])
        sample_rate = raw_eeg.info["sfreq"]
        montage_kind = "standard_1020"
        montage = mne.channels.make_standard_montage(montage_kind)
        raw_eeg_copy=raw_eeg.copy()
        # Fit prep
        prep_params = {'ref_chs': ch_names_eeg,
                       'reref_chs': ch_names_eeg,
                       'line_freqs': np.arange(50, sample_rate/2, 50)}
        prep = PrepPipeline(raw_eeg_copy, prep_params, montage)
        prep.fit()
        raw_eeg = prep.raw
    if report_fName != None:
        fig_raw = raw_eeg.plot(scalings=4e-5,n_channels=32,duration=8)
        fig_raw_psd = raw_eeg.plot_psd()
        report.add_figs_to_section(fig_raw, captions='prep signal space', section='prep')
        report.add_figs_to_section(fig_raw_psd, captions='prep_psd', section='prep')
        report.add_htmls_to_section(htmls =[str(prep.interpolated_channels),str(prep.noisy_channels_original['bad_all'])
                                            ,str(prep.still_noisy_channels)],
                                    captions= ['interpolated channels','bad channels detected', "still noisy channels"], 
                                    section='prep', replace=False)
        report.save(report_fname_2check, overwrite=True)
        report.save(report_fname_editable, overwrite=True)
    

    eeg_len = raw_eeg._data.shape[1]
    emg_df = emg_df.iloc[0:round(emg_freq/raw_eeg.info["sfreq"])* eeg_len]
    ch_types = ['emg']*len(emg_df.columns)
    ch_names = []
    for i in range(len(emg_df.columns)):
        ch_names.append('emg'+str(i+1))
    info = mne.create_info(ch_names=ch_names, sfreq=emg_freq, ch_types=ch_types)
    raw_emg = mne.io.RawArray(emg_df.T, info)
    raw_emg.resample(sfreq=sfreq_final)
    raw_emg.info['highpass'] = fir[0]
    raw_hybrid = raw_eeg.copy().add_channels([raw_emg])
    return raw_hybrid

def epochs_basedon_emg(raw_hybrid, ref_emg, windowLen, step=100, threshold =0.5,report_fName=None, 
                       add_to_existed_report=False, reject_criteria = dict(eeg=30e-5,emg=1e10),
                       flat_criteria = dict(eeg=5e-7),tmin = 0.0, tmax = 3.0, save_fName=None):
    """
    this function takes .set format for eeg and txt format for emg.
    
    Parameters
    -----------
    raw_hybrid: mne raw object 
        The raw object containing aligned eeg and emg
    ref_emg: list of string 
        the emg channels that the algorithm refers to. They should be channels in input raw_hybrid. The algorithm will 
        consider  'the length of the string' as number of movements. 
    report_fName: string
        optional, default to None which will not generate a report for the epoching result.
        When reproty_fName is specified, two reports will be generated at the suggested directory including one in HTML,
        and one in .h5 format. The .h5 format is an edittable report.
    add_to_existed_report: boolean
        It is supposed to be true when one wants to add the epoching report into an existed report.
    windowLen: int
        rough duration estimation of the movement
    step: int
        equivalent to resolution, defaults to 100
    threshold: float
        the threshold should be in [0,1], represnting the quantile of the energy for all windows
    reject_criteria: dict
        epochs containing eeg and emg that exceed rejection criteria will be rejected. defaults to dict(eeg=30e-5,emg=1e10)
    flat_criteria: dict
         epochs containing eeg and emg whose amplitude are lower than flat criteria will be rejected.
         Defaults to dict(eeg=1e-6). If reject_criteria and flat_criteria are both set to None, then no epochs rejection 
         would take place
    tmin: float
        the begining of the epochs with respect to the movement onsets
    tmax: float
        the end of the epochs with respect to the movement onsets
    savefName: string
        the path and filename of the saving epochs. It defaults to None, that is the epochs would not be saved 
        
    Returns
    -------
    
    Examples
    ---------
    
    See Also
    --------
    eeg_emg_alignment

    Warnings
    --------
    
    Notes
    --------

    """
    import numpy as np
    import mne
    onsets = np.array([])
    descriptions = np.array([])
    for i in range(len(ref_emg)):
        raw2cut = raw_hybrid.copy()
        raw2cut = raw2cut.pick_channels([ref_emg[i]])
        df = raw2cut.to_data_frame()[ref_emg[i]].abs()
        emgEnergy = df.rolling(windowLen, win_type='boxcar').sum().dropna()[::step]
        possibleOnsets =np.array(emgEnergy[emgEnergy>emgEnergy.quantile(threshold)].index.tolist())-windowLen
        newOnsets=np.array(firstOnsetD(possibleOnsets))/1000 # convect to seconds
        onsets = np.concatenate((onsets,newOnsets))
        descriptions =np.concatenate(( descriptions, ['movement'+str(i+1)+'Onset']*len(newOnsets)))
    durations = np.zeros_like(onsets)
    annot = mne.Annotations(onset=onsets, duration=durations,
                                        description=descriptions,
                                        orig_time=raw2cut.info['meas_date'])
    #change to raw2cut see effetcs
    raw_validate = raw_hybrid.copy()
    raw_validate.set_annotations(annot)
    events,events_id = mne.events_from_annotations (raw_validate)
    # Here we simply thresholding the epochs to get rid of noisy segment characterized by huge fluctuation.
    if reject_criteria ==None and flat_criteria==None:
        epochs = mne.Epochs(raw_validate,events,tmin=0.0,tmax=3.0,baseline=(0, 0))
    else:
        epochs = mne.Epochs(raw_validate,events,tmin=tmin,reject=reject_criteria, flat=flat_criteria,tmax=tmax,
                            baseline=(0, 0))
    if save_fName!=None:
        epochs.save(save_fName,overwrite=True)
        
    return epochs

def firstOnsetD(possibleOnsets):
    """
    qn auxilary function that identify true movement onsets for all the possible onsets 
    dentified based on energy threshold
    Parameters
    ----------
    possibleOnsets: list
        list of all the possible onsets
    
    Returns
    -------
    true movement onsets
    
    Examples
    ---------
    
    See Also
    --------
    eeg_emg_alignment

    Warnings
    --------
    
    Notes
    --------

    """
    n=len(possibleOnsets)
    st_idx = 0
    onsets = []
    while st_idx < n-1:
        end = st_idx + 1
        dif = possibleOnsets[end] - possibleOnsets[st_idx]
        while end < n - 1 and possibleOnsets[end + 1] - possibleOnsets[end] == dif:
            end += 1
        onsets.append(possibleOnsets[st_idx])
        st_idx = end+1
    return onsets