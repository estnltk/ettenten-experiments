#
#   Utilities for processing UD format EWTB (Estonian Web TreeBank) corpus
#   ( https://github.com/UniversalDependencies/UD_Estonian-EWT/ )
#
#   * load_EWTB_ud_file_with_corrections(fnm) :
#          Loads EWTB corpus' ud file, and provides annotation post-corrections 
#          that improve its comparability to Vabamorf's annotations.
#          Returns the created Text object.
#
#   * align_records(ud_recs, vm_recs) :
#          Aligns UD morph annotations to Vabamorf's annotations. 
#          Use this method for comparing analyses of a single word.
#          Returns tuple: (matches_table, has_full_match).
#
#   * VM2EWTBMorphDiffTagger
#          Finds differences between Vabamorf's morph analysis layer and EWTB's 
#          morph analysis (ud_syntax) layer.
#          By deafult, uses align_records() for comparing annotations.
#          Outputs differences as a layer.
#
#   * get_diff_statistics(...):
#          Summarizes information about morphological annotation mismatches 
#          (and matches) based on the layers created with VM2EWTBMorphDiffTagger.
#          Use this method to get aggregated statistics about mismatches in
#          a corpus of Text-s.
#          Returns a dict with summary results.
#
#   * diff_statistics_html_table(...):
#          Finds detailed difference statistics (uses method get_diff_statistics()) 
#          and outputs results as an HTML table.
#
import os, os.path
import re

from collections import OrderedDict
from collections import defaultdict

from estnltk.text import Layer, Text
from estnltk.taggers import Tagger, Retagger
from estnltk.taggers import CompoundTokenTagger
from estnltk.layer.annotation import Annotation

from estnltk.converters.conll_importer import conll_to_text

# ===========================================================================
#   Importing Text objects from EWTB corpus
#   (Note: this operates on the UD version of the corpus)
# ===========================================================================

class EWTBCorrectionsRewriter:
    '''Provides corrections to EWTB's annotations in order to make them comparable to Vabamorf's ones.'''
    
    verb_endings = re.compile('^(.+)(ma|nud|tud|dud)$')
    
    def rewrite(self, record):
        # Attributes:
        #   id, lemma, upostag, xpostag, feats, head, deprel, deps, misc, parent_span, children, text
        assert 'text' in record, str(record)
        # 1) 'feats' should always be available, even if empty
        if record['feats'] is None:
            record['feats'] = OrderedDict()
        # 2) Rewrite verbs by removing ending -ma, -nud, -tud, -dud
        #    ( so that we can match against Vabamorf's verbs )
        xpostag = record['xpostag']
        upostag = record['upostag']
        if xpostag == 'V':
            record['lemma'] = self.verb_endings.sub('\\1', record['lemma'])
        # 3) Fix ordinal numbers that were marked as adjectives ...
        num_type = record['feats'].get('NumType', None)
        num_form = record['feats'].get('NumForm', None)
        case     = record['feats'].get('Case', None)
        number   = record['feats'].get('Number', None)
        if xpostag == 'N' and upostag == 'ADJ' and num_form == 'Digit' and num_type == 'Ord':
            record['xpostag'] = 'O'
            record['upostag'] = 'NUM'
            xpostag = record['xpostag']
            upostag = record['upostag']
        if xpostag == 'N' and upostag == 'ADJ' and num_form == None and num_type == 'Ord':
            record['xpostag'] = 'O'
            record['upostag'] = 'NUM'
            xpostag = record['xpostag']
            upostag = record['upostag']
        # 4) Small (manual) corrections on annotation details:
        if record['text'] == 'Rääkimata':
            if case == 'Abl':
                record['feats']['Case'] = 'Abe'
        if record['text'] == 'saaksid' and xpostag == 'V':
            if 'Person' not in record['feats']:
                record['feats']['Person'] = '3'
        if record['text'] == 'sattusid' and xpostag == 'V':
            if number == 'Sing':
                record['feats']['Number'] = 'Plur'
        if record['text'] == 'omadega' and xpostag == 'P':
            if case == 'Gen' and number == 'Sing':
                record['feats']['Case'] = 'Com'
                record['feats']['Number'] = 'Plur'
        if record['text'] == 'omad' and xpostag == 'P':
            if number == 'Sing':
                record['feats']['Number'] = 'Plur'
        if record['text'] == 'omade' and xpostag == 'P':
            if number == 'Sing':
                record['feats']['Number'] = 'Plur'
        if record['text'] == 'omi' and xpostag == 'P':
            if number == 'Sing':
                record['feats']['Number'] = 'Plur'
        if record['text'] == 'närvi' and xpostag == 'S':
            if number == 'Sing' and case == 'Ill' and record['lemma'] == 'närvi':
                record['lemma'] = 'närv'
        # Fix broken compound word lemmas
        if record['text'] == 'osanikeringi' and record['lemma'] == 'osanik':
            record['lemma'] = 'osanik+e_ring'
        if record['text'] == 'paksukstegev' and record['lemma'] == 'paksu':
            record['lemma'] = 'paksu+ks_tegev'
        if record['text'] == 'omal-käel-üritajatega' and record['lemma'] == 'omal-käe':
            record['lemma'] = 'oma+l-käe+l-üritaja'
        if record['text'] == 'arvete-lehele' and record['lemma'] == 'arve':
            record['lemma'] = 'arve+te-leht'
        if record['text'] == 'noortekonverents' and record['lemma'] == 'noor':
            record['lemma'] = 'noor+te_konverents'
        if record['text'] == 'müügiletulek' and record['lemma'] == 'müügi':
            record['lemma'] = 'müügi+le_tulek'
        if record['text'] == 'isikukoodilepinguga' and record['lemma'] == 'isikukoodi':
            record['lemma'] = 'isiku_koodi_leping'
        if record['text'] == 'naiseksolemisega' and record['lemma'] == 'naiseks_olemine':
            record['lemma'] = 'naise+ks_olemine'
        # Fix broken lemmas
        if record['text'] == 'suhet-peret' and record['lemma'] == 'suhe-pere':
            record['lemma'] = 'suhe+t-pere'
        if record['text'] == 'ja/või' and record['lemma'] == 'või':
            record['lemma'] = 'ja/või'
        if record['text'] == 'lennuga' and xpostag=='S' and record['lemma'] == 'lennuga':
            record['lemma'] = 'lend'
        return record


