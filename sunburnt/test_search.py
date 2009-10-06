from __future__ import absolute_import

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import datetime
import mx.DateTime

from .schema import SolrSchema, SolrError
from .search import SolrSearch, PaginateOptions, FacetOptions, HighlightOptions, MoreLikeThisOptions

schema_string = \
"""<schema name="timetric" version="1.1">
  <types>
    <fieldType name="string" class="solr.StrField" sortMissingLast="true" omitNorms="true"/>
    <fieldType name="text" class="solr.TextField" sortMissingLast="true" omitNorms="true"/>
    <fieldType name="boolean" class="solr.BoolField" sortMissingLast="true" omitNorms="true"/>
    <fieldType name="int" class="solr.IntField" sortMissingLast="true" omitNorms="true"/>
    <fieldType name="sint" class="solr.SortableIntField" sortMissingLast="true" omitNorms="true"/>
    <fieldType name="long" class="solr.LongField" sortMissingLast="true" omitNorms="true"/>
    <fieldType name="slong" class="solr.SortableLongField" sortMissingLast="true" omitNorms="true"/>
    <fieldType name="float" class="solr.FloatField" sortMissingLast="true" omitNorms="true"/>
    <fieldType name="sfloat" class="solr.SortableFloatField" sortMissingLast="true" omitNorms="true"/>
    <fieldType name="double" class="solr.DoubleField" sortMissingLast="true" omitNorms="true"/>
    <fieldType name="sdouble" class="solr.SortableDoubleField" sortMissingLast="true" omitNorms="true"/>
    <fieldType name="date" class="solr.DateField" sortMissingLast="true" omitNorms="true"/>
  </types>
  <fields>
    <field name="string_field" required="true" type="string"/>
    <field name="text_field" required="true" type="text"/>
    <field name="boolean_field" required="false" type="boolean"/>
    <field name="int_field" required="true" type="int"/>
    <field name="sint_field" type="sint"/>
    <field name="long_field" type="long"/>
    <field name="slong_field" type="slong"/>
    <field name="long_field" type="long"/>
    <field name="slong_field" type="slong"/>
    <field name="float_field" type="float"/>
    <field name="sfloat_field" type="sfloat"/>
    <field name="double_field" type="double"/>
    <field name="sdouble_field" type="sdouble"/>
    <field name="date_field" type="date"/>
  </fields>
  <defaultSearchField>text_field</defaultSearchField>
  <uniqueKey>int_field</uniqueKey>
</schema>"""

schema = SolrSchema(StringIO(schema_string))

class MockInterface(object):
    schema = schema
    def search(self, **kwargs):
        return kwargs


interface = MockInterface()


