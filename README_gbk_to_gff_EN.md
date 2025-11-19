# 🧬 gbk_to_gff.py

A Python script to convert **GenBank (.gbk/.gbff)** files into **GFF3**, preserving essential annotation information and ensuring compatibility with downstream tools such as **Panaroo**, **Roary**, **Prokka**, and various pangenome analysis pipelines.

---
✨ **Author**  
Andrei Giacchetto Felice 

Laboratory of Immunology and Omics Sciences (LimCom)

---

## 📌 Overview

The GenBank format is extremely rich in detail but not always convenient for pangenome workflows or annotation pipelines that require the **GFF3** format.  
This script converts GBK/GBFF files into a standardized GFF3 file while maintaining gene integrity, coordinates, product information, and metadata.

## 📚 About the GFF3 Format

**GFF3 (General Feature Format)** is widely used for genome annotation. Each line describes a feature (gene, CDS, tRNA, etc.) using its type, position, strand, and attributes.

This script generates a fully valid GFF3 file including:
- `##gff-version 3`
- `##sequence-region`
- Features such as `gene`, `CDS`, `tRNA`, `rRNA`, etc.
- Standard attributes: `ID`, `Name`, `product`, `db_xref`, `Parent`, and others
- Optional embedded FASTA section

---

## 🔢 Installation

The script only depends on **Biopython**:

```bash
pip install biopython
```

Clone or copy the file `gbk2gff.py` into your project.

---

## ▶️ Usage

### **Convert a single GBK file to GFF3:**
```bash
python3 gbk2gff.py input.gbk -o output.gff
```

### **Convert multiple GBK files into a single GFF:**
```bash
python3 gbk2gff.py *.gbk -o merged.gff
```

### **Generate GFF with embedded FASTA:**
```bash
python3 gbk2gff.py input.gbk -o output.gff --fasta
```

### **Print GFF directly to the terminal:**
```bash
python3 gbk2gff.py file.gbk
```

---

## 🧠 Features

### ✔ Preserves key annotation fields
- `locus_tag`
- `gene`
- `product`
- `db_xref`
- `note`
- `inference`

### ✔ Consistent IDs  
If a GBK entry has no `locus_tag`, the script automatically generates IDs (`gene_1`, `feat_1`, etc.).

### ✔ Automatic Parent assignment  
The script detects feature overlap to infer biological relationships:
- `CDS → gene`
- `mRNA → gene` (when applicable)

### ✔ Phase calculation (for CDS)  
Compatible with downstream tools that require codon phase information.

### ✔ Full support for CompoundLocation  
Correctly handles fragmented genes and multi-exon structures.

### ✔ Optional embedded FASTA  
Adds a `##FASTA` block at the end of the GFF3 file.

---

## 📜 Example Input (GenBank)

```
LOCUS       contig0001  2450 bp DNA linear
FEATURES             Location/Qualifiers
     gene            100..900
                     /locus_tag="ABC_001"
     CDS             100..900
                     /product="protein X"
```

### 🔄 Equivalent Output in GFF3
```
contig0001	GenBank	gene	100	900	.	+	.	ID=ABC_001;Name=ABC_001
contig0001	GenBank	CDS	100	900	.	+	0	ID=ABC_001_cds;Parent=ABC_001;product=protein X
```

---

## 📄 License
This project is freely available for academic and scientific use.  
For commercial use, please contact the author.
