"""Excel con el catalogo de productos (Admin > Productos > Exportar Excel).

La hoja Productos tiene las mismas columnas que lee el importador (una fila por variante: presentacion + color + codigo),
asi que el archivo se puede corregir en Excel y volver a subir en Importar Excel. La hoja Detalle trae una fila por
producto con lo que el importador no lee (estado, destacado, rendimiento, descripciones) y es solo de consulta: sus
encabezados no son los del importador, para que nunca se tome por la hoja de productos.
"""
from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Alignment

from import_template import IMPORT_COLUMNS, WIDTHS, _style_header

PRODUCTS_SHEET = 'Productos'
DETAIL_SHEET = 'Detalle (no se importa)'
DETAIL_COLUMNS = ['ID', 'NOMBRE', 'MARCA', 'CATEGORIA', 'SUBCATEGORIA', 'SKU', 'ESTADO', 'DESTACADO', 'PRESENTACIONES',
                  'COLORES', 'VARIANTES', 'VARIANTES CON CODIGO', 'RENDIMIENTO', 'DESCRIPCION', 'DESCRIPCION TECNICA']
DETAIL_WIDTHS = [8, 46, 22, 26, 30, 14, 11, 12, 34, 10, 11, 12, 48, 60, 60]


def _put(ws, row, column, value, as_text=False):
    """Escribe una celda. El texto va sin los caracteres de control que Excel no admite y nunca como formula
    (un nombre que empiece por '=' se queda como texto); as_text conserva los ceros de un codigo ('0883')."""
    if isinstance(value, str):
        value = ILLEGAL_CHARACTERS_RE.sub('', value) or None
    cell = ws.cell(row=row, column=column, value=value)
    if isinstance(cell.value, str):
        cell.data_type = 's'
        if as_text:
            cell.number_format = '@'
    return cell


def build_products_export(products):
    """Libro del catalogo. products: lista de dicts ya ordenados, uno por producto (ver app._export_product_data):
    id, name, brand, category, subcategory, sku, active, featured, presentations (nombres), colors (cuantos), yield (texto),
    description, technical_description y variants [{'code', 'color', 'presentation'}]."""
    wb = Workbook()

    # --- Productos: la hoja que se importa (una fila por variante) ---
    ws = wb.active
    ws.title = PRODUCTS_SHEET
    _style_header(ws, IMPORT_COLUMNS, WIDTHS)
    row = 1
    for p in products:
        for v in p['variants']:
            row += 1
            values = [v['code'], p['category'], p['subcategory'], p['brand'], p['name'], v['color'], v['presentation']]
            for column, value in enumerate(values, start=1):
                _put(ws, row, column, value, as_text=(column == 1))
    ws.auto_filter.ref = f'A1:{ws.cell(row=1, column=len(IMPORT_COLUMNS)).column_letter}{row}'

    # --- Detalle: una fila por producto, solo de consulta ---
    detail = wb.create_sheet(DETAIL_SHEET)
    _style_header(detail, DETAIL_COLUMNS, DETAIL_WIDTHS)
    for r, p in enumerate(products, start=2):
        values = [p['id'], p['name'], p['brand'], p['category'], p['subcategory'], p['sku'],
                  'Activo' if p['active'] else 'Inactivo', 'Sí' if p['featured'] else 'No', ', '.join(p['presentations']),
                  p['colors'], len(p['variants']), sum(1 for v in p['variants'] if v['code']), p['yield'],
                  p['description'], p['technical_description']]
        for column, value in enumerate(values, start=1):
            cell = _put(detail, r, column, value, as_text=(column == 6))
            cell.alignment = Alignment(vertical='top')
    detail.freeze_panes = 'C2'
    detail.auto_filter.ref = f'A1:{detail.cell(row=1, column=len(DETAIL_COLUMNS)).column_letter}{max(len(products) + 1, 2)}'

    wb.active = 0   # se abre en la hoja Productos
    return wb
