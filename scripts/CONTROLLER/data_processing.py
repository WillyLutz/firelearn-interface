import numpy as np
import pandas as pd
from scipy.signal import butter, freqz, filtfilt


def butter_filter(signal, order, btype, lowcut=None, highcut=None, cut=None, fs=10000 ):
    nyq = 0.5 * fs
    if cut:
        midcut = cut / nyq
    if lowcut:
        low = lowcut / nyq
    if highcut:
        high = highcut / nyq
    if btype in ["highpass", "lowpass"]:
        b, a = butter(order, midcut, btype=btype)
        w, h = freqz(b, a)
    elif btype in ["bandstop", "bandpass"]:
        b, a = butter(order, [low, high], btype=btype)
        w, h = freqz(b, a)

    #xanswer = (w / (2 * np.pi)) * freq
    #yanswer = 20 * np.log10(abs(h))

    filtered_signal = filtfilt(b, a, signal)

    return filtered_signal  # , xanswer, yanswer


def fast_fourier(dfy, freq):
    fft_df = np.fft.fft(dfy)
    freqs = np.fft.fftfreq(len(dfy), d=1 / freq)

    clean_fft_df = abs(fft_df)
    clean_freqs = abs(freqs[0:len(freqs // 2)])
    return clean_fft_df[:int(len(clean_fft_df) / 2)], clean_freqs[:int(len(clean_freqs) / 2)]



def merge_all_columns_to_mean(df: pd.DataFrame, except_column=""):
    """
    merge_all_columns_to_mean(data: pd.DataFrame, except_column=""):

        average all the columns, except an optional specified one,
        in a data into one. The average is done row-wise.

        Parameters
        ----------
        df: DataFrame
            the data to average
        except_column: str, optional, default: ""
            the name of the column to exclude from the average.
            Will be included in the resulting dataset.

        Returns
        --------
        out: DataFrame
            Dataframe containing on column labeled 'mean', and
            an optional second column based on the
            except_column parameter
    """

    excepted_column = pd.DataFrame()
    if except_column:
        for col in df.columns:
            if except_column in col:
                except_column = col
        excepted_column = df[except_column]
        df.drop(except_column, axis=1, inplace=True)

    df_mean = pd.DataFrame(columns=["mean", ])
    df_mean['mean'] = df.mean(axis=1)

    if except_column != "":
        for col in df.columns:
            if except_column in col:
                except_column = col
        df_mean[except_column] = excepted_column

    return df_mean



def top_n_electrodes(df, n, except_column="TimeStamp [µs]"):
    """
        top_N_electrodes(data, n, except_column):

            Select only the n electrodes with the highest standard
            deviation, symbolizing the highest activity.

            Parameters
            ----------
            df: Dataframe
                Contains the data. If using MEA it has the following
                formatting: the first column contains the time dimension,
                names 'TimeStamp [µs]', while each other represent the
                different electrodes of the MEA, with names going as
                '48 (ID=1) [pV]' or similar.
            n: int
                the number of channels to keep, sorted by the highest
                standard deviation.
            except_column: str, optional, default: 'TimeStamp [µs]'
                The name of a column to exclude of the selection.
                This column will be included in the resulting
                data.

            Returns
            -------
            out: pandas Dataframe
                Dataframe containing only n columns, corresponding
                to the n channels with the highest standard deviation.
                If except_column exists, then this very column is added
                untouched from the original data to the resulting
                one.

            Notes
            -----
            This function only use the standard deviation as metric to
            use to sort the channels. Any modification on this metric
            should be done on the line indicated below.

            Examples
            --------
            >> data = pd.read_csv(file)
            >> df_top = dpr.top_N_electrodes(data=data, n=35, except_column='TimaStamp [µs]")
            Returns a data containing the top 35 channels based on the std of the signal

    """
    # getting the complete name of the column to exclude, in case of slight fluctuation in name
    if except_column:
        for col in df.columns:
            if except_column in col:
                except_column = col

    # managing 'except_column'
    dfc = df.drop(except_column, axis=1)
    df_filtered = pd.DataFrame()
    df_filtered[except_column] = df[except_column]

    # getting the top channels by metric. Metric changes should be done here.
    all_metric = []
    for c in dfc.columns:
        all_metric.append(np.std(dfc[c]))
    top_indices = sorted(range(len(all_metric)), key=lambda i: all_metric[i], reverse=True)[:n]

    # creating resulting data
    for c in dfc.columns:
        id = c.split(")")[0].split("=")[1]
        if int(id) in top_indices:
            df_filtered[c] = dfc[c]

    return df_filtered
