
"""
Programming Guide

The main abstraction Spark provides is a resilient distributed dataset (RDD),
which is a collection of elements partitioned across the nodes of the cluster
that can be operated on in parallel. However, after Spark 2.0, RDDs are
replaced by Dataset, which is strongly-typed like an RDD, but with richer
optimizations under the hood. 

RDD is created through reading data from external storage, or parallelizing
data in the driver. Once created, it can be transformed to another RDD. 
Finilly, a result is valued from RDD and return to the driver program or write
to an external storage.

A second abstraction in Spark is shared variables that can be used in parallel
operations. Spark supports two types of shared variables: broadcast variables,
which can be used to cache a value in memory on all nodes, and accumulators,
which are variables that are only "added" to, such as counters and sums.

To run Spark applications in Python, use the bin/spark-submit script located in
the Spark directory. This script will load Spark's Java/Scala libraries and
allow you to submit applications to a cluster. You can also use bin/pyspark to
launch an interactive Python shell. Behind the scenes, pyspark invokes the more
general spark-submit script.

PySpark requires the same minor version of Python in both driver and workers. It
uses the default python version in PATH, you can specify which version of Python
you want to use by PYSPARK_PYTHON,

Passing Functino
    Most of Spark's transformations, and some of its actions, depend on passing
in functions that are used by Spark to compute data. Each of the core languages
has a slightly different machanism for passing function to Spark.
    In Python, we can pass in top-level(module-level) function or locally
defined functions(including lambda). Any variables that the function reference
(closure) will be serialized along the function. If the variable is an instance
of a class, the hole instance will be sent.


Data Partition
    Spark programs can control their RDDs' partition to reduce communication.
It lets the program ensure that a set of keys will appear together on some
node. This is useful only when a dataset is resued multiple times in
key-oriented operation such as joins.

Submitting Application

    The spark-submit script in Spark’s bin directory is used to launch
applications on a cluster. It acts as a client to the cluster. The main program
submitted is called driver program, which use the SparkContext object to
coordinate the workers.
    Each application gets its own SparkContext and a set of executor JVMs.
These executors stay up for the duration of the whole application. Data cannot
be shared across different instances of SparkContext without writing it to an
external storage system.
    The SparkContext will connect to the cluster manager and acquire executors.
Then it sends the application code (and dependencies) to the executors.
Finally, it sends tasks to the executors to run.
    If your code depends on other projects, you will need to package them
alongside your application in order to distribute the code to a Spark cluster.
For Python, you can use the --py-files argument of spark-submit to add .py,
.zip or .egg files to be distributed with your application. If you depend on
multiple Python files we recommend packaging them into a .zip or .egg.


Cluster Mode

                                                  Worker Node
                                                  +--------------=-+
                -<------------------------------> | Executor       |
                |                                 |      Cache     |
 Driver Program |                     -<--------> | Task  Task ... |
  +--------------+                    |           +----------------+
  | SparkContext | <-----> Cluster Manager                       |
  +--------------+                    |           Worker Node    |
                |                     -<--------> +--------------=-+
                |                                 | Executor       |
                |                                 |      Cache     |
                -<------------------------------> | Task  Task ... |
                                                  +----------------+

    In local mode, driver runs along with an executor in the same Java process.
In claster mode, driver and executors are different processes. Spark depends on
a cluster manager to launch executors and, in certain cases, to launch the
driver. Cluster manager may be Spark master(for standalone mode), Mesos 
master(for Mesos mode) or YARN(for YARN mode).
    Standalone cluster can be launched either manually(starting a master and 
workers by hand) or use launch scripts(loading the config file). Master and
workers may run on a single machine for testing. In client mode, the driver is
launched directly within the client(spark-submit) process. The input and output
of the application is attached to the console. In cluster mode, the driver is
launched from one of the Worker processes inside the cluster. client process
exits as soon as finish submitting without waiting for the application to
finish. Currently(2.2.0), standalone mode does not support cluster mode for
Python application.
    For Mesos mode, when a driver creates a job and starts issuing tasks for
scheduling, determines what slaves handle what tasks. When Mesos runs a task on
a Mesos slave for the first time, that slave must have a Spark binary package
for running the Spark Mesos executor backend. In client mode, the driver and
Spark Mesos framework is launched on the same client machine. Mesos waits for
the driver output. In cluster mode, the driver is launched in the cluster and
the client can find the results of driver from the Mesos Web UI.
    The driver program must listen for and accept incoming connections from its
executors throughout its lifetime. As such, the driver program must be network
addressable from the worker nodes.
    Because the driver schedules tasks on the cluster, it should be run close
to the worker nodes, preferably on the same local area network. If you’d like
to send requests to the cluster remotely, it’s better to open an RPC to the
driver and have it submit operations from nearby than to run a driver far away
from the worker nodes.
























"""
