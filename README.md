Este projeto corrige o tom de um arquivo de áudio para uma escala musical específica ou para os tons mais próximos usando o script autotune_telecom.py.

Descrição
O script autotune_telecom.py permite corrigir o tom de um arquivo de áudio para uma escala musical específica ou para os tons mais próximos. Ele também pode gerar um gráfico dos resultados se desejado.

Requisitos
Python 3.x
Bibliotecas: argparse, functools, pathlib, librosa, matplotlib, numpy, scipy, soundfile, psola
Instalação
Instale as bibliotecas necessárias usando pip:

Uso
Sintaxe
Argumentos
<vocals_file>: Caminho para o arquivo de áudio de entrada.
--plot, -p: (Opcional) Produz um gráfico dos resultados se definido.
--correction-method, -c: (Opcional) Método de correção de tom. Pode ser closest para corrigir para os tons mais próximos ou scale para corrigir para uma escala específica. O padrão é closest.
--scale, -s: (Opcional) Escala musical para correção (ex: "G#:minor"). Usado apenas para o método de correção scale.

Exemplos de Uso
Correção para os tons mais próximos:
python autotune_telecom.py natasha.wav

Correção para uma escala específica (ex: Sol Sustenido Menor):
python autotune_telecom.py natasha.wav --correction-method scale --scale "G#:minor"

Correção para uma escala específica com gráfico dos resultados:
python autotune_telecom.py natasha.wav --correction-method scale --scale "G#:minor" --plot

Notas
Certifique-se de que o formato da escala esteja correto (ex: "G#:minor" em vez de "G# minor").
O arquivo de saída será salvo no mesmo diretório do arquivo de entrada com o sufixo _pitch_corrected.

Este README deve ajudá-lo a entender e utilizar o script autotune_telecom.py de forma eficaz.
