import numpy as np
from firedrake import *
from data_gen import gauge_set
from data_fit import pcn
from solver import solve_tides
from solver import gauge_settwo
# Define the parameters for gauge_set

t_trunc = 0
gauge_num = 20
nsteps = 100
TideSolver, wn, wn1, t, F0, c = solve_tides(c = Constant(0.0001))

# Call the gauge_set function

result = gauge_settwo(TideSolver, wn, wn1, t= t, t_trunc=t_trunc, gauge_num=gauge_num, nsteps=nsteps)
#print(result)
#TideSolver.snes.destroy()

#c.assign(0.001)
#TideSolver, wn, wn1, t, F0, c = solve_tides(c)

#result2 = gauge_settwo(TideSolver, wn, wn1, t= t, t_trunc=t_trunc, gauge_num=gauge_num, nsteps=nsteps)
#print(result2)
#print(np.linalg.norm(result-result2))

#print(result)
# Import the pcn function from data_fit
from data_fit import pcn

# Define the parameters for pcn

iterations = 10
beta = 0.05
cov = np.ones((1, 1))

# Call the pcn function
pcn_result = pcn(TideSolver, wn, wn1, t, result, c=Constant(0.001), iter=iterations, beta=beta, cov=cov, t_trunc = t_trunc, nsteps=nsteps)

# Print or process the pcn_result as needed
print(pcn_result)