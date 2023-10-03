import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
# added_by_me - BEGIN
import time
from pyspark.ml.fpm import FPGrowth
from pyspark.sql.functions import concat
from datetime import datetime
from pytz import timezone
####
from pyspark.ml.feature import VectorAssembler
from pyspark.sql.types import * 
from pyspark.sql.functions import *
from pyspark.ml.feature import StringIndexer
from pyspark.ml.feature import MinMaxScaler
# added_by_me - END


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node S3 bucket csv ver2
S3bucketcsvver2_node1686647301429 = glueContext.create_dynamic_frame.from_catalog(
    database="amdb1",
    table_name="fake_pnl_report_2023_05_06_fabricated_csv_gz",
    transformation_ctx="S3bucketcsvver2_node1686647301429",
)

# Script generated for node S3 bucket csv ver1
S3bucketcsvver1_node1 = glueContext.create_dynamic_frame.from_catalog(
    database="amdb1",
    table_name="fake_pnl_report_2023_05_06_csv_gz",
    transformation_ctx="S3bucketcsvver1_node1",
)


# added_by_me - BEGIN
# toDF() : Converts a DynamicFrame to an Apache Spark DataFrame
# (glue to pyspark structure)

pnl_v1 = S3bucketcsvver1_node1.toDF()
pnl_v2 = S3bucketcsvver2_node1686647301429.toDF()


dx = pnl_v1.columns.index('delim')+1
join_cols = pnl_v1.columns[:dx]
assert join_cols[-1] == 'delim'
# renaming some cols:
pnl_v1r = pnl_v1
pnl_v2r = pnl_v2
for c in pnl_v1.columns[dx:]:
    pnl_v1r = pnl_v1r.withColumnRenamed(c,c+"_v1")
    pnl_v2r = pnl_v2r.withColumnRenamed(c,c+"_v2")
# pnl_v1r.show(3): the rightmost columns will have a name _v1
# pnl_v2r.show(3): the rightmost columns will have a name _v2


# In[9]:


use_hash = False
# when True I will have all the left columns duplicated in the join df


# In[10]:


# rerunnable.
# I compute the md5 of the concatenated string with the values of all the joinable colums
if use_hash:
    pnl_v1rh = pnl_v1r.withColumn('hashcolname',md5(concat_ws('#',array(join_cols))))
    pnl_v2rh = pnl_v2r.withColumn('hashcolname',md5(concat_ws('#',array(join_cols))))
else:
    pnl_v1rh = pnl_v1r
    pnl_v2rh = pnl_v2r


# ### building the join table and flagging the differences in the dependent variables
# ### i.e. the columns on the right

# In[11]:


# rerunnable.
if use_hash:
    pnl_v12 =  pnl_v1rh.join(other=pnl_v2rh,on='hashcolname',how='fullouter') # we assumed inner and fullouter will return the same result
else:
    pnl_v12 = pnl_v1rh.join(other=pnl_v2rh,on=join_cols,how='fullouter') # we assumed inner and fullouter will return the same result

pop_rc = pnl_v12.count()
print('pop_rc:',pop_rc)
#pnl_v12.limit(3).toPandas()


# In[12]:


# rerunnable.
pnl_v12b = pnl_v12
for cc in ["uPnL","rPnL","PnL"]:
    print('adding a diff boolean flag for column',cc,'as',cc+"_isdiff")
    pnl_v12b = pnl_v12b.withColumn(cc+"_isdiff", when(pnl_v12b[cc+"_v1"] == pnl_v12b[cc+"_v2"],0).otherwise(1))
    rc = pnl_v12b.filter(pnl_v12b[cc+"_isdiff"]==lit(1)).count()
    print('diff rowcount:',rc,'- min support should be:',rc/pop_rc) 


# In[13]:


# rerunnable.
print("adding a signal: exp_date == report_date - 1")
T_plus_n_watch = -1
pnl_v12bS = pnl_v12b.withColumn("is_exp_date_m1", when(pnl_v12b.exp_date_repdate_diff == lit(T_plus_n_watch),1).otherwise(0))
print('count of diff:',pnl_v12bS.filter(pnl_v12bS["is_exp_date_m1"]==lit(1)).count())