class EWTBCorrectionsRetagger(Retagger):
    '''Retagger that applies EWTBCorrectionsRewriter.'''
    conf_param = ['rewriter']

    def __init__(self, layer_name):
        self.input_layers = [layer_name]
        self.output_layer = layer_name
        self.output_attributes = []
        self.rewriter = EWTBCorrectionsRewriter()
    
    def _change_layer(self, text, layers, status):
        layer = layers[self.output_layer]
        layer_attribs = layer.attributes
        for span in layer:
            records = span.to_records(with_text=True)
            if isinstance(records, dict):
                records = [ records ]
            span.clear_annotations()
            for record in records:
                self.rewriter.rewrite( record )
                record = { k: record[k] for k in record.keys() if k in layer_attribs }
                span.add_annotation(Annotation(span, **record))
        return layer


def load_EWTB_ud_file_with_corrections( fnm, annotation_layer, add_compound_tokens=True ):
    '''Loads EWTB corpus' ud file with post-corrections that improve comparability to VM's annotations. Returns the Text object. '''
    # Load conll annotations layer
    text = conll_to_text(file = fnm, syntax_layer=annotation_layer)
    # Rewrite layer with postcorrections
    EWTBCorrectionsRetagger(layer_name=annotation_layer).retag( text )
    # Add compound tokens layer (if required)
    if add_compound_tokens and 'compound_tokens' not in text.layers.keys():
        add_empty_compound_tokens_layer( text )
    return text


def add_empty_compound_tokens_layer( text ):
    '''Adds an empty compound tokens layer to the Text object. This is required for morph analysis.'''
    compound_tokens = \
           Layer(name=CompoundTokenTagger.output_layer, \
                 attributes=CompoundTokenTagger.output_attributes, \
                 text_object=text,\
                 ambiguous=False)
    text.add_layer(compound_tokens)


# ===========================================================================
#   Aligning UD annotations with Vabamorf's annotations
#  VM categories:   http://www.filosoft.ee/html_morf_et/morfoutinfo.html
#  UD categories:   https://github.com/EstSyntax/EstUD
#     https://github.com/EstSyntax/EstUD/blob/master/Estonian_UD_2016.pdf
# ===========================================================================

def align_records( ud_word_records, vm_word_records ):
    '''Aligns UD annotations to Vabamorf's annotations. Returns tuple: (matches_table, has_full_match).'''
    matches_table  = []
    has_full_match = False
    assert isinstance(ud_word_records, list), '(!) Input ud_word_records should be a list of analyses.'
    assert len(ud_word_records) == 1, '(!) Input ud_word_records should be disambiguated.'
    for ud_id, ud_rec in enumerate( ud_word_records ):
        for vm_id, vm_rec in enumerate( vm_word_records ):
            # Attempt matching
            local_lemma_match = is_lemma_match( ud_rec, vm_rec )
            local_pos_match   = is_pos_match( ud_rec, vm_rec )
            local_form_match  = is_form_match( ud_rec, vm_rec )
            # If both pos and form match, but lemma does not, attempt to match
            #    without compound boundary markings
            if not local_lemma_match and local_pos_match and local_form_match:
                local_lemma_match = is_lemma_match( ud_rec, vm_rec, \
                                                    match_without_compounds=True )
            local_matches = [local_lemma_match, local_pos_match, local_form_match]
            if all( local_matches ):
                has_full_match = True
            matches_table.append( local_matches )
    return matches_table, has_full_match


