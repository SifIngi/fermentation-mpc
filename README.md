# fermentation-mpc
Model predictive control (MPC) for fermentations

## Description
This program is used for modelling, optimizations and model driven control for fed batch fermentations. It is using a particular serine model based on
mass balances. The growth rates are calculated from online data (CER values) and are input in the model.
Then model simulation is computed, which can predict the compounds of interest until current time points. Afterwards, parameter estimation is made
which uses the previous simulated values, to fit a predictive model. This model is simulated, both with the original feeding values, and also with varying feeding parameters.
Plot of this is generated by plotly and the browser reloads every time there is new incoming online data. Visualization of the plots can be seen in the figure.
Smaller configurations has to be made, in order for it to work in a bioreactor setup.

![](/images/mpc.png)
From the first row the model simulation based on online data can be seen with the predictive model. Experimental data is also shown here.
The second row is future prediction on grams of serine, production rate and serine titer.

## Requirements
The project uses pipenv to handle virtual environment. <br />
Install pipenv here [pipenv installation](https://github.com/pypa/pipenv#installation)

## Installing

To activate the project
```
pipenv shell
```

Install the necessary dependencies
```
pipenv install
```

## Preprocess
The model development and all the preprocess work has been added in the folder "Preprocess".
This was made in Jupiter Notebook using Python version 3 from Anaconda.

## Usage of the program

One can choose to use the modelprediction_CO2.py for only prediction or modelpredictionfeed_CO2,
which can predict and provide an optimal feeding strategy. Herunder example of how to use modelpredictionfeed_CO2.py is described.

#### Before running the script

Set correct path for project folder in parest_copasi, so the parameter task in Copasi can be executed.
Path for where the online data is located, and which file should be watched, has to be set in the modelpredictionfeed_CO2.py

```
watch_file = 'data/SER_C016_Reactor24_4g-LGlycine_0,02FeedRate.csv'
```

#### Models
There are currently 2 models in models.py, which has been made in tellurium.
The fed_batch_model.py, that is used for the prediction models, and the fed_batch_model_mu.py, which is used for the model simulation based on online data.
They can be loaded as:

```
r = fed_batch_model_mu()
r = fed_batch_model()
```

#### Growth rate calculation
This is the code that calculates the growth rate calculations,
if you wish to calculate it in another way, this is the part that needs to be altered

```
online_data = pd.read_csv(watch_file)

# Time from online data is converted to decimals so calculations are possible to make
online_data = (time_to_decimals(online_data))
online_data['Time (hours)'] = online_data['Time (min)']/60

# Set filename of the two experimental datasets
#R23_amounts = pd.read_csv("Preprocess/estimation/fedbatch_amounts/R23_amounts.csv")
R24_amounts = pd.read_csv("Preprocess/estimation/fedbatch_amounts/R24_amounts.csv")

# Use only data from which CER begins
data_frame_selected_values = online_data[np.isfinite(online_data['Bioreactor 24 - CER'])]
data_frame_selected_values.reset_index(inplace=True, drop=True)

# Reset the time, so the first values corresponds to time 0
data_frame_selected_values = data_frame_selected_values.copy()
data_frame_selected_values['Time (hours)'] = data_frame_selected_values['Time (hours)'] - \
                                           data_frame_selected_values['Time (hours)'][0]

tCER = []
tCER.append(0)  # Here set the initial value of tCER if you have that.

for i in range(0, (len(data_frame_selected_values['Time (hours)']) - 1)):
    tCER_i = ((data_frame_selected_values['Bioreactor 24 - CER'][i] +
               data_frame_selected_values['Bioreactor 24 - CER'][i + 1]) / 2) * (
                         data_frame_selected_values['Time (hours)'][i + 1] - data_frame_selected_values['Time (hours)'][
                     i]) + tCER[i]  # [CO2 %]
    tCER.append(tCER_i)

# Online growth rate calculations from CER and tCER
mu = data_frame_selected_values['Bioreactor 24 - CER'] / tCER  # [1/h]
```

#### Parameter estimation
For the parameter estimation part, the models has to be saved as a SBML file, and then uploaded within Copasi.
You have make an estimation task before running this program, and choose which parameters you want to estimate. In this case it worked well with estimating all parameters.
In the program you can then set the lower and upper bounds.

```
# Set bounds for the parameters
parameter_1_lower_bound = "0"
parameter_1_upper_bound = "10"
parameter_2_lower_bound = "0"
parameter_2_upper_bound = "10"
parameter_3_lower_bound = "0"
parameter_3_upper_bound = "100"
parameter_4_lower_bound = "0"
parameter_4_upper_bound = "10"
parameter_5_lower_bound = "0"
parameter_5_upper_bound = "10000000"
parameter_6_lower_bound = "0"
parameter_6_upper_bound = "10"
parameter_7_lower_bound = "0"
parameter_7_upper_bound = "10"
```
Then the estimated parameters will be set in the predictive models in the program automatically.

#### Feeding optimization

The following code handles the feeding optimization, since in this case, there are three expressions
that were chosen to predict with different feeding values (grams of serine, production rate and serine titer), three
predictive model were made. The par is the feeding values that were chosen to simulate with.

```
# Simulate predictive models with different feeding parameters
fp = fed_batch_model()

model_feed_settings(fp, data_frame, alpha, beta, Ks_qs, qs_max, Ki, Ks, mu_max)

m = fp.simulate(data_frame_selected_values['Time (hours)'].iloc[-1],
               data_frame_selected_values['Time (hours)'].iloc[-1] + 5, 50, ['time', 'serine'])

fprate = fed_batch_model()
model_feed_settings(fprate, data_frame, alpha, beta, Ks_qs, qs_max, Ki, Ks, mu_max)

simser = fprate.simulate(data_frame_selected_values['Time (hours)'].iloc[-1],
               data_frame_selected_values['Time (hours)'].iloc[-1] + 5, 50, ['time', 'qpbio'])

fptiter = fed_batch_model()
model_feed_settings(fptiter, data_frame, alpha, beta, Ks_qs, qs_max, Ki, Ks, mu_max)

simtiter = fptiter.simulate(data_frame_selected_values['Time (hours)'].iloc[-1],
               data_frame_selected_values['Time (hours)'].iloc[-1] + 5, 50, ['time', 'sertiter'])


# The varying parameters
par1 = np.linspace(0, fp.mu_set, num=4)
par2 = np.linspace(fp.mu_set, 0.1112, num=4)
par = np.concatenate((par1, par2), axis=None)
par = np.unique(par)

colors = ["blue", "black", "yellow", "pink", "green", "purple", "orange"]

print(data_frame)

production_values = []

# Here the actual simulation starts
for i, j, k in zip([1, 3, 5, 7, 9, 11, 13], par, colors):


    model_feed_settings_loop(fp, data_frame, alpha, beta, Ks_qs, qs_max, Ki, Ks, mu_max, j)

    m = np.hstack([m,fp.simulate(data_frame_selected_values['Time (hours)'].iloc[-1],
               data_frame_selected_values['Time (hours)'].iloc[-1] + 5, 50, ['time', 'serine'])])

    model_feed_settings_loop(fprate, data_frame, alpha, beta, Ks_qs, qs_max, Ki, Ks, mu_max, j)

    simser = np.hstack([simser,fprate.simulate(data_frame_selected_values['Time (hours)'].iloc[-1],
               data_frame_selected_values['Time (hours)'].iloc[-1] + 5, 50, ['time', 'qpbio'])])

    model_feed_settings_loop(fptiter, data_frame, alpha, beta, Ks_qs, qs_max, Ki, Ks, mu_max, j)

    simtiter = np.hstack([simtiter,fptiter.simulate(data_frame_selected_values['Time (hours)'].iloc[-1],
               data_frame_selected_values['Time (hours)'].iloc[-1] + 5, 50, ['time', 'sertiter'])])


    simsergrams = pd.DataFrame(m)
    simserdf = pd.DataFrame(simser)
    simtiterdf = pd.DataFrame(simtiter)

    # Drop the first 2 columns since they are the original ones
    simsergrams.drop([0,1], axis=1, inplace=True)
    simserdf.drop([0, 1], axis=1, inplace=True)
    simtiterdf.drop([0, 1], axis=1, inplace=True)
```

### Further development

The program can not yet detect, when the fed batch phase starts, and growth rate were found to not fit the batch phase.
But it might be able to tryout the program anyway in a bioreactor setup, if the first and second index value of the fed batch phase
from online data were to be manually typed. In this case it was at 25 and 26. Those are used for the simulation time points.

```
start_time = data_frame_selected_values['Time (hours)'][25]
end_time = data_frame_selected_values['Time (hours)'][26]
```

Further development has to be made, regarding the optimal feeding parameter.
If you wish to use the optimized parameter value at an undefined time, then further development has to be made, so the
program knows, when you are using the feeding parameter and then can update all of the models with the new values.

There has been added outcommented code in the modelpredictionfeed_CO2.py, which you can use if you are sure, that you will be using a particular feeding value
(in this case it is production rate) everytime new online data has been registered.

As can be seen in the Pipfile, the Python version used for this program was Python 2.7. It would therefore be ideal, to get the program to work with Python 3.










