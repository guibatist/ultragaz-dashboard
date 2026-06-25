import os
from flask import Flask, render_template
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_30MoOdPeLYVt@ep-muddy-breeze-ahqrx9tg-pooler.c-3.us-east-1.aws.neon.tech/neondb")
engine = create_engine(DATABASE_URL)

def buscar_dados():
    try:
        query = "SELECT unidade, funcionario, cpf, documento, vencimento, status_pendencia FROM pendencias_ultragaz"
        df = pd.read_sql(query, engine)
        
        if df.empty:
            return []

        df['unidade'] = df['unidade'].fillna('NÃO INFORMADA').astype(str).str.strip().str.upper()
        df['funcionario'] = df['funcionario'].fillna('N/A').astype(str).str.strip().str.upper()
        df['documento'] = df['documento'].fillna('OUTROS').astype(str).str.strip().str.upper()
        df['status_pendencia'] = df['status_pendencia'].fillna('DESCONHECIDO').astype(str).str.strip().str.upper()
        
        hoje = pd.Timestamp.now().normalize()
        df['vencimento_dt'] = pd.to_datetime(df['vencimento'], format='%d/%m/%Y', errors='coerce')
        
        df['dias_atraso'] = (hoje - df['vencimento_dt']).dt.days
        df['dias_atraso'] = df['dias_atraso'].fillna(-1).astype(int)
        
        df = df.drop(columns=['vencimento_dt'])
        
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        return []

@app.route('/')
def dashboard():
    dados = buscar_dados()
    return render_template('index.html', dados_json=dados)

if __name__ == '__main__':
    app.run(debug=True)