def is_lemma_match( ud_word_record, vm_word_record, match_without_compounds=False ):
    '''Detects if the lemma from UD annotation matches with Vabamorf's lemma.'''
    ud_norm_lemma = ud_word_record['lemma'].replace('=', '')
    vm_norm_lemma = vm_word_record['root'].replace('=', '')
    if match_without_compounds:
        # Remove compound boundaries before matching
        ud_norm_lemma = ud_norm_lemma.replace('_', '')
        vm_norm_lemma = vm_norm_lemma.replace('_', '')
    if not ud_norm_lemma == vm_norm_lemma:
        if '+' in vm_norm_lemma and any([c.isalnum() for c in vm_norm_lemma]):
            # Try matching without '+' signs
            vm_norm_lemma = vm_norm_lemma.replace('+', '')
    return ud_norm_lemma == vm_norm_lemma


def is_pos_match( ud_word_record, vm_word_record ):
    '''Detects if the partofspeech from UD annotation matches with Vabamorf's partofspeech.'''
    ud_xpos  = ud_word_record['xpostag'] # the old postag
    ud_upos  = ud_word_record['upostag'] # the new (UD) postag
    ud_feats = ud_word_record['feats']
    vm_pos = vm_word_record['partofspeech']
    # Match proper names:  S_PROPN == H 
    if ud_xpos == 'S' and ud_upos == 'PROPN' and vm_pos == 'H':
        return True
    # Match adjectives:
    if ud_xpos == 'A' and ud_upos == 'ADJ':
        ud_degree = ud_feats.get('Degree', None)
        if ud_degree == 'Pos' and vm_pos == 'A':
            return True
        if ud_degree == 'Cmp' and vm_pos == 'C':
            return True
        if ud_degree == 'Sup' and vm_pos == 'U':
            return True
    if ud_xpos == 'A' and ud_upos == 'DET' and vm_pos == 'A':
        return True
    if ud_upos == 'ADJ' and vm_pos == 'G':
        return True
    # Match numerals:
    if ud_upos == 'NUM':
        ud_numtype = ud_feats.get('NumType', None)
        if ud_numtype == 'Card' and vm_pos == 'N':
            return True
        if ud_numtype == 'Ord' and vm_pos == 'O':
            return True
    # Match adverbs:  D == X
    if ud_xpos == 'D' and vm_pos == 'X':
        return True
    # Match interjection:  B == I (actually: I is subtype of B)
    if ud_xpos == 'B' and vm_pos == 'I':
        return True
    # Match emoticons:  E == Z
    if ud_xpos == 'E' and vm_pos == 'Z':
        return True
    # Symbols following a quantitative phrase
    if ud_xpos == 'nominal' and ud_upos=='SYM' and vm_pos == 'Z':
        return True
    return ud_xpos == vm_pos


ud_to_vm_case_mapping = {
    'Nom':'n', 
    'Gen':'g',
    'Par':'p',
    'Ill':'ill',
    'Ine':'in',
    'Ela':'el',
    'All':'all',
    'Ade':'ad',
    'Abl':'abl',
    'Tra':'tr',
    'Ter':'ter',
    'Ess':'es',
    'Abe':'ab',
    'Com':'kom',
}


