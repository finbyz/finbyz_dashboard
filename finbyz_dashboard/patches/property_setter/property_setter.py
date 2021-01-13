from __future__ import unicode_literals
import frappe

def execute():
    doc = frappe.new_doc("Property Setter")
    doc.doctype_or_field = "DocField"
    doc.doc_type = "Dashboard Chart"
    doc.field_name = "document_type"
    doc.property = "depends_on"
    doc.property_type = "Data"
    doc.value = "eval: doc.chart_type !== 'Custom' && doc.chart_type !== 'Report'"
    doc.insert()

    doc1 = frappe.new_doc("Property Setter")
    doc1.doctype_or_field = "DocField"
    doc1.doc_type = "Dashboard Chart"
    doc1.field_name = "chart_type"
    doc1.property = "options"
    doc1.property_type = "Text"
    doc1.value = "Count\nSum\nAverage\nGroup By\nCustom\nReport"
    doc1.insert()

    doc2 = frappe.new_doc("Property Setter")
    doc2.doctype_or_field = "DocField"
    doc2.doc_type = "Dashboard Chart"
    doc2.field_name = "type"
    doc2.property = "options"
    doc2.property_type = "Text"
    doc2.value = "Line\nBar\nPercentage\nPie\nDonut\nHeatmap"
    doc2.default = "Line"
    doc2.insert()


    doc3 = frappe.new_doc("Property Setter")
    doc3.doctype_or_field = "DocField"
    doc3.doc_type = "Dashboard Chart"
    doc3.field_name = "width"
    doc3.property = "reqd"
    doc3.property_type = "Check"
    doc3.value = "0"
    doc3.insert()

    doc4 = frappe.new_doc("Property Setter")
    doc4.doctype_or_field = "DocField"
    doc4.doc_type = "Dashboard Chart"
    doc4.field_name = "width"
    doc4.property = "hidden"
    doc4.property_type = "Check"
    doc4.value = "1"
    doc4.insert()


    doc6 = frappe.new_doc("Property Setter")
    doc6.doctype_or_field = "DocField"
    doc6.doc_type = "Dashboard Chart"
    doc6.field_name = "based_on"
    doc6.property = "depends_on"
    doc6.property_type = "Data"
    doc6.value = "eval: doc.timeseries && ['Count', 'Sum', 'Average'].includes(doc.chart_type)"
    doc6.insert()

    doc7 = frappe.new_doc("Property Setter")
    doc7.doctype_or_field = "DocField"
    doc7.doc_type = "Dashboard Chart"
    doc7.field_name = "based_on"
    doc7.property = "depends_on"
    doc7.property_type = "Data"
    doc7.value = "eval: doc.timeseries && ['Count', 'Sum', 'Average'].includes(doc.chart_type)"
    doc7.insert()

    doc9 = frappe.new_doc("Property Setter")
    doc9.doctype_or_field = "DocField"
    doc9.doc_type = "Dashboard Chart"
    doc9.field_name = "is_public"
    doc9.property = "default"
    doc9.property_type = "Text"
    doc9.value = "1"
    doc9.insert()

    # doc10 = frappe.new_doc("Custom DocPerm")
    # doc10.parent = "Dashboard Chart"
    # doc10.role = "System Manager"
    # doc10.permlevel = 3
    # doc10.read = 1
    # doc10.write = 1
    # doc10.submit = 1
    # doc10.cancel = 1
    # doc10.create = 1
    # doc10.delete = 1
    # doc10.export = 1
    # doc10.save(ignore_permissions=True)

    # doc11 = frappe.new_doc("Custom DocPerm")
    # doc11.parent = "Dashboard"
    # doc11.role = "System Manager"
    # doc11.permlevel = 3
    # doc11.read = 1
    # doc11.write = 1
    # doc11.submit = 1
    # doc11.cancel = 1
    # doc11.create = 1
    # doc11.delete = 1
    # doc11.export = 1
    # doc11.save(ignore_permissions=True)

    # doc12 = frappe.new_doc("Custom DocPerm")
    # doc12.parent = "Number Card"
    # doc12.role = "System Manager"
    # doc12.permlevel = 3
    # doc12.read = 1
    # doc12.write = 1
    # doc12.submit = 1
    # doc12.cancel = 1
    # doc12.create = 1
    # doc12.delete = 1
    # doc12.export = 1
    # doc12.save(ignore_permissions=True)