"""
Copyright (c) 2016 Genome Research Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pandas

from denovoFilter.allele_counts import extract_alt_and_ref_counts, \
    get_recurrent_genes
from denovoFilter.site_deviations import test_sites, test_genes
from denovoFilter.min_depth import min_depth
from denovoFilter.constants import P_CUTOFF, ERROR_RATE

def filter_denovogear_sites(de_novos, status):
    """ set flags for filtering, fail samples with strand bias < threshold, or any 2 of
     (i) both parents have ALTs
     (ii) site-specific parental alts < threshold,
     (iii) gene-specific parental alts < threshold, if > 1 sites called in gene
    
    Args:
        de_novos: dataframe of de novo variants
        status: list (or pandas Series) or boolea
    
    Returns:
        vector of true/false for whether each variant passes the filters
    """
    
    counts = extract_alt_and_ref_counts(de_novos)
    recurrent = get_recurrent_genes(de_novos)
    
    counts['child_alts'] = counts[['child_alt_F', 'child_alt_R']].sum(axis=1)
    counts['child_depth'] = counts[['child_ref_F', 'child_ref_R', 'child_alt_F', 'child_alt_R']].sum(axis=1)
    counts['dad_depth'] = counts[['father_ref_F', 'father_ref_R', 'father_alt_F', 'father_alt_R']].sum(axis=1)
    counts['mom_depth'] = counts[['mother_ref_F', 'mother_ref_R', 'mother_alt_F', 'mother_alt_R']].sum(axis=1)
    
    # only include sites with good sample depths (different threshold for child
    # and parents) and sufficient alts in the child
    good_depth = (counts['child_alts'] > 1) & (counts['child_depth'] > 7) & \
        (counts['dad_depth'] > 5)  &(counts['mom_depth'] > 5)
    status &= good_depth
    
    # check if sites deviate from expected strand bias and parental alt depths
    strand_bias, parental_site_bias = test_sites(counts, status)
    parental_gene_bias = test_genes(counts, strand_bias, status)
    
    # fail SNVs with excessive strand bias. Don't check strand bias in indels.
    overall_pass = (strand_bias >= P_CUTOFF) | (de_novos["ref"].str.len() != 1) | \
        (de_novos["alt"].str.len() != 1)
    
    # find if each de novo has passed each of three different filtering strategies
    # fail sites with gene-specific parental alts, only if >1 sites called per gene
    gene_fail = (parental_gene_bias < P_CUTOFF) & de_novos["symbol"].isin(recurrent)
    site_fail = (parental_site_bias < P_CUTOFF)
    
    counts['parental_depth_threshold'] = counts[['dad_depth', 'mom_depth']].apply(min_depth, error=ERROR_RATE, axis=1)
    
    excess_alts = counts["min_parent_alt"] > counts['parental_depth_threshold']
    
    # exclude sites that fail two of three classes
    sites = pandas.DataFrame({"gene": gene_fail, "site": site_fail, "alts": excess_alts})
    overall_pass[sites.sum(axis=1) >= 2] = False
    
    # drop out sites with poor depths
    overall_pass &= good_depth  
    
    return overall_pass
