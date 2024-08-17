import logging
from typing import Any, Dict, List, Type

import ipdb


class GeneralMethods:
    def to_dict(self, obj: Type = None):
        # https://stackoverflow.com/questions/7963762/what-is-the-most-economical-way-to-convert-nested-python-objects-to-dictionaries
        def my_dict(obj):
            if not hasattr(obj, "__dict__"):
                if isinstance(obj, dict):
                    result = {}
                    for key, val in obj.items():
                        result[key] = my_dict(val)
                    return result
                elif isinstance(obj, list):
                    return [my_dict(item) for item in obj]
                else:
                    return obj

            result = {}
            for key, val in obj.__dict__.items():
                if key.startswith("_"):
                    continue
                if isinstance(val, dict):
                    result[key] = {k: my_dict(v) for k, v in val.items()}
                elif isinstance(val, list):
                    result[key] = [my_dict(item) for item in val]
                else:
                    result[key] = my_dict(val)
            return result

        return my_dict(self if obj is None else obj)

    @staticmethod
    def from_dict(cls: Type, dict_obj: Dict[str, Any], classes: List[Type] = []) -> Any:
        classes_dict = {cls.__name__: cls for cls in classes}

        def my_instance(cls: Type, obj: Type):
            nonlocal classes_dict
            try:
                instance = cls()
            except TypeError:
                instance = cls
            except Exception as e:
                logging.error(e)
            for key, value in obj.items():
                if isinstance(value, dict):
                    class_name = GeneralMethods.cat_to_class(key)
                    for k, v in value.items():
                        if class_name in classes_dict:
                            sub_cls = classes_dict[class_name]
                            sub_instance = my_instance(sub_cls, v)
                            getattr(instance, key)[k] = sub_instance
                        else:
                            getattr(instance, key)[k] = v
                elif isinstance(value, list):
                    class_name = GeneralMethods.cat_to_class(key)
                    for el in value:
                        if class_name in classes_dict:
                            sub_cls = classes_dict[class_name]
                            # ipdb.set_trace() # temp
                            sub_instance = my_instance(sub_cls, el)
                            getattr(instance, key).append(sub_instance)
                        else:
                            getattr(instance, key).append(el)
                else:
                    setattr(instance, key, value)
            return instance

        return my_instance(cls, dict_obj)

    @staticmethod
    def class_to_cat(instance: Type) -> str:
        class_str = type(instance).__name__
        return class_str[0].lower() + class_str[1:] + "s"

    @staticmethod
    def cat_to_class(cat: str) -> Type:
        return cat[0].upper() + cat[1:-1]
