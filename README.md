# LookOut

## Contents
- [File Structure](#file-structure)
    - [Main Algorithm Files](#main-algorithm-files)
    - [Helper Files](#helper-files)
    - [Data Structures](#data-structures)
    - [Config Files](#config-files)
    - [Data Manipulation Files](#data-manipulation-files)
- [Run Instructions](#run-instructions)
- [Output Examples](#output-examples)
- [References](#references)

## File Structure
### Main Algorithm Files

#### test.py
This is the main file to be run. It takes in user arguments and facilitates the call of different functions which take in these passed arguments. 
The flow consists of:
1. Initialize the enviornment
2. Read files and generate features
3. Generate scatter plots for each feature pair and assign outlier scores to points for each scatter plot
4. Obtain the points-of-interest, i.e the global outlier points
5. Generate Time series plots depicting the outliers
6. Run the [LookOut][1] algorithm to obtain the best plots to show to the user

The user arguments are explained as follows:
- `-f` | `--datafile` : The file with data to fit on the model
- `-t` | `--trainfile` : The file with data to train the model
- `-l` | `--logfile` : The logfile ; default - log.txt
- `-df` | `--datafolder` : The folder containing the datafile and trainfile ; default - Data/
- `-lf` | `--logfolder` : The folder containing the logfiles ; default - Logs/
- `-pf` | `--plotfolder` : The folder into which to output the plots ; default - Plots/
- `-d` | `--delimiter` : The csv datafile delimiter ; default - ","  
- `-b` | `--budget` : Number of plots to display ; default - 3
- `-n` | `--number` : Number of outliers to choose ; default - 10
- `-p` | `--pval` : Outlier score scaling factor ; default - 1.0
- `-s` | `--show` : Specify if all generated plots are to be stored in the plotfolder ; default - false
- `-bs` | `--baselines` : Specify if you want to run the baseline algorithms ; default - false
- `-mrg` | `--merge` : Specify if the global set of outliers will be picked from a merged ranklist ; default - false
- `-if` | `--iforests` : Specify if the global set of outliers will be picked using iForests ; default - false
- `-dict` | `--dictated` : Specify if the global set of outliers will be dictated (see feature_file.py) ; default - false

#### LookOut.py
This file takes the bipartite graph between outliers and plots as input and runs the LookOut algorithm to obtain the b (budget) best plots. 
There are also two other baselines that can be run to compare with the Lookout algorithms, namely *Greedy TopK* and *Random Selection*.

#### iForests.py
This file creates an [iForests][2] model. It trains the model via the training data and then attempts to score the test data on the trained model. 
A further improvements on the scores can be done by also further training another model on the test data itself and generating new test scores. 
Then the two obtained scores can be intropolated for best results.

#### ranklist.py
The objective of this file is to process the outlier scores from each pair-wise scatter plot and generate an output data matrix that can be used to populate the bipartite graph. 
We generate two types of output matrices, *scaled_matrix* and *normal_matrix*. 
The *scaled_matrix* is equivalent to the *normal_matrix*, except with all the scores scaled by a factor *pval* with help of a scaling function defined in *helper.py*.

#### outliers.py
This file returns the global outlier objects that serve as the points-of-interest for the user. These global outliers can be calculated via three methods.
1. `merge` : The ranklists, of all the points, from their individual 2-Dimensional iForest scores will be merged into a single ranklist based on a [merging algorithm][3]. 
Then the top *n* ranked points will serve as the set out outliers.
2. `iforests` : The set of *n* outliers will be chosen by running the [iForests][2] algorithm in the complete multidimensional feature space. The top *n* scored points will be chosen.
3. `dictated` : The user will define the set of outlier ids in the *features_file.py*. In this case the number of outliers chosen will be equal to the length of the outlier id list.

#### run\_algos.py
This file along with *test.py* control the flow of the program. This file particularly looks at creating the environment to run the LookOut algorithm.
1. This file takes in the intermediate outputs: *rank_list*, *outliers*, and *features*. 
2. It then calls *ranklist.py* to generate *scaled_matrix* and *normal_matrix*.
3. Then the *scaled_matrix* is used to generate the bipartite graph which is passed on to *LookOut.py* which in-turn produces the final list of best plots.
4. The various metrics of the chosen plots are calculated using the **Algorithm Helpers** functions in *helper.py*.
5. The repective *focus_plots* are created and saved to the Plots Folder.

***

### Helper Files

#### helper.py
This file contains various helper functions that are used by several of the algorithm files. It serves a dual purpose of removing unnecessary logic from the main files and also increases reusability of code.
Broadly the helper functions can be grouped as:
- **Data Analysis Functions** : These functions will return different statistical metrics on the input data (list format), such as, _min_, _max_, _mean_, _median_, and *std_dev*.
- **Pandas Data Parse Functions** : Several functions specifically designed to get pandas data object as input. They either calculate different metrics or perform minor fixes on the data.
- **Feature Handlers** : These functions help manipulate and merge multiple features required for generating plots and iForest scores.
- **Scaling Function** : Contains the logic to scale the outlier scores of each point before comparing.
- **Algorithm Helpers** : These functions, *get_coverage* and *generate_frequency_list*, calculate necessary metrics critical to the LookOut algorithm.
- **Initialize Environment** : This function parses user arguments and check if all the required folders are and files are avaiable during runtime.

#### plot\_functions.py
This file contains functions that help create different type of plots that might be useful to the user. It consists of the four mian functions:
1. **generate_scatter_plots** : This function makes calls to *scatter_plot* function and itterates over a list of feature pairs. It helps consolidate the scores of the points in each of the generated scatter plots in a variable *rank_matrix*.
2. **scatter_plot** : This function, when given two features, will create a scatter plot image that is saved to a folder and also generates outlier scores of the points w.r.t. the two features using the iForests algorithm in 2 dimensions.
3. **scatter_outliers** : This function creates the final user output focus-plots (scatter plots) that have highlight outliying points in easy to see colors.
4. **time_series_plots** : This function is responsible to create the time series plots for each of the features w.r.t the multiday averages.

***

### Data Structures

#### structures.py
This file declares four classes that are used by the LookOut algorithm to calculate the best visualization plots.
1. __Outlier__ : These class objects define an outlier in the bipartite graph, maintaining its identity and edge weight
2. __Plot__ : These class objects define a plot in the bipartite graph, maintaining its identity and global influence
3. __Edge__ : These class objects map the relation between an _outlier object_ and a _plot object_
4. __Graph__ : This class defines a global object that declares the bipartitie graph between outliers and plots. It consists of several member function to update and manipulate the graph based on rules defined by the LookOut algorithm.

#### data.py
This file declares two classes that deal with data representation
1. __Feature__ : An object of this class contians all the logistical information required to handle the data of a feature we have defined. It contains the following fields:
    - _name_ : The feature name
    - _description_ : The displayed description of the feature
    - _type_ : Define the type of the data from either {continuous, discrete, or time_series}
    - _log_ : Mentions whether the data should be represented on log scale or linear scale
    - _analytics_ : Basic stats of the included data such as mean, median, min, max and std_dev
    - _data_ : The actual numeric data of the feature
    - _ids_ : The identity entity labels of each data entry
2. __Outlier__ : Objects of this class help capture important information of some selected points of interest. Each object contains the following fields:
    - _id_ : The outlier id
    - _score_ : A calculated anomaly score for this object / outlier
    - _anomaly_ : A bool value which specifies if the outlier appears as an outlier or not
    - *raw_data* : The raw feature values of the outlier
    - *stat_data* : The aggregate values of the raw data including *mean* and *std_dev*
    - *ratios* : The ratio of the raw data w.r.t the *mean* and *std_dev* of the aggregates

***

### Config Files

#### display.py
This file contains parameters that specify the display variables such as the terminal color prompts, and the styling of standard logging functions. 

#### feature\_file.py
This file include all the data and feature specific variables:
- `identity_field` is used to declare the identity object column
- `identity_is_time` is used to specify that the identity object is time based. Will be used to make the time-series graphs
- `entry_limit` defines the lower limit for the number of entires of an object from the *identity_field*. An object with fewer entries than the limit will be ignored.
- `time_series_data` defines that the data is temporal in nature or not with time based data entries
- `timestamp_field` declares the column name that contains the timestamp data
- `aggregate_fields` is a list of the aggregate field columns
- `object_fields` is a list of the object field columns
- `norm_field` declares any aggregate column to use as the base. All other aggregate fields will be normalized based on this base column.
- `outlier_list` is used to particularly observe the characteristics of certain points of focus. This is a list of the object ids of those objects. 

***

### Data Manipulation Files

#### create\_files.py
This file is used to create a datafile (.csv) with desired entries. The user can provide their preferences via the following options:
- `-t` | `--team` : The team id ; default - 15 (LimeStone)  
- `-p` | `--product` : The product id ; default - 2 (Futures)
- `-v` | `--venue` : The venue id ; default - 23 (CME)
- `-s` | `--sid` : The symbol id ; default - 0
- `-y` | `--year` : The year of historical file ; default - 2018
- `-m` | `--month` : The month of historical file ; default - 5
- `-d` | `--day` : The day of historical file ; default - 29 
- `-b` | `--bucket` : The bucket size (data sampling rate in seconods) ; default - 30
- `-pr` | `--period` : The periodicity of the data ; default - 0 (1 day)

It makes a call to the elastic search engine with all the above parameters and generates a corresponding file (csv) which is placed in the Data folder.

#### extract.py
This file is used to create a datafile (.csv) with desired entries. The user can provide their preferences via the following options:
- `-f` | `--datafile` : The file from which to extract data ; default - ""  
- `-t` | `--targetfile` : The file to export the data ; default - target.csv
- `-m` | `--mode` : specify type of extraction {full, partial, random} ; default - full
- `-p` | `--portion` : Fraction of data to extract ; default - 1.0
- `-i` | `--include` : Specify columns to include ; default - all
- `-e` | `--exclude` : Specify columns to exclude ; default - none

It reads a csv file and generates a corresponding target file (csv) which is placed in the Data folder. It should be used in conjunction to the *create\_files.py* to further selectively modify the data.

#### read\_data.py
This file is used to extract features from the read datafile. It makes use of the python pandas library and transforms the data to create feature data objects. 
There are four main processing steps in this file:
1. Read File
    - It reads the csv file data based on a delimiter and creates a pandas dataframe object. A boolean parameter can be passed, *train*, which helps specify to read the train file or test file
2. Transform Data
    - Apply filters to remove unwanted rows. `entry_limit` variable declared and defined in *feature\_files.py* is one such filter.
    For current aggregated time series data we disable it with `entry_limit = 0` 
    - Calculate time series. Features like object *Lifetime* and *Inter-Arrival Time* are added as columns to the pandas dataframe. Currently for aggreagated data we wont calculate and time series features.
3. Create Features
    - Features are of Four categories
        - __Identity Features__ : These are the objects of identity and stores their `IDs` and `COUNT`
        - __Time Series Features__ : These are data temporal features like `LIFETIME`, `IAT_VAR_MEAN`, `MEAN_IAT` and `MEDIAN_IAT`. In case of aggregated time series data we wont create time series features.
        - __Aggregate Features__ : The features containing data that can be aggregated (summed, averaged, etc.). For an aggregate data column _field_ we calculate features `FIELD`(summed) and `stddev_FIELD`. Note) we currently work with aggregated data so the `stddev_FIELD` features can be obtained from the train file.
        - __Object Fields__ : The features containing identities like object names. For an object data column _field_ we calculate features `FIELD`(unique count).
4. Normalize Features
    - First we delete flat features (Near zero mean or std_dev)
    - Second we scale the numeric feature values using a scale algorithm.

## Run Instructions
There are two stages to run the code: __Data Preparation__ and __Run LookOut__
### Data Preparation
##### Step 1) 
Call on *create_files.py* to get a readable csv file for a particular team, venue, product and date. Read [here](#create_filespy) for argument specification.  
Note) You will have to set the file path `HIST_DATA_DIR` to a suitable location to access the raw files.

`python create_files.py -t <team_id> -y <year> -m <month> -d <day>  [args list]`

##### Step 2) (optional)
Call on *extract.py* to further filterout unwanted columns. Read [here](#extractpy) for argument specification.  
Note) This step can be ignored if no columns have to be deleted

`python extract.py -f <datafile> -t <targetfile> [args list]`

e.g. Lets extract certain columns from the data

`python extract.py -f <datafile> -t <targetfile> -i ['orders', 'cancels', 'trades', 'buyShares', 'sellShares']`

### Run LookOut
##### Step 1) 
Modify *feature_file.py* to the appropriate specification. Current default values should work okay.

``` python
identity_field = 'ts_epoch'
identity_is_time = True
entry_limit = 0                 # The minimum entries that must exist per identity item (Set to 0 to disable)
time_series_data = False        # Calculates lifetimes and IAT data (should be set to false if only one entry per identity)
timestamp_field = 'TIMESTAMP'   # Used only if time_series_data is set to true
aggregate_fields = ['orders', 'cancels', 'trades', 'buyShares', 'sellShares', 'buyTradeShares', \
                    'sellTradeShares', 'buyNotional', 'sellNotional', 'buyTradeNotional', \
                    'sellTradeNotional', 'alters', 'selfTradePrevention']
object_fields = []
norm_field = 'orders'
outlier_list = []]
```

##### Step 2)
Run the LookOut Algorithm on the files generated from the Data Preparation stage with the configuations specified in the *feature_file.py*. Read [here](#testpy) for argument specification.

`python test.py -f <filename> -t <trainfile> -b <budget> -n <number> [-mrg | -if | -dict] (-if recommended) [args list]`

The *-f (filename)* and *-t (trainfile)* must be specified by the user.  
The *-b (budget)* and *-n (number of outliers)* have default values of 3 and 10 respectively. They don't have to be specified, but it is good practice to declare them.  
It is recommended to use the *-if (iForests)* for best results in calculating global outliers. Look [here](#outlierspy) for more information.  

## Output Examples
The outputs of the algorithm are reflected in the Plots folder. There will be three tyoes of files here:
1. scatterplot.pdf - This contains all the scatter plots created for the pairwise features
2. timeseries.pdf - This is the time series data plot for each feature from the test file w.r.t the average aggregated values in the trainfile
3. LookOut-n-b-i-(train).png - These are the output focus plots from the algorithm. n - number of outliers, b - budget, and i - i^th plot. 
For each value of n, b and i there are two pngs: the first one is the testfile scatter plot and the second, appeneded with *train* is the trainfile scatter plot for that chosen feature pair.

Let us look at some LookOut-n-b-i-(train).png with n = 6 and b = 3

| <img src="./images/LookOut-6-3-0.png" alt="drawing" width="400px"/> | <img src="./images/LookOut-6-3-1.png" alt="drawing" width="400px"/> | <img src="./images/LookOut-6-3-2.png" alt="drawing" width="400px"/> | 
|:--:| :--:| :--:|
| *LookOut-6-3-0.png* | *LookOut-6-3-1.png* | *LookOut-6-3-2.png* |

| <img src="./images/LookOut-6-3-0-train.png" alt="drawing" width="400px"/> | <img src="./images/LookOut-6-3-1-train.png" alt="drawing" width="400px"/> | <img src="./images/LookOut-6-3-2-train.png" alt="drawing" width="400px"/> | 
|:--:| :--:| :--:|
| *LookOut-6-3-0-train.png* | *LookOut-6-3-1-train.png* | *LookOut-6-3-2-train.png* |


## References
1. [LookOut][1]
2. [iForests][2] 
3. [Ranklist Merge Algorithm][3] 

[1]: https://arxiv.org/pdf/1710.05333.pdf        
[2]: https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf 
[3]: https://people.cs.umass.edu/~sheldon/papers/cikm15-camera.pdf
