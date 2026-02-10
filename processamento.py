from dataclasses import dataclass
from typing import Callable, Optional, Tuple
import os
import shutil

from robo import SalusRobot


@dataclass
class LoteConfig:
    origem: str
    destino: str
    sistema: str
    copiar: bool = False
    on_progress: Optional[Callable[[float, str], None]] = None
    on_finish: Optional[Callable[[int, bool], None]] = None


def processar_lote(config: LoteConfig, logger: Callable[[str], None], stop_event) -> Tuple[int, bool]:
    bot = SalusRobot(logger, stop_event, config.sistema)

    logger(f"--- INICIANDO LOTE ({config.sistema}) ---")
    logger(f"Origem: {config.origem}")
    logger(f"Destino: {config.destino}")

    arquivos = sorted(
        entry.name
        for entry in os.scandir(config.origem)
        if entry.is_file() and entry.name.lower().endswith(".pdf")
    )
    total = len(arquivos)

    if total == 0:
        logger("Nenhum arquivo PDF encontrado na pasta de origem.")
        if config.on_finish:
            config.on_finish(0, False)
        return 0, False

    logger(f"Total de arquivos na fila: {total}")

    for index, arquivo in enumerate(arquivos, start=1):
        if stop_event.is_set():
            break

        progresso = index / total
        if config.on_progress:
            config.on_progress(
                progresso,
                f"Processando arquivo {index} de {total}: {arquivo}",
            )

        caminho_completo = os.path.join(config.origem, arquivo)
        id_paciente = "".join(filter(str.isdigit, arquivo))

        try:
            sucesso, msg = bot.executar_sequencia(id_paciente, caminho_completo, config.sistema)
        except Exception as exc:
            sucesso, msg = False, f"Erro inesperado: {exc}"

        if sucesso:
            acao_texto = "Copiando" if config.copiar else "Movendo"
            logger(f"✅ {arquivo}: Sucesso! {acao_texto} para concluídos...")
            try:
                destino = os.path.join(config.destino, arquivo)
                if config.copiar:
                    shutil.copy2(caminho_completo, destino)
                else:
                    shutil.move(caminho_completo, destino)
            except Exception as exc:
                logger(f"⚠️ Erro ao finalizar arquivo: {exc}")
        else:
            logger(f"❌ {arquivo}: Falhou ({msg}). Mantendo na origem.")

    interrompido = stop_event.is_set()
    if config.on_finish:
        config.on_finish(total, interrompido)
    return total, interrompido
