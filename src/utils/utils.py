from xml.etree.ElementTree import Element, SubElement


def parse_multiplicity(mult):
    if ".." in mult:
        min_mult, max_mult = mult.split("..")
        return min_mult, max_mult
    return mult, mult


def generate_xml(class_name, classes):
    cls = classes[class_name]
    elem = Element(class_name)
    for attr in cls["attributes"]:
        attr_elem = SubElement(elem, attr["name"])
        attr_elem.text = attr["type"]
    for child in cls["children"]:
        child_elem = generate_xml(child, classes)
        elem.append(child_elem)
    return elem
