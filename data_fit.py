import numpy as np
from firedrake import *
from solver import solve_tides, gauge_settwo

def pcn(TideSolver, wn, wn1, t, y_act, c = Constant(0.001), iter = 10, beta = 0.01, cov = np.ones((1,1)), t_trunc = 900, nsteps = 1200):

  import numpy as np
  import matplotlib.pyplot as plt
  """
  inputs

  n: an integer which represents the number of iterations
  c
  beta: Weight; number between 0 and 1 
  cov: a nxn covariance matrix

  output

  c
  """

  def phi(y_act, y_obs):
    """
    Return phi value
    """
    entries = y_act-y_obs
    squared_norm = np.linalg.norm(entries) ** 2
    res = squared_norm *20
    print(res)
    return res

  lengt = 1
  J = np.log(c.dat.data)[0]
  acc_probs = []
  # Initialize an empty list to store sampled c values
  exp_J_hats = []
  cumulative_avg = np.exp(J)

  for k in ProgressBar(f'iterations').iter(range(iter)):
    
    xi = np.random.multivariate_normal(np.zeros(( lengt, )), cov , size = lengt)#Centred Gaussian Measure
    #positive J ~ multivariate normal (log c0, )
    #c = exp(J) 
    #generate both c from the same distribution
    J_hat = np.sqrt(1 - beta**2)*J + beta*xi[0][0]
    print(np.exp(J_hat))
    unif = np.random.uniform(0,1) 
    
    TideSolver.snes.destroy()
    c.assign(Constant(np.exp(J)))
    TideSolver, wn, wn1, t, F0, c = solve_tides(c)
    y_obs_c = gauge_settwo(TideSolver, wn, wn1, t, t_trunc = t_trunc, gauge_num = 20, nsteps = nsteps)

    TideSolver.snes.destroy()
    c.assign(Constant(np.exp(J_hat)))
    TideSolver, wn, wn1, t, F0, c = solve_tides(c)

    y_obs_c_hat = gauge_settwo(TideSolver, wn, wn1, t, t_trunc = t_trunc, gauge_num = 20, nsteps = nsteps)
    
    d = np.exp(phi(y_act, y_obs_c) - phi(y_act, y_obs_c_hat))
    acc_prob = np.minimum(1, d)
    
    print(acc_prob)

    
    acc_probs.append(acc_prob)
    exp_J_hats.append(np.exp(J_hat))
    
    if unif <= acc_prob:
       J = J_hat
       print("accepted")
       cumulative_avg = (cumulative_avg * k + np.exp(J_hat))/(k + 1)
    # Append the sampled c value to the list
    
    print("c = " + str(np.exp(J)))
  
  plt.clf()

  # Add a vertical line at the true value of c
  true_c = 0.0001
  plt.scatter(range(iter), exp_J_hats)
  plt.xlabel("Iteration")
  plt.ylabel("Sampled c")
  plt.title("PCN Sampling - Scatter Plot")
  

  plt.show()
  plt.savefig("post_dist.pdf")

  # Save the results to a file
  np.savetxt('pcn_results.txt', np.array([np.exp(J)]), fmt='%.6f')
  np.savetxt('acc_probs.txt', np.array(acc_probs), fmt='%.6f')
  np.savetxt('exp_J_hats.txt', np.array(exp_J_hats), fmt='%.6f')
  np.savetxt('cumulative_avg.txt', np.array([cumulative_avg]), fmt='%.6f')
  
  acp = sum(acc_probs)/len(acc_probs)
  
  return np.exp(J), acc_probs, exp_J_hats, cumulative_avg, acp