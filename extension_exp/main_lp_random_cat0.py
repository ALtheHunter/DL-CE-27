from __future__ import division
from time import time
from utils.access_my_generated_data import datasplit
from utils.utils import LP_BP_avg_err
from scipy import sparse
import os
import numpy as np
import tensorflow as tf

flags = tf.app.flags

flags.DEFINE_integer('input_dim', 512, "Input dimension [512]")
flags.DEFINE_integer("emb_dim", 15, "Number of measurements [10]")
flags.DEFINE_integer("num_samples", 40000, "Number of total samples [40000]")
flags.DEFINE_string("checkpoint_dir", "../results/20200519_deepMIMOdataset_lp_random_cat0/",
                    "Directory name to save the checkpoints \
                    [../results/]")
flags.DEFINE_integer("num_random_dataset", 1,
                     "Number of random read_result [1]")
flags.DEFINE_integer("num_experiment", 1,
                     "Number of experiments for each datasets [1]")

FLAGS = flags.FLAGS


# models parameters
input_dim = FLAGS.input_dim
emb_dim = FLAGS.emb_dim
num_samples = FLAGS.num_samples

# checkpoint directory
checkpoint_dir = FLAGS.checkpoint_dir
if not os.path.exists(checkpoint_dir):
    os.makedirs(checkpoint_dir)

# number of experiments
num_random_dataset = FLAGS.num_random_dataset
num_experiment = FLAGS.num_experiment

results_dict = {}


def merge_dict(a, b):
    """Merge two dictionaries"""
    for k in b.keys():
        if k in a:
            a[k].append(b[k])
        else:
            a[k] = [b[k]]


def l1_min(X, input_dim, emb_dim):
    """
    Args:
        X: csr_matrix, shape=(num_sample, input_dim)
    """
    # random Gaussian matrix
    G = np.random.randn(input_dim, emb_dim)/np.sqrt(input_dim)
    np.save(checkpoint_dir+'Gaussian_{}x{}.npy'.format(emb_dim, input_dim), G)
    Y = X.dot(G) # sparse.csr_matrix.dot
    g_err, g_exact, _ = LP_BP_avg_err(np.transpose(G), Y, X, use_pos=False)
    g_err_pos, g_exact_pos, _ = LP_BP_avg_err(np.transpose(G), Y, X, use_pos=True)

    res = {}
    res['lp_gaussian_err'] = g_err
    res['lp_gaussian_exact'] = g_exact
    res['lp_gaussian_err_pos'] = g_err_pos
    res['lp_gaussian_exact_pos'] = g_exact_pos
    return res


for dataset_i in range(num_random_dataset):

    _, _, X_test = datasplit(num_samples=num_samples,
                             train_ratio=0.8,
                             valid_ratio=0.1)
    x = X_test.todense()
    x = np.concatenate((x, np.zeros_like(x)), axis=1)
    X_test = sparse.csr_matrix(x)

    print(np.shape(X_test))

    res = {}
    # l1 minimization
    print("Start lP_BP......")
    t0 = time()
    res = l1_min(X_test, input_dim, emb_dim)
    t1 = time()
    print("lP_BP takes {} sec.".format(t1 - t0))
    merge_dict(results_dict, res)
    print(res)


# save results_dict
file_name = ('res_'+'input_%d_'+'emb_%02d.npy') \
            % (input_dim, emb_dim)
file_path = checkpoint_dir + file_name
np.save(file_path, results_dict)