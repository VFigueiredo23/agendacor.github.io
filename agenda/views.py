from django.shortcuts import render
import requests
from datetime import datetime, timedelta
import pytz

#chave de API google 

GOOGLE_API_KEY = 'AIzaSyCdspxqHtO2x7vK_Satf9NWbGry1OyvCFA'
GOOGLE_CALENDAR_ID = 'contato@cor.rio'

def listar_eventos(request):
    url = f"https://www.googleapis.com/calendar/v3/calendars/{GOOGLE_CALENDAR_ID}/events"
    params = {
        'key': GOOGLE_API_KEY,
        'timeMin': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z',
        'singleEvents': True,
        'orderBy': 'startTime'
    }
    response = requests.get(url, params=params)
    dados = response.json()
    eventos_br = []

    fuso = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso)

    for item in dados.get('items', []):
        titulo = item.get('summary', 'Sem título')
        descricao = item.get('description', '')
        local = item.get('location', 'Não informado')
        inicio = item.get('start', {}).get('dateTime') or item.get('start', {}).get('date')
        fim = item.get('end', {}).get('dateTime') or item.get('end', {}).get('date')

        if 'T' in inicio:
            inicio_dt = datetime.fromisoformat(inicio.replace('Z', '+00:00')).astimezone(fuso)
            fim_dt = datetime.fromisoformat(fim.replace('Z', '+00:00')).astimezone(fuso)

            if inicio_dt.date() != agora.date():
                continue

            inicio_formatado = inicio_dt.strftime('%H:%M')
            fim_formatado = fim_dt.strftime('%H:%M')

            if agora > fim_dt:
                status = 'Finalizada'
            elif inicio_dt <= agora <= fim_dt:
                status = 'Em andamento'
            elif 0 <= (inicio_dt - agora).total_seconds() <= 600:
                status = 'Em breve'
            else:
                status = 'Agendada'
        else:
            data_evento = datetime.fromisoformat(inicio).date()

            if data_evento != agora.date():
                continue

            inicio_dt = fim_dt = None
            inicio_formatado = 'Dia inteiro'
            fim_formatado = 'Dia inteiro'
            status = 'Em andamento'

        eventos_br.append({
            'titulo': titulo,
            'inicio': inicio_formatado,
            'fim': fim_formatado,
            'descricao': descricao,
            'local': local,
            'status': status
        })

    # 🔄 Correção: agrupar e ordenar os eventos **fora do loop**
    def extrair_horario(evento):
        try:
            return datetime.strptime(evento['inicio'], '%H:%M').time()
        except:
            return datetime.min.time()

    eventos_nao_finalizados = [e for e in eventos_br if e['status'] != 'Finalizada']
    eventos_finalizados = [e for e in eventos_br if e['status'] == 'Finalizada']

    eventos_nao_finalizados.sort(key=extrair_horario)
    eventos_finalizados.sort(key=extrair_horario)

    eventos_ordenados = eventos_nao_finalizados + eventos_finalizados

    return render(request, 'agenda/lista_eventos.html', {'eventos': eventos_ordenados})



def home(request):
    return render(request, 'home.html')
