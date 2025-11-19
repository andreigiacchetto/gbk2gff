# 🧬 gbk_to_gff.py

Um script em Python para converter arquivos **GenBank (.gbk/.gbff)** para **GFF3**, preservando informações essenciais de anotação e garantindo compatibilidade com ferramentas downstream como **Panaroo**, **Roary**, **Prokka** e pipelines de pangenômica.

---
✨ Author
Andrei Giacchetto Felice

Laboratory of Immunology and Omics Sciences (LimCom)
---

## 📌 Visão Geral

O formato GenBank é extremamente rico em detalhes, mas nem sempre prático para análises de pangenômica ou pipelines de anotação que exigem o formato **GFF3**. Este script converte arquivos GBK/GBFF em GFF3 padronizado, mantendo integridade dos genes, coordenadas, produtos e metadados.

## 📚 Sobre o Formato GFF3

O formato **GFF3 (General Feature Format)** é amplamente utilizado para anotação genômica. Cada linha descreve uma feature (gene, CDS, tRNA, etc.) com: posição, fita, tipo e atributos.

O script produz um GFF3 totalmente válido contendo:
- `##gff-version 3`
- `##sequence-region`
- Features: `gene`, `CDS`, `tRNA`, `rRNA`, etc.
- Atributos standard: `ID`, `Name`, `product`, `db_xref`, `Parent`, entre outros
- Suporte opcional a FASTA incorporado

---

## 🔢 Instalação

O script depende apenas do **Biopython**:

```bash
pip install biopython
```

Clone ou copie o arquivo `gbk2gff.py` para o seu projeto.

---

## ▶️ Uso

### **Converter um arquivo GBK para GFF3:**
```bash
python3 gbk2gff.py entrada.gbk -o saida.gff
```

### **Converter múltiplos GBK em um único GFF:**
```bash
python3 gbk2gff.py *.gbk -o combinados.gff
```

### **Gerar GFF + FASTA embutido:**
```bash
python3 gbk2gff.py entrada.gbk -o saida.gff --fasta
```

### **Saída no terminal:**
```bash
python3 gbk2gff.py arquivo.gbk
```

---

## 🧠 Funcionalidades

### ✔ Preserva atributos essenciais
- `locus_tag`
- `gene`
- `product`
- `db_xref`
- `note`
- `inference`

### ✔ IDs consistentes
Se o GBK não tiver `locus_tag`, IDs são gerados automaticamente (`gene_1`, `feat_1`, etc.).

### ✔ Parent automático
O script detecta sobreposição entre features para criar relações:
- `CDS → gene`
- `mRNA → gene` (quando aplicável)

### ✔ Cálculo de phase (para CDS)
Compatível com ferramentas downstream que usam codificação de fase de códon.

### ✔ Suporte a localizações compostas (CompoundLocation)
Trabalha corretamente com genes fragmentados ou exons múltiplos.

### ✔ FASTA opcional embutido
Inclui um bloco `##FASTA` ao final do arquivo GFF3.

---

## 📜 Exemplo de Entrada (GenBank)

```
LOCUS       contig0001  2450 bp DNA linear
FEATURES             Location/Qualifiers
     gene            100..900
                     /locus_tag="ABC_001"
     CDS             100..900
                     /product="protein X"
```

### 🔄 Saída equivalente em GFF3
```
contig0001	GenBank	gene	100	900	.	+	.	ID=ABC_001;Name=ABC_001
contig0001	GenBank	CDS	100	900	.	+	0	ID=ABC_001_cds;Parent=ABC_001;product=protein X
```

---

📄 License
This project is freely available for academic and scientific use. For commercial use, please contact the author.
