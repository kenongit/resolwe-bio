#!/usr/bin/env python2
import argparse
import build_gene_info_common as build

parser = argparse.ArgumentParser(description='Build gene info (Homo sapiens).')
parser.add_argument('--annotation', help='Annotation (GTF) file')
parser.add_argument('--gene_info', help='NCBI "Gene_Info" file')
parser.add_argument('--uniprotKB', help='Uniprot mapping file')
parser.add_argument('--output', help='Output "GeneInfo" file')

args = parser.parse_args()


all_transcript_ids = set()
transcriptId2GeneName = {}
transcriptId2GeneID = {}
transcriptId2variant = {}
GeneID2EntrezID = {}
GeneID2synonyms = {}
GeneID2description = {}
GeneID2Omim = {}
EntrezID2UniprotKB = {}

with open(args.annotation) as annotation_file:
    for line in annotation_file:
        if "transcript_id" in line:
            trans_id = build.get_transcript_id(line)

            all_transcript_ids.add(trans_id)
            transcriptId2variant[trans_id] = build.get_transcript_name(line)
            transcriptId2GeneID[trans_id] = build.get_gene_id(line)
            transcriptId2GeneName[trans_id] = build.get_gene_name(line)

with open(args.gene_info) as gene_info:
    gene_info.readline()

    for line in gene_info:
        if "Ensembl" in line:
            a = line.split('\t')
            ens_id = build.get_ensembl_id(a[5])

            GeneID2synonyms[ens_id] = a[4]
            GeneID2description[ens_id] = a[8]
            GeneID2EntrezID[ens_id] = a[1]
            GeneID2Omim[ens_id] = build.get_omim_id(a[5])

with open(args.uniprotKB) as uniprot:
    for line in uniprot:
        l = line.split('\t')
        if l[2] != '':
            EntrezID2UniprotKB[l[2]] = l[0]

with open(args.output, "w") as f:
    f.write('\t'.join(["Gene ID", "Gene Name", "Synonyms", "Gene Products", "Entrez ID", "Ensembl ID",
            "OMIM ID", "UniprotKB ID", "Variant Number"]) + '\n')

    for trans_id in all_transcript_ids:
        gene_id = transcriptId2GeneID[trans_id]

        if gene_id not in GeneID2EntrezID:
            continue

        entrez_id = GeneID2EntrezID[gene_id]
        gene_name = transcriptId2GeneName[trans_id]
        ens_id = transcriptId2GeneID[trans_id]
        variant = transcriptId2variant[trans_id]

        synonyms = GeneID2synonyms[gene_id] if gene_id in GeneID2synonyms else 'N/A'
        description = GeneID2description[gene_id] if gene_id in GeneID2description else  'N/A'
        omim_id = GeneID2Omim[gene_id] if gene_id in GeneID2Omim else 'N/A'

        uniprotKB = 'N/A'
        if gene_id in GeneID2EntrezID and GeneID2EntrezID[gene_id] in EntrezID2UniprotKB:
            uniprotKB = EntrezID2UniprotKB[GeneID2EntrezID[gene_id]]

        f.write('\t'.join([trans_id, gene_name, synonyms, description, entrez_id, ens_id,
                omim_id, uniprotKB, variant]) + '\n')