def is_form_match( ud_word_record, vm_word_record ):
    '''Detects if the form (features) from UD annotation matches with Vabamorf's form.'''
    ud_xpos  = ud_word_record['xpostag'] # the old postag
    ud_upos  = ud_word_record['upostag'] # the new (UD) postag
    ud_feats = ud_word_record['feats']
    vm_pos   = vm_word_record['partofspeech']
    vm_form  = vm_word_record['form']
    #  Nominal: ud has both case and number
    if 'Number' in ud_feats and 'Case' in ud_feats:
        ud_number = ud_feats['Number']
        ud_number_norm = 'pl' if ud_number == 'Plur' else ud_number
        ud_number_norm = 'sg' if ud_number_norm == 'Sing' else ud_number_norm
        number_match = vm_form.startswith(ud_number_norm+' ')
        ud_case = ud_feats['Case']
        assert ud_case in ud_to_vm_case_mapping, \
               '(!) Unexpected case {!r} in: {!r}'.format(ud_case, ud_word_record)
        case_match = vm_form.endswith(' '+ud_to_vm_case_mapping[ud_case])
        # Special case: long illative
        if ud_case == 'Ill' and not case_match:
            # Try to match the "long illative" with the short one 
            case_match   = vm_form.endswith('adt')
            number_match = (ud_number_norm == 'sg')
        # Special case: numbers with digits in singular nominative:
        #   ( allow Vabamorf to leave case unspecified )
        if ud_xpos in ['N', 'O'] and vm_pos in ['N', 'O']:
            if vm_word_record['form'] in ['?', '']      and \
               ud_feats.get('NumForm', None) == 'Digit' and \
               ud_feats.get('Case', None)    == 'Nom'   and \
               ud_feats.get('Number', None)  == 'Sing':
                return True
        return number_match and case_match
    # Empty forms: adjectives without case info
    ud_no_number_nor_case = ('Number' not in ud_feats) and ('Case' not in ud_feats)
    ud_degree    = ud_feats.get('Degree',   None)
    ud_verb_form = ud_feats.get('VerbForm', None)
    if ud_xpos == 'A' and ud_degree == 'Pos' and vm_pos == 'A':
        if len(vm_word_record['form']) == 0 and ud_no_number_nor_case:
            return True
        if ud_verb_form == 'Sup' and ud_feats.get('Case', None) == 'Abe':
            if len(vm_word_record['form']) == 0 and \
               vm_word_record['root'].endswith('mata'):
                return True
    if ud_xpos == 'A' and ud_upos == 'DET' and vm_pos == 'A':
        if len(vm_word_record['form']) == 0 and ud_no_number_nor_case:
            return True
    if ud_xpos == 'G' and vm_pos == 'G':
        if len(vm_word_record['form']) == 0 and ud_no_number_nor_case:
            return True
    # Empty forms: adverbs, adpositions, conjunctions and punctuation
    if ud_xpos == 'D' and vm_pos == 'D':
        if len(vm_word_record['form']) == 0 and ud_no_number_nor_case:
            return True
    if ud_xpos == 'K' and vm_pos == 'K':
        if len(vm_word_record['form']) == 0 and ud_no_number_nor_case:
            return True
    if ud_xpos == 'J' and vm_pos == 'J':
        if len(vm_word_record['form']) == 0 and ud_no_number_nor_case:
            return True
    if ud_xpos == 'X' and vm_pos == 'X':
        if len(vm_word_record['form']) == 0 and ud_no_number_nor_case:
            return True
    if ud_xpos == 'Z' and vm_pos == 'Z':
        if len(vm_word_record['form']) == 0 and ud_no_number_nor_case:
            return True
    if ud_xpos == 'nominal' and ud_upos=='SYM' and vm_pos == 'Z':
        if len(vm_word_record['form']) == 0 and ud_no_number_nor_case:
            return True
    # Empty forms: "particles", interjections, emoticons
    if ud_xpos in ['I', 'B'] and vm_pos in ['I', 'B']:
        if len(vm_word_record['form']) == 0 and ud_no_number_nor_case:
            return True
    if ud_xpos == 'E' and vm_pos in ['Z', 'E']:
        if len(vm_word_record['form']) == 0 and ud_no_number_nor_case:
            return True
    # Missing case information in abbreviations and numbers
    if ud_xpos == 'Y' and vm_pos == 'Y':
        if vm_word_record['form'] in ['?',''] and ud_no_number_nor_case:
            return True
    ud_num_type = ud_feats.get('NumType', None) # Card, Ord
    # Empty forms: numbers without case information
    if ud_xpos in ['N', 'O'] and vm_pos in ['N', 'O']:
        if vm_word_record['form'] in ['?', ''] and ud_no_number_nor_case:
            return True
    # If both are empty then we can declare a match
    if len(vm_word_record['form']) == 0 and len(ud_feats.keys()) == 0:
        return True
    # Match verbs
    if ud_xpos == 'V' and vm_pos == 'V':
        # Get UD's category values
        ud_verb_form   = ud_feats.get('VerbForm', None)     # Fin, Inf, Part, Sup, Conv
        ud_voice       = ud_feats.get('Voice',    None)     # Act, Pass
        ud_mood        = ud_feats.get('Mood',     None)     # Ind, Imp, Cnd, Qou
        ud_case        = ud_feats.get('Case',     None)     # Ill, Ine, Ela, Tra, Abe
        ud_number      = ud_feats.get('Number',   None)     # Plur, Sing
        ud_person      = ud_feats.get('Person',   None)     # 1, 2, 3
        ud_tense       = ud_feats.get('Tense',    None)     # Past, Pres
        ud_polarity    = ud_feats.get('Polarity', None)     # Neg
        ud_connegative = ud_feats.get('Connegative', None)  # Yes
        assert not (ud_xpos == 'V' and ud_case != None and ud_number != None), \
               '(!) There should be no such verb: {!r}!'.format( ud_word_record )
        # V1) Infinite forms
        # pure infinite
        if ud_verb_form == 'Inf' and vm_form == 'da':
            return True
        # supine personal
        if ud_verb_form == 'Sup' and ud_voice == 'Act':
            if ud_case == 'Ill' and vm_form == 'ma':
                return True
            if ud_case == 'Ine' and vm_form == 'mas':
                return True
            if ud_case == 'Ela' and vm_form == 'mast':
                return True
            if ud_case == 'Tra' and vm_form == 'maks':
                return True
            if ud_case == 'Abe' and vm_form == 'mata':
                return True
        # supine impersonal
        if ud_verb_form == 'Sup' and ud_voice == 'Pass':
            if vm_form == 'tama':
                return True
        # nud/tud
        if ud_verb_form == 'Part' and ud_tense == 'Past':
            if ud_voice == 'Act'  and vm_form == 'nud':
                return True
            if ud_voice == 'Pass' and vm_form == 'tud':
                return True
        # ger
        if ud_verb_form == 'Conv' and vm_form == 'des':
            return True
        # V2) Negatives:
        if ud_polarity == 'Neg' or ud_connegative == 'Yes':
           # neg auxiliary
           if ud_upos == 'AUX' and vm_form == 'neg':
                return True
           # neg personal 
           if ud_voice == 'Act':
               # # Ind, Imp, Cnd, Qou
               if ud_mood == 'Ind' and ud_tense == 'Pres' and vm_form in ['o', 'neg o']:
                    return True
               if ud_mood == 'Imp' and ud_tense == 'Pres' and ud_person == '2' and ud_number == 'Sing' and \
                  vm_form in ['o']:
                    return True
               if ud_mood == 'Imp' and ud_tense == 'Pres' and ud_person == '2' and ud_number == 'Plur' and \
                  vm_form in ['neg ge']:
                    return True
               if ud_mood == 'Imp' and ud_tense == 'Pres' and ud_person == '3' and ud_number == 'Plur' and \
                  vm_form in ['neg gu']:
                    return True
               if ud_mood == 'Ind' and ud_tense == 'Past' and vm_form in ['nud', 'neg nud']:
                    return True
               if ud_mood == 'Cnd' and ud_tense == 'Pres' and vm_form in ['neg ks', 'ks']:
                    return True
           # neg impersonal 
           if ud_voice == 'Pass':
               if ud_mood == 'Ind' and ud_tense == 'Pres' and vm_form in ['ta']:
                    return True
        ud_affirmative = (not ud_polarity == 'Neg') and (not ud_connegative == 'Yes')
        # V3) Indicative, affirmative
        if ud_affirmative and ud_mood == 'Ind':
            # Present tense
            if ud_number == 'Sing'   and ud_tense == 'Pres' and ud_person == '1' and vm_form == 'n':
                return True
            if ud_number == 'Plur'   and ud_tense == 'Pres' and ud_person == '1' and vm_form == 'me':
                return True
            if ud_number == 'Sing'   and ud_tense == 'Pres' and ud_person == '2' and vm_form == 'd':
                return True
            if ud_number == 'Plur'   and ud_tense == 'Pres' and ud_person == '2' and vm_form == 'te':
                return True
            if ud_number == 'Sing'   and ud_tense == 'Pres' and ud_person == '3' and vm_form == 'b':
                return True
            if ud_number == 'Plur'   and ud_tense == 'Pres' and ud_person == '3' and vm_form == 'vad':
                return True
            if ud_voice == 'Pass' and ud_tense == 'Pres' and ud_person == None    and vm_form == 'takse':
                # Passive voice
                return True
            # Past tense
            if ud_number == 'Sing'  and ud_tense == 'Past' and ud_person == '1' and vm_form == 'sin':
                return True
            if ud_number == 'Plur'  and ud_tense == 'Past' and ud_person == '1' and vm_form == 'sime':
                return True
            if ud_number == 'Sing'  and ud_tense == 'Past' and ud_person == '2' and vm_form == 'sid':
                return True
            if ud_number == 'Plur'  and ud_tense == 'Past' and ud_person == '2' and vm_form == 'site':
                return True
            if ud_number == 'Sing'  and ud_tense == 'Past' and ud_person == '3' and vm_form == 's':
                return True
            if ud_number == 'Plur'  and ud_tense == 'Past' and ud_person == '3' and vm_form == 'sid':
                return True
            if ud_voice == 'Pass' and ud_tense == 'Past' and ud_person == None and vm_form == 'ti':
                # Passive voice
                return True
        # V4) Imperative, affirmative
        if ud_affirmative and ud_mood == 'Imp':
            if ud_number == 'Sing'  and ud_tense == 'Pres' and ud_person == None and ud_voice == 'Act' and \
               vm_form == 'gu':
                return True
            if ud_number == 'Sing'  and ud_tense == 'Pres' and ud_person == '2' and ud_voice == 'Act' and \
               vm_form == 'o':
                return True
            if ud_number == 'Sing'  and ud_tense == 'Pres' and ud_person == '3' and ud_voice == 'Act' and \
               vm_form == 'gu':
                return True
            if ud_number == 'Plur'  and ud_tense == 'Pres' and ud_person == '1' and ud_voice == 'Act' and \
               vm_form == 'gem':
                return True
            if ud_number == 'Plur'  and ud_tense == 'Pres' and ud_person == '2' and ud_voice == 'Act' and \
               vm_form == 'ge':
                return True
            if ud_number == 'Plur'  and ud_tense == 'Pres' and ud_person == '3' and ud_voice == 'Act' and \
               vm_form == 'gu':
                return True
        # V5) Quotative, affirmative
        if ud_affirmative and ud_mood == 'Qot':
            if ud_tense == 'Pres' and ud_voice == 'Act' and \
               vm_form in ['vat']:
                return True
            if ud_tense == 'Pres' and ud_voice == 'Pass' and \
               vm_form in ['tavat']:
                return True
        # V6) Conditional, affirmative
        if ud_affirmative and ud_mood == 'Cnd':
            # Present tense
            if ud_tense == 'Pres' and ud_voice == 'Act' and ud_number == 'Sing' and ud_person == '1' and \
               vm_form in ['ksin', 'ks']:
                return True
            if ud_tense == 'Pres' and ud_voice == 'Act' and ud_number == 'Sing' and ud_person == '2' and \
               vm_form in ['ksid', 'ks']:
                return True
            if ud_tense == 'Pres' and ud_voice == 'Act' and ud_number == 'Sing' and ud_person == '3' and \
               vm_form in ['ks']:
                return True
            if ud_tense == 'Pres' and ud_voice == 'Act' and ud_number == 'Plur' and ud_person == '1' and \
               vm_form in ['ksime', 'ks']:
                return True
            if ud_tense == 'Pres' and ud_voice == 'Act' and ud_number == 'Plur' and ud_person == '2' and \
               vm_form in ['ksite', 'ks']:
                return True
            if ud_tense == 'Pres' and ud_voice == 'Act' and ud_number == 'Plur' and ud_person == '3' and \
               vm_form in ['ksid', 'ks']:
                return True
            if ud_voice == 'Act'  and ud_tense == 'Pres' and ud_person == None  and  \
               vm_form == 'ks':
                return True
            # Past tense
            if ud_tense == 'Past' and ud_voice == 'Act' and ud_number == 'Sing' and ud_person == '1' and \
               vm_form in ['nuksin', 'nuks']:
                return True
            if ud_tense == 'Past' and ud_voice == 'Act' and ud_number == 'Sing' and ud_person == '2' and \
               vm_form in ['nuksid', 'nuks']:
                return True
            if ud_tense == 'Past' and ud_voice == 'Act' and ud_number == 'Sing' and ud_person == '3' and \
               vm_form in ['nuks']:
                return True
            if ud_tense == 'Past' and ud_voice == 'Act' and ud_number == 'Plur' and ud_person == '1' and \
               vm_form in ['nuksime', 'nuks']:
                return True
            if ud_tense == 'Past' and ud_voice == 'Act' and ud_number == 'Plur' and ud_person == '2' and \
               vm_form in ['nuksite', 'nuks']:
                return True
            if ud_tense == 'Past' and ud_voice == 'Act' and ud_number == 'Plur' and ud_person == '3' and \
               vm_form in ['nuksid', 'nuks']:
                return True
        if ud_mood == 'Cnd'  and ud_tense == 'Pres' and ud_voice == 'Pass' and ud_number == None  and ud_person == None and \
           vm_form in ['taks']:
            # Conditional impersonal
            return True
    return False

