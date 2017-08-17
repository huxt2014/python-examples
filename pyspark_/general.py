

from pyspark import SparkContext, SparkConf


config = SparkConf().setAppName('localTest').setMaster("local")
sc = SparkContext(conf=config)

###############################################################################
#                               RDD creation
#    There are two ways to create RDDs: parallelizing an existing collection in
# your driver program, or referencing a dataset in an external storage system,
# such as a shared filesystem, HDFS, HBase, or any data source offering a Hadoop
# InputFormat.
#     One important parameter for parallel collections is the number of
# partitions to cut the dataset into. Spark will run one task for each partition
# of the cluster.
#     If using a path on the local filesystem, the file must also be accessible
# at the same path on worker nodes. Either copy the file to all workers or use a
# network-mounted shared file system.

# $ PYSPARK_DRIVER_PYTHON=ipython ./bin/pyspark --master local
###############################################################################

# parallelize collections #####################################
disData = sc.parallelize([1, 2, 3, 4])
dis_kv = sc.parallelize([('a', 1), ('b', 1)])

# text file, either local path, or hdfs://, s3n://, etc URI
disFile = sc.textFile("README.md")

# SequenceFile
rdd = sc.parallelize(range(1, 4)).map(lambda x: (x, "a"*x))
rdd.saveAsSequenceFile("seq_file")
sorted(sc.sequenceFile("seq_file").collect())


###############################################################################
#                                RDD operation
#     RDDs support two types of operations: transformations(create a new
# dataset) and actions(return a value to the driver program).
#     All transformations in Spark are lazy, and are only computed when an
# action requires.
#     By default, each transformed RDD may be recomputed each time you run an
# action on it. However, you may also persist an RDD in memory, disk or
# replicated across multiple nodes.
###############################################################################

lines = sc.textFile("README.md")


def map_p(iter_object):
    words_per_partition = []
    for line in iter_object:
        words_per_partition += line.strip().split(" ")
    return words_per_partition

# transformation #############################################
# simple transformation
line_length = lines.map(lambda s: len(s))                # one by one map
words = lines.flatMap(lambda s: s.strip().split(' '))    # one to many map
words = words.filter(lambda w: w != "")                  # filter

# pseudo set operation
distinct_words = words.distinct()

# key-value pair(tuple) operation
word_kv = words.map(lambda w: (w, 1))                    # key-value pair
word_count = word_kv.reduceByKey(lambda a, b: a+b)

# the function is called for each partition
words = lines.mapPartitions(map_p)

# actions ####################################################
# the function should be commutative and associative
line_length.reduce(lambda a, b: a+b)
# return all the element as an array to the driver
line_length.collect()
line_length.count()
line_length.first()
line_length.take(10)         # bring a subset of the RDD to the driver


###############################################################################
#                                passing function
#     Spark’s API relies heavily on passing functions in the driver program to
# run on the cluster.
#     For closure, the global variables refered by function will be copied to
# each executor. Change these variables in the executor has no effect on the
# driver's variable. To update a variable in the driver, use Accumulator.
###############################################################################





