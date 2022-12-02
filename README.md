# Big Data Cluster
1. A estrutura de big data usada nesse trabalho está totalmente descrita [aqui](https://github.com/Antonio-Borges-Rufino/Hadoop_Ecosystem).
2. Assume-se que para repodução das tarefas, usa-se um cluster igual ou similar a esse apresentado.

# Detalhes do projeto
1. O monitoramento de recursos ambientais se tornou uma importante ferramenta nos últimos anos, muito disso se deu por causa do crescente interesse das autoridades de monitorar seus ecossistemas. Sabendo da importância que esse tipo de pesquisa tem, uma ONG chamada rios vivos (Nome teórico) decidiu monitorar a temperatura da superficie de pontos específicos do rio amazonas. A temperatura da água é um importante indicador de processos oceânicos, e vital para o ecossistema marinho.
2. Para realizar esse trabalho, pensou-se na sequinte estrutura.  
  -> 1. Colocar sensores de temperatura em lugares estratégicos.   
  -> 2. Coletar dados dos sensores em um espaço de tempo de 1 hora.  
  -> 3. Guardar esse dados em uma base de dados de fácil acesso.  
  -> 4. Construir uma api para acesso dos dados de forma fácil.
3. Levando em consideração as especificações do projeto, decidiu-se usar um sistema big data de stream.

# Arquitetura do projeto
![](https://github.com/Antonio-Borges-Rufino/IoT_Data_Enginer_Streamin/blob/main/Sensor%201.png)
1. A arquitetura de funcionamento está representada na imagem acima.
2. Primeiro, os sensores se comunicarão diretamente com o Kafka através do protocolo de ioT MQTT.
3. O kafka é um sistema de mensageria baseado em key:value, para o nosso projeto, a key será estruturada como ano-mes-dia-hora-sensor1/sensor2, enquanto o value vai ser o valor da temperatura registrada em kelvins.
4. Depois que o kafka receber os dados dos sensores, as mensagens vão ser lidas pelo spark strean em tempo real, esse serviço deve ficar rodando no back-end.
5. O spark não vai necessariamente precisar fazer algum tipo de análise nos dados, apesar de que isso pode ser muito bem vindo, pode-se futuramente trabalhar em identificações de anomalias.
6. Por fim, o spark deve salvar o registro no banco de dados redis, essa base de dados foi escolhida pois é extremamente rápida e simples, podendo facilmente se utilizada na persistencia de dados em stream.
7. Para facilitar o acesso aos dados, foi contruida uma apiRest para acessar os dados do redis.

# Obtendo os dados e o problema do MQTT
![](https://github.com/Antonio-Borges-Rufino/IoT_Data_Enginer_Streamin/blob/main/SENSOR%201.PNG)
1. Apesar do projeto ser baseado em uma conversa intermediada entre os sensores e o kafka pelo MQTT, na prática isso é dificil de fazer se voce não tem os sensores nem um serviço MQTT online.
2. Para contornar esse problema, simulei a parte do sensor+MQTT-Broker através de um código python.
3. Para não sair muito da idéia, extrai informações reais de temperatura das localizações mostrada na imagem acima, portanto, admiti-se que esses são os sensores e que os dados retirados de temperatura são os dados fornecidos.
4. As imagens de satélite são de estrutura temporais diárias, portanto, teoricamente não teríamos como extrair em horas, como o sensor deve fornecer. Para contornar esse problema, foi baixada imagens diárias entre os anos de 2003 e 2010. Para extrair os pontos do mapa, usou-se apenas as 2 primeiras casas decimais após a vírgula, para poder ficar em conformância com a resolução do satélite e cada imagem representa uma hora do dia, de forma linear.
5. A função que faz o download da imagem e a extração dos pontos é descrita abaixo.
```
def get_data(nome):
  link="https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MUR-JPL-L4-GLOB-v4.1/"+nome+"090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc"
  subprocess.run(["wget",'-c','-O'+nome,'--user=XXXXXXX','--password=XXXXX',link]) 
  temp = xr.open_dataset("/content/"+nome)
  sensor1 = temp.sel(lat=-2.90,lon=-60.56).analysed_sst.data[0]
  sensor2 = temp.sel(lat=-2.50,lon=-55.00).analysed_sst.data[0]
  return [[-2.90,-60.56,sensor1],[-2.50,-55.00,sensor2]]
```
6. Explicação do código:  
  -> 1. É passado como parâmetro o nome do arquivo, a construção do nome vai ser explicado mais adiante.  
  -> 2. Depois, usa-se o nome do arquivo dentro do link de download, optei por colocar em uma variável separada para poder ficar mais organizado.  
  -> 3. A função subprocess.rum é quem realiza comandos do terminal no python, ela quem vai baixar a imagem rastel do satélite.  
  -> 4. xr.open_dataset é uma função de uma biblioteca responsável por fazer varreduras e extrações em imagens rastel, nela, pode-se trabalhar a maioria dos formatos,         como NetCDF, NetCDF4 dentre outras.  
  -> 5. As linhas sesor1 e sensor2 são responsaveis por extrair as informações dos metadados das imagens, nesse caso,usa-se a função sel da biblioteca xarray para extrair a temperatura das coordenadas passadas nos parametros lat e lon.    
7. O código abaixo representa como foi feito o download das imagens e a suas respectivas extrações. Apesar de poder deixar um looping de ano, possuia limitações de tempo, então para deixar menos dificultoso meu trabalho, coloquei o ano como uma variavel setavel. 
```
ano_i = 2010
for mes in range(1,13):
  data = list()
  for dia in range(1,32):
    if dia < 10:
      dia_ = '0'+str(dia)
    else:
      dia_ = str(dia)
    if mes < 10:
      mes_ = '0'+str(mes)
    else:
      mes_ = str(mes)
    nome = str(ano_i)+str(mes_)+str(dia_)
    try:
      dados = get_data(nome)
      data.append(dados[0])
      data.append(dados[1])
      subprocess.run(['rm','/content/'+nome])
    except:
      print("Erro do dia: {}".format(dia))
  data = pd.DataFrame(data,columns=['Lat','Lon','Temp'])  
  nome = str(ano_i)+str(mes)+".csv"
  data.to_csv(nome)
```  
8. Explicação do código  
  -> 1. A variavel ano_i vai receber o ano que a imagem pertence.  
  -> 2. O primei laço for é respectivo aos meses do ano.  
  -> 3. a variavel data vai receber as informações dos 2 pontos para cada dia do mes.  
  -> 4. A extração dos pontos é feita dentro do laço dia,que é respectivo para cada dia. Aqui, eu faço uma verificação simples para adicionar 0 ao nome, pois a formatação do link das imagens exige um 0 a esquerda de todo numero menor que 10.  
  -> 5. O nome é a junção do ano+mes+dia no link de download explicado anteriormente, por exemplo, 01/10/2010 == 01102010.  
  -> 6. o próximo passo é fazer o donwload e a extração dos pontos a partir da função get_data já explicada, e colocando dentro da variavel data (para o mes todo).  
  -> 7. Depois que todos os meses foram baixados, transformo a variavel data em um dataframe pandas e salvo apenas com o nome ano+mes.csv, esses dados vão ser unidos logo a frente.  
9. Após a obtenção de todos os dataset mensais de cada ano, todos os arquivos foram zipados juntos para facilitar a manipulação dos datasets.
10. Com os dataset zipados juntos, coloquei eles no google colab para poder fazer o ultimo processamento dessa fase, que é a criação de um superdataset.
11. Para deszipar, usei o seguinte comando:
```
!unzip data.zip
```
12. com todos os dataset prontos, o seguinte código foi executado:
```
df_final = pd.DataFrame(data=None,columns=['Lat','Lon','Temp'])
for ano in [2003,2004,2005,2006,2007,2008,2009,2010]:
  for mes in range(1,13):
    arq = "/content/data/"+str(ano)+str(mes)+".csv"
    df = pd.read_csv(arq,usecols=['Lat','Lon','Temp'])
    df_final = pd.concat([df_final,df])
df_final = df_final.reset_index()
df_final.to_csv("sensor_data.csv")
```
13. Explicação do código:  
  -> 1. A variavel df_final recebe um dataframe pandas vazio com as colunas Lat, Lon e Temp. Essas colunas são referentes a latitude, longitude e temperatura.  
  -> 2. O laço for vai percorrer todos os anos baixados e o segundo laço todos os meses de cada ano.  
  -> 3. Como a estrutura dos dataset são ano+mes, basta acessar cada um dos dataset gerados a partir de str(ano)+str(mes)+'.csv' em uma nova variavel e depois concatenar com a variavel df_final, que deve receber todos os dataframes.  
  -> 4. Após a concatenação, resetei os indexs para que não fique confuso e salvei o novo dataframe.  
14. O código completo pode ser acessado [aqui](https://github.com/Antonio-Borges-Rufino/IoT_Data_Enginer_Streamin/blob/main/Get_Data_Sensor.ipynb).
15. Os dados zipados podem ser acessados [aqui](https://github.com/Antonio-Borges-Rufino/IoT_Data_Enginer_Streamin/blob/main/data.zip), enquanto os dados únicos em um único DF podem ser acessados [aqui](https://github.com/Antonio-Borges-Rufino/IoT_Data_Enginer_Streamin/blob/main/sensor_data.csv)

# Simulando o sensor + MQTT Broker
1. Dada a dificuldade de usar um broker MQTT externo, decidi apenas simular uma conversa entre o kafka e o broker, para poder inserir no kafka os dados usei a biblioteca KafkaProducer do python.
2. O código foi executado pelo jupyter notebook do ambiente virtual do cluster, para mais informações, acesso o cluster base proposto no início do projeto.
3. O código foi dividido em 2 partes, uma foi para teste, a outra era para simular uma operação real de 1 hora, a que vai ser descrita é a de teste, que envia uma mensagem para o kafka de 5 em 5 segundos.
4. Código do simulador:
```
producer = KafkaProducer(bootstrap_servers='localhost:9092')
df = pd.read_csv("/home/hadoop/sensor_data.csv",usecols=['Lat','Lon','Temp'])
ano = 2022
mes = [0,1,2,3,4,5,6,7,8,9,10,11]
dias = [31,28,31,30,31,30,31,31,30,31,30,31]
dataset_posix = 0
while True:
    for mes_ in mes:
        for dia in range(1,dias[mes_]+1):
            for hora in range(0,24):
                if dataset_posix%2 == 0:
                    key_ = str(ano)+"-"+str(mes_+1)+"-"+str(dia)+"-"+str(hora)+"-"+"sensor1"
                    key_ = key_.encode(encoding='utf-8')
                    sensor = df.iloc[dataset_posix]
                    sensor = str(sensor[2])
                    value_ = sensor.encode(encoding='utf-8')
                    producer.send('data_sensor', key=key_, value=value_)
                    dataset_posix = dataset_posix + 1
                    if dataset_posix >= len(df):
                        dataset_posix = 0
                else:
                    key_ = str(ano)+"-"+str(mes_+1)+"-"+str(dia)+"-"+str(hora)+"-"+"sensor2"
                    key_ = key_.encode(encoding='utf-8')
                    sensor = df.iloc[dataset_posix]
                    sensor = str(sensor[2])
                    value_ = sensor.encode(encoding='utf-8')
                    producer.send('data_sensor', key=key_, value=value_)
                    dataset_posix = dataset_posix + 1
                    if dataset_posix >= len(df):
                        dataset_posix = 0
                sleep(5)            
    ano = ano + 1
```  
5. Explicando o código:  
  -> 1. A variavel producer recebe o objeto de conexão com o kafka e a variavel df recebe o dataset feito no passo anterior.  
  -> 2. As variaveis ano, mes e dia serão usadas para a key do kafka, por isso elas constroem os laços.  
  -> 3. O laço while True realiza o stream pro kafka, ela so para de enviar informação quando explicitado pelo usuário, no nosso caso, parando a célula.  
  -> 4. Existem 3 laços temporais, que vão servir para a construção da key, que deve ser ano-mes-dia-hora-sensor, nesse caso, a variavel ano é estática.  
  -> 5. A variavel dataset_posix é a variavel que vai controlar o percurso dentro do pandas dtaframe, inclusive, ela vai ser resetada quando a quantidade total de linhas do dataset for usada, fazendo que volte a linha 0 de novo.  
  -> 6. A verificação feita é so para distinguir qual sensor está mandando a mensagem, caso seja uma posição par é o sensor1, e impar é o sensor2.  
  -> 7. Dentro da verificação, cria a key do kafka, já mostrada, depois codifica para byte, que é o padrão aceito pelo kafka.  
  -> 8. A variavel sensor traz as informações do dataset presentes na linha que dataset_posix está apontando através da função iloc.  
  -> 9. Como a informação vem com todas as tabelas, extrai-se apenas a coluna referente ao valor de temperatura, já que sabemos a lat e lon do sensor que vai mandar a informação.  
  -> 10. Depois transforma o dado em byte também e envia a mensagem para o kafka através da função send.     
  -> 11. No kafka, o tópico data_sensor vai receber a informção,sendo ela, qual sensor enviou a mensagem, em que momento do tempo isso foi enviado e qual a informação que foi enviada (temperatura).  
  -> 12. A mesma coisa é feita no else, mudando apenas o sensor.  
  -> 13. Depois de rodar o código e enviar a mensagem, o programa descansa 5 segundos com o método sleep() e depois refaz tudo de novo até ser explicitamente parado pelo usuário.  
6. Outro código com sleep maior e uma formatação diferente pode ser encontrado junto desse explicado [aqui](https://github.com/Antonio-Borges-Rufino/IoT_Data_Enginer_Streamin/blob/main/Sensor-MQTT-Insert-Kafka.ipynb).

# Spark streaming capturando dados do kafka e persistindo no redis
1. O código do cliente spark foi feito totalmente em python e deve ser executando usando o spark-submit.
2. Aqui, o programa python vai ficar buscando novas mensagens do kafka de 15 em 15 segundos, como o insert no kafka se dá em tempos de 5 segundos, vai aparecer no terminal 3 linhas por vez, mas mesmo assim vai inserir normalmente no banco.
3. O código abaixo cria o spark session para o projeto:
```
spark = SparkSession
spark = spark.builder
spark = spark.appName("teste")
spark = spark.getOrCreate()

spark.sparkContext.setLogLevel("OFF")
```
4. Foi retirado o log do spark no código acima, pois dificulta a visualização do que o programa está fazendo.
5. Depois, chama-se a leitura em stream do kafka utilizando o readStream do spark:
```
kafka_df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("subscribe", "data_sensor").option("maxFilesPerTrigger",1).load()
```
6. Explicando o código:  
  -> 1. Kafka é passado como modo de leitura do spark, depois em option, é passado a porta onde vai se escutar o servidor kafka.  
  -> 2. Em subscribe, colocamos o tópico que queremos obter as mensagens, finalizando colocando uma quantidade de leitura de registros em 1, ou seja, cada registro vai ser lido individualmente.  
7. Após isso, começamos efetivamente a ler os dados que chegam do serviço de mensageria, utilizando:
```
query = kafka_df.writeStream.format("kafka").option("checkpointLocation","/tmp/spark").foreach(RowPrinter()).trigger(processingTime="15 seconds").start().awaitTermination()
```
8. Explicando o código:  
  -> 1. A função writeStream.format indica qual o tipo de leitura que o spark deve ter. Por não ser padrão do spark, o tipo kafka deve ser passado como parametro na execução do código, isso vai ser demonstrado mais adiante.  
  -> 2. A função checkpointLocation mostra a pasta temporaria do hdfs.  
  -> 3. A função foreach() vai executar uma classe, que nesse caso é RowPrinter(), e nessa classe vão ser passadas as informações de cada que o spark le do kafka conforme o parâmetro maxFilesPerTrigger. E nessa classe também que vão ser feitos os processamentos dos dados.  
  -> 4. A função processingTime determina em segundos a quantidade de tempo que o spark vai contatar o kafka sobre novas mensagens.  
  -> 5. A função awaitTermination faz com que o código só seja parado caso isso aconteça explicitamente pelo usuário usando o cntrl+c ou através de alguma condição de parada imposta na classe RowPrinter que implemente a função query.stop(). 
9. A classe que é passada como parâmetro possui um ciclo de vida bem estabelecido, e é de extrema importancia para poder fazer a manutenção dos dados em ambientes que você não pode fazer execuções em paralelo, como é o caso do databricks. A classe é descrita melhor abaixo:
```
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
```
10. Explicando o código:  
  -> 1. A classe precisa implementar obrigatóriamente 3 métodos, são eles; o open, o process e o close.  
  -> 2. O método open é o primeiro a ser chamado, ele da informações de qual linha está sendo pega dentro da pilha. O método process é quem efetivamente vai fazer a manutenção dos dados, no nosso caso, usei dentro de um bloco try except a inserção das linhas no banco redis através da função redis. É importante observar que redis.Redis precisa ser instanciado toda vez, pois a classe principal também precisa ser sempre instanciada.  
  -> 3. Ainda em process, é descodificada a key e o value, que são entregues no formato byte e inseridas diretamente no banco redis utilizando a função insert.  
  -> 4. Finalizando com o método close, que tem a função de apresentar algum erro caso exista, ou alguma mensagem de término de processamento.  
11. Com o código finalizado, basta salvar e executar dentro do yarn utilizando o spark-submit:  
```
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 /home/hadoop/Spark-GET-MQTT-Kafka-Data.py
``` 
12. Percebe-se a utilização da tag --packages, é ela quem indica o jar do tipo kafka. Esse jar não é nativo, portanto deve-se usar o apontador, e após a indicação do jar, coloca o caminho do arquivo python com o código pyspark e executa.
13. O código vai ficar esperando até que o código de insert no kafka seja executado também.
14. Para ver a construção completa do código, acesse [aqui](https://github.com/Antonio-Borges-Rufino/IoT_Data_Enginer_Streamin/blob/main/Spark-GET-MQTT-Kafka-Data.py).

# Api de acesso
1. Para a construção da API de acesso aos dados, usou-se a biblioteca flask do python.
2. A estrutura de acesso deve ser o link de acesso, que nesse caso é o servidor local 127.0.0.1/{ano}-{mes}-{dia}-{hora}.
3. Todos os períodes menores que 10 não devem ter o 0 na frente, por exemplo: 127.0.0.1/2022-1-1-22. Para maiores que 10 ou igual é normal.
4. A saída deve ser um json com os dados de ambos os sensores. No caso, sempre um sensor vai receber Null por causa da estrutura de inserção dos dados.
5. O código da função get está descrito abaixo:
```
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
```
6. Explicando o código:  
  -> 1. A classe TodoSimple(Resource) vai receber os links de acesso e a função get recebe os dados que vem do link.  
  -> 2. A variavel get_data recebe a conexão com o redis, e as variaveis inform e inform_ recebem as strings de busca, acrescentando apenas qual o sensor deve ser buscado.  
  -> 3. A variavel sensor1 é quem recebe o resultado do banco, e também é feita uma verificação para saber se foi retornado algum resultado. Essa verificação é necessária para que não de erro na hora de retornar o JSON.  
  -> 4. A variavel sensor2 passa pelo exato mesmo processo da variavel sensor1.  
  -> 5. Após isso, o servidor retorna a informação através de um JSON que é exibido na tela, como acontece em apisRest.  
7. Depois da classe ser construida, instancia-se ela dentro do servidor utilizando:
```
api.add_resource(TodoSimple, '/<string:key>')
```
8. Para ligar o servidor, utilize o comando abaixo dentro do ambiente virtual projetos:
```
python3 /home/hadoop/API-Redis-Get-Data.py
```
9. Todo o código da API está disponível [aqui](https://github.com/Antonio-Borges-Rufino/IoT_Data_Enginer_Streamin/blob/main/API-Redis-Get-Data.py)