# ===========================================================================
# ===========================================================================
#   Comparing annotations. Getting statistics
# ===========================================================================
# ===========================================================================

class VM2EWTBMorphDiffTagger(Tagger):
    """Finds differences between Vabamorf's morph analysis layer and EWTB's morph analysis (ud_syntax) layer."""
    
    conf_param = ['vm_morph_layer', 'ud_syntax_layer', 'compare_function', 
                  'count_mismatch_details', 'show_lemmas', 'show_postags', 'show_forms']
    output_attributes = ('root_match', 'pos_match', 'form_match')
    
    def __init__(self,
                 vm_morph_layer: str,
                 ud_syntax_layer: str,
                 output_layer: str,
                 compare_function = align_records,
                 count_mismatch_details: bool = True,
                 show_lemmas: bool  = True,
                 show_postags: bool = True, 
                 show_forms: bool   = True ):
         self.input_layers = [vm_morph_layer, ud_syntax_layer]
         self.vm_morph_layer  = vm_morph_layer
         self.ud_syntax_layer = ud_syntax_layer
         self.output_layer = output_layer
         self.compare_function = compare_function
         self.count_mismatch_details = False
         if count_mismatch_details:
             self.count_mismatch_details = True
         self.show_forms = False
         if show_forms:
             self.show_forms = True
             self.output_attributes = ('vm_form', 'ud_form') + self.output_attributes
         self.show_postags = False
         if show_postags:
             self.show_postags = True
             self.output_attributes = ('vm_pos', 'ud_pos') + self.output_attributes
         self.show_lemmas = False
         if show_lemmas:
             self.show_lemmas = True
             self.output_attributes = ('vm_root', 'ud_lemma') + self.output_attributes


    def _make_layer(self, text, layers, status):
        vm_layer = layers[ self.vm_morph_layer  ]
        ud_layer = layers[ self.ud_syntax_layer ]
        assert vm_layer.text_object is ud_layer.text_object
        assert len(vm_layer) == len(ud_layer), \
                '(!) Layers contain unequal number of elements: {} vs {}'.format( len(vm_layer), len(ud_layer) )
        layer = Layer(
            name=self.output_layer,
            parent=self.vm_morph_layer,
            attributes=self.output_attributes,
            text_object=vm_layer.text_object,
            ambiguous=True
            )
        comparable_items = 0
        matching_items   = 0
        mismatching_proper_names = 0
        mismatching_punct        = 0
        mismatching_symbols      = 0
        words_ambiguities = []
        for wid, morph_word in enumerate( vm_layer ):
            # Get comparable records
            ud_word = ud_layer[wid]
            ud_word_records = ud_word.to_records()
            vm_word_records = morph_word.to_records()
            if isinstance( ud_word_records, dict ):
                ud_word_records = [ ud_word_records ]
            words_ambiguities.append( len(vm_word_records) )
            # Get the result
            matches_table, has_full_match = \
                self.compare_function( ud_word_records, vm_word_records )
            if has_full_match:
                matching_items += 1
            if not has_full_match:
                for mid, [root_match, pos_match, form_match] in enumerate(matches_table):
                    vm_morph_annotation = morph_word.annotations[mid]
                    attributes = {
                        'root_match': root_match, 
                        'pos_match':  pos_match, 
                        'form_match': form_match
                    }
                    if self.show_lemmas:
                        attributes['vm_root']  = vm_word_records[mid]['root']
                        attributes['ud_lemma'] = ud_word_records[0]['lemma']
                    if self.show_postags:
                        attributes['vm_pos'] = vm_word_records[mid]['partofspeech']
                        attributes['ud_pos'] = ud_word_records[0]['xpostag']+'_'+ud_word_records[0]['upostag']
                    if self.show_forms:
                        attributes['vm_form'] = vm_word_records[mid]['form']
                        attributes['ud_form'] = ud_word_records[0]['feats']
                    layer.add_annotation(vm_morph_annotation.span, **attributes)
                # Record type of mismatch
                if self.count_mismatch_details:
                    xpostag = ud_word_records[0]['xpostag']
                    upostag = ud_word_records[0]['upostag']
                    if upostag == 'PROPN':
                        mismatching_proper_names += 1
                    if upostag == 'PUNCT':
                        mismatching_punct += 1
                    if upostag == 'SYM':
                        mismatching_symbols += 1
            comparable_items += 1
        layer.meta['words_total'] = comparable_items
        layer.meta['matching_words'] = matching_items
        layer.meta['mismatching_words'] = comparable_items - matching_items
        layer.meta['avg_variants_per_word'] = sum(words_ambiguities) / len(words_ambiguities)
        layer.meta['ambiguous_words'] = len([amb for amb in words_ambiguities if amb > 1])
        if self.count_mismatch_details:
            layer.meta['mismatching_propn_words'] = mismatching_proper_names
            layer.meta['mismatching_punct_words'] = mismatching_punct
            layer.meta['mismatching_symb_words']  = mismatching_symbols
        return layer


