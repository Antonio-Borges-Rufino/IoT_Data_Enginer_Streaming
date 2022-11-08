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
4. As imagens de satélite são de estrutura temporais diárias, portanto, teoricamente não teríamos como extrair em horas, como o sensor deve fornecer. Para contornar esse problema, foi baixada imagens diárias entre os anos de 2003 e 2013. Para extrair os pontos do mapa, usou-se apenas as 2 primeiras casas decimais após a vírgula, para poder ficar em conformância com a resolução do satélite e cada imagem representa uma hora do dia, de forma linear.
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
  -> É passado como parâmetro o nome do arquivo, a construção do nome vai ser explicado mais adiante.  
  -> Depois, usa-se o nome do arquivo dentro do link de download, optei por colocar em uma variável separada para poder ficar mais organizado.  
  -> A função subprocess.rum é quem realiza comandos do terminal no python, ela quem vai baixar a imagem rastel do satélite.  
  -> xr.open_dataset é uma função de uma biblioteca responsável por fazer varreduras e extrações em imagens rastel, nela, pode-se trabalhar a maioria dos formatos, como NetCDF, NetCDF4 dentre outras.  
  -> As linhas sesor1 e sensor2 são responsaveis por extrair as informações dos metadados das imagens, nesse caso,usa-se a função sel da biblioteca xarray para extrair a temperatura das coordenadas passadas nos parametros lat e lon.  


```
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 /home/hadoop/Spark-GET-MQTT-Kafka-Data.py
``` 
