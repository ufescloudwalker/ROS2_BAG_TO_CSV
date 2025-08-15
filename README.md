# ROS2_BAG_TO_CSV

Este programa foi desenvolvido para **converter todos os tópicos registrados** em um arquivo ROS 2 **rosbag** para **arquivos CSV** e **imagens**.  
Oferece uma solução de automação para a extração de dados em larga escala, incluindo a captura e armazenamento de informações provenientes de tópicos de imagem.

---

## 🖥️ Requisitos

- **Sistema Operacional:** Ubuntu 22.04 LTS  
- **ROS 2:** Humble Hawksbill (LTS)  
- **Python:** 3.10+  
- Bibliotecas necessárias:
  ```bash
  pip install opencv-python cv_bridge
  ```

---

## 📂 Estrutura de Pastas

Antes de executar o programa, crie as seguintes pastas (ou utilize parâmetros para definir caminhos personalizados):

```
ROS2_BAG_TO_CSV/
├── bags/        # Contém as pastas com os arquivos .db3 e .yaml
├── docs/        # (Opcional) Local onde serão salvos os arquivos CSV
├── processed/   # Contém os bags já processados (CSV + imagens)
```

- **`bags/`** → Local onde devem ser colocadas as pastas de bag com `.db3` e `.yaml`.
- **`processed/`** → Após o processamento, cada bag gerará:
  - `/csv/` → Arquivos CSV (um por tópico).
  - `/images/` → Imagens extraídas (nomes baseados no timestamp).
- **`docs/`** → Diretório alternativo para salvar CSVs (opcional).

---

## ⚙️ Argumentos Disponíveis

O script aceita os seguintes argumentos opcionais para personalizar os diretórios de entrada e saída:

| Argumento         | Tipo   | Padrão       | Descrição |
|-------------------|--------|--------------|-----------|
| `--bags_dir`      | Path   | `./bags`     | Caminho absoluto ou relativo para o diretório que contém as pastas com os arquivos `.db3` e `.yaml` do rosbag. |
| `--docs_dir`      | Path   | `./docs`     | Diretório onde serão salvos todos os arquivos CSV gerados a partir dos tópicos. |
| `--processed_dir` | Path   | `./processed`| Diretório onde será criada uma pasta para cada bag processado, contendo subpastas `csv/` e `images/`. |

### 📌 Exemplo de uso

- Usando caminhos padrão:
```bash
python3 main.py
```

- Usando diretórios personalizados:
```bash
python3 main.py \
  --bags_dir "/home/user/meus_bags" \
  --docs_dir "/home/user/documentos_csv" \
  --processed_dir "/home/user/bags_processados"
```

### 🛠️ Notas
- Os caminhos podem ser **absolutos** (`/home/user/...`) ou **relativos** (`./meu_diretorio`).
- Certifique-se de que todos os diretórios passados existam antes de executar o script.
- O diretório `processed_dir` será organizado da seguinte forma para cada bag:
```
processed/
 └── nome_do_bag/
     ├── csv/     # Todos os CSVs gerados
     └── images/  # Imagens extraídas do tópico /head_front_camera/rgb/image_raw
```

---

## 📋 Fluxo de Processamento

1. **Preparar arquivos:**  
   - Coloque as pastas contendo `.db3` e `.yaml` dentro de `bags/`.
2. **Executar o script** para converter todos os tópicos para CSV e extrair imagens.  
3. **Verificar processamento:**  
   - Confirme que os arquivos CSV e imagens foram gerados em `processed/`.
4. **Limpeza:**  
   - Após confirmar o processamento, remova os arquivos `.db3` e `.yaml` originais para liberar espaço.

---

## 🖼️ Extração de Imagens

O programa extrai automaticamente todas as imagens do tópico:
```
/head_front_camera/rgb/image_raw
```
Cada imagem é salva em **PNG**, nomeada com o **timestamp** (`sec_nanosec.png`).

Exemplo:
```
123_456000000.png
123_789000000.png
```

---

## 📜 Licença

Este projeto está licenciado sob a [Apache 2.0 License](LICENSE).
