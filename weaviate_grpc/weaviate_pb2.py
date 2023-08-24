# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: weaviate.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eweaviate.proto\x12\x0cweaviategrpc\x1a\x1cgoogle/protobuf/struct.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"A\n\x13\x42\x61tchObjectsRequest\x12*\n\x07objects\x18\x01 \x03(\x0b\x32\x19.weaviategrpc.BatchObject\"\x81\x04\n\x0b\x42\x61tchObject\x12\x0c\n\x04uuid\x18\x01 \x01(\t\x12\x0e\n\x06vector\x18\x02 \x03(\x02\x12\x38\n\nproperties\x18\x03 \x01(\x0b\x32$.weaviategrpc.BatchObject.Properties\x12\x12\n\nclass_name\x18\x04 \x01(\t\x12\x0e\n\x06tenant\x18\x05 \x01(\t\x1a\xdd\x01\n\nProperties\x12\x33\n\x12non_ref_properties\x18\x01 \x01(\x0b\x32\x17.google.protobuf.Struct\x12M\n\x10ref_props_single\x18\x02 \x03(\x0b\x32\x33.weaviategrpc.BatchObject.RefPropertiesSingleTarget\x12K\n\x0fref_props_multi\x18\x03 \x03(\x0b\x32\x32.weaviategrpc.BatchObject.RefPropertiesMultiTarget\x1a=\n\x19RefPropertiesSingleTarget\x12\r\n\x05uuids\x18\x01 \x03(\t\x12\x11\n\tprop_name\x18\x02 \x01(\t\x1aW\n\x18RefPropertiesMultiTarget\x12\r\n\x05uuids\x18\x01 \x03(\t\x12\x11\n\tprop_name\x18\x02 \x01(\t\x12\x19\n\x11target_collection\x18\x03 \x01(\t\"\x8e\x01\n\x11\x42\x61tchObjectsReply\x12=\n\x07results\x18\x01 \x03(\x0b\x32,.weaviategrpc.BatchObjectsReply.BatchResults\x12\x0c\n\x04took\x18\x02 \x01(\x02\x1a,\n\x0c\x42\x61tchResults\x12\r\n\x05index\x18\x01 \x01(\x05\x12\r\n\x05\x65rror\x18\x02 \x01(\t\"\xe3\x03\n\rSearchRequest\x12\x12\n\nclass_name\x18\x01 \x01(\t\x12\r\n\x05limit\x18\x02 \x01(\r\x12\x41\n\x15\x61\x64\x64itional_properties\x18\x03 \x01(\x0b\x32\".weaviategrpc.AdditionalProperties\x12\x33\n\x0bnear_vector\x18\x04 \x01(\x0b\x32\x1e.weaviategrpc.NearVectorParams\x12\x33\n\x0bnear_object\x18\x05 \x01(\x0b\x32\x1e.weaviategrpc.NearObjectParams\x12,\n\nproperties\x18\x06 \x01(\x0b\x32\x18.weaviategrpc.Properties\x12\x37\n\rhybrid_search\x18\x07 \x01(\x0b\x32 .weaviategrpc.HybridSearchParams\x12\x33\n\x0b\x62m25_search\x18\x08 \x01(\x0b\x32\x1e.weaviategrpc.BM25SearchParams\x12\x0e\n\x06offset\x18\t \x01(\r\x12\x0f\n\x07\x61utocut\x18\n \x01(\r\x12\r\n\x05\x61\x66ter\x18\x0b \x01(\t\x12\x0e\n\x06tenant\x18\x0c \x01(\t\x12&\n\x07\x66ilters\x18\r \x01(\x0b\x32\x15.weaviategrpc.Filters\"\x18\n\x08strArray\x12\x0c\n\x04vals\x18\x01 \x03(\t\"\x18\n\x08intArray\x12\x0c\n\x04vals\x18\x01 \x03(\x05\"\x1a\n\nfloatArray\x12\x0c\n\x04vals\x18\x01 \x03(\x01\"\x19\n\tboolArray\x12\x0c\n\x04vals\x18\x01 \x03(\x08\"5\n\tdateArray\x12(\n\x04vals\x18\x01 \x03(\x0b\x32\x1a.google.protobuf.Timestamp\"\xc8\x06\n\x07\x46ilters\x12\x34\n\x08operator\x18\x01 \x01(\x0e\x32\".weaviategrpc.Filters.OperatorType\x12\n\n\x02on\x18\x02 \x03(\t\x12&\n\x07\x66ilters\x18\x03 \x03(\x0b\x32\x15.weaviategrpc.Filters\x12\x13\n\tvalue_str\x18\x04 \x01(\tH\x00\x12\x13\n\tvalue_int\x18\x05 \x01(\x03H\x00\x12\x14\n\nvalue_bool\x18\x06 \x01(\x08H\x00\x12\x15\n\x0bvalue_float\x18\x07 \x01(\x02H\x00\x12\x30\n\nvalue_date\x18\x08 \x01(\x0b\x32\x1a.google.protobuf.TimestampH\x00\x12\x31\n\x0fvalue_str_array\x18\t \x01(\x0b\x32\x16.weaviategrpc.strArrayH\x00\x12\x31\n\x0fvalue_int_array\x18\n \x01(\x0b\x32\x16.weaviategrpc.intArrayH\x00\x12\x33\n\x10value_bool_array\x18\x0b \x01(\x0b\x32\x17.weaviategrpc.boolArrayH\x00\x12\x35\n\x11value_float_array\x18\x0c \x01(\x0b\x32\x18.weaviategrpc.floatArrayH\x00\x12\x33\n\x10value_date_array\x18\r \x01(\x0b\x32\x17.weaviategrpc.dateArrayH\x00\"\xb4\x02\n\x0cOperatorType\x12\x11\n\rOperatorEqual\x10\x00\x12\x14\n\x10OperatorNotEqual\x10\x01\x12\x17\n\x13OperatorGreaterThan\x10\x02\x12\x1c\n\x18OperatorGreaterThanEqual\x10\x03\x12\x14\n\x10OperatorLessThan\x10\x04\x12\x19\n\x15OperatorLessThanEqual\x10\x05\x12\x0f\n\x0bOperatorAnd\x10\x06\x12\x0e\n\nOperatorOr\x10\x07\x12\x1a\n\x16OperatorWithinGeoRange\x10\x08\x12\x10\n\x0cOperatorLike\x10\t\x12\x12\n\x0eOperatorIsNull\x10\n\x12\x17\n\x13OperatorContainsAny\x10\x0b\x12\x17\n\x13OperatorContainsAll\x10\x0c\x42\x0c\n\ntest_value\"\xb4\x01\n\x14\x41\x64\x64itionalProperties\x12\x0c\n\x04uuid\x18\x01 \x01(\x08\x12\x0e\n\x06vector\x18\x02 \x01(\x08\x12\x18\n\x10\x63reationTimeUnix\x18\x03 \x01(\x08\x12\x1a\n\x12lastUpdateTimeUnix\x18\x04 \x01(\x08\x12\x10\n\x08\x64istance\x18\x05 \x01(\x08\x12\x11\n\tcertainty\x18\x06 \x01(\x08\x12\r\n\x05score\x18\x07 \x01(\x08\x12\x14\n\x0c\x65xplainScore\x18\x08 \x01(\x08\"]\n\nProperties\x12\x1a\n\x12non_ref_properties\x18\x01 \x03(\t\x12\x33\n\x0eref_properties\x18\x02 \x03(\x0b\x32\x1b.weaviategrpc.RefProperties\"\xc6\x01\n\x12HybridSearchParams\x12\r\n\x05query\x18\x01 \x01(\t\x12\x12\n\nproperties\x18\x02 \x03(\t\x12\x0e\n\x06vector\x18\x03 \x03(\x02\x12\r\n\x05\x61lpha\x18\x04 \x01(\x02\x12@\n\x0b\x66usion_type\x18\x05 \x01(\x0e\x32+.weaviategrpc.HybridSearchParams.FusionType\",\n\nFusionType\x12\n\n\x06RANKED\x10\x00\x12\x12\n\x0eRELATIVE_SCORE\x10\x01\"5\n\x10\x42M25SearchParams\x12\r\n\x05query\x18\x01 \x01(\t\x12\x12\n\nproperties\x18\x02 \x03(\t\"\xb0\x01\n\rRefProperties\x12\x1a\n\x12reference_property\x18\x02 \x01(\t\x12\x33\n\x11linked_properties\x18\x03 \x01(\x0b\x32\x18.weaviategrpc.Properties\x12\x34\n\x08metadata\x18\x04 \x01(\x0b\x32\".weaviategrpc.AdditionalProperties\x12\x18\n\x10which_collection\x18\x05 \x01(\t\"l\n\x10NearVectorParams\x12\x0e\n\x06vector\x18\x01 \x03(\x02\x12\x16\n\tcertainty\x18\x02 \x01(\x01H\x00\x88\x01\x01\x12\x15\n\x08\x64istance\x18\x03 \x01(\x01H\x01\x88\x01\x01\x42\x0c\n\n_certaintyB\x0b\n\t_distance\"h\n\x10NearObjectParams\x12\n\n\x02id\x18\x01 \x01(\t\x12\x16\n\tcertainty\x18\x02 \x01(\x01H\x00\x88\x01\x01\x12\x15\n\x08\x64istance\x18\x03 \x01(\x01H\x01\x88\x01\x01\x42\x0c\n\n_certaintyB\x0b\n\t_distance\"H\n\x0bSearchReply\x12+\n\x07results\x18\x01 \x03(\x0b\x32\x1a.weaviategrpc.SearchResult\x12\x0c\n\x04took\x18\x02 \x01(\x02\"\x86\x01\n\x0cSearchResult\x12\x32\n\nproperties\x18\x01 \x01(\x0b\x32\x1e.weaviategrpc.ResultProperties\x12\x42\n\x15\x61\x64\x64itional_properties\x18\x02 \x01(\x0b\x32#.weaviategrpc.ResultAdditionalProps\"\xef\x02\n\x15ResultAdditionalProps\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06vector\x18\x02 \x03(\x02\x12\x1a\n\x12\x63reation_time_unix\x18\x03 \x01(\x03\x12\"\n\x1a\x63reation_time_unix_present\x18\x04 \x01(\x08\x12\x1d\n\x15last_update_time_unix\x18\x05 \x01(\x03\x12%\n\x1dlast_update_time_unix_present\x18\x06 \x01(\x08\x12\x10\n\x08\x64istance\x18\x07 \x01(\x02\x12\x18\n\x10\x64istance_present\x18\x08 \x01(\x08\x12\x11\n\tcertainty\x18\t \x01(\x02\x12\x19\n\x11\x63\x65rtainty_present\x18\n \x01(\x08\x12\r\n\x05score\x18\x0b \x01(\x02\x12\x15\n\rscore_present\x18\x0c \x01(\x08\x12\x15\n\rexplain_score\x18\r \x01(\t\x12\x1d\n\x15\x65xplain_score_present\x18\x0e \x01(\x08\"\xc8\x01\n\x10ResultProperties\x12\x33\n\x12non_ref_properties\x18\x01 \x01(\x0b\x32\x17.google.protobuf.Struct\x12\x34\n\tref_props\x18\x02 \x03(\x0b\x32!.weaviategrpc.ReturnRefProperties\x12\x12\n\nclass_name\x18\x03 \x01(\t\x12\x35\n\x08metadata\x18\x04 \x01(\x0b\x32#.weaviategrpc.ResultAdditionalProps\"\\\n\x13ReturnRefProperties\x12\x32\n\nproperties\x18\x01 \x03(\x0b\x32\x1e.weaviategrpc.ResultProperties\x12\x11\n\tprop_name\x18\x02 \x01(\t2\xa4\x01\n\x08Weaviate\x12\x42\n\x06Search\x12\x1b.weaviategrpc.SearchRequest\x1a\x19.weaviategrpc.SearchReply\"\x00\x12T\n\x0c\x42\x61tchObjects\x12!.weaviategrpc.BatchObjectsRequest\x1a\x1f.weaviategrpc.BatchObjectsReply\"\x00\x42#Z!github.com/weaviate/weaviate/grpcb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'weaviate_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z!github.com/weaviate/weaviate/grpc'
  _BATCHOBJECTSREQUEST._serialized_start=95
  _BATCHOBJECTSREQUEST._serialized_end=160
  _BATCHOBJECT._serialized_start=163
  _BATCHOBJECT._serialized_end=676
  _BATCHOBJECT_PROPERTIES._serialized_start=303
  _BATCHOBJECT_PROPERTIES._serialized_end=524
  _BATCHOBJECT_REFPROPERTIESSINGLETARGET._serialized_start=526
  _BATCHOBJECT_REFPROPERTIESSINGLETARGET._serialized_end=587
  _BATCHOBJECT_REFPROPERTIESMULTITARGET._serialized_start=589
  _BATCHOBJECT_REFPROPERTIESMULTITARGET._serialized_end=676
  _BATCHOBJECTSREPLY._serialized_start=679
  _BATCHOBJECTSREPLY._serialized_end=821
  _BATCHOBJECTSREPLY_BATCHRESULTS._serialized_start=777
  _BATCHOBJECTSREPLY_BATCHRESULTS._serialized_end=821
  _SEARCHREQUEST._serialized_start=824
  _SEARCHREQUEST._serialized_end=1307
  _STRARRAY._serialized_start=1309
  _STRARRAY._serialized_end=1333
  _INTARRAY._serialized_start=1335
  _INTARRAY._serialized_end=1359
  _FLOATARRAY._serialized_start=1361
  _FLOATARRAY._serialized_end=1387
  _BOOLARRAY._serialized_start=1389
  _BOOLARRAY._serialized_end=1414
  _DATEARRAY._serialized_start=1416
  _DATEARRAY._serialized_end=1469
  _FILTERS._serialized_start=1472
  _FILTERS._serialized_end=2312
  _FILTERS_OPERATORTYPE._serialized_start=1990
  _FILTERS_OPERATORTYPE._serialized_end=2298
  _ADDITIONALPROPERTIES._serialized_start=2315
  _ADDITIONALPROPERTIES._serialized_end=2495
  _PROPERTIES._serialized_start=2497
  _PROPERTIES._serialized_end=2590
  _HYBRIDSEARCHPARAMS._serialized_start=2593
  _HYBRIDSEARCHPARAMS._serialized_end=2791
  _HYBRIDSEARCHPARAMS_FUSIONTYPE._serialized_start=2747
  _HYBRIDSEARCHPARAMS_FUSIONTYPE._serialized_end=2791
  _BM25SEARCHPARAMS._serialized_start=2793
  _BM25SEARCHPARAMS._serialized_end=2846
  _REFPROPERTIES._serialized_start=2849
  _REFPROPERTIES._serialized_end=3025
  _NEARVECTORPARAMS._serialized_start=3027
  _NEARVECTORPARAMS._serialized_end=3135
  _NEAROBJECTPARAMS._serialized_start=3137
  _NEAROBJECTPARAMS._serialized_end=3241
  _SEARCHREPLY._serialized_start=3243
  _SEARCHREPLY._serialized_end=3315
  _SEARCHRESULT._serialized_start=3318
  _SEARCHRESULT._serialized_end=3452
  _RESULTADDITIONALPROPS._serialized_start=3455
  _RESULTADDITIONALPROPS._serialized_end=3822
  _RESULTPROPERTIES._serialized_start=3825
  _RESULTPROPERTIES._serialized_end=4025
  _RETURNREFPROPERTIES._serialized_start=4027
  _RETURNREFPROPERTIES._serialized_end=4119
  _WEAVIATE._serialized_start=4122
  _WEAVIATE._serialized_end=4286
# @@protoc_insertion_point(module_scope)
