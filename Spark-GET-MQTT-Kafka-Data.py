#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from pyspark.sql import SparkSession
import redis


spark = SparkSession
spark = spark.builder
spark = spark.appName("teste")
spark = spark.getOrCreate()

spark.sparkContext.setLogLevel("OFF")

kafka_df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("subscribe", "data_sensor").option("maxFilesPerTrigger",1).load()
      
def func_call(df,batch_id):
  df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
  requests = df.rdd.map(lambda x: x.value).collect()
  print(requests)
  
class RowPrinter:
    def open(self, partition_id, epoch_id):
        #print("Opened %d, %d" % (partition_id, epoch_id))
        return True
    def process(self, row):
        #redis.set(row.value.decode('UTF-8'),str(row.timestamp))
        try:
            redis_insert = redis.Redis('localhost',port=6379)
            key = row.key.decode('UTF-8')
            value = row.value.decode('UTF-8')
            redis_insert.set(key,value)
            print("Dados inseridos: key {} Value {}".format(key,value))
        except:
            print("Erro")
    def close(self, error):
        print("Closed with error: %s" % str(error))
        #query.stop()

query = kafka_df.writeStream.format("kafka").option("checkpointLocation","/tmp/spark").foreach(RowPrinter()).trigger(processingTime="15 seconds").start().awaitTermination()

