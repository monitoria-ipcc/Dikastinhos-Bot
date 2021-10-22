#  Basic Dependences
import os
import json
import pytz
import discord
import requests
from random import choice
from datetime import datetime
from discord.ext import tasks
from keep_alive import keep_alive
#  Translator
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ApiException
#  Weebhook
from discord_webhook import DiscordWebhook


name_server = "CIn - Introdução à Programação - 2021.1"
client = discord.Client()

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return translate(quote)

def translate(message):
  try:
    autenticator = IAMAuthenticator(os.environ['TRAD'])
    version = '2019-04-04'  # last update
    url_api = os.environ['URL_API_TRAD']
    
    language_translator = LanguageTranslatorV3(
                            version=f'{version}',
                            authenticator=autenticator)
    #language_translator.set_disable_ssl_verification(True)
    language_translator.set_service_url(url_api)

    translation = language_translator.translate(
                    text=message,
                    model_id='en-pt').get_result()
    translation = translation["translations"][0]["translation"]
    return translation

  except ApiException as err:
    return "Method failed with status code " + str(err.code) + ": " + err.message

def get_joke():
  response = requests.get("https://icanhazdadjoke.com/")
  data = response.text.split('<p class="subtitle">')
  joke = data[1].split("</p>")[0]
  return translate(joke)

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  current_time.start()

@tasks.loop(minutes=1)
async def current_time():
  #  Datetime Server
  local_tz = pytz.timezone('America/Recife')
  now = datetime.now().replace(tzinfo=pytz.utc).astimezone(local_tz)
  now = local_tz.normalize(now).strftime("%Y-%m-%d -> %H-%M")
  #  Datetime List
  new_list_date = "2021-10-22 -> 09-53"
  #  Mensage to New List
  image = discord.Embed()
  url = "https://imgur.com/aO8i4cd.png"
  image.set_image(url=url)
  students = [x for x in client.guilds if x.name == name_server][0]
  students = [x for x in students.roles if x.name == "Alunos"][0]
  response = f"{students.mention}, A lista de Laços de Repetição encerrou, espero que tenham conseguido ^-^! e como sempre:\n**Lista nova liberada!** :kissing_closed_eyes: (desde hoje cedo né kk)\nAssunto da lista: **Funções**"
  #  Send Mensage in the some datetime
  if now == new_list_date:
    channel = client.get_channel(889472152951218211)
    await channel.send(response, embed=image)

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  if msg.startswith('+help'):
    msgm = "> Sobre :grin::\n`Olá eu sou o Dikastinhos, um bot criado pela Monitoria de IP do CIn, para deixar a comunicação um pouco mais distraída.`\n\n> Comandos :robot::\n`+monitor` : Chama um monitor para tirar dúvidas relacionadas ás listas.\n`+professor` : Chama um professor para tirar dúvidas relacionadas a matrícula, disciplina e tals.\n`+piada` : O Dikastinho está tentando ser piadista, mas ler suas piadas é pôr sua consciência em risco.\n`+frase`: Frases de Pessoas famosas, para se inspirar a terminar a lista!\n`+faustão`: Sim! Ele mesmo! O maior ídolo do dikastinho kkkk"
    await message.channel.send(content=msgm)

  if msg.startswith('+monitor'):
    image = discord.Embed()
    url = "https://cdn.discordapp.com/attachments/846908305887985674/849397984688865319/bd9ad862-ab23-45c6-92b4-d51b1e0d9079.webp"
    image.set_image(url=url)
    monitores = discord.utils.get(message.guild.roles, name="Monitores")
    await message.channel.send(content=f"Procurando {monitores.mention}!!! {message.author.mention} precisa de ajuda :laughing:", embed=image)

  if msg.startswith('+professor'):
    teacher = discord.utils.get(message.guild.roles, name="Professores")
    msgm = f"Procurando {teacher.mention}. {message.author.mention} precisa de ajuda :laughing:"
    await message.channel.send(msgm)

  if msg.startswith('+piada'):
    joke = get_joke()
    await message.channel.send(joke)

  if msg.startswith('+frase'):
    quote = get_quote()
    await message.channel.send(quote)

  if msg.startswith('+faustão'):
    content = choice(open("fhrases_fausto.txt", 'r').read().split("\n")) 
    webhook = DiscordWebhook(url=os.environ['WebHook_URL'], username="Faustão", content=content)
    webhook.execute()

keep_alive()
client.run(os.environ['TOKEN'])