# In[14]:


# rerunnable.
# disposable columns...
pnl_v12bS = pnl_v12bS.drop("trade_date_repdate_diff")
pnl_v12bS = pnl_v12bS.drop("exp_date_repdate_diff")


# ### the table ready for the rule mining: 

# In[15]:


# pnl_v12bS.printSchema()
# pnl_v12bS.columns


# In[16]:


#pnl_v12bS.limit(3).toPandas()


# ## start of rule-mining

# In[17]:


from pyspark.sql.functions import concat


# In[18]:


def get_basket(pnl,rule_antecedent_cols,rule_consequent_col):
    # https://stackoverflow.com/questions/51325092/pyspark-fp-growth-algorithm-raise-valueerrorparams-must-be-either-a-param
    # you cannot have an array in a cell containing 0 multiple times. array items must be unique. so:
    rule_ac = rule_antecedent_cols + rule_consequent_col
    for rulecol in rule_ac:
        # every value in every column in rule_ac is prefixed with its own column name and "=".
        pnl = pnl.withColumn(rulecol, concat(lit(rulecol+"="),col(rulecol)))

    return pnl.select('id',array(rule_ac).alias("items"))


# In[19]:


def get_itempopularity(model,rule_consequent_cols):
    assert len(rule_consequent_cols)==1
    watch_conseq = rule_consequent_cols[0] + "=1" # 'uPnL_diff=1'
    print('watch_conseq:',watch_conseq)
    watch_alias = 'is_conseq_in'
    #colz_alias = 'diff_included_in_C'

    itempopularity = model.freqItemsets
    # ... FutureWarning: Deprecated in 3.0.0. Use SparkSession.builder.getOrCreate() instead
    # ... not under my control

    itempopularity.createOrReplaceTempView("itempopularity")
    # Then Query the temp view
    #print("Top 20")
    dfo = spark.sql("SELECT * FROM itempopularity ORDER BY freq desc")
    #dfo.printSchema()
    dofd=dfo.select('items','freq',size(dfo.items).alias('size'),array_contains(dfo.items, lit(watch_conseq)).alias(watch_alias))
        # ... .where(  # .collect()
    return dofd


# In[20]:


def get_relevantbasketpopularity(ipdf):
    watch_alias = 'is_conseq_in'
    return ipdf.where('size >= 2 and '+ watch_alias) # do not include the baskets with a single item


# In[21]:


def show_assoc(model,display,rule_consequent_cols):
    watch_conseq = rule_consequent_cols[0] + "=1" # 'uPnL_diff=1'
    print('watching conseq:',watch_conseq)
    #watch_alias = 'is_conseq_in'
    colz_alias = 'diff_included_in_C'

    assoc = model.associationRules
    assoc.createOrReplaceTempView("assoc")
    # Then Query the temp view
    df2a = spark.sql("SELECT * FROM assoc ORDER BY confidence desc")
    df2b = df2a.select('antecedent','consequent','confidence','lift','support', \
             size(df2a.antecedent).alias('lenA'),size(df2a.consequent).alias('lenC'), \
             array_contains(df2a.consequent,watch_conseq).alias(colz_alias))
    dofdx2 = df2b.where(colz_alias)
    
    if display == "all,confid desc":
        return df2a
    if display == "all+criteria":
        return df2b
    if display == "top assoc":
        # df2b = show_assoc(model,"all+criteria
        # dofdx2 = df2b.where('lenC==1 and Cisdpnlnz')
        return dofdx2.orderBy(col("lift").desc(),col("lenA").asc())
    if display == "top assoc for csv output":
        dofdx2noa = dofdx2.withColumn("antecedent", concat_ws(",",col("antecedent")))
        dofdx2noa = dofdx2noa.withColumn("consequent", concat_ws(",",col("consequent")))
        return dofdx2noa
            ## dofdx2noa.toPandas().to_csv(fname_v1+".output."+rule_consequent_cols[0]+".assoc.csv")
            # dofdx2noa.coalesce(1).write.option("header",True).mode('overwrite').csv(fname_v1+".assoc.csv")
            # thanks https://stackoverflow.com/questions/43661660/spark-how-to-write-a-single-csv-file-without-folder


