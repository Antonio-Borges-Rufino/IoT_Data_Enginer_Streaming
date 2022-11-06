# Big Data Cluster
1. A estrutura de big data usada nesse trabalho está totalmente descrita [aqui](https://github.com/Antonio-Borges-Rufino/Hadoop_Ecosystem)
2. Assume-se que para repodução das tarefas, usa-se um cluster igual ou similar a esse apresentado

# Detalhes do projeto
1. O monitoramento de recursos ambientais se tornaram uma importante ferramente nos ultimos anos, muito disso se deu por causa do crescente interesse das autoridades de monitorar seus ecossistemas. Sabendo da importancia que esse tipo de pesquisa tem, uma ONG chamada rios vivos (Nome teórico) decidiu monitorar a temperatura da superficie de pontos específicos do rio amazonas. A temperatura da água é um importante indicador de processos oceânicos, e vital para o ecossistema marinho.
2. Para realizar esse trabalho, pensou-se na sequinte estrutura  
  -> 1. Colocar sensores de temperatura em lugares estratégicos   
  -> 2. Coletar dados dos sensores em um espaço de tempo de 1 hora  
  -> 3. Guardar esse dados em uma base de dados de fácil acesso  
  -> 4. Apresentar os dados de forma interativa através de uma interface gráfica
3. Levando em consideração as especificações do projeto, decidiu-se usar um sistema big data de stream.

# Arquitetura do projeto
```
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 /home/hadoop/Spark-GET-MQTT-Kafka-Data.py
``` 
