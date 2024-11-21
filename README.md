# FireLearn GUI v0.2.0: Walkthrough tutorial
This document is aimed at the users of FireLearn GUI. 
# Processing


> <img height="30" src="data/help/red_warning.png" width="30"/>
> 
> Please note that the different processes are following a specific order, and can not be modified. 
> Consider the order to be the order of presentation of the functionalities in this document.
> As such, it can be considered to be
> 
> [sorting](#sorting-multiple-files) > [file beheading (using raw MEA recordings)](#using-raw-mea-recordings) > 
> [electrode selection](#selecting-electrodes) > [down sampling](#recordings-down-sampling) >
> [filtering](#filtering) > [fast fourier transform](#fast-fourier-transform) >
> [smoothing](#smoothing) > [averaging electrode signal](#averaging-electrodes) >
> [dataset making](#resulting-datasets) > [post-processing](#post-processing) 
> 
> Depending on which feature is enabled or disabled.

### Example: directory structure
For this document we will proceed considering this recommanded directory structure : 
```
DATA (most parent common directory)
│
└───T0
│   └───INF
│   │   file.txt
│   │   file1_Analog.csv
│   │   file2_Analog.csv
│   │   file3_Analog.csv
│   │   file4_Analog.csv
│   └───MOCK
│   │   └───[...]
│   └───SPIKE
│   │   └───[...]
└───T30
│   └───[...]
└───T24
    └───[...]
```
## Sorting multiple files

This functionality aims at looking for and using multiple files under a common parent 
directory, no matter how distant it is. 

### Selecting parent directory
Click the `Open` button of `Path to parent directory` entry to select the parent directory.
The selected directory must be a parent of all the files you want to process.
For a multiple files processing, you _must_ switch on the `Sorting multiple files` switch.

For instance, using [this directory structure](#example-directory-structure), all the files that
are children to the most parent directory (here `/DATA`) are subject to be comprised in the processing.

To specify which files to include or exclude of the processing, 
refer to [the include/exclude option](#include-and-exclude-files-for-the-processing).



### Include and exclude files for the processing
With this functionality, you can specify which file to include or exclude from the selection.
Both the inclusion and exclusion works by looking at the content of the absolute paths of the files 
(e.g. `H:\Electrical activity\DATA\T0\INF\Electrode Raw Data1_Analog.csv`). 

As such, the inclusion uses the AND logic operator : 
**The file is included if ALL the `to include` specifications are present in the absolute path**.
On the other hand, the exclusion uses the OR logic operation :
**The file is excluded if ANY of the 'to exclude' specifications are present in the absolute path**.
Combining both gates, a file will be included for the processing if its absolute path 
**contains all the `to include` specifications and none of the `to exclude` specifications**.

Those `to include` and `to exclude` specifications are case-sensitive, so `Analog.csv` is different 
from `analog.csv`.

To add a specification, type it in the corresponding entry, then either click on the `+` button, or press 
the `Return` key. To remove a specification, type it in the corresponding entry, then either click on the 
`-` button or press `Ctrl-BackSpace` combination.

In this example, all the files containing `Analog.csv` and who does not contain `T30` in their absolute
paths will be included for further processing.

#### Indicating targets for learning

It is possible to make an entry correspond with a label, based on its path. To do so, indicate in the
`Target key` entry a sequence of characters to find in the path of the file. Then indicate in the `Target value`
entry the corresponding label. When creating the resulting files for the analysis, a `key` (label) will then be
attributed to an entry. 

E.g. : As per the following figure, only the files that contains  "Analog.csv" **AND** "T0" **AND DO NOT CONTAIN** "TTX"
in their absolute paths will be used for further processing.

<img height="460" width="660" src="data/help/include_exclude.png" />




> <img height="30" width="30" src="data/help/yellow_warning.png" />
> 
> Be it for including or excluding, the sequence will be searched in the absolute path and not
> only on the file name. 

> <img height="30" width="30" src="data/help/red_warning.png">
> 
> The said sequences does not search for "separated sequences" and does not recognise if the sequence
> is a word in itself. It will only look at the sequence character-wise. As such when choosing the 
> sequences you want to include or exclude, be aware of what can be in your absolute paths.
> 
> > E.g.: Your project is in a folder named 'HIV PROJECT', and further away in the children folders
> > you name the different recording conditions such as 'NI' (not infected), 'HIV' (infected by HIV)
> > BUT to select the files you specify in To exclude 'HIV', **all of your files will be excluded since
> > 'HIV' as a sequence is also present in the project folder 'HIV PROJECT' and not only as a 'condition'**.
> > 
> > To remediate to such issue, it is possible to look for the sequence '/HIV/' (use your operating system path 
> > separator) instead to ensure that we only look
> > at the folder named 'HIV' and not 'HIV PROJECT'.


### Single file analysis
In order to process a single file, switch on the corresponding switch and select the wanted file
using the `Open` button.

### Using raw MEA recordings
This functionality simply behead the file a specified number of rows. In the case of normed files from
MEA recordings , there is a header of 6 rows containing metadata before the actual recording data. 
Be aware that there must not be anything apart from the data and a row of headers.


### Selecting electrodes

Allow to select the columns (electrodes, in case of MEA recordings) with a `mode` `metric` combination.
Any column that contains 'time' (case-insensitive) in its header will be ignored.

### Recordings down sampling

This functionality will divide row-wisely every file in `n` selected pieces of equal lengths.
e.g. In our walkthrough example, we use 1 minute long recordings.
Specifying a down sampling at `30` implies that the recordings will be divided in 30 pieces of 2 seconds.

> <img src="data/help/red_warning.png" width="30" height="30">
>
> If the [make resulting files as dataset](#post-processing) function is not used, be aware that each file
selected during the [selection process](#sorting-multiple-files) will generate an equal number of different
based on the [down sampling](#recordings-down-sampling).

### Filtering

Allow the user to apply a Butterworth filter to the data.

For the use of `Lowpass` and `Highpass` filters, the first frequency `f1 (Hz)` corresponds to the cut
frequency, and teh second frequency `f2 (Hz)` must be left emptied.
For the use of `Bandstop` and `Bandpass` filters, the second frequency `f2 (Hz)` corresponds to the high-cut
frequency and must be specified.

In order to filter harmonics, the user can choose to filter only the `Even` harmonics (2nd, 4th, 6th...),
or the `Odd` harmonics (1st, 3rd, 5th...) or `All` (1st, 2nd, 3rd, 4th...) up till the `nth` harmonic.

E.g. with an harmonic frequency of 100 Hz, filtering the odd harmonics up to the 10th will filter the 
following frequencies : 
_100 Hz(1st), 300 Hz(3rd), 500 Hz(5th), 700 Hz(7th), 900 Hz(9th)_

### Fast Fourier Transform

Applies a Fast Fourier Transform to the data (post-filtering, if the filtering is enabled). 
The sampling rate must be specified.

### Smoothing

Smoothens the signal down to `n` final values. `n` must be inferior to the number of data point.

### Averaging electrodes

Average all columns (except the 'x' column, usually TimeStamp) into one column.

### Resulting datasets

> <img src="data/help/red_warning.png" width="30 height=30">
> 
>This feature overwrites the saving of the intermediate files (e.g. those created 
> from the [down sampling](#recordings-down-sampling) functionality) and save only
> a final file 'DATASET' csv file.

> <img src="data/help/yellow_warning.png" width="30 height=30">
>
>This feature is only available if the [average electrode signal](#averaging-electrodes) is enabled. 

Enabling this feature will merge all the processed files issued from the 
[signal averaging](#averaging-electrodes) such as each merged signal results in one row in the dataset.

### Post-processing

The first option allows to add a random key as combination of 6 alphanumerical characters to the 
resulting filenames.

The second adds a timestamp of format `year-month-day-hour-minute` (at the time the file is being 
processed).

The third adds a specified keyword to the resulting filenames.

> <img src="data/help/yellow_warning.png" width="30" height="30">
>
> These customisations do not replace the file name, which will depend on the processes it will undergo.
> They only are added at the end of the standard file name.


Allow to specify the directory where the resulting files will be saved.


### Miscellaneous


# Learning

# Analysis
## Plot

## Features importance

## Principal Component Analysis

## Confusion matrix

# Miscellaneous