# ===========================================================================
# ===========================================================================


def get_diff_statistics( texts_list, diff_layer, leave_out_udpos=[], ascii_format=True ):
    '''Acquires detailed statistics about morphological annotation mismatches in text objects. Returns a dict with results.'''
    assert isinstance(texts_list, list), \
           '(!) The first input argument must be a list of Text objects.'
    assert all([isinstance(text, Text) for text in texts_list]), \
           '(!) The first input argument must be a list of Text objects.'
    assert isinstance(leave_out_udpos, list), \
           '(!) leave_out_udpos must be a list of strings.'
    assert all([isinstance(udpos, str) for udpos in leave_out_udpos]), \
           '(!) leave_out_udpos must be a list of strings.'
    mismatches_stats = defaultdict(int)
    mismatches_total = 0
    words_total      = 0
    ambiguous_words  = 0
    macro_avg_variants_per_word = []
    for text in texts_list:
        assert diff_layer in text.layers.keys(), \
               '(!) Text {!r} is missing the layer {!r}.'.format( text, diff_layer )
        mismatches_in_text = 0
        for difference in text[diff_layer]:
            recs = difference.to_records()
            # Find vm analysis that contains maximum amount of matches
            maximal_mismatch_str = None
            maximal_match_count  = 0
            # Apply filters (if required)
            if leave_out_udpos:
                unwanted_udpos = [udpos for udpos in leave_out_udpos if udpos in recs[0]['ud_pos']]
                if len(unwanted_udpos) > 0:
                    continue
            for rec in recs:
                root_match = rec['root_match']
                pos_match  = rec['pos_match']
                form_match = rec['form_match']
                c = ([root_match, pos_match, form_match]).count( True )
                if c >= maximal_match_count:
                    maximal_match_count = c
                    if not ascii_format:
                        # Format for HTML
                        root_str = ' + ROOT ' if root_match else ' – ROOT '
                        pos_str  = ' + POSTAG ' if pos_match  else ' – POSTAG '
                        form_str = ' + FORM ' if form_match else ' – FORM '
                    else:
                        # Format for terminal
                        root_str = '(+) ROOT ' if root_match else '(-) ROOT '
                        pos_str  = '(+) POSTAG ' if pos_match  else '(-) POSTAG '
                        form_str = '(+) FORM ' if form_match else '(-) FORM '
                    maximal_mismatch_str = root_str+'|'+pos_str+'|'+form_str
            # Record the maximal match
            mismatches_stats[maximal_mismatch_str] += 1
            mismatches_in_text += 1
        mismatches_total += mismatches_in_text
        words_total      += text[diff_layer].meta['words_total']
        ambiguous_words  += text[diff_layer].meta['ambiguous_words']
        macro_avg_variants_per_word.append( text[diff_layer].meta['avg_variants_per_word'] )
    from statistics import mean as py_mean
    results = {
       'text_objects' : len(texts_list),
       'words_total'  : words_total,
       'mismatches_total' : mismatches_total,
       'mismatches_statistics' : mismatches_stats,
       'ambiguous_total' : ambiguous_words,
       'avg_analyses_per_word': round( py_mean(macro_avg_variants_per_word), 2)
    }
    # Add percentages
    def percent_str(x, all):
        return '({:.2f}%)'.format(x*100.0/all)
    results['mismatches_%'] = percent_str(mismatches_total, words_total)
    mismatches_stats_per = defaultdict(str)
    for key in mismatches_stats.keys():
        mismatches_stats_per[key] = percent_str(mismatches_stats[key], mismatches_total)
    results['mismatches_statistics_%'] = mismatches_stats_per
    results['ambiguous_words_%'] = percent_str(ambiguous_words, words_total)
    return results



