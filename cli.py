import argparse
import threading

from processamento import LoteConfig, processar_lote


def main() -> int:
    parser = argparse.ArgumentParser(description="Processa lotes do Voox Salus via CLI.")
    parser.add_argument("--origem", required=True, help="Pasta de origem dos PDFs.")
    parser.add_argument("--destino", required=True, help="Pasta de destino dos PDFs.")
    parser.add_argument(
        "--sistema",
        required=True,
        choices=["BIOCROMA", "BIOVIDA"],
        help="Sistema alvo para o processamento.",
    )
    parser.add_argument(
        "--copiar",
        action="store_true",
        help="Copia os arquivos em vez de mover.",
    )
    args = parser.parse_args()

    stop_event = threading.Event()

    config = LoteConfig(
        origem=args.origem,
        destino=args.destino,
        sistema=args.sistema,
        copiar=args.copiar,
    )

    total, interrompido = processar_lote(config, print, stop_event)
    if interrompido:
        print("Processamento interrompido.")
        return 1
    print(f"Processamento finalizado. Total processado: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
