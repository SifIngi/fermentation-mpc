import os
from bs4 import BeautifulSoup

# Needs to be done to generalize the program:
# 1) Delete 1 experimental data if there is only 1 experimental data to estimate from.
# 2) Delete and create more parameters that needs to be estimated.
# 3) Set length of experimental data
# 4) Choose the step size
# 5) Choose the parameter estimation algorithm

# From cps to xml
os.rename('model_copasi.cps', 'model_copasi.xml')

soup = BeautifulSoup(open('model_copasi.xml', 'r'), 'xml')
infile = open('model_copasi.xml', "w")

# Choose filename for experimental dataset nr 1
Experiment_0 = [s for s in soup.find_all('ParameterGroup') if s["name"] == "Experiment"][0]
file_name = [s for s in Experiment_0.find_all("Parameter") if s["name"] == "File Name"][0]
file_name["value"] = "R1_data_in_moles.csv"  # Here we type the filename of the data

# Choose filename for experimental dataset nr 2
Experiment_1 = [s for s in soup.find_all('ParameterGroup') if s["name"] == "Experiment_1"][0]
file_name = [s for s in Experiment_1.find_all("Parameter") if s["name"] == "File Name"][0]
file_name["value"] = "R2_data_in_moles.csv"  # Here we type the filename of the data

# Parameters:

parameter_1 = [s for s in soup.find_all('ParameterGroup') if s["name"] == "FitItem"][0]
lower_bound_1 = [s for s in parameter_1.find_all('Parameter') if s['name'] == "LowerBound"][0]
# Set lower bound instead of 0.
lower_bound_1['value'] = '0'
upper_bound_1 = [s for s in parameter_1.find_all('Parameter') if s['name'] == "UpperBound"][0]
# Set upper bound instead of 100.
upper_bound_1['value'] = '100'

parameter_2 = [s for s in soup.find_all('ParameterGroup') if s["name"] == "FitItem"][1]
lower_bound_2 = [s for s in parameter_2.find_all('Parameter') if s['name'] == "LowerBound"][0]
# Set lower bound instead of 0.
lower_bound_2['value'] = '0'
upper_bound_2 = [s for s in parameter_2.find_all('Parameter') if s['name'] == "UpperBound"][0]
# Set lower bound instead of 100.
upper_bound_2['value'] = '100'

parameter_3 = [s for s in soup.find_all('ParameterGroup') if s["name"] == "FitItem"][2]
lower_bound_3 = [s for s in parameter_3.find_all('Parameter') if s['name'] == "LowerBound"][0]
# Set lower bound instead of 0.
lower_bound_3['value'] = '0'
upper_bound_3 = [s for s in parameter_3.find_all('Parameter') if s['name'] == "UpperBound"][0]
# Set lower bound instead of 100.
upper_bound_3['value'] = '100'

parameter_4 = [s for s in soup.find_all('ParameterGroup') if s["name"] == "FitItem"][3]
lower_bound_4 = [s for s in parameter_4.find_all('Parameter') if s['name'] == "LowerBound"][0]
# Set lower bound instead of 0.
lower_bound_4['value'] = '0'
upper_bound_4 = [s for s in parameter_4.find_all('Parameter') if s['name'] == "UpperBound"][0]
# Set lower bound instead of 100.
upper_bound_4['value'] = '100'

infile.write(soup.prettify().encode(soup.original_encoding))
infile.close()

# From xml to cps
os.rename('model_copasi.xml', 'model_copasi.cps')

# Run the parameterestimation in Copasi for the model from the terminal
# A report of parameters is also written as parameter_report
#os.system("/Applications/COPASI/CopasiSE model_copasi.cps --save model_copasi.cps")
os.system("/Users/s144510/Documents/fermentationtool/CopasiSE model_copasi.cps --save model_copasi.cps")

# Get the results
os.rename('model_copasi.cps', 'model_copasi.xml')
soup = BeautifulSoup(open('model_copasi.xml', 'r'), 'xml')
# infile = open('test.xml', "w")

result_parameter_1 = [s for s in soup.find_all('ParameterGroup') if s["name"] == "FitItem"][0]
result_parameter_1 = [s for s in result_parameter_1.find_all('Parameter') if s['name'] == "StartValue"][0]
alpha = result_parameter_1['value']

result_parameter_2 = [s for s in soup.find_all('ParameterGroup') if s["name"] == "FitItem"][1]
result_parameter_2 = [s for s in result_parameter_2.find_all('Parameter') if s['name'] == "StartValue"][0]
beta = result_parameter_2['value']

result_parameter_3 = [s for s in soup.find_all('ParameterGroup') if s["name"] == "FitItem"][2]
result_parameter_3 = [s for s in result_parameter_3.find_all('Parameter') if s['name'] == "StartValue"][0]
kc = result_parameter_3['value']

result_parameter_4 = [s for s in soup.find_all('ParameterGroup') if s["name"] == "FitItem"][3]
result_parameter_4 = [s for s in result_parameter_4.find_all('Parameter') if s['name'] == "StartValue"][0]
mu_max = result_parameter_4['value']
# infile.write(soup.prettify().encode(soup.original_encoding))

print(alpha, beta, kc, mu_max)

infile.close()
os.rename('model_copasi.xml', 'model_copasi.cps')

