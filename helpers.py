import os
import xml.etree.cElementTree as element_tree


def indent(elem, level=0):
    i = "\n" + level * "\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def check_or_create_dirs(root_dir, object_name):
    img_directory = root_dir + 'images/' + object_name
    annotation_directory = root_dir + 'annotation/' + object_name

    if not os.path.exists(img_directory):
        os.makedirs(img_directory)

    if not os.path.exists(annotation_directory):
        os.makedirs(annotation_directory)


def create_annotation(root_dir, object_name, file_name, x, y, width, height, orig_width, orig_height):
    annotation = element_tree.Element("annotation")
    element_tree.SubElement(annotation, "folder").text = object_name

    element_tree.SubElement(annotation, "filename").text = file_name
    source = element_tree.SubElement(annotation, "source")
    element_tree.SubElement(source, "database").text = 'DatasetGenerator Onix-Systems'

    size = element_tree.SubElement(annotation, "size")
    element_tree.SubElement(size, "width").text = str(orig_width)
    element_tree.SubElement(size, "height").text = str(orig_height)
    element_tree.SubElement(size, "depth").text = '3'

    element_tree.SubElement(annotation, "segment").text = '0'
    object_xml = element_tree.SubElement(annotation, "object")
    element_tree.SubElement(object_xml, "name").text = object_name

    element_tree.SubElement(object_xml, "pose").text = 'Unspecified'
    element_tree.SubElement(object_xml, "truncated").text = '0'
    element_tree.SubElement(object_xml, "difficult").text = '0'

    bndbox = element_tree.SubElement(object_xml, "bndbox")
    element_tree.SubElement(bndbox, "xmin").text = str(x)
    element_tree.SubElement(bndbox, "ymin").text = str(y)
    element_tree.SubElement(bndbox, "xmax").text = str(x + width)
    element_tree.SubElement(bndbox, "ymax").text = str(y + height)

    indent(annotation)
    tree = element_tree.ElementTree(annotation)

    tree.write(root_dir + 'annotation/' + object_name + '/' + file_name, encoding="utf-8")
