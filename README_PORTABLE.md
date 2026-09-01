# Distribuição portátil para Windows

Execute `build_windows.bat` em um computador de desenvolvimento com o ambiente
virtual `.venv` pronto. O pacote será gerado em `release\Synaptomancer`.

Para distribuir, compacte ou copie **a pasta `Synaptomancer` inteira**. No
computador de destino, basta descompactar, conectar o ESP32 por USB e abrir
`Synaptomancer.exe`; Python e as bibliotecas não precisam ser instalados.

Se o Windows tiver bloqueado os arquivos baixados de outro computador, clique
com o botão direito no arquivo `.zip`, escolha **Propriedades**, marque
**Desbloquear**, aplique e só então extraia a pasta.

Os arquivos de dados, traduções e plugins ficam ao lado do executável. As
aquisições e os demais dados criados pelo usuário permanecem na pasta `data`
desse pacote portátil.
