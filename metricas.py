import pandas as pd
from dateutil.relativedelta import relativedelta


def calcular_metricas_periodicas(df: pd.DataFrame, meses_no_periodo: pd.Timestamp, coluna_data: str = 'data') -> dict:
    # Data de corte
    data_corte = pd.Timestamp.now() - relativedelta(months=meses_no_periodo)

    # Cópia para não alterar o DataFrame original
    df = df.copy()

    # 1. Converter e filtrar datas
    df[coluna_data] = pd.to_datetime(df[coluna_data]).dt.tz_localize(None)
    df_filtrado = df[df[coluna_data] < data_corte.replace(day=1)]

    # 2. Agrupar por trimestre civil (QE = Quarter End)
    periodos = df_filtrado.resample('QE', on=coluna_data).size()

    # 3. Calcular métricas
    ultimo = periodos.iloc[-1] if len(periodos) > 0 else 0
    penultimo = periodos.iloc[-2] if len(periodos) > 1 else ultimo

    try:
        delta = ((ultimo - penultimo) / penultimo) * 100
    except ZeroDivisionError:
        delta = 0.0

    return {
        'ultimo_periodo': ultimo,
        'penultimo_periodo': penultimo,
        'delta_percentual': delta
    }


def calcular_frequencia(df: pd.DataFrame, coluna: str, valor: str) -> int:
    """
    Calcula a frequência de um valor específico em uma coluna do DataFrame

    Args:
        df: DataFrame contendo os dados
        coluna: Nome da coluna para filtrar
        valor: Valor específico para buscar na coluna

    Returns:
        Quantidade de ocorrências do valor na coluna especificada

    Raises:
        ValueError: Se a coluna não existir no DataFrame
    """
    try:
        if coluna not in df.columns:
            raise ValueError(f"A coluna '{coluna}' não existe no DataFrame")

        return len(df[df[coluna] == valor])

    except KeyError as e:
        raise ValueError(f"Erro ao acessar a coluna: {str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"Erro inesperado ao calcular frequência: {str(e)}") from e
