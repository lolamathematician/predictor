import predictor

def dict_equality(dict1, dict2):
    n, m = len(dict1), len(dict2)
    if n != m:
        return False
    for key1 in dict1.keys():
        if not(key1 in dict2 and dict1[key1] == dict2[key1]):
            return False
    return True
rp = predictor.ResultProcessor()
test_dict = {"field1": "value1",
             "field2": "value2",
             "field3": "value3"}
fields_to_keep = ["field1", "field2"]
rp.configure(fields_to_keep)
return_dict = rp.process_one(test_dict)
assert dict_equality(return_dict, {"field2": "value2", "field1": "value1"}), "Dicts not equal, something has gone wrong..."