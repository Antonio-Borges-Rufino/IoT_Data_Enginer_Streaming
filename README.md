# Big Data Cluster
1. A estrutura de big data usada nesse trabalho está totalmente descrita [aqui](https://github.com/Antonio-Borges-Rufino/Hadoop_Ecosystem).
2. Assume-se que para repodução das tarefas, usa-se um cluster igual ou similar a esse apresentado.

# Detalhes do projeto
1. O monitoramento de recursos ambientais se tornaram uma importante ferramente nos ultimos anos, muito disso se deu por causa do crescente interesse das autoridades de monitorar seus ecossistemas. Sabendo da importancia que esse tipo de pesquisa tem, uma ONG chamada rios vivos (Nome teórico) decidiu monitorar a temperatura da superficie de pontos específicos do rio amazonas. A temperatura da água é um importante indicador de processos oceânicos, e vital para o ecossistema marinho.
2. Para realizar esse trabalho, pensou-se na sequinte estrutura.  
  -> 1. Colocar sensores de temperatura em lugares estratégicos.   
  -> 2. Coletar dados dos sensores em um espaço de tempo de 1 hora.  
  -> 3. Guardar esse dados em uma base de dados de fácil acesso.  
  -> 4. Apresentar os dados de forma interativa através de uma interface gráfica.
3. Levando em consideração as especificações do projeto, decidiu-se usar um sistema big data de stream.

# Arquitetura do projeto
![](https://github.com/Antonio-Borges-Rufino/IoT_Data_Enginer_Streamin/blob/main/Sensor%201.png)
1. A arquitetura de funcionamento está representada na imagem acima.
2. Primeiro, os sensores se comunicarão diretamente com o Kafka através do protocolo de ioT MQTT.
3. O kafka é um sistema de mensageria baseado em key:value, para o nosso projeto, a key será estruturada como ano-mes-dia-hora-sensor1/sensor2, enquanto o value vai ser o valor da temperatura registrada em kelvins.
4. Depois que o kafka receber os dados dos sensores, as mensagens vão ser lidas pelo spark strean em tempo real, esse serviço deve ficar rodando no back-end.
5. O spark não vai necessariamente precisar fazer algum tipo de análise nos dados, apesar de que isso pode ser muito bem vindo, pode-se futuramente trabalhar em identificações de anomalias.
6. Por fim, o spark deve salvar o registro no banco de dados redis, essa base de dados foi escolhida pois é extremamente rápida e simples, podendo facilmente se utilizada na persistencia de dados em stream.
7. Para facilitar a visualização dos dados, foi construída uma interface gráfica que deve mostrar graficamente e de qualquer máquina com acesso ao redis as informações em tempo real.

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
1. 

```
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 /home/hadoop/Spark-GET-MQTT-Kafka-Data.py
``` 
