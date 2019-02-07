# Setting up variables and such.

import qcodes as qc
from pytopo.mplplots.init_nb_plotting import *
from pytopo.mplplots import plots
from pytopo.mplplots import tools as plottools

qc.config['core']['db_location'] = r"D:\OneDrive\BF2\Data\experiments.db"
qc.config.user.current_sample = "181002_67_d1_CD20190121"

qc.initialise_database()
