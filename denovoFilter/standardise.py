"""
Copyright (c) 2015 Wellcome Trust Sanger Institute

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

def standardise_columns(de_novos):
    """ subset down to specific columns
    
    Args:
        de_novos dataframe of de novo variants
    
     Returns:
        data frame with only the pertinent columns included
    """
    
    columns = ["person_stable_id", "chrom", "pos", "ref", "alt",
        "symbol", "consequence", "max_af", "pp_dnm"]
    
    if 'pass' in de_novos.columns:
        columns.append('pass')
    if 'strand_bias' in de_novos.columns:
        columns += ['maf_and_dnm_check', 'in_segdup', 'strand_bias',
            'parental_site_bias', 'parental_gene_bias', 'excess_parental_alts']
    
    return de_novos[columns].copy()