def diff_statistics_html_table( texts_list, diff_layer, leave_out_udpos=[], display=True, show_ambiguity=False ):
    '''Finds detailed difference statistics (uses method get_diff_statistics()) and outputs results as an HTML table.'''
    results = get_diff_statistics( texts_list, diff_layer, leave_out_udpos=leave_out_udpos, ascii_format=False )
    import pandas
    from IPython.display import HTML, display
    pandas.set_option('display.max_colwidth', -1)
    # 1) Overall statistics
    x_filters = 'leave_out_udpos: '+str(leave_out_udpos) if leave_out_udpos else str([])
    overall_results = {'total_words':str(results['words_total']),
                       'texts':results['text_objects'],
                       'mismatching_words':str(results['mismatches_total']),
                       'mismatching_%':results['mismatches_%'],
                       'filters': x_filters }
    overall_table = pandas.DataFrame(data=overall_results,
                                     columns=['texts','total_words', 'mismatching_words', 'mismatching_%', 'filters'],
                                     index=[0])
    table = overall_table.to_html(index=False)
    table = ['<h4>Summary of morphological analyses matching</h4>', table]
    if show_ambiguity:
        # 2) Get detailed ambiguity statistics
        amb_results = {'ambiguous_words':     str(results['ambiguous_total']),
                       'ambiguous_%':         str(results['ambiguous_words_%']),
                       'avg_analyses_per_word': str(results['avg_analyses_per_word'])
        }
        amb_table = pandas.DataFrame(data=amb_results,
                                     columns=['ambiguous_words','ambiguous_%', 'avg_analyses_per_word'],
                                     index=[0])
        table.extend( ('<h4>Details on ambiguity</h4>', amb_table.to_html(index=False),) )
    else:
        # 2) Get detailed mismatch statistics
        mm_labels = sorted( list(results['mismatches_statistics'].keys()), \
                            key=results['mismatches_statistics'].get, \
                            reverse=True )
        mm_values = [ ( str(results['mismatches_statistics'][label]),str(results['mismatches_statistics_%'][label]) ) for label in mm_labels ]
        missed_table = pandas.DataFrame(mm_values, index=mm_labels)
        #missed_table.style.set_properties(**{'text-align': 'left'})
        missed_table.style.set_table_styles(
              [{"selector": "th", "props": [("text-align", "left")]}]
        )
        missed_table = missed_table.to_html(header=False)
        table.extend( ('<h4>Details on mismatches</h4>', missed_table,) )
    return '\n'.join(table) if not display else display(HTML('\n'.join(table)))

