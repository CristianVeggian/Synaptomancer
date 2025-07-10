# TODO

## Conectividade
- [x] Implementar reconhecimento automático do tipo de conexão:
  - Serial
  - BLE (Bluetooth Low Energy)
  - Outros, se aplicável
- [ ] Implementar detecção automática de endereços MAC dos BLEs

## Criação de Perfil
- [x] Permitir que o usuário escolhas quantas e quais classes quer durante a coleta na interface
- [x] Adicionar increment == 11, max == 99 para controlar números das classes 

## Coleta de Dados
- [x] Arrumar ColetaWorker
- [ ] Testar com sinal simulado na Cyton
- [ ] Implementar funcionalidade de ver/salvar dados filtrados ou brutos
- [ ] Implementar threshold para identificar ruídos

## Processamento de Dados
- [ ] Implementar métodos de classificação
- [ ] Implementar métodos de pré-processamento 

## Execução da Imagética
- [x] Adicionar tempo de espera aleatório entre imagéticas
  - Informar **média** e **desvio padrão**
- [x] Adicionar **feedback visual** e **sonoro** durante a execução da imagética
- [ ] Adicionar **indicação de mudança de classe** no gráfico
- [ ] Adicionar **feedback sonoro** vocalizado ao invés de beep

## Estado da Aplicação
- [ ] Implementar controle de estado do programa
  - Salvar estado atual na **pasta `temp/`**
  - Restaurar estado ao reiniciar o programa

## Validação
- [ ] Validar todas as entradas do usuário
  - Verificar tipo, formato e consistência
