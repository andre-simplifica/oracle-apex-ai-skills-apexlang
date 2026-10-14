# Oracle APEX AI Skills APEXlang

Kit de skills para **Oracle APEX 26.2**, com APEXlang como código da aplicação editável e versionado. O fluxo começa pela avaliação de uma aplicação recém-migrada, cria seu primeiro baseline completo e permite editar, validar, importar e verificar mudanças.

Este é um repositório separado do [Oracle APEX AI Skills](https://github.com/andre-simplifica/oracle-apex-ai-skills), que continua atendendo aos projetos APEX 24.2 pelo fluxo SQL. Os nomes das skills e os diretórios de instalação são diferentes, permitindo manter os dois kits.

## Requisitos

- APEX mínimo **26.2**; versão atualmente revisada: **26.2**.
- **SQLcl 26.3+** e **ORDS 26.3+**.
- Banco suportado: 19c RU 19.18+ ou Oracle AI Database 26ai 23.26.0+.
- Versões futuras do APEX exigem revisão do inventário Oracle, APIs, ferramentas e mudanças no formato. Não são liberadas automaticamente.

A instalação dos arquivos não conecta ao banco. A versão do ambiente e a identidade da aplicação precisam ser confirmadas antes do trabalho conectado.

## Instalação no projeto

Peça ao agente:

```text
Instale neste projeto o Oracle APEX AI Skills APEXlang a partir de
https://github.com/andre-simplifica/oracle-apex-ai-skills-apexlang.
Preserve os padrões existentes e o kit anterior. Fixe o commit de origem,
revise o plano, instale e execute status/doctor. Não conecte nem altere o
Oracle como parte da instalação dos arquivos.
```

A skill principal é `$oracle-apex-ai-skills-apexlang`. O instalador cria as quatro skills em `.agents/skills/`, o contexto independente em `.oracle-apexlang/` e os utilitários em `Util/apexlang/`. Perfis, padrões, relatório de prontidão e migrações pertencem ao projeto e são preservados nas atualizações.

Consulte [instalação Codex](docs/install-codex.md) e [Claude Code](docs/install-claude-code.md). A documentação técnica permanece em inglês.

## Primeira aplicação migrada

Peça a avaliação e o primeiro baseline APEXlang completo. O agente deverá confirmar as versões, exportar para uma área nova, preservar recuperação SQL, conferir páginas/arquivos, validar toda a árvore e analisar os avisos do CODESCAN.

Refresh de tema, Compatibility Mode, Upgrade Application e correções de metadados são avaliados conforme a aplicação. A exportação não autoriza executar essas mudanças. O primeiro commit do baseline fica separado das alterações de comportamento.

Na migração de aplicações antigas, a skill também avalia a configuração geral: Application Definition, segurança, interface/PWA, temas/assets, substitutions, Component Settings e New Features. Quando o escopo ainda não estiver decidido, pergunta se o usuário quer revisão com ajustes automáticos, somente revisão ou apenas a migração solicitada. Se já houver autorização, segue sem perguntar novamente. Veja o [roteiro reutilizável](skills/oracle-apexlang-dev/references/application-migration-review.md).

Os estados são explícitos:

- `EXPORTED_NOT_VALIDATED`: exportado, com validação incompleta ou falha.
- `BASELINE_VALIDATED`: inventário conferido e compilador aprovado; o teste real pode estar pendente.
- `READY_FOR_DEVELOPMENT`: ciclo autorizado de importação em DEV e testes funcionais/de autorização concluídos.

Veja o [fluxo completo](skills/oracle-apexlang-export/references/readiness-and-first-baseline.md).

## Desenvolvimento diário

O agente consulta os componentes oficiais da Oracle, altera os arquivos necessários, valida a aplicação inteira e compara com uma exportação recente para preservar mudanças do Builder. A importação seletiva atende mudanças elegíveis em desenvolvimento/teste; produção recebe a aplicação completa validada.

Após a importação autorizada, são verificados o fluxo real, as permissões e uma nova exportação. Working Copies compartilham objetos e dados do banco; os locks cooperativos continuam necessários para alterações em objetos compartilhados.

O kit inclui as quatro skills oficiais Oracle de APEXlang 26.2, fixadas por commit e hashes, referências das novidades/APIs, procedimentos SQLcl 26.3, planos de importação sem execução automática e atualização gerenciada do projeto.

## Validação e limites

```bash
python3 -m venv .tmp/validation-env
source .tmp/validation-env/bin/activate
python3 -m pip install -r requirements-dev.txt
bash scripts/validate_repo.sh
```

Os testes locais verificam instalação, preservação de arquivos, versões, referências, planos e falhas do compilador. Exemplos oficiais foram validados offline com SQLcl 26.3. Isso não significa que uma aplicação real tenha sido importada ou testada em produção. [Evidências](docs/validation.md).

[Atualizações](docs/update-and-contribute.md) · [README em inglês](README.md) · [Licenças](THIRD_PARTY_NOTICES.md)
