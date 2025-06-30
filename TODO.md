# TODO

## Conectividade
- [x] Implementar reconhecimento automático do tipo de conexão:
  - Serial
  - BLE (Bluetooth Low Energy)
  - Outros, se aplicável
- [ ] Implementar detecção automática de endereços MAC dos BLEs

## Criação de Perfil
- [ ] Permitir que o usuário escolhas quantas e quais classes quer durante a coleta na interface

## Coleta de Dados
- [x] Arrumar ColetaWorker
- [ ] Testar com sinal simulado na Cyton

## Processamento de Dados
- [ ] Implementar métodos de classificação
- [ ] Implementar métodos de pré-processamento 

## Execução da Imagética
- [x] Adicionar tempo de espera aleatório entre imagéticas
  - Informar **média** e **desvio padrão**
- [ ] Adicionar **feedback visual** e **sonoro** durante a execução da imagética

## Estado da Aplicação
- [ ] Implementar controle de estado do programa
  - Salvar estado atual na **pasta `temp/`**
  - Restaurar estado ao reiniciar o programa

## Validação
- [ ] Validar todas as entradas do usuário
  - Verificar tipo, formato e consistência
