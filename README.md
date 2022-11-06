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
![](https://github.com/Antonio-Borges-Rufino/IoT_Data_Enginer_Streamin/blob/main/Sensor%201.png)
1. A arquitetura de funcionamento está representada na imagem acima.
2. Primeiro, os sensores se comunicarão diretamente com o Kafka através do protocolo de ioT MQTT.
3. O kafka é um sistema de mensageria baseado em key:value, para o nosso projeto, a key será estruturada como ano-mes-dia-hora-sensor1/sensor2, enquanto o value vai ser o valor da temperatura registrada em kelvins.
4. Depois que o kafka receber os dados dos sensores, as mensagens vão ser lidas pelo spark strean em tempo real, esse serviço deve ficar rodando no back-end.
5. O spark não vai necessariamente precisar fazer algum tipo de análise nos dados, apesar de que isso pode ser muito bem vindo, pode-se futuramente trabalhar em identificações de anomalias
6. Por fim, o spark deve salvar o registro no banco de dados redis, essa base de dados foi escolhida pois é extremamente rápida e simples, podendo facilmente se utilizada na persistencia de dados em stream.
7. Para facilitar a visualização dos dados, foi construída uma interface gráfica que deve mostrar graficamente e de qualquer máquina com acesso ao redis as informações em tempo real
```
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 /home/hadoop/Spark-GET-MQTT-Kafka-Data.py
``` 
