#!/usr/bin/env python3
"""
gbk_to_gff.py

Converte um (ou vários) arquivo(s) GenBank (.gbk/.gbff) para GFF3.

Uso:
    python3 gbk_to_gff.py input.gbk -o output.gff

Opções principais:
    -o, --output    Arquivo de saída GFF3 (padrão: stdout)
    --fasta         Anexa as sequências FASTA ao final do GFF (##FASTA)
    -s, --source    Campo source no GFF (padrão: "GenBank")

Notas:
- Requer Biopython (pip install biopython).
- Preserva atributos úteis: ID (locus_tag or generated), Name (gene/product), product, gene, locus_tag, db_xref.
- Tenta atribuir Parent para CDS/ mRNA apontando para gene quando possível.

"""

import sys
import argparse
from collections import defaultdict
from Bio import SeqIO
from Bio.SeqFeature import CompoundLocation, FeatureLocation


def format_attrs(attrs_dict):
    """Formata um dicionário de atributos em string GFF3 (escape simples)."""
    parts = []
    for k, v in attrs_dict.items():
        if v is None:
            continue
        if isinstance(v, (list, tuple)):
            val = ",".join(str(x) for x in v)
        else:
            val = str(v)
        # substituir caracteres proibidos simples
        val = val.replace(";", "%3B").replace("=", "%3D")
        parts.append(f"{k}={val}")
    return ";".join(parts)


def feature_bounds(feat):
    """Retorna (start, end, strand) 1-based closed coordinates para a feature.
    Para localizações compostas, start é o menor, end o maior. strand é +1 ou -1.
    """
    loc = feat.location
    # tratar CompoundLocation
    if isinstance(loc, CompoundLocation):
        starts = [int(part.nofuzzy_start) for part in loc.parts]
        ends = [int(part.nofuzzy_end) for part in loc.parts]
        start = min(starts) + 1
        end = max(ends)
        strand = loc.parts[0].strand
    else:
        start = int(loc.nofuzzy_start) + 1
        end = int(loc.nofuzzy_end)
        strand = loc.strand
    strand_char = "+" if strand == 1 or strand is None else "-"
    return start, end, strand_char


def safe_get_qual(feat, key):
    v = feat.qualifiers.get(key)
    if not v:
        return None
    # geralmente é lista
    return v[0] if isinstance(v, list) and len(v) == 1 else ",".join(v)


def make_id(prefix, counter):
    return f"{prefix}_{counter}"


def gbk_to_gff(records, out_handle, source="GenBank", write_fasta=False):
    out_handle.write("##gff-version 3\n")
    seq_fasta = []

    for rec_idx, rec in enumerate(records, start=1):
        seqid = rec.id
        # imprimir sequence-region (opcional)
        out_handle.write(f"##sequence-region {seqid} 1 {len(rec.seq)}\n")
        seq_fasta.append((seqid, rec.seq))

        gene_id_counter = 1
        feat_id_counter = 1

        # map gene features to IDs to allow Parent linking
        gene_by_location = {}

        for feat in rec.features:
            ftype = feat.type
            # ignorar features sem localização
            try:
                start, end, strand = feature_bounds(feat)
            except Exception:
                continue

            attrs = {}

            locus_tag = safe_get_qual(feat, 'locus_tag') or safe_get_qual(feat, 'locus')
            gene_name = safe_get_qual(feat, 'gene')
            product = safe_get_qual(feat, 'product')
            db_xref = feat.qualifiers.get('db_xref')

            # ID generation
            if locus_tag:
                fid = locus_tag
            else:
                # se é gene, prefira geneN, senão featN
                prefix = 'gene' if ftype.lower() == 'gene' else 'feat'
                fid = make_id(prefix, feat_id_counter)
                feat_id_counter += 1

            attrs['ID'] = fid
            if gene_name:
                attrs['Name'] = gene_name
            if product:
                attrs['product'] = product
            if db_xref:
                attrs['db_xref'] = ",".join(db_xref) if isinstance(db_xref, list) else db_xref

            # incluir outros qualifiers menores (note: não exhaustivo)
            for k in ('note', 'locus_tag', 'gene_synonym', 'product', 'inference'):
                if k in feat.qualifiers and k not in attrs:
                    attrs[k] = safe_get_qual(feat, k)

            # registry for gene -> to be used as Parent for mRNA/CDS
            if ftype.lower() == 'gene':
                gene_by_location[(start, end, strand)] = fid

            # attempt to link CDS or mRNA to a gene by overlap
            if ftype.lower() in ('cds', 'mrna', 'mRNA'):
                # search for overlapping gene
                parent = None
                for (gstart, gend, gstrand), gid in gene_by_location.items():
                    # simple overlap test
                    if not (end < gstart or start > gend):
                        parent = gid
                        break
                if parent:
                    attrs['Parent'] = parent

                # GFF phase calculation for CDS
                phase = '.'
                if ftype.lower() == 'cds':
                    # try codon_start qualifier
                    codon_start = safe_get_qual(feat, 'codon_start')
                    try:
                        if codon_start is not None:
                            phase = str((int(codon_start) - 1) % 3)
                        else:
                            # compute from start coordinate (0-based)
                            phase = str((int(feat.location.nofuzzy_start)) % 3)
                    except Exception:
                        phase = '.'
                else:
                    phase = '.'
            else:
                phase = '.'

            # build attributes string
            attr_str = format_attrs(attrs)

            # write GFF line: seqid, source, type, start, end, score, strand, phase, attributes
            score = feat.qualifiers.get('score', '.')
            score_str = safe_get_qual(feat, 'score') or '.'

            out_handle.write(f"{seqid}\t{source}\t{ftype}\t{start}\t{end}\t{score_str}\t{strand}\t{phase}\t{attr_str}\n")

    if write_fasta:
        out_handle.write("##FASTA\n")
        for seqid, seq in seq_fasta:
            out_handle.write(f">{seqid}\n")
            # wrap at 60
            s = str(seq)
            for i in range(0, len(s), 60):
                out_handle.write(s[i:i+60] + "\n")


def main():
    p = argparse.ArgumentParser(description='Converte GenBank para GFF3 (suporta múltiplas entradas)')
    p.add_argument('input', nargs='+', help='Arquivo(s) GenBank de entrada (.gbk, .gbff)')
    p.add_argument('-o', '--output', help='Arquivo GFF3 de saída (default: stdout)')
    p.add_argument('--fasta', action='store_true', help='Anexa sequências FASTA ao final (##FASTA)')
    p.add_argument('-s', '--source', default='GenBank', help='Campo source no GFF')

    args = p.parse_args()

    # abrir saída
    out = open(args.output, 'w') if args.output else sys.stdout

    # iterar arquivos de entrada (SeqIO.parse aceita múltiplos, mas fazemos manualmente)
    records = []
    for inp in args.input:
        try:
            for rec in SeqIO.parse(inp, 'genbank'):
                records.append(rec)
        except Exception as e:
            sys.stderr.write(f"Erro lendo {inp}: {e}\n")
            sys.exit(1)

    gbk_to_gff(records, out_handle=out, source=args.source, write_fasta=args.fasta)

    if args.output:
        out.close()


if __name__ == '__main__':
    main()

