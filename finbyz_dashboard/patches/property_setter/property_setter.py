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
    doc2.property = "reqd"
    doc2.property_type = "Check"
    doc2.value = "0"
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

    doc5 = frappe.new_doc("Property Setter")
    doc5.doctype_or_field = "DocField"
    doc5.doc_type = "Dashboard Chart"
    doc5.field_name = "type"
    doc5.property = "hidden"
    doc5.property_type = "Check"
    doc5.value = "1"
    doc5.insert()

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