# # setting the consequent

# In[22]:


minSupport_ = 0.0012
minConfidence_ = 0.9


# ## consequent 1: rPnL

# In[23]:


# this pandas is now ready for rule-mining.
rule_antecedent_cols = [ "trade_ccy","product","disc_curve","fx_cut","market","PnL_ccy","is_exp_date_m1" ]
rule_consequent_cols = ["rPnL_isdiff"]
#rule_consequent_cols = [ "uPnL_diff"] # , "rPnL_diff"] # , "PnL_diff" ]

# ac = antec and conseq

# goal: to build datafram pnl3 with items column with the fields above


# In[24]:


pnlb = get_basket(pnl_v12bS,rule_antecedent_cols,rule_consequent_cols)
#pnlb.limit(3).toPandas()


# In[25]:


# above are the "market baskets", each with a number of items. Let's mine antecedent/consequent rules.


# In[26]:


# https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.ml.fpm.FPGrowth.html = 3.4.0
# https://spark.apache.org/docs/3.1.1/api/python/reference/api/pyspark.ml.fpm.FPGrowth.html
import time
from pyspark.ml.fpm import FPGrowth
fpGrowth = FPGrowth(itemsCol="items", minSupport=minSupport_, minConfidence=minConfidence_) # minSupport=0.2, minConfidence=0.1
model = fpGrowth.fit(pnlb)

# now you have the model.


# ### by the way - see items' popularity

# In[27]:


epoch_a = time.time()
ipdf = get_itempopularity(model,rule_consequent_cols)
print('df rowcount:',ipdf.count())
epoch_z = time.time()
#print('elapsed:',round(epoch_z - epoch_a,1),'s')
print("elapsed: %.1f s" % (epoch_z - epoch_a))
#ipdf.limit(5).toPandas()    


# ### by the way - see relevant baskets popularity

# In[28]:


dofdx = get_relevantbasketpopularity(ipdf)
#dofdx.limit(10).toPandas()


# In[29]:


if False:
    df2a = show_assoc(model,"all,confid desc",rule_consequent_cols)
    print("Top 20:")
    #df2a.limit(20).toPandas()


# In[30]:


if False:
    df2b = show_assoc(model,"all+criteria",rule_consequent_cols)
    #df2b.limit(20).toPandas()


# ### show antec -> conseq order by lift DESC, len(antecs) ASC

# In[31]:


dofdx2 = show_assoc(model,"top assoc",rule_consequent_cols)
#dofdx2.limit(20).toPandas()


# ### comments:
# - The 2nd implied rule (row 1) is exactly the rule that was applied to introduce fabricated differences.
# - The 1st implied rule (row 0) is a byproduct of rule 2: in our input, trade_ccy=AUDUSD ⇒ PnL_ccy=AUD

# ### saving to csv

# In[32]:


dofdx2o = show_assoc(model,"top assoc for csv output",rule_consequent_cols)
#dofdx2o.toPandas().to_csv(fname_v1+".output.conseq-"+rule_consequent_cols[0]+".assoc.csv")


from awsglue.dynamicframe import DynamicFrame
#Converts a DataFrame to a DynamicFrame
# (pyspark to glue structure)
Join_node1686647385380 = DynamicFrame.fromDF(dofdx2o,glueContext,"Join_node1686647385380").repartition(1)

# added_by_me - END


# Script generated for node S3 bucket
S3bucket_node3 = glueContext.write_dynamic_frame.from_options(
    frame=Join_node1686647385380,
    connection_type="s3",
    format="csv",
    connection_options={
        "path": "s3://am1misc/pyspark/",
        "compression": "gzip",
        "partitionKeys": [],
    },
    transformation_ctx="S3bucket_node3",
)

job.commit()