good_query_data = {
    "query_by_term":(
        (["hello"], {},
         {"q":u"hello"}),
        (["hello"], {"int_field":3},
         {"q":u"hello int_field:3"}),
        (["hello", "world"], {},
         {"q":u"hello world"}),
        # NB this next is not really what we want,
        # probably this should warn
        (["hello world"], {},
         {"q":u"hello world"}),
        ),

    "query_by_phrase":(
        (["hello"], {},
         # Do we actually want this many quotes in here?
         {"q":u"\"hello\""}),
        (["hello"], {"int_field":3},
         {"q":u"int_field:3 \"hello\""}), # Non-text data is always taken to be a term, and terms come before phrases, so order is reversed
        (["hello", "world"], {},
         {"q":u"\"hello\" \"world\""}),
        (["hello world"], {},
         {"q":u"\"hello world\""}),
        ),

    "filter_by_term":(
        (["hello"], {},
         {"fq":u"hello"}),
        (["hello"], {"int_field":3},
         {"fq":u"hello int_field:3"}),
        (["hello", "world"], {},
         {"fq":u"hello world"}),
        # NB this next is not really what we want,
        # probably this should warn
        (["hello world"], {},
         {"fq":u"hello world"}),
        ),

    "filter_by_phrase":(
        (["hello"], {},
         # Do we actually want this many quotes in here?
         {"fq":u"\"hello\""}),
        (["hello"], {"int_field":3},
         {"fq":u"int_field:3 \"hello\""}),
        (["hello", "world"], {},
         {"fq":u"\"hello\" \"world\""}),
        (["hello world"], {},
         {"fq":u"\"hello world\""}),
        ),

    "query":(
        (["hello"], {},
         {"q":u"hello"}),
        (["hello"], {"int_field":3},
         {"q":u"hello int_field:3"}),
        (["hello", "world"], {},
         {"q":u"hello world"}),
        (["hello world"], {},
         {"q":u"\"hello world\""}),
        ),

    "filter":(
        (["hello"], {},
         {"fq":u"hello"}),
        (["hello"], {"int_field":3},
         {"fq":u"hello int_field:3"}),
        (["hello", "world"], {},
         {"fq":u"hello world"}),
        (["hello world"], {},
         {"fq":u"\"hello world\""}),
        ),

    "query":(
        ([], {"boolean_field":True},
         {"q":u"boolean_field:true"}),
        ([], {"boolean_field":"false"},
         {"q":u"boolean_field:true"}), # boolean field takes any truth-y value
        ([], {"boolean_field":0},
         {"q":u"boolean_field:false"}),
        ([], {"int_field":3},
         {"q":u"int_field:3"}),
        ([], {"int_field":3.1}, # casting from float should work
         {"q":u"int_field:3"}),
        ([], {"sint_field":3},
         {"q":u"sint_field:3"}),
        ([], {"sint_field":3.1}, # casting from float should work
         {"q":u"sint_field:3"}),
        ([], {"long_field":2**31},
         {"q":u"long_field:2147483648"}),
        ([], {"slong_field":2**31},
         {"q":u"slong_field:2147483648"}),
        ([], {"float_field":3.0},
         {"q":u"float_field:3.0"}),
        ([], {"float_field":3}, # casting from int should work
         {"q":u"float_field:3.0"}),
        ([], {"sfloat_field":3.0},
         {"q":u"sfloat_field:3.0"}),
        ([], {"sfloat_field":3}, # casting from int should work
         {"q":u"sfloat_field:3.0"}),
        ([], {"double_field":3.0},
         {"q":u"double_field:3.0"}),
        ([], {"double_field":3}, # casting from int should work
         {"q":u"double_field:3.0"}),
        ([], {"sdouble_field":3.0},
         {"q":u"sdouble_field:3.0"}),
        ([], {"sdouble_field":3}, # casting from int should work
         {"q":u"sdouble_field:3.0"}),
        ([], {"date_field":datetime.datetime(2009, 1, 1)},
         {"q":u"date_field:2009-01-01T00:00:00.000000Z"}),
        ([], {"date_field":mx.DateTime.DateTime(2009, 1, 1)},
         {"q":u"date_field:2009-01-01T00:00:00.000000Z"}),
        ),

    "query":(
        ([], {"int_field__lt":3},
         {"q":u"int_field:{* TO 3}"}),
        ([], {"int_field__gt":3},
         {"q":u"int_field:{3 TO *}"}),
        ([], {"int_field__rangeexc":(-3, 3)},
         {"q":u"int_field:{-3 TO 3}"}),
        ([], {"int_field__rangeexc":(3, -3)},
         {"q":u"int_field:{-3 TO 3}"}),
        ([], {"int_field__lte":3},
         {"q":u"int_field:[* TO 3]"}),
        ([], {"int_field__gte":3},
         {"q":u"int_field:[3 TO *]"}),
        ([], {"int_field__range":(-3, 3)},
         {"q":u"int_field:[-3 TO 3]"}),
        ([], {"int_field__range":(3, -3)},
         {"q":u"int_field:[-3 TO 3]"}),
        ),
    }

def check_query_data(method, args, kwargs, output):
    solr_search = SolrSearch(interface)
    assert getattr(solr_search, method)(*args, **kwargs).execute() == output

def test_query_data():
    for method, data in good_query_data.items():
        for args, kwargs, output in data:
            yield check_query_data, method, args, kwargs, output

bad_query_data = (
    {"int_field":"a"},
    {"int_field":2**31},
    {"int_field":-(2**31)-1},
    {"long_field":"a"},
    {"long_field":2**63},
    {"long_field":-(2**63)-1},
    {"float_field":"a"},
    {"float_field":2**1000},
    {"float_field":-(2**1000)},
    {"double_field":"a"},
    {"double_field":2**2000},
    {"double_field":-(2**2000)},
)

def check_bad_query_data(kwargs):
    solr_search = SolrSearch(interface)
    try:
        solr_search.query(**kwargs).execute()
    except SolrError:
        pass
    else:
        assert False

def test_bad_query_data():
    for kwargs in bad_query_data:
        yield check_bad_query_data, kwargs


