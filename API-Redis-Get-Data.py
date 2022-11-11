#!/usr/bin/env python
# coding: utf-8

# In[3]:


from flask import Flask, request
from flask_restful import Resource, Api
import redis

app = Flask(__name__)
api = Api(app)

class TodoSimple(Resource):
    def get(self, key):
      get_data = redis.Redis('localhost',port=6379)
      inform = str(key)+'-sensor1'
      inform_ = str(key)+'-sensor2'
      sensor1 = get_data.get(inform)
      if sensor1 == None:
        sensor1 = "None"
      else:
        sensor1 = sensor1.decode('UTF-8')
        sensor1 = str(sensor1)
      sensor2 = get_data.get(inform_)
      if sensor2 == None:
        sensor2 = "None"
      else:
        sensor2 = sensor2.decode('UTF-8')
        sensor2 = str(sensor2)
      return {"sensor1":sensor1,"sensor2":sensor2}

api.add_resource(TodoSimple, '/<string:key>')

if __name__ == '__main__':
    app.run(debug=True)


# In[ ]:




