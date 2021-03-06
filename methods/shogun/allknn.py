'''
  @file allknn.py
  @author Marcus Edel

  All K-Nearest-Neighbors with shogun.
'''

import os
import sys
import inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from log import *
from timer import *

import numpy as np
from shogun.Features import RealFeatures, MulticlassLabels
from shogun.Classifier import KNN as SKNN
from shogun.Distance import EuclideanDistance

'''
This class implements the All K-Nearest-Neighbors benchmark.
'''
class ALLKNN(object):

  ''' 
  Create the All K-Nearest-Neighbors benchmark instance.
  
  @param dataset - Input dataset to perform All K-Nearest-Neighbors on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the shogun libary to implement All K-Nearest-Neighbors.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not 
  successful.
  '''
  def AllKnnShogun(self, options):
    def RunAllKnnShogun(q):
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the query 
      # file. 
      try:
        Log.Info("Loading dataset", self.verbose)
        if len(self.dataset) == 2:
          referenceData = np.genfromtxt(self.dataset[0], delimiter=',')
          queryData = np.genfromtxt(self.dataset[1], delimiter=',')
          queryFeat = RealFeatures(queryFeat.T)
        else:
          referenceData = np.genfromtxt(self.dataset, delimiter=',')

        # Labels are the last row of the dataset.
        labels = MulticlassLabels(referenceData[:, (referenceData.shape[1] - 1)])
        referenceData = referenceData[:,:-1]
      
        with totalTimer:
          # Get all the parameters.
          k = re.search("-k (\d+)", options)
          if not k:
            Log.Fatal("Required option: Number of furthest neighbors to find.")
            q.put(-1)
            return -1
          else:
            k = int(k.group(1))
            if (k < 1 or k > referenceData.shape[0]):
              Log.Fatal("Invalid k: " + k.group(1) + "; must be greater than 0"
                + " and less or equal than " + str(referenceData.shape[0]))
              q.put(-1)
              return -1

          referenceFeat = RealFeatures(referenceData.T)
          distance = EuclideanDistance(referenceFeat, referenceFeat)

          # Perform All K-Nearest-Neighbors.
          model = SKNN(k, distance, labels)
          model.train()      

          if len(self.dataset) == 2:
            out = model.apply(queryFeat).get_labels()
          else:
            out = model.apply(referenceFeat).get_labels()
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunAllKnnShogun, self.timeout)

  '''
  Perform All K-Nearest-Neighbors. If the method has been successfully 
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negativ value if the method was not 
  successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform ALLKNN.", self.verbose)

    return self.AllKnnShogun(options)