good_option_data = {
    PaginateOptions:(
        ({"start":5, "rows":10},
         {"start":5, "rows":10}),
        ({"start":5, "rows":None},
         {"start":5}),
        ({"start":None, "rows":10},
         {"rows":10}),
        ),
    FacetOptions:(
        ({"fields":"int_field"},
         {"facet":True, "facet.field":["int_field"]}),
        ({"fields":["int_field", "text_field"]},
         {"facet":True, "facet.field":["int_field","text_field"]}),
        ({"prefix":"abc"},
         {"facet":True, "facet.prefix":"abc"}),
        ({"prefix":"abc", "sort":True, "limit":3, "offset":25, "mincount":1, "missing":False, "method":"enum"},
         {"facet":True, "facet.prefix":"abc", "facet.sort":True, "facet.limit":3, "facet.offset":25, "facet.mincount":1, "facet.missing":False, "facet.method":"enum"}),
        ({"fields":"int_field", "prefix":"abc"},
         {"facet":True, "facet.field":["int_field"], "f.int_field.facet.prefix":"abc"}),
        ({"fields":"int_field", "prefix":"abc", "limit":3},
         {"facet":True, "facet.field":["int_field"], "f.int_field.facet.prefix":"abc", "f.int_field.facet.limit":3}),
        ({"fields":["int_field", "text_field"], "prefix":"abc", "limit":3},
         {"facet":True, "facet.field":["int_field", "text_field"], "f.int_field.facet.prefix":"abc", "f.int_field.facet.limit":3, "f.text_field.facet.prefix":"abc", "f.text_field.facet.limit":3, }),
        ),
    HighlightOptions:(
        ({"fields":"int_field"},
         {"hl":True, "hl.fl":"int_field"}),
        ({"fields":["int_field", "text_field"]},
         {"hl":True, "hl.fl":"int_field,text_field"}),
        ({"snippets":3},
         {"hl":True, "hl.snippets":3}),
        ({"snippets":3, "fragsize":5, "mergeContinuous":True, "requireFieldMatch":True, "maxAnalyzedChars":500, "alternateField":"text_field", "maxAlternateFieldLength":50, "formatter":"simple", "simple.pre":"<b>", "simple.post":"</b>", "fragmenter":"regex", "usePhraseHighlighter":True, "highlightMultiTerm":True, "regex.slop":0.2, "regex.pattern":"\w", "regex.maxAnalyzedChars":100},
        {"hl":True, "hl.snippets":3, "hl.fragsize":5, "hl.mergeContinuous":True, "hl.requireFieldMatch":True, "hl.maxAnalyzedChars":500, "hl.alternateField":"text_field", "hl.maxAlternateFieldLength":50, "hl.formatter":"simple", "hl.simple.pre":"<b>", "hl.simple.post":"</b>", "hl.fragmenter":"regex", "hl.usePhraseHighlighter":True, "hl.highlightMultiTerm":True, "hl.regex.slop":0.2, "hl.regex.pattern":"\w", "hl.regex.maxAnalyzedChars":100}),
        ({"fields":"int_field", "snippets":"3"},
         {"hl":True, "hl.fl":"int_field", "f.int_field.hl.snippets":3}),
        ({"fields":"int_field", "snippets":3, "fragsize":5},
         {"hl":True, "hl.fl":"int_field", "f.int_field.hl.snippets":3, "f.int_field.hl.fragsize":5}),
        ({"fields":["int_field", "text_field"], "snippets":3, "fragsize":5},
         {"hl":True, "hl.fl":"int_field,text_field", "f.int_field.hl.snippets":3, "f.int_field.hl.fragsize":5, "f.text_field.hl.snippets":3, "f.text_field.hl.fragsize":5}),
        ),
    MoreLikeThisOptions:(
        ({"fields":"int_field"},
         {"mlt":True, "mlt.fl":"int_field"}),
        ({"fields":["int_field", "text_field"]},
         {"mlt":True, "mlt.fl":"int_field,text_field"}),
        ({"fields":["text_field", "string_field"], "query_fields":{"text_field":0.25, "string_field":0.75}},
         {"mlt":True, "mlt.fl":"string_field,text_field", "mlt.qf":"text_field^0.25 string_field^0.75"}),
        ({"fields":"text_field", "count":1},
         {"mlt":True, "mlt.fl":"text_field", "mlt.count":1}),
        ),
    }

def check_good_option_data(OptionClass, kwargs, output):
    optioner = OptionClass(schema)
    optioner.update(**kwargs)
    assert optioner.options == output

def test_good_option_data():
    for OptionClass, option_data in good_option_data.items():
        for kwargs, output in option_data:
            yield check_good_option_data, OptionClass, kwargs, output


# All these tests should really nominate which exception they're going to throw.
bad_option_data = {
    PaginateOptions:(
        {"start":-1, "rows":None}, # negative start
        {"start":None, "rows":-1}, # negative rows
        ),
    FacetOptions:(
        {"fields":"myarse"}, # Undefined field
        {"oops":True}, # undefined option
        {"limit":"a"}, # invalid type
        {"sort":"yes"}, # invalid choice
        {"offset":-1}, # invalid value
        ),
    HighlightOptions:(
        {"fields":"myarse"}, # Undefined field
        {"oops":True}, # undefined option
        {"snippets":"a"}, # invalid type
        {"alternateField":"yourarse"}, # another invalid option
        ),
    MoreLikeThisOptions:(
        {"fields":"myarse"}, # Undefined field
        {"fields":"text_field", "query_fields":{"text_field":0.25, "string_field":0.75}}, # string_field in query_fields, not fields
        {"fields":"text_field", "query_fields":{"text_field":"a"}}, # Non-float value for boost
        {"fields":"text_field", "oops":True}, # undefined option
        {"fields":"text_field", "count":"a"} # Invalid value for option
        ),
    }

def check_bad_option_data(OptionClass, kwargs):
    paginate = OptionClass(schema)
    try:
        paginate.update(**kwargs)
    except SolrError:
        pass
    else:
        assert False

def test_bad_option_data():
    for OptionClass, option_data in bad_option_data.items():
        for kwargs in option_data:
            yield check_bad_option_data, OptionClass, kwargs
