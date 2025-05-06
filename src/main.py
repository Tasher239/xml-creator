import xml.etree.ElementTree as ET
import json
from xml.etree.ElementTree import tostring

from src.utils.utils import parse_multiplicity, generate_xml


def main():
    tree = ET.parse("input/impulse_test_input.xml")
    root = tree.getroot()

    classes = {}
    for class_elem in root.findall(".//Class"):
        class_name = class_elem.get("name")
        is_root = class_elem.get("isRoot") == "true"
        documentation = class_elem.get("documentation")
        attributes = [
            {"name": attr_elem.get("name"), "type": attr_elem.get("type")}
            for attr_elem in class_elem.findall("Attribute")
        ]
        classes[class_name] = {
            "isRoot": is_root,
            "documentation": documentation,
            "attributes": attributes,
            "children": [],
        }

    multiplicities = {}
    for agg_elem in root.findall(".//Aggregation"):
        source = agg_elem.get("source")
        target = agg_elem.get("target")
        source_mult = agg_elem.get("sourceMultiplicity")
        min_mult, max_mult = parse_multiplicity(source_mult)
        multiplicities[source] = {"min": min_mult, "max": max_mult}
        if target in classes:
            classes[target]["children"].append(source)

    root_class = next((name for name, cls in classes.items() if cls["isRoot"]), None)

    xml_root = generate_xml(root_class, classes)
    xml_str = tostring(xml_root, encoding="unicode")
    with open("out/config.xml", "w") as f:
        f.write(xml_str)

    meta_list = []
    for class_name, cls in classes.items():
        meta = {
            "class": class_name,
            "documentation": cls["documentation"],
            "isRoot": cls["isRoot"],
        }

        if not cls["isRoot"] and class_name in multiplicities:
            meta["min"] = multiplicities[class_name]["min"]
            meta["max"] = multiplicities[class_name]["max"]

        parameters = [
            {"name": attr["name"], "type": attr["type"]} for attr in cls["attributes"]
        ] + [{"name": child, "type": "class"} for child in cls["children"]]
        meta["parameters"] = parameters
        meta_list.append(meta)

    with open("out/meta.json", "w") as f:
        json.dump(meta_list, f, indent=4)

    with open("input/config.json", "r") as f:
        config = json.load(f)
    with open("input/patched_config.json", "r") as f:
        patched_config = json.load(f)

    additions = [
        {"key": key, "value": patched_config[key]}
        for key in patched_config
        if key not in config
    ]
    deletions = [key for key in config if key not in patched_config]
    updates = [
        {"key": key, "from": config[key], "to": patched_config[key]}
        for key in config
        if key in patched_config and config[key] != patched_config[key]
    ]
    delta = {"additions": additions, "deletions": deletions, "updates": updates}
    with open("out/delta.json", "w") as f:
        json.dump(delta, f, indent=4)

    res_config = config.copy()
    for key in deletions:
        res_config.pop(key, None)
    for update in updates:
        res_config[update["key"]] = update["to"]
    for addition in additions:
        res_config[addition["key"]] = addition["value"]

    with open("out/res_patched_config.json", "w") as f:
        json.dump(res_config, f, indent=4)


if __name__ == "__main__":
    main()
